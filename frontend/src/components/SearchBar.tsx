import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Search, X } from 'lucide-react';

interface SearchBarProps {
  value?: string;
  placeholder?: string;
  onSearch: (query: string) => void;
  className?: string;
}

export const SearchBar: React.FC<SearchBarProps> = ({
  value = '',
  placeholder,
  onSearch,
  className = '',
}) => {
  const { t } = useTranslation();
  const [searchTerm, setSearchTerm] = useState(value);

  useEffect(() => {
    setSearchTerm(value);
  }, [value]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch(searchTerm.trim());
  };

  const handleClear = () => {
    setSearchTerm('');
    onSearch('');
  };

  return (
    <form
      onSubmit={handleSubmit}
      className={`relative flex items-center w-full max-w-2xl ${className}`}
    >
      <div className="relative w-full">
        <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
          <Search className="w-5 h-5 text-emerald-700" />
        </div>
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => {
            setSearchTerm(e.target.value);
            onSearch(e.target.value);
          }}
          placeholder={placeholder || t('documents.search_placeholder')}
          className="w-full pl-11 pr-24 py-3 bg-white border border-slate-300 rounded-xl shadow-sm text-slate-800 placeholder-slate-400 text-sm md:text-base focus:outline-none focus:ring-2 focus:ring-emerald-600 focus:border-transparent transition-all"
        />
        {searchTerm && (
          <button
            type="button"
            onClick={handleClear}
            className="absolute inset-y-0 right-14 pr-2 flex items-center text-slate-400 hover:text-slate-600 transition-colors"
            title={t('common.cancel')}
          >
            <X className="w-4 h-4" />
          </button>
        )}
        <button
          type="submit"
          className="absolute inset-y-1.5 right-1.5 px-4 bg-emerald-700 hover:bg-emerald-800 text-white text-xs md:text-sm font-medium rounded-lg transition-colors flex items-center justify-center shadow-sm"
        >
          {t('nav.search')}
        </button>
      </div>
    </form>
  );
};
