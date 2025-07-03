interface StatusTableData {
  frente: string;
  andamento: number;
  aprovado: number;
  concluido: number;
  reprovado: number;
  total: number;
  percentualAprovado: number;
}

interface StatusTableProps {
  data: StatusTableData[];
  title: string;
}

export const StatusTable = ({ data, title }: StatusTableProps) => {
  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'aprovado':
        return 'bg-sipal-green text-white';
      case 'andamento':
        return 'bg-blue-500 text-white';
      case 'concluido':
        return 'bg-sipal-blue text-white';
      case 'reprovado':
        return 'bg-sipal-red text-white';
      default:
        return 'bg-gray-500 text-white';
    }
  };

  const getPercentageColor = (percentage: number) => {
    if (percentage >= 80) return 'text-sipal-green font-bold';
    if (percentage >= 60) return 'text-sipal-yellow font-bold';
    return 'text-sipal-red font-bold';
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-[var(--shadow-card)] mb-6">
      <h2 className="text-xl font-bold text-sipal-blue mb-4">{title}</h2>
      <div className="overflow-x-auto">
        <table className="w-full border-collapse">
          <thead>
            <tr className="bg-sipal-blue text-white">
              <th className="border border-gray-300 p-3 text-left">Frente</th>
              <th className="border border-gray-300 p-3 text-center">Andamento</th>
              <th className="border border-gray-300 p-3 text-center">Aprovado</th>
              <th className="border border-gray-300 p-3 text-center">Concluído</th>
              <th className="border border-gray-300 p-3 text-center">Reprovado</th>
              <th className="border border-gray-300 p-3 text-center">Total Geral</th>
              <th className="border border-gray-300 p-3 text-center">% Aprovação</th>
            </tr>
          </thead>
          <tbody>
            {data.map((row, index) => (
              <tr key={index} className="hover:bg-sipal-gray/50 transition-colors">
                <td className="border border-gray-300 p-3 font-medium">{row.frente}</td>
                <td className="border border-gray-300 p-3 text-center">{row.andamento}</td>
                <td className="border border-gray-300 p-3 text-center">
                  <span className="inline-block bg-sipal-green text-white px-2 py-1 rounded text-sm">
                    {row.aprovado}
                  </span>
                </td>
                <td className="border border-gray-300 p-3 text-center">{row.concluido}</td>
                <td className="border border-gray-300 p-3 text-center">{row.reprovado}</td>
                <td className="border border-gray-300 p-3 text-center font-bold">{row.total}</td>
                <td className={`border border-gray-300 p-3 text-center ${getPercentageColor(row.percentualAprovado)}`}>
                  {row.percentualAprovado}%
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};