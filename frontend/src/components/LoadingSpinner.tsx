import React from 'react';
import { useTranslation } from 'react-i18next';
import { Loader2 } from 'lucide-react';

interface LoadingSpinnerProps {
  message?: string;
  size?: 'sm' | 'md' | 'lg';
  fullHeight?: boolean;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  message,
  size = 'md',
  fullHeight = false,
}) => {
  const { t } = useTranslation();
  const displayMsg = message || t('common.loading');

  const sizeClasses = {
    sm: 'w-5 h-5',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  };

  return (
    <div
      className={`flex flex-col items-center justify-center p-6 ${
        fullHeight ? 'min-h-[60vh]' : ''
      }`}
    >
      <div className="relative">
        <Loader2 className={`${sizeClasses[size]} text-emerald-700 animate-spin`} />
        <div className="absolute inset-0 rounded-full border-2 border-emerald-200 border-t-transparent animate-ping opacity-25" />
      </div>
      {displayMsg && (
        <p className="mt-3 text-sm text-slate-600 font-medium tracking-wide">
          {displayMsg}
        </p>
      )}
    </div>
  );
};
