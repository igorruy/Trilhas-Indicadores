import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
import io
import numpy as np
import plotly.graph_objects as go
from PIL import ImageGrab
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import tempfile
import os
import pdfkit

st.set_page_config(page_title='Status da Construção das Trilhas', layout='wide')

st.title('STATUS DA CONSTRUÇÃO DAS TRILHAS')

col_upload1, col_upload2 = st.columns(2)
with col_upload1:
    uploaded_file = st.file_uploader('Selecione o arquivo Excel com as trilhas:', type=['xlsx'], key='uploader1')
with col_upload2:
    uploaded_file_itens = st.file_uploader('Selecione o arquivo Excel com os passos (aba Items):', type=['xlsx'], key='uploader2')

if uploaded_file and uploaded_file_itens:
    df = pd.read_excel(uploaded_file, sheet_name='Trilhas Detalhadas')
    df_itens = pd.read_excel(uploaded_file_itens, sheet_name='Items')

    # Extrair trilha do campo Deliverable (antes do ponto)
    df_itens['Trilha'] = df_itens['Deliverable'].astype(str).str.split('.').str[0]
    # Contar passos por trilha
    passos_por_trilha = df_itens.groupby('Trilha').size().reset_index(name='Qtd Passos')
    # Contar passos por equipe
    passos_por_equipe = df_itens.groupby('Team').size().reset_index(name='Qtd Passos')

    # Função para buscar coluna por similaridade
    def encontrar_coluna(possibilidades, colunas):
        for p in possibilidades:
            for c in colunas:
                if isinstance(c, str) and p.lower() == c.lower().strip():
                    return c
        return None

    # Possíveis nomes para as colunas principais (ajustado conforme mapeamento do usuário)
    col_dono = encontrar_coluna([
        'Aprovador Responsável', 'Dono de Processo', 'Dono Processo', 'Dono do Processo', 'Dono de processo', 'Dono de Processo '], list(df.columns))
    col_frente = encontrar_coluna(['Frente'], list(df.columns))
    col_ciclo = encontrar_coluna(['Ciclo de Teste', 'Ciclo'], list(df.columns))
    col_trilha = encontrar_coluna(['ID da Trilha', 'Trilha'], list(df.columns))
    col_total_var_dim = encontrar_coluna(['Total (Trilha + Variações) Dimensões', 'Total (Trilha + Variações) Dimensão'], list(df.columns))
    col_status_aprov = encontrar_coluna(['Status', 'Status Aprovação', 'Status de Aprovação'], list(df.columns))

    # Adicionar coluna de trilha base (prefixo) na planilha principal
    if col_trilha and col_trilha in df.columns:
        df['Trilha_Base'] = df[col_trilha].astype(str).str.split('.').str[0]
    else:
        df['Trilha_Base'] = ''

    # Merge para trazer quantidade de passos para cada trilha
    df = df.merge(passos_por_trilha, left_on='Trilha_Base', right_on='Trilha', how='left')
    df['Qtd Passos'] = df['Qtd Passos'].fillna(0).astype(int)

    # Filtros dinâmicos combinados
    col1, col2, col3 = st.columns(3)
    with col1:
        dono_processo = st.multiselect('Aprovador Responsável', options=sorted(df[col_dono].dropna().unique()) if (col_dono and isinstance(col_dono, str) and col_dono in df.columns) else [])
    with col2:
        frente = st.multiselect('Frente', options=sorted(df[col_frente].dropna().unique()) if (col_frente and isinstance(col_frente, str) and col_frente in df.columns) else [])
    with col3:
        ciclo_options = sorted(df[col_ciclo].dropna().unique()) if (col_ciclo and isinstance(col_ciclo, str) and col_ciclo in df.columns) else []
        ciclo = st.selectbox('Ciclo de Teste', options=ciclo_options)

    # Aplicar filtros combinados (se algum filtro estiver selecionado)
    df_filtrado = df.copy()
    if col_dono and isinstance(col_dono, str) and col_dono in df_filtrado.columns and dono_processo:
        df_filtrado = df_filtrado[df_filtrado[col_dono].isin(dono_processo)]
    if col_frente and isinstance(col_frente, str) and col_frente in df_filtrado.columns and frente:
        df_filtrado = df_filtrado[df_filtrado[col_frente].isin(frente)]
    if col_ciclo and isinstance(col_ciclo, str) and col_ciclo in df_filtrado.columns and ciclo:
        df_filtrado = df_filtrado[df_filtrado[col_ciclo] == ciclo]

    # --- CARDS/KPIs NO TOPO ---
    if ciclo:
        st.markdown('---')
        st.subheader('Indicadores de Trilhas Aprovadas')
        if col_ciclo and col_status_aprov and col_total_var_dim and col_trilha and col_ciclo in df.columns and col_status_aprov in df.columns and col_total_var_dim in df.columns:
            # Ciclo atual
            df_ciclo = df[(df[col_ciclo] == ciclo) & (df[col_status_aprov] == 'Aprovado')]
            total_aprovadas = df_ciclo[col_trilha].nunique()
            total_aprovadas_var_dim = int(df_ciclo[col_total_var_dim].sum())
            # Ciclo anterior
            idx_ciclo = ciclo_options.index(ciclo)
            if idx_ciclo > 0:
                ciclo_anterior = ciclo_options[idx_ciclo - 1]
                df_ciclo_ant = df[(df[col_ciclo] == ciclo_anterior) & (df[col_status_aprov] == 'Aprovado')]
                total_aprovadas_ant = df_ciclo_ant[col_trilha].nunique()
                total_aprovadas_var_dim_ant = int(df_ciclo_ant[col_total_var_dim].sum())
                diff = total_aprovadas - total_aprovadas_ant
                perc = (diff / total_aprovadas_ant * 100) if total_aprovadas_ant else 0
                diff_var = total_aprovadas_var_dim - total_aprovadas_var_dim_ant
                perc_var = (diff_var / total_aprovadas_var_dim_ant * 100) if total_aprovadas_var_dim_ant else 0
                col_kpi1, col_kpi2 = st.columns(2)
                col_kpi1.metric(f'Trilhas Aprovadas - {ciclo}', total_aprovadas, f"{diff} ({perc:.1f}%) vs {ciclo_anterior}")
                col_kpi2.metric(f'Trilhas Aprovadas c/ Variações e Dimensões - {ciclo}', total_aprovadas_var_dim, f"{diff_var} ({perc_var:.1f}%) vs {ciclo_anterior}")
            else:
                col_kpi1, col_kpi2 = st.columns(2)
                col_kpi1.metric(f'Trilhas Aprovadas - {ciclo}', total_aprovadas)
                col_kpi2.metric(f'Trilhas Aprovadas c/ Variações e Dimensões - {ciclo}', total_aprovadas_var_dim)
        else:
            st.warning('Colunas de ciclo, status, trilha ou variações/dimensões não encontradas para KPIs.')

    # Exemplo de tabela de status de aprovação
    st.subheader('Status de Aprovação')
    if col_status_aprov and isinstance(col_status_aprov, str) and col_status_aprov in df_filtrado.columns:
        status_aprov = df_filtrado.groupby(col_status_aprov).size().reset_index(name='Quantidade')
        st.dataframe(status_aprov)
    else:
        st.warning('Coluna de status de aprovação não encontrada.')

    # --- TABELA RESUMO POR FRENTE ---
    st.subheader('Resumo por Frente')
    if col_frente and col_status_aprov and col_frente in df_filtrado.columns and col_status_aprov in df_filtrado.columns:
        # Calcular aprovados e outros status
        aprovados = df_filtrado[df_filtrado[col_status_aprov] == 'Aprovado'].groupby(col_frente)[col_trilha].count()
        outros = df_filtrado[df_filtrado[col_status_aprov] != 'Aprovado'].groupby(col_frente)[col_trilha].count()
        total = df_filtrado.groupby(col_frente)[col_trilha].count()
        resumo_frente = pd.DataFrame({
            'Aprovados': aprovados,
            'Outros Status': outros,
            'Total': total
        }).fillna(0).astype(int)
        resumo_frente['% Aprovado'] = 100 * resumo_frente['Aprovados'] / resumo_frente['Total']
        resumo_frente['% Outros Status'] = 100 * resumo_frente['Outros Status'] / resumo_frente['Total']
        resumo_frente = resumo_frente[['Aprovados', 'Outros Status', 'Total', '% Aprovado', '% Outros Status']]
        st.dataframe(resumo_frente)
        # Gráfico de barras agrupadas para %
        fig, ax = plt.subplots(figsize=(10, 5))
        x = np.arange(len(resumo_frente.index))
        width = 0.35
        ax.bar(x - width/2, resumo_frente['% Aprovado'], width, label='% Aprovado', color='green')
        ax.bar(x + width/2, resumo_frente['% Outros Status'], width, label='% Outros Status', color='orange')
        ax.set_xticks(x)
        ax.set_xticklabels(resumo_frente.index, rotation=45, ha='right')
        ax.set_ylabel('%')
        ax.set_title('Percentual de Status por Frente')
        ax.legend()
        st.pyplot(fig)
    else:
        st.warning('Colunas de Frente ou Status não encontradas para resumo.')

    # --- INDICADORES DE TOTAL DE TRILHAS E PASSOS ---
    st.subheader('Indicadores Gerais')
    colA, colB = st.columns(2)
    with colA:
        if col_trilha and col_trilha in df_filtrado.columns:
            st.metric('Total de Trilhas', int(df_filtrado[col_trilha].nunique()))
    with colB:
        if 'Total de Passos' in df_filtrado.columns:
            st.metric('Total de Passos', int(df_filtrado['Total de Passos'].sum()))

    # --- TABELA RESUMO POR APROVADOR RESPONSÁVEL ---
    st.subheader('Resumo por Aprovador Responsável')
    if col_dono and col_status_aprov and col_dono in df_filtrado.columns and col_status_aprov in df_filtrado.columns:
        aprovados_aprov = df_filtrado[df_filtrado[col_status_aprov] == 'Aprovado'].groupby(col_dono)[col_trilha].count()
        outros_aprov = df_filtrado[df_filtrado[col_status_aprov] != 'Aprovado'].groupby(col_dono)[col_trilha].count()
        total_aprov = df_filtrado.groupby(col_dono)[col_trilha].count()
        resumo_aprovador = pd.DataFrame({
            'Aprovados': aprovados_aprov,
            'Outros Status': outros_aprov,
            'Total': total_aprov
        }).fillna(0).astype(int)
        resumo_aprovador['% Aprovado'] = 100 * resumo_aprovador['Aprovados'] / resumo_aprovador['Total']
        resumo_aprovador['% Outros Status'] = 100 * resumo_aprovador['Outros Status'] / resumo_aprovador['Total']
        resumo_aprovador = resumo_aprovador[['Aprovados', 'Outros Status', 'Total', '% Aprovado', '% Outros Status']]
        st.dataframe(resumo_aprovador)
        # Gráfico de barras agrupadas para %
        fig4, ax4 = plt.subplots(figsize=(10, 5))
        x = np.arange(len(resumo_aprovador.index))
        width = 0.35
        ax4.bar(x - width/2, resumo_aprovador['% Aprovado'], width, label='% Aprovado', color='green')
        ax4.bar(x + width/2, resumo_aprovador['% Outros Status'], width, label='% Outros Status', color='orange')
        ax4.set_xticks(x)
        ax4.set_xticklabels(resumo_aprovador.index, rotation=45, ha='right')
        ax4.set_ylabel('%')
        ax4.set_title('Percentual de Status por Aprovador Responsável')
        ax4.legend()
        st.pyplot(fig4)
    else:
        st.warning('Colunas de Aprovador ou Status não encontradas para resumo.')

    # --- ALERTAS VISUAIS ---
    if col_status_aprov and col_status_aprov in df_filtrado.columns:
        taxa_aprov = (df_filtrado[col_status_aprov] == 'Aprovado').sum() / len(df_filtrado) * 100 if len(df_filtrado) > 0 else 0
        if taxa_aprov < 50:
            st.error(f'Atenção: Baixa taxa de aprovação geral ({taxa_aprov:.1f}%)!')
        elif taxa_aprov < 80:
            st.warning(f'Alerta: Taxa de aprovação moderada ({taxa_aprov:.1f}%)')
        else:
            st.success(f'Taxa de aprovação saudável ({taxa_aprov:.1f}%)')

    # Nova tabela e gráfico de passos por Equipe
    st.subheader('Passos por Equipe')
    # Mapear status das trilhas aprovadas
    trilhas_aprovadas = set(df[df[col_status_aprov] == 'Aprovado']['Trilha_Base'])
    df_itens['Aprovado'] = df_itens['Trilha'].isin(trilhas_aprovadas)
    passos_aprovados = df_itens[df_itens['Aprovado']].groupby('Team').size().reset_index(name='Passos Aprovados')
    passos_outros = df_itens[~df_itens['Aprovado']].groupby('Team').size().reset_index(name='Passos Outros Status')
    passos_equipes = pd.merge(passos_aprovados, passos_outros, on='Team', how='outer').fillna(0)
    passos_equipes['Passos Aprovados'] = passos_equipes['Passos Aprovados'].astype(int)
    passos_equipes['Passos Outros Status'] = passos_equipes['Passos Outros Status'].astype(int)
    st.dataframe(passos_equipes)
    # Gráfico de barras agrupadas
    fig3, ax3 = plt.subplots(figsize=(10, 5))
    x = np.arange(len(passos_equipes['Team']))
    width = 0.35
    ax3.bar(x - width/2, passos_equipes['Passos Aprovados'], width, label='Passos Aprovados', color='green')
    ax3.bar(x + width/2, passos_equipes['Passos Outros Status'], width, label='Passos Outros Status', color='orange')
    ax3.set_xticks(x)
    ax3.set_xticklabels(passos_equipes['Team'], rotation=45, ha='right')
    ax3.set_ylabel('Quantidade de Passos')
    ax3.set_title('Quantidade de Passos por Equipe')
    ax3.legend()
    st.pyplot(fig3)

    # --- Ajustar cores dos gráficos ---
    COLOR_AZUL = '#0074C1'
    COLOR_AMARELO = '#FFD600'
    COLOR_VERMELHO = '#C10000'
    COLOR_VERDE = '#22B573'

    # Exemplo de uso das cores em gráficos matplotlib:
    # ax.bar(..., color=COLOR_AZUL)
    # Para gráficos de status, use as cores conforme o status
    # Exemplo para gráfico de barras agrupadas:
    # ax.bar(x - width/2, resumo_frente['% Aprovado'], width, label='% Aprovado', color=COLOR_VERDE)
    # ax.bar(x + width/2, resumo_frente['% Outros Status'], width, label='% Outros Status', color=COLOR_VERMELHO)

    # --- Botões de download ---
    st.markdown('---')
    st.subheader('Exportar Relatório')

    # Salvar gráficos principais como imagem para embutir no HTML
    fig.savefig('grafico_trilhas.png')
    grafico_trilhas_base64 = ''
    with open('grafico_trilhas.png', 'rb') as img_file:
        import base64
        grafico_trilhas_base64 = base64.b64encode(img_file.read()).decode('utf-8')

    # Exportar como HTML estilizado com todos os indicadores
    if st.button('Exportar como HTML (Completo)'):
        html_content = f'''
        <html>
        <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; background: #f5f5f5; }}
            .header {{ display: flex; align-items: center; background: #fff; padding: 16px; border-radius: 10px; margin-bottom: 16px; }}
            .logo {{ width: 120px; height: 60px; background: #eee; border-radius: 8px; margin-right: 24px; display: flex; align-items: center; justify-content: center; font-weight: bold; color: #888; }}
            .title {{ font-size: 2rem; font-weight: bold; color: #0074C1; }}
            .kpi-row {{ display: flex; gap: 24px; margin-bottom: 16px; }}
            .kpi-card {{ background: #fff; border-radius: 10px; padding: 18px 32px; box-shadow: 0 2px 8px #0001; min-width: 200px; text-align: center; }}
            .kpi-label {{ font-size: 1.1rem; color: #888; }}
            .kpi-value {{ font-size: 2.2rem; font-weight: bold; color: #22B573; }}
            .kpi-diff {{ font-size: 1rem; color: #C10000; }}
            .section {{ background: #fff; border-radius: 10px; padding: 18px 24px; margin-bottom: 18px; box-shadow: 0 2px 8px #0001; }}
            h2 {{ color: #0074C1; }}
            table {{ border-collapse: collapse; width: 100%; margin: 12px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: center; }}
            th {{ background: #0074C1; color: #fff; }}
            .info-box {{ background: #FFD600; color: #222; border-radius: 8px; padding: 12px 18px; margin: 12px 0; font-weight: bold; }}
            .img-graph {{ width: 100%; max-width: 600px; margin: 0 auto; display: block; }}
        </style>
        </head>
        <body>
            <div class="header">
                <div class="logo">LOGO</div>
                <div class="title">STATUS DA CONSTRUÇÃO DAS TRILHAS</div>
            </div>
            <div class="kpi-row">
                <div class="kpi-card">
                    <div class="kpi-label">Trilhas Aprovadas - {ciclo}</div>
                    <div class="kpi-value">{total_aprovadas}</div>
                    <div class="kpi-diff">{diff if 'diff' in locals() else ''}</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Trilhas Aprovadas c/ Variações e Dimensões - {ciclo}</div>
                    <div class="kpi-value">{total_aprovadas_var_dim}</div>
                    <div class="kpi-diff">{diff_var if 'diff_var' in locals() else ''}</div>
                </div>
            </div>
            <div class="section">
                <h2>Status da Construção das Trilhas</h2>
                {resumo_frente.to_html(index=True) if 'resumo_frente' in locals() else ''}
            </div>
            <div class="section">
                <h2>Resumo por Aprovador Responsável</h2>
                {resumo_aprovador.to_html(index=True) if 'resumo_aprovador' in locals() else ''}
            </div>
            <div class="section">
                <h2>Gráfico de Status das Trilhas</h2>
                <img class="img-graph" src="data:image/png;base64,{grafico_trilhas_base64}" />
            </div>
            <div class="section">
                <h2>Passos por Equipe</h2>
                {passos_equipes.to_html(index=True) if 'passos_equipes' in locals() else ''}
            </div>
            <div class="info-box">
                INFORMATIVO: Espaço para mensagem customizada do projeto.
            </div>
            <div class="section">
                <b>Como enviar por e-mail:</b><br>
                1. Baixe este arquivo HTML.<br>
                2. Abra o arquivo no navegador.<br>
                3. Selecione todo o conteúdo (Ctrl+A), copie (Ctrl+C) e cole (Ctrl+V) no corpo do e-mail no Outlook.<br>
                <br>
                <a href="mailto:?subject=Status das Trilhas&body=Veja o relatório em anexo ou cole o HTML no corpo do e-mail.">Clique aqui para abrir o Outlook</a>
            </div>
        </body>
        </html>
        '''
        with open('relatorio_trilhas.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        with open('relatorio_trilhas.html', 'rb') as f:
            st.download_button('Baixar HTML Completo', f, file_name='relatorio_trilhas.html', mime='text/html')
        st.success('Relatório exportado como HTML completo!')

    # Exportar como PDF (usando pdfkit)
    if st.button('Exportar como PDF (Estilizado)'):
        # Gera o mesmo HTML estilizado e converte para PDF
        pdfkit.from_file('relatorio_trilhas.html', 'relatorio_trilhas.pdf')
        with open('relatorio_trilhas.pdf', 'rb') as f:
            st.download_button('Baixar PDF', f, file_name='relatorio_trilhas.pdf', mime='application/pdf')
        st.success('Relatório exportado como PDF!')

    # Exportar como Imagem (apenas gráficos principais)
    if st.button('Exportar Gráficos como Imagem (PNG)'):
        fig.savefig('grafico_trilhas.png')
        with open('grafico_trilhas.png', 'rb') as f:
            st.download_button('Baixar Gráfico PNG', f, file_name='grafico_trilhas.png', mime='image/png')
        st.success('Gráfico exportado como imagem PNG!')
else:
    st.info('Faça upload das duas planilhas Excel para visualizar o relatório.') 