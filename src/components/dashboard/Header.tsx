import { Calendar } from "lucide-react";

export const Header = () => {
  const currentDate = new Date().toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });

  return (
    <div className="bg-white rounded-lg shadow-[var(--shadow-header)] p-6 mb-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-6">
          <div className="w-20 h-20 bg-sipal-blue rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-sm">SIPAL</span>
          </div>
          <div>
            <h1 className="text-3xl font-bold text-sipal-blue">
              STATUS DA CONSTRUÇÃO DAS TRILHAS - TI CICLO 2
            </h1>
            <p className="text-sipal-gray-dark text-sm mt-1">
              Volume de Trilhas e Passos já criados | Status da Aprovação
            </p>
          </div>
        </div>
        <div className="text-right text-sm text-sipal-gray-dark">
          <div className="flex items-center gap-2">
            <Calendar className="w-4 h-4" />
            <span>Dados atualizados em {currentDate}</span>
          </div>
        </div>
      </div>
    </div>
  );
};