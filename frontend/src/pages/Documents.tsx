import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { FileText, Filter, RefreshCw, PlusCircle, AlertCircle } from 'lucide-react';
import { Link } from 'react-router-dom';
import { DocumentItem } from '../types';
import { listDocuments, searchDocuments, deleteDocument } from '../api/client';
import { DocumentCard } from '../components/DocumentCard';
import { SearchBar } from '../components/SearchBar';
import { LoadingSpinner } from '../components/LoadingSpinner';

export const Documents: React.FC = () => {
  const { t, i18n } = useTranslation();
  const isBengali = i18n.language?.startsWith('bn');

  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [activeFilter, setActiveFilter] = useState<string>('all');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const fetchDocs = async (query = searchQuery, filter = activeFilter) => {
    try {
      setLoading(true);
      setErrorMessage(null);

      let docs: DocumentItem[] = [];
      if (query.trim()) {
        docs = await searchDocuments(query.trim(), filter === 'all' ? undefined : filter);
      } else {
        docs = await listDocuments({
          doc_type: filter === 'all' ? undefined : filter,
        });
      }
      setDocuments(Array.isArray(docs) ? docs : []);
    } catch (err: any) {
      console.error('Error fetching documents:', err);
      setDocuments([]);
      setErrorMessage(err.message || t('common.error'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocs(searchQuery, activeFilter);
  }, [activeFilter]);

  const handleSearch = (q: string) => {
    setSearchQuery(q);
    fetchDocs(q, activeFilter);
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm(t('detail.confirm_delete') || 'Are you sure you want to delete this document?')) {
      return;
    }
    try {
      await deleteDocument(id);
      setDocuments((prev) => prev.filter((d) => d.id !== id));
    } catch (err) {
      console.error('Failed to delete document:', err);
    }
  };

  const filterTabs = [
    { key: 'all', label: t('documents.filter_all') },
    { key: 'khatian', label: t('upload.khatian') },
    { key: 'porcha', label: t('upload.porcha') },
    { key: 'deed', label: t('upload.deed') },
  ];

  const formatNumber = (num: number) => {
    if (!isBengali) return String(num);
    const bnDigits = ['০', '১', '২', '৩', '৪', '৫', '৬', '৭', '৮', '৯'];
    return String(num).replace(/[0-9]/g, (d) => bnDigits[Number(d)]);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            {t('documents.title')}
          </h1>
          <p className="text-slate-500 text-xs sm:text-sm mt-1">
            {formatNumber(documents.length)} {t('documents.total_found')}
          </p>
        </div>

        <Link
          to="/upload"
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-emerald-700 hover:bg-emerald-800 text-white font-semibold text-sm transition-all shadow-sm active:scale-95 shrink-0 self-start md:self-auto"
        >
          <PlusCircle className="w-4 h-4" />
          <span>{t('home.upload_btn')}</span>
        </Link>
      </div>

      {/* Search & Filter Bar */}
      <div className="flex flex-col lg:flex-row gap-4 items-stretch lg:items-center justify-between bg-white p-4 sm:p-5 rounded-2xl border border-slate-200 shadow-xs">
        <SearchBar
          value={searchQuery}
          onSearch={handleSearch}
          placeholder={t('documents.search_placeholder')}
          className="flex-1"
        />

        {/* Filter Tabs */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 lg:pb-0 scrollbar-none">
          <Filter className="w-4 h-4 text-slate-400 mr-1 shrink-0 hidden sm:block" />
          {filterTabs.map((tab) => (
            <button
              key={tab.key}
              type="button"
              onClick={() => setActiveFilter(tab.key)}
              className={`px-3.5 py-2 rounded-xl text-xs md:text-sm font-semibold whitespace-nowrap transition-all ${
                activeFilter === tab.key
                  ? 'bg-emerald-700 text-white shadow-xs'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Error state */}
      {errorMessage && (
        <div className="p-4 rounded-2xl bg-rose-50 border border-rose-200 text-rose-700 text-sm flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-5 h-5 shrink-0 text-rose-600" />
            <span>{errorMessage}</span>
          </div>
          <button
            type="button"
            onClick={() => fetchDocs()}
            className="inline-flex items-center gap-1 text-xs font-bold text-rose-800 hover:underline"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>{t('common.retry')}</span>
          </button>
        </div>
      )}

      {/* Content Grid */}
      {loading ? (
        <LoadingSpinner fullHeight />
      ) : documents.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {documents.map((doc) => (
            <DocumentCard key={doc.id} document={doc} onDelete={handleDelete} />
          ))}
        </div>
      ) : (
        /* Empty State */
        <div className="bg-white rounded-3xl border border-slate-200 p-12 text-center space-y-4 shadow-xs">
          <div className="w-16 h-16 rounded-full bg-slate-100 mx-auto flex items-center justify-center text-slate-400">
            <FileText className="w-8 h-8" />
          </div>
          <div className="space-y-1">
            <h3 className="text-lg font-bold text-slate-800">
              {t('documents.no_results')}
            </h3>
            {searchQuery && (
              <p className="text-sm text-slate-500">
                "{searchQuery}" এর জন্য কোনো ফলাফল নেই
              </p>
            )}
          </div>
          <div className="flex items-center justify-center gap-3 pt-2">
            {searchQuery && (
              <button
                type="button"
                onClick={() => {
                  setSearchQuery('');
                  fetchDocs('', activeFilter);
                }}
                className="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-xs sm:text-sm transition-colors"
              >
                {t('documents.clear_search')}
              </button>
            )}
            <Link
              to="/upload"
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-emerald-700 hover:bg-emerald-800 text-white font-semibold text-xs sm:text-sm transition-colors shadow-xs"
            >
              <PlusCircle className="w-4 h-4" />
              <span>{t('home.upload_btn')}</span>
            </Link>
          </div>
        </div>
      )}
    </div>
  );
};
