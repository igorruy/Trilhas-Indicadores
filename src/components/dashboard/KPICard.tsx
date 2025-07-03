interface KPICardProps {
  title: string;
  value: string | number;
  percentage?: number;
  subtitle?: string;
  variant?: 'primary' | 'secondary' | 'warning' | 'success';
  size?: 'small' | 'large';
}

export const KPICard = ({ 
  title, 
  value, 
  percentage, 
  subtitle, 
  variant = 'primary',
  size = 'small'
}: KPICardProps) => {
  const getVariantStyles = () => {
    switch (variant) {
      case 'primary':
        return 'bg-white border-l-4 border-sipal-blue';
      case 'secondary':
        return 'bg-sipal-blue text-white';
      case 'warning':
        return 'bg-sipal-yellow-light border-l-4 border-sipal-yellow';
      case 'success':
        return 'bg-sipal-green-light border-l-4 border-sipal-green';
      default:
        return 'bg-white border-l-4 border-sipal-blue';
    }
  };

  const sizeStyles = size === 'large' ? 'p-8' : 'p-6';

  return (
    <div className={`${getVariantStyles()} ${sizeStyles} rounded-lg shadow-[var(--shadow-card)] hover:shadow-[var(--shadow-card-hover)] transition-all duration-300`}>
      <div className="text-center">
        <h3 className={`text-sm font-medium mb-2 ${variant === 'secondary' ? 'text-white/80' : 'text-sipal-gray-dark'}`}>
          {title}
        </h3>
        <div className={`text-4xl font-bold mb-1 ${variant === 'secondary' ? 'text-white' : 'text-sipal-blue'}`}>
          {value}
          {percentage && (
            <span className="text-2xl ml-1">%</span>
          )}
        </div>
        {subtitle && (
          <p className={`text-xs ${variant === 'secondary' ? 'text-white/70' : 'text-sipal-gray-dark'}`}>
            {subtitle}
          </p>
        )}
      </div>
    </div>
  );
};