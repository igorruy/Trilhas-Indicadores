interface InfoCardProps {
  title: string;
  content: string;
  variant?: 'info' | 'warning' | 'success' | 'error';
}

export const InfoCard = ({ title, content, variant = 'info' }: InfoCardProps) => {
  const getVariantStyles = () => {
    switch (variant) {
      case 'info':
        return 'bg-blue-50 border-blue-200 text-blue-800';
      case 'warning':
        return 'bg-sipal-yellow text-gray-800';
      case 'success':
        return 'bg-sipal-green-light border-sipal-green text-green-800';
      case 'error':
        return 'bg-sipal-red-light border-sipal-red text-red-800';
      default:
        return 'bg-sipal-yellow text-gray-800';
    }
  };

  return (
    <div className={`${getVariantStyles()} p-4 rounded-lg border-l-4 mb-6`}>
      <div className="flex items-start">
        <div className="flex-1">
          <h4 className="font-bold text-sm mb-2">{title}</h4>
          <p className="text-sm leading-relaxed">{content}</p>
        </div>
      </div>
    </div>
  );
};