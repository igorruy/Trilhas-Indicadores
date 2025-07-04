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
from datetime import datetime
import email
from email.message import EmailMessage
import base64
import imgkit
from html2image import Html2Image
import traceback
from PIL import Image, ImageChops
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time
import asyncio
from pyppeteer import launch

st.set_page_config(page_title='Status da Construção das Trilhas', layout='wide')

st.title('STATUS DA CONSTRUÇÃO DAS TRILHAS')

col_upload1, col_upload2 = st.columns(2)
with col_upload1:
    uploaded_file = st.file_uploader('Selecione o arquivo Excel com as trilhas:', type=['xlsx'], key='uploader1')
with col_upload2:
    uploaded_file_itens = st.file_uploader('Selecione o arquivo Excel com os passos (aba Items):', type=['xlsx'], key='uploader2')

# Após os imports, adicione:
table_style = (
    'style="border-collapse:separate;border-spacing:0;width:100%;font-size:1rem;background:#fff;"'
)
th_style = (
    'style="background:#0074C1;color:#fff;padding:10px 6px;text-align:center;border-bottom:2px solid #e0e0e0;font-weight:600;"'
)
td_style = (
    'style="padding:10px 6px;text-align:center;border-bottom:1px solid #f0f0f0;"'
)
def zebra_table(html):
    # Ajustar para que o nome do índice fique na linha do cabeçalho
    if '<th></th>' in html and 'class="dataframe"' in html:
        idx_name = ''
        try:
            idx_name = html.split('<th></th>')[1].split('</tr>')[0].split('>')[1].split('<')[0]
        except:
            idx_name = ''
        if idx_name:
            html = html.replace('<th></th>', f'<th>{idx_name}</th>', 1)
    linhas = html.split('<tr>')
    if len(linhas) > 2 and ('Frente' in linhas[1] or 'Aprovador Responsável' in linhas[1]):
        linhas = [linhas[0]] + linhas[2:]
    resultado = [linhas[0]]
    for i, linha in enumerate(linhas[1:]):
        # Adiciona classe 'total-row' à última linha
        if i == len(linhas[1:]) - 1:
            resultado.append(f'<tr class="total-row">{linha}')
        else:
            resultado.append(f'<tr>{linha}')
    html = ''.join(resultado)
    html = html.replace('<table border="0" class="styled-table"', '<table')
    html = html.replace('<table ', '<table class="styled-table" ')
    return html

# Garantir que as variáveis existem, mesmo se não houver upload
resumo_frente_html = ''
resumo_aprovador_html = ''
status_aprov_html = ''
indicadores_gerais_html = ''
passos_equipes_html = ''
grafico_trilhas_base64 = ''
grafico_aprovador_base64 = ''
grafico_passos_equipes_base64 = ''
data_atual = ''

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

    # ... cálculo das variáveis ...
    # Calcule dias restantes para o prazo de entrega
    data_final = datetime(2025, 7, 18)
    dias_restantes = (data_final - datetime.now()).days
    # Corrigir o valor de 'Em andamento'
    if isinstance(df_filtrado, pd.DataFrame):
        total_trilhas = int(df_filtrado[col_trilha].nunique()) if col_trilha and col_trilha in df_filtrado.columns else 0
        aprovadas = int(df_filtrado[df_filtrado[col_status_aprov] == 'Aprovado'][col_trilha].nunique()) if col_trilha and col_status_aprov and col_trilha in df_filtrado.columns and col_status_aprov in df_filtrado.columns else 0
    else:
        total_trilhas = 0
        aprovadas = 0
    em_andamento = total_trilhas - aprovadas
    # Definir valores padrão para indicadores do ciclo anterior
    diff = 0
    perc = 0
    diff_var = 0
    perc_var = 0
    ciclo_anterior = ''
    total_aprovadas = 0
    total_aprovadas_var_dim = 0
    if ciclo:
        if col_ciclo and col_status_aprov and col_total_var_dim and col_trilha and col_ciclo in df.columns and col_status_aprov in df.columns and col_total_var_dim in df.columns:
            df_ciclo = df[(df[col_ciclo] == ciclo) & (df[col_status_aprov] == 'Aprovado')]
            total_aprovadas = df_ciclo[col_trilha].nunique()
            total_aprovadas_var_dim = int(df_ciclo[col_total_var_dim].sum())
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
    # --- CARDS/KPIs NO TOPO (VISUAL STREAMLIT) ---
    st.markdown('---')
    st.subheader('Indicadores Gerais')
    col_kpi1, col_kpi2, col_kpi3, col_kpi4, col_kpi5 = st.columns(5)
    col_kpi1.metric('Total de Trilhas', total_trilhas)
    col_kpi2.metric('Aprovadas', aprovadas)
    col_kpi3.metric('Em andamento', em_andamento)
    if isinstance(df_filtrado, pd.DataFrame) and col_status_aprov and col_status_aprov in df_filtrado.columns:
        percentual_aprov_geral = (df_filtrado[col_status_aprov] == 'Aprovado').sum() / len(df_filtrado) * 100 if len(df_filtrado) > 0 else 0
    else:
        percentual_aprov_geral = 0
    col_kpi4.metric('% Aprovação Geral', f'{percentual_aprov_geral:.1f}%')
    col_kpi5.metric('Restam dias para o prazo', dias_restantes, help='Prazo final: 18/07/2025')

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
                # Cálculo das diferenças
                diff_color = '#488432' if diff >= 0 else '#c10000'
                diff_var_color = '#488432' if diff_var >= 0 else '#c10000'
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
            'Em andamento': outros,
            'Total': total
        }).fillna(0).astype(int)
        resumo_frente['% Aprovado'] = 100 * resumo_frente['Aprovados'] / resumo_frente['Total']
        resumo_frente['% Em andamento'] = 100 * resumo_frente['Em andamento'] / resumo_frente['Total']
        # Formatar porcentagens para uma casa decimal
        resumo_frente['% Aprovado'] = resumo_frente['% Aprovado'].map(lambda x: f"{x:.1f}")
        resumo_frente['% Em andamento'] = resumo_frente['% Em andamento'].map(lambda x: f"{x:.1f}")
        resumo_frente = resumo_frente[['Aprovados', 'Em andamento', 'Total', '% Aprovado', '% Em andamento']]
        st.dataframe(resumo_frente)
        # Gráfico de barras empilhadas para %
        COLOR_VERDE = '#22B573'
        COLOR_AMARELO = '#FFD600'
        resumo_frente_plot = resumo_frente.copy()
        resumo_frente_plot['% Aprovado'] = resumo_frente_plot['% Aprovado'].astype(float)
        resumo_frente_plot['% Em andamento'] = resumo_frente_plot['% Em andamento'].astype(float)
        fig, ax = plt.subplots(figsize=(10, 5))
        x = np.arange(len(resumo_frente_plot.index))
        # Barras empilhadas
        bars1 = ax.bar(x, resumo_frente_plot['% Aprovado'], label='% Aprovado', color=COLOR_VERDE)
        bars2 = ax.bar(x, resumo_frente_plot['% Em andamento'], bottom=resumo_frente_plot['% Aprovado'], label='% Em andamento', color=COLOR_AMARELO)
        ax.set_xticks(x)
        ax.set_xticklabels(resumo_frente_plot.index, rotation=45, ha='right', fontsize=12)
        ax.set_ylabel('%', fontsize=13)
        ax.set_ylim(0, 100)
        ax.set_title('Percentual de Status por Frente', fontsize=15)
        ax.legend(fontsize=12)
        ax.grid(axis='y', linestyle='--', alpha=0.4)
        # Exibir valores nas barras empilhadas
        for i, (aprov, andamento) in enumerate(zip(resumo_frente_plot['% Aprovado'], resumo_frente_plot['% Em andamento'])):
            ax.annotate(f'{aprov:.1f}%',
                        xy=(i, aprov/2),
                        xytext=(0, 0),
                        textcoords="offset points",
                        ha='center', va='center', fontsize=11, color='black')
            ax.annotate(f'{andamento:.1f}%',
                        xy=(i, aprov + andamento/2),
                        xytext=(0, 0),
                        textcoords="offset points",
                        ha='center', va='center', fontsize=11, color='black')
        plt.tight_layout()
        st.pyplot(fig)
        # Após calcular resumo_frente, adicione linha de totais como última linha
        if not resumo_frente.empty:
            total_row = {
                'Aprovados': resumo_frente['Aprovados'].sum(),
                'Em andamento': resumo_frente['Em andamento'].sum(),
                'Total': resumo_frente['Total'].sum(),
                '% Aprovado': f"{resumo_frente['% Aprovado'].astype(float).mean():.1f}",
                '% Em andamento': f"{resumo_frente['% Em andamento'].astype(float).mean():.1f}"
            }
            resumo_frente.loc['Total'] = total_row
            resumo_frente = resumo_frente.reset_index()
            # Move 'Total' para última linha
            if 'index' in resumo_frente.columns:
                total_row_df = resumo_frente[resumo_frente['index'] == 'Total']
                resumo_frente = pd.concat([resumo_frente[resumo_frente['index'] != 'Total'], total_row_df], ignore_index=True)
                resumo_frente = resumo_frente.rename(columns={'index': ''})
        resumo_frente_html = zebra_table(resumo_frente.to_html(index=False, border=0, classes='styled-table')) if 'resumo_frente' in locals() else ''
    else:
        st.warning('Colunas de Frente ou Status não encontradas para resumo.')

    # --- TABELA RESUMO POR APROVADOR RESPONSÁVEL ---
    st.subheader('Resumo por Aprovador Responsável')
    if col_dono and col_status_aprov and col_dono in df_filtrado.columns and col_status_aprov in df_filtrado.columns:
        aprovados_aprov = df_filtrado[df_filtrado[col_status_aprov] == 'Aprovado'].groupby(col_dono)[col_trilha].count()
        outros_aprov = df_filtrado[df_filtrado[col_status_aprov] != 'Aprovado'].groupby(col_dono)[col_trilha].count()
        total_aprov = df_filtrado.groupby(col_dono)[col_trilha].count()
        resumo_aprovador = pd.DataFrame({
            'Aprovados': aprovados_aprov,
            'Em andamento': outros_aprov,
            'Total': total_aprov
        }).fillna(0).astype(int)
        resumo_aprovador['% Aprovado'] = 100 * resumo_aprovador['Aprovados'] / resumo_aprovador['Total']
        resumo_aprovador['% Em andamento'] = 100 * resumo_aprovador['Em andamento'] / resumo_aprovador['Total']
        # Formatar porcentagens para uma casa decimal
        resumo_aprovador['% Aprovado'] = resumo_aprovador['% Aprovado'].map(lambda x: f"{x:.1f}")
        resumo_aprovador['% Em andamento'] = resumo_aprovador['% Em andamento'].map(lambda x: f"{x:.1f}")
        resumo_aprovador = resumo_aprovador[['Aprovados', 'Em andamento', 'Total', '% Aprovado', '% Em andamento']]
        st.dataframe(resumo_aprovador)
        # Gráfico de barras empilhadas para %
        resumo_aprovador_plot = resumo_aprovador.copy()
        resumo_aprovador_plot['% Aprovado'] = resumo_aprovador_plot['% Aprovado'].astype(float)
        resumo_aprovador_plot['% Em andamento'] = resumo_aprovador_plot['% Em andamento'].astype(float)
        fig4, ax4 = plt.subplots(figsize=(10, 5))
        x = np.arange(len(resumo_aprovador_plot.index))
        # Barras empilhadas
        bars1 = ax4.bar(x, resumo_aprovador_plot['% Aprovado'], label='% Aprovado', color=COLOR_VERDE)
        bars2 = ax4.bar(x, resumo_aprovador_plot['% Em andamento'], bottom=resumo_aprovador_plot['% Aprovado'], label='% Em andamento', color=COLOR_AMARELO)
        ax4.set_xticks(x)
        ax4.set_xticklabels(resumo_aprovador_plot.index, rotation=45, ha='right', fontsize=12)
        ax4.set_ylabel('%', fontsize=13)
        ax4.set_ylim(0, 100)
        ax4.set_title('Percentual de Status por Aprovador Responsável', fontsize=15)
        ax4.legend(fontsize=12)
        ax4.grid(axis='y', linestyle='--', alpha=0.4)
        # Exibir valores nas barras empilhadas
        for i, (aprov, andamento) in enumerate(zip(resumo_aprovador_plot['% Aprovado'], resumo_aprovador_plot['% Em andamento'])):
            ax4.annotate(f'{aprov:.1f}%',
                        xy=(i, aprov/2),
                        xytext=(0, 0),
                        textcoords="offset points",
                        ha='center', va='center', fontsize=11, color='black')
            ax4.annotate(f'{andamento:.1f}%',
                        xy=(i, aprov + andamento/2),
                        xytext=(0, 0),
                        textcoords="offset points",
                        ha='center', va='center', fontsize=11, color='black')
        plt.tight_layout()
        st.pyplot(fig4)
        # Após calcular resumo_aprovador, adicione linha de totais como última linha
        if not resumo_aprovador.empty:
            total_row = {
                'Aprovados': resumo_aprovador['Aprovados'].sum(),
                'Em andamento': resumo_aprovador['Em andamento'].sum(),
                'Total': resumo_aprovador['Total'].sum(),
                '% Aprovado': f"{resumo_aprovador['% Aprovado'].astype(float).mean():.1f}",
                '% Em andamento': f"{resumo_aprovador['% Em andamento'].astype(float).mean():.1f}"
            }
            resumo_aprovador.loc['Total'] = total_row
            resumo_aprovador = resumo_aprovador.reset_index()
            # Move 'Total' para última linha
            if 'index' in resumo_aprovador.columns:
                total_row_df = resumo_aprovador[resumo_aprovador['index'] == 'Total']
                resumo_aprovador = pd.concat([resumo_aprovador[resumo_aprovador['index'] != 'Total'], total_row_df], ignore_index=True)
                resumo_aprovador = resumo_aprovador.rename(columns={'index': ''})
        resumo_aprovador_html = zebra_table(resumo_aprovador.to_html(index=False, border=0, classes='styled-table')) if 'resumo_aprovador' in locals() else ''
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
    # Renomear a coluna do DataFrame inteiro de "Passos Outros Status" para "Passos Em andamento"
    passos_equipes = passos_equipes.rename(columns={'Passos Outros Status': 'Passos Em andamento'})
    # Adicione linha de totais como última linha em Passos por Equipe
    if not passos_equipes.empty:
        total_row = {
            'Team': 'Total',
            'Passos Aprovados': passos_equipes['Passos Aprovados'].sum(),
            'Passos Em andamento': passos_equipes['Passos Em andamento'].sum()
        }
        passos_equipes = pd.concat([passos_equipes[passos_equipes['Team'] != 'Total'], pd.DataFrame([total_row])], ignore_index=True)
    st.dataframe(passos_equipes)
    # Gráfico de barras agrupadas
    fig3, ax3 = plt.subplots(figsize=(10, 5))
    x = np.arange(len(passos_equipes['Team']))
    width = 0.35
    bars1 = ax3.bar(x - width/2, passos_equipes['Passos Aprovados'], width, label='Passos Aprovados', color='green')
    bars2 = ax3.bar(x + width/2, passos_equipes['Passos Em andamento'], width, label='Passos Em andamento', color='orange')
    ax3.set_xticks(x)
    ax3.set_xticklabels(passos_equipes['Team'], rotation=45, ha='right', fontsize=11)
    ax3.set_ylabel('Quantidade de Passos')
    ax3.set_title('Quantidade de Passos por Equipe')
    ax3.legend()
    plt.subplots_adjust(bottom=0.22)
    # Adicionar totalizadores acima das barras (padrão: fonte preta, normal)
    for bar in bars1:
        height = bar.get_height()
        ax3.annotate(f'{int(height)}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=11, color='black')
    for bar in bars2:
        height = bar.get_height()
        ax3.annotate(f'{int(height)}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=11, color='black')
    st.pyplot(fig3)

    # --- Ajustar cores dos gráficos ---
    COLOR_AZUL = '#0074C1'
    COLOR_VERMELHO = '#C10000'

    # --- Botões de download ---
    st.markdown('---')
    st.subheader('Exportar Relatório')

    # Salvar gráficos principais como imagem para embutir no HTML
    fig.savefig('grafico_trilhas.png')
    with open('grafico_trilhas.png', 'rb') as img_file:
        grafico_trilhas_base64 = base64.b64encode(img_file.read()).decode('utf-8')
    fig4.savefig('grafico_aprovador.png')
    with open('grafico_aprovador.png', 'rb') as img_file:
        grafico_aprovador_base64 = base64.b64encode(img_file.read()).decode('utf-8')
    fig3.savefig('grafico_passos_equipes.png')
    with open('grafico_passos_equipes.png', 'rb') as img_file:
        grafico_passos_equipes_base64 = base64.b64encode(img_file.read()).decode('utf-8')
    # Tabelas em HTML
    status_aprov_html = zebra_table(status_aprov.to_html(index=True, border=0, classes='styled-table')) if 'status_aprov' in locals() else ''
    passos_equipes_html = zebra_table(passos_equipes.to_html(index=False, border=0, classes='styled-table')) if 'passos_equipes' in locals() else ''
    # Adicionar todas as seções no HTML exportado
    with open('public/sipal_logo.png', 'rb') as img_file:
        logo_base64 = base64.b64encode(img_file.read()).decode('utf-8')
    # Gerar indicadores_gerais_html para exportação
    indicadores_gerais_html = f'''
    <div class="section" style="margin-top:0;margin-bottom:24px;">
        <div class="section-title" style="font-size:1.25em;margin-bottom:16px;">Comparativo com ciclo anterior</div>
        <div style="display:flex;gap:18px;flex-wrap:wrap;justify-content:center;">
            <div style="flex:1 1 260px;min-width:220px;max-width:320px;background:#f9fafb;border:1.5px solid #e5e7eb;border-radius:12px;padding:18px 12px;text-align:center;">
                <div style="font-size:1.1em;color:#022928;font-weight:600;">Trilhas Aprovadas</div>
                <div style="font-size:2em;font-weight:bold;color:#488432;">{total_aprovadas}</div>
                <div style="font-size:1em;color:#64748b;">{ciclo}</div>
                <div style="margin-top:8px;font-size:1em;color:{'#488432' if diff>=0 else '#c10000'};">{diff:+d} ({perc:.1f}%){' vs ' + ciclo_anterior if ciclo_anterior else ''}</div>
            </div>
            <div style="flex:1 1 260px;min-width:220px;max-width:320px;background:#f9fafb;border:1.5px solid #e5e7eb;border-radius:12px;padding:18px 12px;text-align:center;">
                <div style="font-size:1.1em;color:#022928;font-weight:600;">Trilhas Aprovadas c/ Variações e Dimensões</div>
                <div style="font-size:2em;font-weight:bold;color:#3cb5c7;">{total_aprovadas_var_dim}</div>
                <div style="font-size:1em;color:#64748b;">{ciclo}</div>
                <div style="margin-top:8px;font-size:1em;color:{'#488432' if diff_var>=0 else '#c10000'};">{diff_var:+d} ({perc_var:.1f}%){' vs ' + ciclo_anterior if ciclo_anterior else ''}</div>
            </div>
        </div>
    </div>
    '''
    # Garantir data de geração do relatório
    data_atual = datetime.now().strftime('%d/%m/%Y %H:%M')
    html_content = f'''
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="utf-8">
        <title>Status da Construção das Trilhas - Ciclo 3</title>
        <style>
            body {{ margin: 0 !important; background: #fff !important; font-family: Arial, Helvetica, sans-serif; }}
            .container {{ margin: 0 auto !important; max-width: 900px; background: #fff; border-radius: 18px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); overflow: hidden; padding-bottom: 32px; border-left: 2px solid #e0e7ef; border-right: 2px solid #e0e7ef; border-top: none; border-bottom: none; min-height: 3000px !important; }}
            .header {{ background: #022928; color: #fff; padding: 32px 32px 16px 32px; text-align: center; }}
            .header-title {{ font-size: 2.3em; font-weight: 700; margin-bottom: 8px; }}
            .header-logo {{ max-width: 110px; max-height: 80px; display: block; margin: 0 auto 12px auto; }}
            .kpi-grid-wrapper {{ width: 100%; display: flex; justify-content: center; }}
            .kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px; margin: 32px 0 24px 0; width: 100%; }}
            .kpi-card {{ text-align: center; padding: 18px 8px 12px 8px; border-radius: 10px; border: 1px solid #f0f0f0; background: #f9fafb; }}
            .kpi-total {{ background: #f9fafb; color: #374151; border-color: #e5e7eb; }}
            .kpi-aprov {{ background: #ecfdf5; color: #22B573; border-color: #bbf7d0; }}
            .kpi-exec {{ background: #f0f9ff; color: #3cb5c7; border-color: #bae6fd; }}
            .kpi-bloq {{ background: #fef2f2; color: #c10000; border-color: #fecaca; }}
            .kpi-pend {{ background: #f9fafb; color: #64748b; border-color: #e5e7eb; }}
            .kpi-perc {{ background: #f0fdf4; color: #488432; border-color: #bbf7d0; }}
            .kpi-dias {{ background: #f0f9ff; color: #022928; border-color: #bae6fd; }}
            .kpi-value {{ font-size: 1.7em; font-weight: bold; margin-bottom: 2px; }}
            .kpi-label {{ font-size: 0.95em; color: inherit; font-weight: 500; }}
            .section {{ margin: 0 24px 36px 24px; background: #fff; border-radius: 12px; padding: 32px 24px 24px 24px; box-shadow: 0 2px 8px #0001; }}
            .section-title {{ color: #022928; font-size: 1.6em; font-weight: 700; margin-bottom: 18px; }}
            .table-container {{ background: #fff; border-radius: 10px; box-shadow: 0 1px 4px #0001; padding: 18px 8px 8px 8px; margin-bottom: 24px; overflow-x: auto; }}
            .img-container {{ text-align: center; margin: 32px 0 0 0; }}
            .img-container img {{ max-width: 100%; border-radius: 10px; box-shadow: 0 2px 8px #0001; }}
            .footer {{ background: #f1f5f9; padding: 20px 30px; text-align: center; color: #64748b; font-size: 0.95em; border-top: 1px solid #e2e8f0; }}
            .table-container table {{ width: 100%; border-collapse: separate; border-spacing: 0; background: #fff; border-radius: 12px; overflow: hidden; font-size: 1em; margin: 0; box-shadow: 0 1px 4px #0001; }}
            .table-container th {{ background: #022928; color: #fff; padding: 12px 8px; text-align: center; font-weight: 700; border-bottom: 2px solid #e0e0e0; }}
            .table-container td {{ padding: 12px 8px; text-align: center; border-bottom: 1px solid #f0f0f0; background: #fff; }}
            .table-container tr:nth-child(even) td {{ background: #f4f8fb; }}
            .table-container tr:hover td {{ background: #e6f7f1; }}
            .table-container tr:last-child td,
            .table-container tr.total-row td {{ background: #e6f7f1 !important; font-weight: bold; color: #022928; }}
            .table-container tr:last-child td {{ border-bottom: none; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <img src="data:image/png;base64,{logo_base64}" alt="Logo SIPAL Digital" class="header-logo" />
                <div class="header-title">STATUS DA CONSTRUÇÃO DAS TRILHAS</div>
            </div>
            <div class="kpi-grid-wrapper">
              <div class="kpi-grid">
                <div class="kpi-card kpi-total">
                    <div class="kpi-value">{total_trilhas}</div>
                    <div class="kpi-label">Total de Trilhas</div>
                </div>
                <div class="kpi-card kpi-aprov">
                    <div class="kpi-value">{aprovadas}</div>
                    <div class="kpi-label">Aprovadas</div>
                </div>
                <div class="kpi-card kpi-exec">
                    <div class="kpi-value">{em_andamento}</div>
                    <div class="kpi-label">Em andamento</div>
                </div>
                <div class="kpi-card kpi-perc">
                    <div class="kpi-value">{percentual_aprov_geral:.1f}%</div>
                    <div class="kpi-label">% Aprovação Geral</div>
                </div>
                <div class="kpi-card kpi-dias">
                    <div class="kpi-value">{dias_restantes}</div>
                    <div class="kpi-label">Restam dias para o prazo<br><span style='font-size:0.9em;color:#3cb5c7;'>(18/07/2025)</span></div>
                </div>
              </div>
            </div>
            {indicadores_gerais_html}
            <div class="section">
                <div class="section-title">Status de Aprovação</div>
                <div class="table-container">{status_aprov_html}</div>
            </div>
            <div class="section">
                <div class="section-title">Resumo por Frente</div>
                <div class="table-container">{resumo_frente_html}</div>
                <div style="font-size:0.98em;color:#64748b;margin:8px 0 0 4px;"><em>* Listado apenas Frentes com trilhas criadas para o ciclo</em></div>
                <div class="img-container"><img src="data:image/png;base64,{grafico_trilhas_base64}" /></div>
            </div>
            <div class="section">
                <div class="section-title">Resumo por Aprovador Responsável</div>
                <div class="table-container">{resumo_aprovador_html}</div>
                <div style="font-size:0.98em;color:#64748b;margin:8px 0 0 4px;"><em>* Listado apenas Donos de Processo com trilhas definidas em seu nome</em></div>
                <div class="img-container"><img src="data:image/png;base64,{grafico_aprovador_base64}" /></div>
            </div>
            <div class="section">
                <div class="section-title">Passos por Equipe</div>
                <div class="table-container">{passos_equipes_html}</div>
                <div class="img-container"><img src="data:image/png;base64,{grafico_passos_equipes_base64}" /></div>
            </div>
            <div class="footer">
                Relatório gerado automaticamente em {data_atual}.<br/>
                <span style="color:#022928;font-weight:bold;">SIPAL +DIGITAL</span>
            </div>
        </div>
    </body>
    </html>
    '''
    # Ajuste no CSS do HTML para remover margens externas e garantir altura suficiente
    html_content = html_content.replace('body {', 'body { margin: 0 !important; background: #fff !important;')
    html_content = html_content.replace('.container {', '.container { margin: 0 auto !important; min-height: 3000px !important;')
    with open('relatorio_trilhas.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    with open('relatorio_trilhas.html', 'rb') as f:
        col_html, col_eml = st.columns(2)
        with col_html:
            st.download_button(
                label="Baixar HTML Completo",
                data=html_content,
                file_name="relatorio_trilhas.html",
                mime="text/html",
                key="download_html"
            )
        with col_eml:
            msg = EmailMessage()
            msg['Subject'] = "Status da Construção das Trilhas"
            msg['From'] = "seu@email.com"
            msg['To'] = "destinatario@email.com"
            msg.set_content("Seu cliente de e-mail não suporta HTML. Veja o relatório em anexo.")
            msg.add_alternative(html_content, subtype='html')
            eml_bytes = msg.as_bytes()
            st.download_button(
                label="Baixar E-mail (EML)",
                data=eml_bytes,
                file_name="relatorio_trilhas.eml",
                mime="message/rfc822",
                key="download_eml"
            )
    st.success('Relatório exportado como HTML completo!')