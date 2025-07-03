import { useState } from "react";
import html2canvas from "html2canvas";
import jsPDF from "jspdf";
import { Button } from "@/components/ui/button";
import { ExportPreview } from "./ExportPreview";
import { toast } from "@/hooks/use-toast";
import { Download, FileText, Image, Mail, Eye } from "lucide-react";

interface ExportButtonsProps {
  dashboardRef: React.RefObject<HTMLDivElement>;
  currentData?: any;
}

export const ExportButtons = ({ dashboardRef, currentData }: ExportButtonsProps) => {
  const [isExporting, setIsExporting] = useState(false);

  // Função para exportar como HTML estilizado
  const exportAsHTML = async () => {
    setIsExporting(true);
    try {
      const htmlContent = generateHTMLReport(currentData);
      
      const blob = new Blob([htmlContent], { type: 'text/html;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `sipal_dashboard_${new Date().toISOString().split('T')[0]}.html`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      
      toast({
        title: "Sucesso",
        description: "Relatório HTML exportado com sucesso!",
      });
    } catch (error) {
      toast({
        title: "Erro",
        description: "Erro ao exportar HTML: " + (error as Error).message,
        variant: "destructive",
      });
    } finally {
      setIsExporting(false);
    }
  };

  // Função para exportar como PDF
  const exportAsPDF = async () => {
    if (!dashboardRef.current) return;
    
    setIsExporting(true);
    try {
      const canvas = await html2canvas(dashboardRef.current, {
        scale: 2,
        useCORS: true,
        allowTaint: true,
        backgroundColor: '#f5f5f5'
      });
      
      const imgData = canvas.toDataURL('image/png');
      const pdf = new jsPDF('p', 'mm', 'a4');
      
      const imgWidth = 210;
      const pageHeight = 295;
      const imgHeight = (canvas.height * imgWidth) / canvas.width;
      let heightLeft = imgHeight;
      let position = 0;

      // Adicionar primeira página
      pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
      heightLeft -= pageHeight;

      // Adicionar páginas adicionais se necessário
      while (heightLeft >= 0) {
        position = heightLeft - imgHeight;
        pdf.addPage();
        pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
        heightLeft -= pageHeight;
      }
      
      pdf.save(`sipal_dashboard_${new Date().toISOString().split('T')[0]}.pdf`);
      
      toast({
        title: "Sucesso",
        description: "Dashboard exportado como PDF com sucesso!",
      });
    } catch (error) {
      toast({
        title: "Erro",
        description: "Erro ao exportar PDF: " + (error as Error).message,
        variant: "destructive",
      });
    } finally {
      setIsExporting(false);
    }
  };

  // Função para exportar como imagem PNG
  const exportAsPNG = async () => {
    if (!dashboardRef.current) return;
    
    setIsExporting(true);
    try {
      const canvas = await html2canvas(dashboardRef.current, {
        scale: 2,
        useCORS: true,
        allowTaint: true,
        backgroundColor: '#f5f5f5'
      });
      
      const link = document.createElement('a');
      link.download = `sipal_dashboard_${new Date().toISOString().split('T')[0]}.png`;
      link.href = canvas.toDataURL();
      link.click();
      
      toast({
        title: "Sucesso",
        description: "Dashboard exportado como imagem com sucesso!",
      });
    } catch (error) {
      toast({
        title: "Erro",
        description: "Erro ao exportar imagem: " + (error as Error).message,
        variant: "destructive",
      });
    } finally {
      setIsExporting(false);
    }
  };

  // Função para abrir email com relatório
  const sendByEmail = () => {
    const subject = encodeURIComponent("Status da Construção das Trilhas - TI Ciclo 2");
    const body = encodeURIComponent(`
Olá,

Segue o relatório atualizado do Status da Construção das Trilhas - TI Ciclo 2.

Para visualizar o relatório completo, acesse: ${window.location.href}

Principais indicadores:
• 75,5% das trilhas aprovadas (492 de 652)
• Prazo prorrogado até 15/06
• Acompanhamento em tempo real disponível

Atenciosamente,
Equipe SIPAL Digital
    `);
    
    window.open(`mailto:?subject=${subject}&body=${body}`);
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-[var(--shadow-card)] mb-6">
      <h2 className="text-xl font-bold text-sipal-blue mb-4">Exportar Relatório</h2>
      <div className="flex flex-wrap gap-4 mb-4">
        <Button 
          onClick={exportAsHTML}
          disabled={isExporting}
          className="bg-sipal-blue hover:bg-sipal-blue-light"
        >
          <FileText className="w-4 h-4 mr-2" />
          {isExporting ? "Exportando..." : "Exportar HTML"}
        </Button>
        
        <Button 
          onClick={exportAsPDF}
          disabled={isExporting}
          variant="outline"
          className="border-sipal-blue text-sipal-blue hover:bg-sipal-blue hover:text-white"
        >
          <Download className="w-4 h-4 mr-2" />
          {isExporting ? "Exportando..." : "Exportar PDF"}
        </Button>
        
        <Button 
          onClick={exportAsPNG}
          disabled={isExporting}
          variant="outline"
          className="border-sipal-green text-sipal-green hover:bg-sipal-green hover:text-white"
        >
          <Image className="w-4 h-4 mr-2" />
          {isExporting ? "Exportando..." : "Exportar PNG"}
        </Button>
        
        <Button 
          onClick={sendByEmail}
          variant="outline"
          className="border-sipal-yellow text-gray-800 hover:bg-sipal-yellow"
        >
          <Mail className="w-4 h-4 mr-2" />
          Enviar por Email
        </Button>
        
        <ExportPreview 
          htmlContent={generateHTMLReport(currentData)} 
          title="Relatório HTML"
        />
      </div>
      
      <div className="mt-4 p-4 bg-sipal-gray/30 rounded-lg">
        <h4 className="font-bold text-sm mb-2">Como usar as exportações:</h4>
        <ul className="text-sm text-sipal-gray-dark space-y-1">
          <li><strong>HTML:</strong> Arquivo completo com estilos para visualização offline ou compartilhamento</li>
          <li><strong>PDF:</strong> Formato padrão para documentação e arquivamento</li>
          <li><strong>PNG:</strong> Imagem de alta qualidade para apresentações</li>
          <li><strong>Email:</strong> Abre o cliente de email com template pré-preenchido</li>
        </ul>
      </div>
    </div>
  );
};

// Função para gerar HTML completo do relatório
const generateHTMLReport = (data: any) => {
  const currentDate = new Date().toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });

  return `
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SIPAL - Status da Construção das Trilhas</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #f3f4f6 0%, #fefefe 100%);
            color: #333;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            display: flex;
            align-items: center;
            background: white;
            padding: 24px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0, 116, 193, 0.1);
            margin-bottom: 24px;
        }
        
        .logo {
            width: 80px;
            height: 80px;
            background: #0074C1;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            margin-right: 24px;
        }
        
        .title-section h1 {
            color: #0074C1;
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 8px;
        }
        
        .title-section p {
            color: #6b7280;
            font-size: 1rem;
        }
        
        .date-info {
            margin-left: auto;
            text-align: right;
            color: #6b7280;
            font-size: 0.9rem;
        }
        
        .kpi-section {
            display: grid;
            grid-template-columns: 1fr 2fr;
            gap: 24px;
            margin-bottom: 24px;
        }
        
        .kpi-card {
            background: #0074C1;
            color: white;
            padding: 32px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 8px 25px rgba(0, 116, 193, 0.15);
        }
        
        .kpi-title {
            font-size: 1rem;
            opacity: 0.9;
            margin-bottom: 16px;
        }
        
        .kpi-value {
            font-size: 4rem;
            font-weight: bold;
            margin-bottom: 8px;
        }
        
        .kpi-subtitle {
            font-size: 0.9rem;
            opacity: 0.8;
        }
        
        .info-card {
            background: #FFD600;
            color: #1f2937;
            padding: 24px;
            border-radius: 12px;
            border-left: 4px solid #f59e0b;
        }
        
        .info-card h4 {
            font-weight: bold;
            margin-bottom: 12px;
        }
        
        .section {
            background: white;
            padding: 24px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0, 116, 193, 0.1);
            margin-bottom: 24px;
        }
        
        .section h2 {
            color: #0074C1;
            font-size: 1.5rem;
            font-weight: bold;
            margin-bottom: 16px;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 16px 0;
        }
        
        th, td {
            border: 1px solid #d1d5db;
            padding: 12px;
            text-align: center;
        }
        
        th {
            background: #0074C1;
            color: white;
            font-weight: bold;
        }
        
        tr:nth-child(even) {
            background: #f9fafb;
        }
        
        tr:hover {
            background: #f3f4f6;
        }
        
        .status-approved {
            background: #22B573;
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: bold;
        }
        
        .percentage-high {
            color: #22B573;
            font-weight: bold;
        }
        
        .percentage-medium {
            color: #f59e0b;
            font-weight: bold;
        }
        
        .percentage-low {
            color: #dc2626;
            font-weight: bold;
        }
        
        .best-practices {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-around;
            gap: 20px;
            margin: 20px 0;
        }
        
        .practice-step {
            flex: 1;
            min-width: 200px;
            max-width: 250px;
            text-align: center;
        }
        
        .step-number {
            width: 48px;
            height: 48px;
            border-radius: 50%;
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 1.2rem;
            margin: 0 auto 16px;
        }
        
        .step-1 { background: #8b5cf6; }
        .step-2 { background: #06b6d4; }
        .step-3 { background: #10b981; }
        .step-4 { background: #14b8a6; }
        .step-5 { background: #3b82f6; }
        
        .step-title {
            font-weight: bold;
            color: #0074C1;
            margin-bottom: 8px;
            font-size: 0.9rem;
        }
        
        .step-description {
            font-size: 0.8rem;
            color: #6b7280;
            line-height: 1.4;
        }
        
        .footer-info {
            background: white;
            padding: 24px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0, 116, 193, 0.1);
            margin-top: 24px;
        }
        
        .footer-info a {
            color: #0074C1;
            text-decoration: none;
            font-weight: medium;
        }
        
        .footer-info a:hover {
            text-decoration: underline;
        }
        
        @media print {
            body { background: white; }
            .container { max-width: none; padding: 0; }
            .section { box-shadow: none; border: 1px solid #ddd; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">SIPAL</div>
            <div class="title-section">
                <h1>STATUS DA CONSTRUÇÃO DAS TRILHAS - TI CICLO 2</h1>
                <p>Volume de Trilhas e Passos já criados | Status da Aprovação</p>
            </div>
            <div class="date-info">
                📅 Dados atualizados em ${currentDate}
            </div>
        </div>
        
        <div class="kpi-section">
            <div class="kpi-card">
                <div class="kpi-title">TRILHAS APROVADAS PARA O CICLO 2</div>
                <div class="kpi-value">75,5%</div>
                <div class="kpi-subtitle">492 de 652<br>✅ Resultado abaixo da meta</div>
            </div>
            
            <div class="info-card">
                <h4>INFORMATIVO</h4>
                <p>Tendo em vista que algumas frentes não finalizaram a construção e aprovação das trilhas para o Ciclo 2 de teste integrado, o prazo para conclusão será estendido até domingo, 15/06. A BPH Digital bloqueará automaticamente a edição e aprovação do Ciclo 2 a partir das 00h de segunda-feira, 16/06.</p>
            </div>
        </div>
        
        <div class="section">
            <h2>STATUS DA CONSTRUÇÃO DAS TRILHAS</h2>
            <table>
                <thead>
                    <tr>
                        <th>Frente</th>
                        <th>Andamento</th>
                        <th>Aprovado</th>
                        <th>Concluído</th>
                        <th>Reprovado</th>
                        <th>Total Geral</th>
                        <th>% Aprovação</th>
                    </tr>
                </thead>
                <tbody>
                    <tr><td>Comercial</td><td>11</td><td><span class="status-approved">10</span></td><td>43</td><td>21</td><td><strong>110</strong></td><td class="percentage-low">23%</td></tr>
                    <tr><td>Controladoria</td><td>5</td><td><span class="status-approved">0</span></td><td>0</td><td>0</td><td><strong>12</strong></td><td class="percentage-medium">58%</td></tr>
                    <tr><td>Finanças</td><td>0</td><td><span class="status-approved">0</span></td><td>0</td><td>0</td><td><strong>201</strong></td><td class="percentage-high">100%</td></tr>
                    <tr><td>Fiscal</td><td>0</td><td><span class="status-approved">0</span></td><td>0</td><td>0</td><td><strong>18</strong></td><td class="percentage-high">100%</td></tr>
                    <tr><td>Manufatura</td><td>0</td><td><span class="status-approved">0</span></td><td>0</td><td>0</td><td><strong>22</strong></td><td class="percentage-high">100%</td></tr>
                    <tr><td>Originação</td><td>51</td><td><span class="status-approved">9</span></td><td>1</td><td>0</td><td><strong>101</strong></td><td class="percentage-medium">40%</td></tr>
                    <tr><td>Suprimentos</td><td>7</td><td><span class="status-approved">0</span></td><td>2</td><td>0</td><td><strong>188</strong></td><td class="percentage-high">95%</td></tr>
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <h2>BOAS PRÁTICAS NA CONSTRUÇÃO E APROVAÇÃO DAS TRILHAS</h2>
            <div class="best-practices">
                <div class="practice-step">
                    <div class="step-number step-1">1</div>
                    <div class="step-title">Definição de Usuário Testador</div>
                    <div class="step-description">Confirme se todos os usuários testadores foram adicionados ao processo.</div>
                </div>
                <div class="practice-step">
                    <div class="step-number step-2">2</div>
                    <div class="step-title">Criação de Dimensões de Dados</div>
                    <div class="step-description">Verifique se as dimensões de dados estão corretamente criadas para as trilhas.</div>
                </div>
                <div class="practice-step">
                    <div class="step-number step-3">3</div>
                    <div class="step-title">Verificação de Duplicidade</div>
                    <div class="step-description">Certifique-se de que não há atividades duplicadas na trilha.</div>
                </div>
                <div class="practice-step">
                    <div class="step-number step-4">4</div>
                    <div class="step-title">Verificação de Cenário</div>
                    <div class="step-description">Confirme se o cenário existe para a Sipal, incluindo todas as fiscais entidades/recebidas.</div>
                </div>
                <div class="practice-step">
                    <div class="step-number step-5">5</div>
                    <div class="step-title">Validação Cross-Área</div>
                    <div class="step-description">Tanto os Key User e o Dono do Processo devem validar as trilhas com as áreas envolvidas.</div>
                </div>
            </div>
        </div>
        
        <div class="footer-info">
            <p><strong>Um novo status consolidado será encaminhado próxima segunda-feira, 16/06, com as trilhas que fizeram parte do Ciclo 2 de Teste Integrado</strong></p>
            <br>
            <p><strong>É possível acompanhar o status de aprovação através do Painel de Aprovação da BPH Digital:</strong></p>
            <a href="https://bph.sipal.com.br/bph/trilhas/painel-aprovacao" target="_blank">https://bph.sipal.com.br/bph/trilhas/painel-aprovacao</a>
            <br><br>
            <p><em>Relatório gerado automaticamente em ${currentDate}</em></p>
        </div>
    </div>
</body>
</html>
  `;
};