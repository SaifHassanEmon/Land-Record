import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';

export const useLanguage = () => {
  const { i18n, t } = useTranslation();
  const currentLanguage = i18n.language?.startsWith('bn') ? 'bn' : (i18n.language || 'bn');
  const isBengali = currentLanguage === 'bn';

  useEffect(() => {
    if (isBengali) {
      document.body.classList.add('font-bengali');
      document.body.classList.remove('font-english');
      document.documentElement.lang = 'bn';
    } else {
      document.body.classList.remove('font-bengali');
      document.body.classList.add('font-english');
      document.documentElement.lang = 'en';
    }
    localStorage.setItem('preferred_language', currentLanguage);
  }, [currentLanguage, isBengali]);

  const toggleLanguage = () => {
    const nextLang = isBengali ? 'en' : 'bn';
    i18n.changeLanguage(nextLang);
  };

  const setLanguage = (lang: 'bn' | 'en') => {
    i18n.changeLanguage(lang);
  };

  return {
    language: currentLanguage,
    isBengali,
    toggleLanguage,
    setLanguage,
    t,
  };
};
