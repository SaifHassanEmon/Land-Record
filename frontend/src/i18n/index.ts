import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import bn from './bn.json';
import en from './en.json';

const savedLanguage = localStorage.getItem('preferred_language') || 'bn';

i18n
  .use(initReactI18next)
  .init({
    resources: {
      bn: {
        translation: bn,
      },
      en: {
        translation: en,
      },
    },
    lng: savedLanguage,
    fallbackLng: 'bn',
    interpolation: {
      escapeValue: false, // react already escapes values
    },
  });

export default i18n;
