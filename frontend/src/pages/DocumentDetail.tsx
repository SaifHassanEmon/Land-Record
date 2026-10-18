import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  ArrowLeft,
  Calendar,
  Download,
  Trash2,
  Copy,
  Check,
  FileText,
  Layers,
  ZoomIn,
  Building2,
  ShieldCheck,
  AlertCircle,
  ExternalLink,
} from 'lucide-react';
import { DocumentItem } from '../types';
import { getDocument, deleteDocument, normalizeConfidence } from '../api/client';
import { DocumentBadge } from '../components/DocumentBadge';
import { LoadingSpinner } from '../components/LoadingSpinner';

export const DocumentDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { t, i18n } = useTranslation();
  const isBengali = i18n.language?.startsWith('bn');

  const [document, setDocument] = useState<DocumentItem | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'fields' | 'ocr'>('fields');
  const [copied, setCopied] = useState<boolean>(false);
  const [zoomPreview, setZoomPreview] = useState<boolean>(false);

  useEffect(() => {
    async function loadDoc() {
      if (!id) return;
      try {
        setLoading(true);
        setError(null);
        const data = await getDocument(id);
        setDocument(data);
      } catch (err: any) {
        console.error('Error fetching document:', err);
        setError(err.message || t('common.error'));
      } finally {
        setLoading(false);
      }
    }
    loadDoc();
  }, [id, t]);

  const handleDelete = async () => {
    if (!document || !window.confirm(t('detail.confirm_delete'))) return;
    try {
      await deleteDocument(document.id);
      navigate('/documents');
    } catch (err) {
      console.error('Failed to delete document:', err);
    }
  };

  const handleCopyOcr = () => {
    if (!document?.ocr_text) return;
    navigator.clipboard.writeText(document.ocr_text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return '';
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString(isBengali ? 'bn-BD' : 'en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return dateStr;
    }
  };

  if (loading) {
    return <LoadingSpinner fullHeight />;
  }

  if (error || !document) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 text-center space-y-4">
        <div className="w-16 h-16 rounded-full bg-rose-50 text-rose-600 mx-auto flex items-center justify-center">
          <AlertCircle className="w-8 h-8" />
        </div>
        <h2 className="text-2xl font-bold text-slate-800">{t('common.error')}</h2>
        <p className="text-slate-600">{error || 'দলিল পাওয়া যায়নি'}</p>
        <Link
          to="/documents"
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-emerald-700 text-white font-semibold text-sm hover:bg-emerald-800 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>{t('common.back')}</span>
        </Link>
      </div>
    );
  }

  const confVal = normalizeConfidence(document.confidence);

  // Confidence styling: green >80%, yellow 60-80%, red <60%
  let confColorText = 'text-rose-600';
  let confBg = 'bg-rose-50 border-rose-200';
  let confBar = 'bg-rose-500';
  if (confVal >= 80) {
    confColorText = 'text-emerald-700';
    confBg = 'bg-emerald-50 border-emerald-200';
    confBar = 'bg-emerald-600';
  } else if (confVal >= 60) {
    confColorText = 'text-amber-700';
    confBg = 'bg-amber-50 border-amber-200';
    confBar = 'bg-amber-500';
  }

  const fields = document.extracted_fields || {};

  // Defined metadata fields with labels
  const fieldList = [
    { key: 'owner', label: t('detail.owner'), value: fields.owner },
    { key: 'district', label: t('detail.district'), value: fields.district },
    { key: 'upazila', label: t('detail.upazila'), value: fields.upazila },
    { key: 'mouza', label: t('detail.mouza'), value: fields.mouza },
    { key: 'plot', label: t('detail.plot'), value: fields.plot },
    { key: 'area', label: t('detail.area'), value: fields.area },
    { key: 'khatian_no', label: t('detail.khatian_no'), value: fields.khatian_no },
    { key: 'deed_no', label: t('detail.deed_no'), value: fields.deed_no },
    { key: 'seller', label: t('detail.seller'), value: fields.seller },
    { key: 'buyer', label: t('detail.buyer'), value: fields.buyer },
    { key: 'amount', label: t('detail.amount'), value: fields.amount },
    { key: 'reg_date', label: t('detail.reg_date'), value: fields.reg_date },
  ].filter((f) => f.value !== undefined && f.value !== null && f.value !== '');

  // Detect any additional unknown fields
  const standardKeys = new Set([
    'owner',
    'district',
    'upazila',
    'mouza',
    'plot',
    'area',
    'khatian_no',
    'deed_no',
    'seller',
    'buyer',
    'amount',
    'reg_date',
  ]);
  const extraFields = Object.entries(fields).filter(([k]) => !standardKeys.has(k));

  const isPdf =
    document.file_name.toLowerCase().endsWith('.pdf') ||
    document.mime_type === 'application/pdf';

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Top Breadcrumb & Action bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-200">
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={() => navigate('/documents')}
            className="p-2 rounded-xl bg-white border border-slate-200 text-slate-600 hover:text-emerald-700 hover:bg-emerald-50 transition-colors shadow-xs"
            title={t('common.back')}
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <h1 className="text-xl sm:text-2xl font-bold text-slate-900 truncate max-w-md sm:max-w-xl">
                {document.file_name}
              </h1>
              <DocumentBadge type={document.doc_type} size="sm" />
              <DocumentBadge status={document.status} size="sm" />
            </div>
            <div className="flex items-center gap-2 text-xs text-slate-500 mt-1">
              <Calendar className="w-3.5 h-3.5" />
              <span>
                {t('detail.created')}: {formatDate(document.created_at)}
              </span>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2.5">
          {document.file_url && (
            <a
              href={document.file_url}
              download={document.file_name}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 text-xs sm:text-sm font-semibold transition-colors shadow-xs"
            >
              <Download className="w-4 h-4 text-emerald-700" />
              <span>{t('common.download')}</span>
            </a>
          )}

          <button
            type="button"
            onClick={handleDelete}
            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-rose-50 border border-rose-200 hover:bg-rose-100 text-rose-700 text-xs sm:text-sm font-semibold transition-colors shadow-xs"
          >
            <Trash2 className="w-4 h-4 text-rose-600" />
            <span>{t('common.delete')}</span>
          </button>
        </div>
      </div>

      {/* Confidence Header Bar */}
      <div className={`p-4 rounded-2xl border ${confBg} flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-xs`}>
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-white shadow-xs">
            <ShieldCheck className={`w-5 h-5 ${confColorText}`} />
          </div>
          <div>
            <span className="text-xs font-semibold text-slate-500 block uppercase tracking-wider">
              {t('detail.confidence')}
            </span>
            <span className={`text-xl font-extrabold ${confColorText}`}>
              {confVal}% নির্ভুলতা স্কোর
            </span>
          </div>
        </div>

        {/* Progress meter */}
        <div className="w-full sm:w-64 space-y-1">
          <div className="w-full h-2.5 bg-slate-200/70 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-700 ${confBar}`}
              style={{ width: `${confVal}%` }}
            />
          </div>
          <div className="flex justify-between text-[10px] text-slate-500 font-medium">
            <span>০%</span>
            <span>৬০%</span>
            <span>১০০%</span>
          </div>
        </div>
      </div>

      {/* Two-panel layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Panel: Original Document Image / PDF Viewer */}
        <div className="lg:col-span-6 space-y-4">
          <div className="bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="p-4 border-b border-slate-100 flex items-center justify-between bg-slate-50">
              <div className="flex items-center gap-2">
                <FileText className="w-4 h-4 text-emerald-700" />
                <h3 className="font-bold text-slate-800 text-sm">
                  {t('detail.original_doc')}
                </h3>
              </div>
              <div className="flex items-center gap-2">
                {document.file_url && (
                  <a
                    href={document.file_url}
                    target="_blank"
                    rel="noreferrer"
                    className="p-1.5 rounded-lg text-slate-500 hover:text-emerald-700 hover:bg-white transition-colors"
                    title="নতুন ট্যাবে খুলুন"
                  >
                    <ExternalLink className="w-4 h-4" />
                  </a>
                )}
                <button
                  type="button"
                  onClick={() => setZoomPreview(!zoomPreview)}
                  className="p-1.5 rounded-lg text-slate-500 hover:text-emerald-700 hover:bg-white transition-colors"
                  title="জুম পরিবর্তন করুন"
                >
                  <ZoomIn className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Document display area */}
            <div
              className={`p-4 bg-slate-100 flex items-center justify-center min-h-[420px] max-h-[620px] overflow-auto relative ${
                zoomPreview ? 'cursor-zoom-out' : 'cursor-zoom-in'
              }`}
              onClick={() => setZoomPreview(!zoomPreview)}
            >
              {document.file_url ? (
                isPdf ? (
                  <iframe
                    src={document.file_url}
                    title={document.file_name}
                    className="w-full h-[540px] rounded-xl border border-slate-200 bg-white"
                  />
                ) : (
                  <img
                    src={document.file_url}
                    alt={document.file_name}
                    className={`rounded-xl object-contain shadow-md transition-transform duration-300 ${
                      zoomPreview ? 'scale-125 my-8' : 'max-h-[500px] w-auto'
                    }`}
                  />
                )
              ) : (
                /* Styled official document mock representation */
                <div
                  className={`w-full max-w-md bg-amber-50/70 p-8 rounded-xl border-2 border-amber-200/80 shadow-md text-slate-800 font-serif space-y-5 transition-transform ${
                    zoomPreview ? 'scale-110' : ''
                  }`}
                >
                  <div className="text-center border-b-2 border-amber-800/40 pb-4 space-y-1">
                    <div className="w-12 h-12 rounded-full border-2 border-[#006A4E] mx-auto flex items-center justify-center bg-white shadow-xs">
                      <div className="w-6 h-6 rounded-full bg-[#F42A41]" />
                    </div>
                    <p className="text-xs font-bold text-amber-950 uppercase tracking-wider">
                      গণপ্রজাতন্ত্রী বাংলাদেশ সরকার
                    </p>
                    <h4 className="text-base font-extrabold text-amber-900">
                      {document.doc_type === 'khatian'
                        ? 'সি.এস. / আর.এস. খতিয়ান'
                        : document.doc_type === 'porcha'
                        ? 'চূড়ান্ত পর্চা রেকর্ড'
                        : 'সাব-রেজিস্ট্রি সাফ কবলা দলিল'}
                    </h4>
                    <p className="text-[11px] text-amber-800">
                      নথি নম্বর: {fields.khatian_no || fields.deed_no || '৭৮/২০২৪'}
                    </p>
                  </div>

                  <div className="space-y-2 text-xs text-amber-900/90 leading-relaxed">
                    <p>
                      <strong>মৌজা:</strong> {fields.mouza || 'বাড্ডা'}, <strong>উপজেলা:</strong>{' '}
                      {fields.upazila || 'গুলশান'}, <strong>জেলা:</strong>{' '}
                      {fields.district || 'ঢাকা'}
                    </p>
                    <p>
                      <strong>দাগ নং:</strong> {fields.plot || '৪৫০'}, <strong>পরিমাণ:</strong>{' '}
                      {fields.area || '০.১৫ একর'}
                    </p>
                    <p>
                      <strong>স্বত্বাধিকারী:</strong> {fields.owner || 'মোঃ রফিকুল ইসলাম'}
                    </p>
                  </div>

                  <div className="pt-4 border-t border-dashed border-amber-800/30 flex justify-between items-center text-[11px] text-amber-800 italic">
                    <span>* স্ক্যান কপি সংরক্ষিত</span>
                    <span className="font-bold border border-amber-700/50 px-2 py-0.5 rounded text-[10px]">
                      সত্যায়িত
                    </span>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Right Panel: Tabs for Extracted Fields & OCR Text */}
        <div className="lg:col-span-6 space-y-4">
          <div className="bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden flex flex-col min-h-[500px]">
            {/* Tab Headers */}
            <div className="flex border-b border-slate-200 bg-slate-50/80 p-2 gap-2">
              <button
                type="button"
                onClick={() => setActiveTab('fields')}
                className={`flex-1 py-3 px-4 rounded-2xl font-bold text-sm flex items-center justify-center gap-2 transition-all ${
                  activeTab === 'fields'
                    ? 'bg-white text-emerald-800 shadow-sm border border-slate-200/80'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                }`}
              >
                <Layers className="w-4 h-4 text-emerald-700" />
                <span>{t('detail.extracted_fields')}</span>
                <span className="text-xs bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded-full">
                  {fieldList.length}
                </span>
              </button>

              <button
                type="button"
                onClick={() => setActiveTab('ocr')}
                className={`flex-1 py-3 px-4 rounded-2xl font-bold text-sm flex items-center justify-center gap-2 transition-all ${
                  activeTab === 'ocr'
                    ? 'bg-white text-emerald-800 shadow-sm border border-slate-200/80'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                }`}
              >
                <FileText className="w-4 h-4 text-emerald-700" />
                <span>{t('detail.ocr_text')}</span>
              </button>
            </div>

            {/* Tab Content */}
            <div className="p-6 flex-1 flex flex-col">
              {activeTab === 'fields' ? (
                /* Extracted Fields Tab */
                <div className="space-y-4 flex-1">
                  {fieldList.length > 0 ? (
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
                      {fieldList.map((item) => (
                        <div
                          key={item.key}
                          className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200/70 hover:border-emerald-200 transition-colors"
                        >
                          <span className="text-xs font-semibold text-slate-500 block mb-1">
                            {item.label}
                          </span>
                          <span className="text-sm font-bold text-slate-900 break-words">
                            {item.value}
                          </span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="p-8 text-center text-slate-400 italic">
                      {t('detail.no_fields')}
                    </div>
                  )}

                  {/* Extra custom fields if any */}
                  {extraFields.length > 0 && (
                    <div className="pt-4 border-t border-slate-100 space-y-2">
                      <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                        অন্যান্য মেটাডাটা
                      </h4>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        {extraFields.map(([k, val]) => (
                          <div
                            key={k}
                            className="p-3 rounded-xl bg-slate-50 border border-slate-200/70"
                          >
                            <span className="text-xs font-medium text-slate-500 block capitalize">
                              {k.replace(/_/g, ' ')}
                            </span>
                            <span className="text-xs font-semibold text-slate-800 break-all">
                              {typeof val === 'object' ? JSON.stringify(val) : String(val)}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                /* OCR Text Tab */
                <div className="space-y-4 flex-1 flex flex-col">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-slate-500">
                      অক্ষর সংখ্যা: {document.ocr_text ? document.ocr_text.length : 0}
                    </span>
                    <button
                      type="button"
                      onClick={handleCopyOcr}
                      disabled={!document.ocr_text}
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-emerald-50 hover:bg-emerald-100 text-emerald-800 text-xs font-semibold transition-colors disabled:opacity-50"
                    >
                      {copied ? (
                        <>
                          <Check className="w-3.5 h-3.5 text-emerald-600" />
                          <span>{t('detail.copied')}</span>
                        </>
                      ) : (
                        <>
                          <Copy className="w-3.5 h-3.5 text-emerald-700" />
                          <span>{t('detail.copy_ocr')}</span>
                        </>
                      )}
                    </button>
                  </div>

                  <div className="flex-1 relative">
                    <textarea
                      readOnly
                      value={document.ocr_text || t('detail.no_ocr')}
                      rows={14}
                      className="w-full h-full p-4 rounded-2xl bg-slate-50 border border-slate-200 text-slate-800 font-mono text-xs sm:text-sm leading-relaxed resize-none focus:outline-none focus:ring-2 focus:ring-emerald-500"
                    />
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
