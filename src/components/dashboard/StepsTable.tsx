interface StepsData {
  equipe: string;
  trilhas: number;
  passos: number;
}

interface StepsTableProps {
  data: StepsData[];
  title: string;
}

export const StepsTable = ({ data, title }: StepsTableProps) => {
  const totalTrilhas = data.reduce((sum, item) => sum + item.trilhas, 0);
  const totalPassos = data.reduce((sum, item) => sum + item.passos, 0);

  return (
    <div className="bg-white p-6 rounded-lg shadow-[var(--shadow-card)] mb-6">
      <h2 className="text-xl font-bold text-sipal-blue mb-4">{title}</h2>
      <div className="mb-4 text-sm text-sipal-gray-dark">
        Mediante as trilhas criadas até o momento (considerando todos os status), 
        a tabela abaixo apresenta a quantidade de trilhas e passos criados por cada equipe no Ciclo 2.
      </div>
      <div className="overflow-x-auto">
        <table className="w-full border-collapse">
          <thead>
            <tr className="bg-sipal-blue text-white">
              <th className="border border-gray-300 p-3 text-left">Equipes</th>
              <th className="border border-gray-300 p-3 text-center">Trilhas</th>
              <th className="border border-gray-300 p-3 text-center">Passos</th>
            </tr>
          </thead>
          <tbody>
            {data.map((row, index) => (
              <tr key={index} className="hover:bg-sipal-gray/50 transition-colors">
                <td className="border border-gray-300 p-3 font-medium">{row.equipe}</td>
                <td className="border border-gray-300 p-3 text-center font-bold text-sipal-blue">{row.trilhas}</td>
                <td className="border border-gray-300 p-3 text-center font-bold text-sipal-blue">{row.passos}</td>
              </tr>
            ))}
            <tr className="bg-sipal-gray font-bold">
              <td className="border border-gray-300 p-3">Total Geral</td>
              <td className="border border-gray-300 p-3 text-center text-sipal-blue">{totalTrilhas}</td>
              <td className="border border-gray-300 p-3 text-center text-sipal-blue">{totalPassos}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div className="mt-4 text-sm text-sipal-gray-dark">
        <p>Até o atual momento foram criadas <strong className="text-sipal-blue">{totalTrilhas} trilhas</strong> na BPH Digital, que 
        combinado com as variações e dimensões dos dados resultam em <strong className="text-sipal-blue">{totalPassos} trilhas e {totalPassos} passos</strong>.</p>
        <p className="mt-2">
          <span className="text-orange-600">⚠️</span> O prazo para conclusão foi 
          <strong className="text-orange-600"> prorrogado até 15/06</strong>.
        </p>
      </div>
    </div>
  );
};