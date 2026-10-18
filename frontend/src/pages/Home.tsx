import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  Upload,
  Search,
  FileText,
  ScrollText,
  Award,
  Layers,
  ArrowRight,
  ShieldCheck,
  Cpu,
  Database,
  Building2,
} from 'lucide-react';
import { DocumentItem, DocumentStats } from '../types';
import { getStats, listDocuments } from '../api/client';
import { DocumentCard } from '../components/DocumentCard';
import { LoadingSpinner } from '../components/LoadingSpinner';

export const Home: React.FC = () => {
  const { t, i18n } = useTranslation();
  const isBengali = i18n.language?.startsWith('bn');

  const [stats, setStats] = useState<DocumentStats>({
    total: 0,
    khatian: 0,
    porcha: 0,
    deed: 0,
  });
  const [recentDocs, setRecentDocs] = useState<DocumentItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    async function loadDashboardData() {
      try {
        setLoading(true);
        const [statsData, docsData] = await Promise.all([getStats(), listDocuments()]);
        setStats(statsData || { total: 0, khatian: 0, porcha: 0, deed: 0 });
        // Show last 5 documents
        setRecentDocs(Array.isArray(docsData) ? docsData.slice(0, 5) : []);
      } catch (err) {
        console.error('Failed to load dashboard data:', err);
        setRecentDocs([]);
      } finally {
        setLoading(false);
      }
    }
    loadDashboardData();
  }, []);

  const formatNumber = (num: number) => {
    if (!isBengali) return String(num);
    const bnDigits = ['০', '১', '২', '৩', '৪', '৫', '৬', '৭', '৮', '৯'];
    return String(num).replace(/[0-9]/g, (d) => bnDigits[Number(d)]);
  };

  const statCards = [
    {
      title: t('home.total_docs'),
      count: stats.total,
      icon: Layers,
      color: 'bg-emerald-50 text-emerald-700 border-emerald-200',
      iconBg: 'bg-emerald-600 text-white',
    },
    {
      title: t('home.khatian_count'),
      count: stats.khatian,
      icon: ScrollText,
      color: 'bg-teal-50 text-teal-700 border-teal-200',
      iconBg: 'bg-teal-600 text-white',
    },
    {
      title: t('home.porcha_count'),
      count: stats.porcha,
      icon: FileText,
      color: 'bg-blue-50 text-blue-700 border-blue-200',
      iconBg: 'bg-blue-600 text-white',
    },
    {
      title: t('home.deed_count'),
      count: stats.deed,
      icon: Award,
      color: 'bg-amber-50 text-amber-700 border-amber-200',
      iconBg: 'bg-amber-600 text-white',
    },
  ];

  return (
    <div className="space-y-12">
      {/* Hero Section with Bangladesh deep green and red accents */}
      <section className="relative overflow-hidden bg-gradient-to-br from-[#00533d] via-[#006A4E] to-[#004230] text-white py-16 md:py-24 px-4 sm:px-6 lg:px-8 shadow-inner">
        {/* Decorative background circle */}
        <div className="absolute -right-20 -top-20 w-96 h-96 rounded-full bg-[#F42A41]/20 blur-3xl pointer-events-none" />
        <div className="absolute -left-20 -bottom-20 w-96 h-96 rounded-full bg-emerald-400/10 blur-3xl pointer-events-none" />

        <div className="max-w-7xl mx-auto relative z-10 text-center md:text-left md:flex md:items-center md:justify-between gap-10">
          <div className="max-w-3xl space-y-5">
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white/10 backdrop-blur-md text-emerald-200 text-xs md:text-sm font-semibold border border-white/20">
              <span className="w-2.5 h-2.5 rounded-full bg-[#F42A41]" />
              <span>{t('home.subtitle')}</span>
            </div>

            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight leading-tight">
              {t('home.title')}
            </h1>

            <p className="text-base sm:text-lg text-emerald-100 font-normal leading-relaxed max-w-2xl">
              {t('home.description')}
            </p>

            {/* Quick action buttons */}
            <div className="pt-3 flex flex-wrap items-center justify-center md:justify-start gap-4">
              <Link
                to="/upload"
                className="inline-flex items-center gap-2.5 px-6 py-3.5 rounded-xl font-bold text-sm md:text-base text-emerald-950 bg-white hover:bg-emerald-50 active:scale-95 transition-all shadow-lg hover:shadow-xl"
              >
                <Upload className="w-5 h-5 text-[#006A4E]" />
                <span>{t('home.upload_btn')}</span>
              </Link>

              <Link
                to="/documents"
                className="inline-flex items-center gap-2.5 px-6 py-3.5 rounded-xl font-bold text-sm md:text-base text-white bg-[#004e39] hover:bg-[#003e2d] border border-emerald-400/30 active:scale-95 transition-all shadow-md"
              >
                <Search className="w-5 h-5 text-emerald-300" />
                <span>{t('home.search_btn')}</span>
              </Link>
            </div>
          </div>

          {/* Visual Badge Card */}
          <div className="hidden lg:flex flex-col items-center justify-center p-8 bg-white/10 backdrop-blur-md rounded-3xl border border-white/20 text-center shadow-2xl shrink-0 w-80">
            <div className="w-20 h-20 rounded-full bg-[#006A4E] border-4 border-white/30 flex items-center justify-center shadow-lg relative mb-4">
              <div className="w-10 h-10 rounded-full bg-[#F42A41] flex items-center justify-center">
                <Building2 className="w-6 h-6 text-white" />
              </div>
            </div>
            <h3 className="font-bold text-lg text-white">{t('home.subtitle')}</h3>
            <p className="text-xs text-emerald-200 mt-1">স্বচ্ছ, সহজ ও ডিজিটাল ভূমি ব্যবস্থাপনা</p>
            <div className="mt-4 pt-4 border-t border-white/15 w-full flex justify-around text-center">
              <div>
                <p className="text-xl font-extrabold text-white">{formatNumber(stats.total)}</p>
                <p className="text-[11px] text-emerald-200">{t('home.total_docs')}</p>
              </div>
              <div className="border-r border-white/15" />
              <div>
                <p className="text-xl font-extrabold text-white">৯৮%</p>
                <p className="text-[11px] text-emerald-200">{t('detail.confidence')}</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
        {/* Stats Grid */}
        <section>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6">
            {statCards.map((card, idx) => {
              const Icon = card.icon;
              return (
                <div
                  key={idx}
                  className={`p-5 rounded-2xl border ${card.color} bg-white shadow-xs hover:shadow-md transition-all flex flex-col justify-between`}
                >
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-xs md:text-sm font-semibold text-slate-600">
                      {card.title}
                    </span>
                    <div className={`p-2.5 rounded-xl ${card.iconBg} shadow-sm`}>
                      <Icon className="w-4 h-4 md:w-5 md:h-5" />
                    </div>
                  </div>
                  <div className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
                    {loading ? (
                      <span className="inline-block w-8 h-8 rounded bg-slate-200 animate-pulse" />
                    ) : (
                      formatNumber(card.count)
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </section>

        {/* Feature Highlights */}
        <section className="bg-white p-6 sm:p-8 rounded-3xl border border-slate-200 shadow-xs">
          <div className="text-center max-w-xl mx-auto mb-8">
            <h2 className="text-xl sm:text-2xl font-bold text-slate-900">
              {t('home.features_title')}
            </h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="p-5 rounded-2xl bg-emerald-50/60 border border-emerald-100 flex items-start gap-4">
              <div className="p-3 rounded-xl bg-emerald-600 text-white shrink-0 shadow-sm">
                <Cpu className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-bold text-slate-900 text-base mb-1">
                  {t('home.ocr_feature_title')}
                </h3>
                <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
                  {t('home.ocr_feature_desc')}
                </p>
              </div>
            </div>

            <div className="p-5 rounded-2xl bg-blue-50/60 border border-blue-100 flex items-start gap-4">
              <div className="p-3 rounded-xl bg-blue-600 text-white shrink-0 shadow-sm">
                <Search className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-bold text-slate-900 text-base mb-1">
                  {t('home.search_feature_title')}
                </h3>
                <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
                  {t('home.search_feature_desc')}
                </p>
              </div>
            </div>

            <div className="p-5 rounded-2xl bg-amber-50/60 border border-amber-100 flex items-start gap-4">
              <div className="p-3 rounded-xl bg-amber-600 text-white shrink-0 shadow-sm">
                <ShieldCheck className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-bold text-slate-900 text-base mb-1">
                  {t('home.secure_feature_title')}
                </h3>
                <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
                  {t('home.secure_feature_desc')}
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Recent Documents Section */}
        <section className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl sm:text-2xl font-bold text-slate-900">
                {t('home.recent_title')}
              </h2>
            </div>
            <Link
              to="/documents"
              className="inline-flex items-center gap-1.5 text-sm font-semibold text-emerald-700 hover:text-emerald-800 transition-colors"
            >
              <span>{t('home.view_all')}</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>

          {loading ? (
            <LoadingSpinner />
          ) : recentDocs.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {recentDocs.map((doc) => (
                <DocumentCard key={doc.id} document={doc} />
              ))}
            </div>
          ) : (
            <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center space-y-4">
              <div className="w-12 h-12 rounded-full bg-slate-100 mx-auto flex items-center justify-center text-slate-400">
                <Database className="w-6 h-6" />
              </div>
              <p className="text-slate-500 text-sm max-w-sm mx-auto">{t('home.no_recent')}</p>
              <Link
                to="/upload"
                className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-emerald-700 text-white font-medium text-sm hover:bg-emerald-800 transition-colors shadow-sm"
              >
                <Upload className="w-4 h-4" />
                <span>{t('home.upload_btn')}</span>
              </Link>
            </div>
          )}
        </section>
      </div>
    </div>
  );
};
