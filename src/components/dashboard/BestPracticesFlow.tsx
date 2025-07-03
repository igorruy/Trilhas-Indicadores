export const BestPracticesFlow = () => {
  const steps = [
    {
      number: 1,
      title: "Definição de Usuário Testador",
      description: "Confirme se todos os usuários testadores foram adicionados ao processo.",
      color: "bg-purple-500"
    },
    {
      number: 2,
      title: "Criação de Dimensões de Dados",
      description: "Verifique se as dimensões de dados estão corretamente criadas para as trilhas.",
      color: "bg-cyan-500"
    },
    {
      number: 3,
      title: "Verificação de Duplicidade",
      description: "Certifique-se de que não há atividades duplicadas na trilha.",
      color: "bg-green-500"
    },
    {
      number: 4,
      title: "Verificação de Cenário",
      description: "Confirme se o cenário existe para a Sipal, incluindo todas as fiscais entidades/recebidas.",
      color: "bg-teal-500"
    },
    {
      number: 5,
      title: "Validação Cross-Área",
      description: "Tanto os Key User e o Dono do Processo devem validar as trilhas com as áreas envolvidas.",
      color: "bg-blue-500"
    }
  ];

  return (
    <div className="bg-white p-6 rounded-lg shadow-[var(--shadow-card)] mb-6">
      <h2 className="text-xl font-bold text-sipal-blue mb-6">BOAS PRÁTICAS NA CONSTRUÇÃO E APROVAÇÃO DAS TRILHAS</h2>
      <div className="flex flex-wrap justify-center gap-4">
        {steps.map((step, index) => (
          <div key={step.number} className="flex flex-col items-center max-w-48">
            <div className={`${step.color} text-white rounded-full w-12 h-12 flex items-center justify-center font-bold text-lg mb-3`}>
              {step.number}
            </div>
            <div className="text-center">
              <h3 className="font-bold text-sm text-sipal-blue mb-2">{step.title}</h3>
              <p className="text-xs text-sipal-gray-dark leading-relaxed">{step.description}</p>
            </div>
            {index < steps.length - 1 && (
              <div className="hidden lg:block w-8 h-0.5 bg-sipal-gray mt-6 absolute translate-x-32"></div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};