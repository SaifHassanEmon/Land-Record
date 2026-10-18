import React from 'react';
import { Globe } from 'lucide-react';
import { useLanguage } from '../hooks/useLanguage';

interface LanguageToggleProps {
  className?: string;
}

export const LanguageToggle: React.FC<LanguageToggleProps> = ({ className = '' }) => {
  const { isBengali, toggleLanguage } = useLanguage();

  return (
    <button
      type="button"
      onClick={toggleLanguage}
      className={`inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-sm font-semibold transition-all duration-200 shadow-sm border border-emerald-200 bg-white hover:bg-emerald-50 text-emerald-900 active:scale-95 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 ${className}`}
      title={isBengali ? 'Switch to English' : 'বাংলায় পরিবর্তন করুন'}
      aria-label="Change language"
    >
      <Globe className="w-4 h-4 text-emerald-700 animate-spin-slow" />
      <span className="tracking-wide">
        {isBengali ? 'বাংলা' : 'English'}
      </span>
      <span className="text-[10px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded-md bg-emerald-700 text-white">
        {isBengali ? 'BN' : 'EN'}
      </span>
    </button>
  );
};
