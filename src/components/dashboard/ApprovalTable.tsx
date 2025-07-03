interface ApprovalData {
  responsavel: string;
  outrosStatus: number;
  aprovado: number;
  totalGeral: number;
  percentualAprovacao: number;
}

interface ApprovalTableProps {
  data: ApprovalData[];
  title: string;
}

export const ApprovalTable = ({ data, title }: ApprovalTableProps) => {
  const getPercentageColor = (percentage: number) => {
    if (percentage >= 80) return 'text-sipal-green font-bold';
    if (percentage >= 60) return 'text-blue-600 font-bold';
    return 'text-sipal-red font-bold';
  };

  const getApprovalIcon = (percentage: number) => {
    if (percentage === 100) return '✅';
    if (percentage >= 80) return '✅';
    if (percentage === 0) return '⚠️';
    return '🔸';
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-[var(--shadow-card)] mb-6">
      <h2 className="text-xl font-bold text-sipal-blue mb-4">{title}</h2>
      <div className="overflow-x-auto">
        <table className="w-full border-collapse">
          <thead>
            <tr className="bg-sipal-blue text-white">
              <th className="border border-gray-300 p-3 text-left">Aprovador Responsável</th>
              <th className="border border-gray-300 p-3 text-center">Outros Status</th>
              <th className="border border-gray-300 p-3 text-center">Aprovado</th>
              <th className="border border-gray-300 p-3 text-center">Total Geral</th>
              <th className="border border-gray-300 p-3 text-center">% Aprovação</th>
            </tr>
          </thead>
          <tbody>
            {data.map((row, index) => (
              <tr key={index} className="hover:bg-sipal-gray/50 transition-colors">
                <td className="border border-gray-300 p-3 font-medium">{row.responsavel}</td>
                <td className="border border-gray-300 p-3 text-center">{row.outrosStatus}</td>
                <td className="border border-gray-300 p-3 text-center">
                  <span className="inline-block bg-sipal-green text-white px-2 py-1 rounded text-sm">
                    {row.aprovado}
                  </span>
                </td>
                <td className="border border-gray-300 p-3 text-center font-bold">{row.totalGeral}</td>
                <td className={`border border-gray-300 p-3 text-center ${getPercentageColor(row.percentualAprovacao)}`}>
                  <span className="flex items-center justify-center gap-1">
                    <span>{getApprovalIcon(row.percentualAprovacao)}</span>
                    <span>{row.percentualAprovacao}%</span>
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};