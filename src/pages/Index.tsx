import { useRef } from "react";
import { Header } from "@/components/dashboard/Header";
import { KPICard } from "@/components/dashboard/KPICard";
import { InfoCard } from "@/components/dashboard/InfoCard";
import { StatusTable } from "@/components/dashboard/StatusTable";
import { ApprovalTable } from "@/components/dashboard/ApprovalTable";
import { StepsTable } from "@/components/dashboard/StepsTable";
import { BestPracticesFlow } from "@/components/dashboard/BestPracticesFlow";
import { ExportButtons } from "@/components/dashboard/ExportButtons";

const Index = () => {
  // Mock data based on the dashboard image
  const statusData = [
    { frente: "Comercial", andamento: 11, aprovado: 10, concluido: 43, reprovado: 21, total: 110, percentualAprovado: 23 },
    { frente: "Controladoria", andamento: 5, aprovado: 0, concluido: 0, reprovado: 0, total: 12, percentualAprovado: 58 },
    { frente: "Finanças", andamento: 0, aprovado: 0, concluido: 0, reprovado: 0, total: 201, percentualAprovado: 100 },
    { frente: "Fiscal", andamento: 0, aprovado: 0, concluido: 0, reprovado: 0, total: 18, percentualAprovado: 100 },
    { frente: "Manufatura", andamento: 0, aprovado: 0, concluido: 0, reprovado: 0, total: 22, percentualAprovado: 100 },
    { frente: "Originação", andamento: 51, aprovado: 9, concluido: 1, reprovado: 0, total: 101, percentualAprovado: 40 },
    { frente: "Suprimentos", andamento: 7, aprovado: 0, concluido: 2, reprovado: 0, total: 188, percentualAprovado: 95 }
  ];

  const approvalData = [
    { responsavel: "Não definido", outrosStatus: 24, aprovado: 0, totalGeral: 24, percentualAprovacao: 0 },
    { responsavel: "Adriano Yassoyama Martins", outrosStatus: 0, aprovado: 3, totalGeral: 3, percentualAprovacao: 100 },
    { responsavel: "Ana Lopes", outrosStatus: 0, aprovado: 176, totalGeral: 176, percentualAprovacao: 100 },
    { responsavel: "Andréia Zenatti", outrosStatus: 40, aprovado: 0, totalGeral: 40, percentualAprovacao: 0 },
    { responsavel: "Claudio Oliveira", outrosStatus: 0, aprovado: 175, totalGeral: 175, percentualAprovacao: 100 },
    { responsavel: "Eder Feitosa", outrosStatus: 0, aprovado: 25, totalGeral: 25, percentualAprovacao: 100 },
    { responsavel: "Fábio Luiz Bernardi", outrosStatus: 0, aprovado: 4, totalGeral: 4, percentualAprovacao: 100 },
    { responsavel: "Gustavo Leda Minetto", outrosStatus: 0, aprovado: 32, totalGeral: 32, percentualAprovacao: 100 },
    { responsavel: "Ricardo Lavarias", outrosStatus: 77, aprovado: 19, totalGeral: 132, percentualAprovacao: 27 },
    { responsavel: "Rodrigo Biagi", outrosStatus: 0, aprovado: 18, totalGeral: 18, percentualAprovacao: 100 },
    { responsavel: "Vilmar Debiasi", outrosStatus: 0, aprovado: 23, totalGeral: 23, percentualAprovacao: 100 }
  ];

  const stepsData = [
    { equipe: "Comercial - SD", trilhas: 88, passos: 678 },
    { equipe: "Controladoria - CO", trilhas: 80, passos: 240 },
    { equipe: "Financeiro -FI-AP/AR", trilhas: 448, passos: 3236 },
    { equipe: "Financeiro-FI-AA/GL", trilhas: 165, passos: 443 },
    { equipe: "Fiscal", trilhas: 609, passos: 3999 },
    { equipe: "Logística - TM", trilhas: 90, passos: 902 },
    { equipe: "Manufatura - PM", trilhas: 16, passos: 80 },
    { equipe: "Manufatura - PP", trilhas: 12, passos: 111 },
    { equipe: "MXC - Gestão Pátios", trilhas: 76, passos: 503 },
    { equipe: "Originação - ACM", trilhas: 138, passos: 1434 },
    { equipe: "Originação - CM", trilhas: 10, passos: 116 },
    { equipe: "Suprimentos - MM", trilhas: 241, passos: 3252 }
  ];

  const dashboardRef = useRef<HTMLDivElement>(null);

  return (
    <div className="min-h-screen bg-[var(--gradient-dashboard)] p-6">
      <div className="max-w-7xl mx-auto" ref={dashboardRef}>
        <Header />
        
        {/* Main KPI Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          <div className="lg:col-span-1">
            <KPICard 
              title="TRILHAS APROVADAS PARA O CICLO 2"
              value="75,5"
              percentage={75.5}
              subtitle="492 de 652"
              variant="secondary"
              size="large"
            />
            <div className="mt-2 text-xs text-sipal-gray-dark bg-white p-2 rounded text-center">
              ✅ Resultado abaixo da meta
            </div>
          </div>
          
          <div className="lg:col-span-2">
            <InfoCard 
              title="INFORMATIVO"
              content="Tendo em vista que algumas frentes não finalizaram a construção e aprovação das trilhas para o Ciclo 2 de teste integrado, o prazo para conclusão será estendido até domingo, 15/06. A BPH Digital bloqueará automaticamente a edição e aprovação do Ciclo 2 a partir das 00h de segunda-feira, 16/06."
              variant="warning"
            />
          </div>
        </div>

        {/* Status Table */}
        <StatusTable 
          data={statusData}
          title="STATUS DA CONSTRUÇÃO DAS TRILHAS"
        />

        {/* Approval Table */}
        <ApprovalTable 
          data={approvalData}
          title="NOVO INDICADOR - Status de aprovação das trilhas com base no aprovador definido"
        />

        {/* Steps and Teams Table */}
        <StepsTable 
          data={stepsData}
          title="VOLUME DE TRILHAS E PASSOS POR EQUIPE"
        />

        {/* Best Practices Flow */}
        <BestPracticesFlow />

        {/* Export Buttons */}
        <ExportButtons dashboardRef={dashboardRef} />

        {/* Footer Info */}
        <div className="bg-white p-6 rounded-lg shadow-[var(--shadow-card)] mb-6">
          <div className="text-sm text-sipal-gray-dark space-y-2">
            <p><strong>Um novo status consolidado será encaminhado próxima segunda-feira, 16/06, com as trilhas que fizeram parte do Ciclo 2 de Teste Integrado</strong></p>
            <p><strong>É possível acompanhar o status de aprovação através do Painel de Aprovação da BPH Digital:</strong></p>
            <a href="https://bph.sipal.com.br/bph/trilhas/painel-aprovacao" 
               className="text-sipal-blue hover:underline font-medium">
              https://bph.sipal.com.br/bph/trilhas/painel-aprovacao
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Index;
