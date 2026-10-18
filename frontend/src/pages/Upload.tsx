import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  Upload as UploadIcon,
  FileCheck,
  Download,
  CheckCircle2,
  AlertCircle,
  Sparkles,
  FileText,
  X,
  ArrowRight,
  Layers,
} from 'lucide-react';
import { DocType, DemoDoc } from '../types';
import {
  uploadDocument,
  getDemoDocs,
  uploadAllDemoDocs,
  apiClient,
} from '../api/client';
import { DocumentBadge } from '../components/DocumentBadge';
import { LoadingSpinner } from '../components/LoadingSpinner';

export const Upload: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [docType, setDocType] = useState<DocType>('khatian');
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [uploadSuccess, setUploadSuccess] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Demo docs states
  const [demoDocs, setDemoDocs] = useState<DemoDoc[]>([]);
  const [loadingDemoDocs, setLoadingDemoDocs] = useState<boolean>(true);
  const [isUploadingAllDemo, setIsUploadingAllDemo] = useState<boolean>(false);
  const [demoSuccessMsg, setDemoSuccessMsg] = useState<string | null>(null);

  useEffect(() => {
    async function fetchDemos() {
      try {
        setLoadingDemoDocs(true);
        const docs = await getDemoDocs();
        setDemoDocs(docs);
      } catch (err) {
        console.error('Failed to load demo docs:', err);
      } finally {
        setLoadingDemoDocs(false);
      }
    }
    fetchDemos();
  }, []);

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      setSelectedFile(file);
      setErrorMessage(null);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setSelectedFile(e.target.files[0]);
      setErrorMessage(null);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) {
      setErrorMessage(t('upload.select_file_warning'));
      return;
    }

    try {
      setIsUploading(true);
      setErrorMessage(null);
      await uploadDocument(selectedFile, docType);
      setUploadSuccess(true);

      // Redirect to documents list after a brief delay
      setTimeout(() => {
        navigate('/documents');
      }, 1200);
    } catch (err: any) {
      console.error('Upload failed:', err);
      setErrorMessage(err.message || t('common.error'));
    } finally {
      setIsUploading(false);
    }
  };

  const handleUploadAllDemo = async () => {
    try {
      setIsUploadingAllDemo(true);
      setErrorMessage(null);
      await uploadAllDemoDocs();
      setDemoSuccessMsg(t('upload.upload_all_success'));

      setTimeout(() => {
        navigate('/documents');
      }, 1200);
    } catch (err: any) {
      console.error('Upload all demo docs failed:', err);
      setErrorMessage(err.message || t('common.error'));
    } finally {
      setIsUploadingAllDemo(false);
    }
  };

  const handleDownloadDemo = async (demo: DemoDoc) => {
    try {
      // Direct download trigger
      const downloadEndpoint = demo.download_url || `/demo-docs/${demo.id}/download`;
      const fullUrl = downloadEndpoint.startsWith('http')
        ? downloadEndpoint
        : `${apiClient.defaults.baseURL || '/api/v1'}${downloadEndpoint.startsWith('/') ? '' : '/'}${downloadEndpoint}`;

      // Open in new tab or trigger download
      window.open(fullUrl, '_blank');
    } catch (err) {
      console.error('Failed to download demo doc:', err);
    }
  };

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return '';
    const kb = bytes / 1024;
    if (kb < 1024) return `${kb.toFixed(1)} KB`;
    return `${(kb / 1024).toFixed(1)} MB`;
  };

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-12">
      {/* Header */}
      <div className="text-center max-w-2xl mx-auto space-y-2">
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
          {t('upload.title')}
        </h1>
        <p className="text-slate-600 text-sm sm:text-base">
          {t('home.description')}
        </p>
      </div>

      {/* Main Upload Form */}
      <div className="bg-white rounded-3xl border border-slate-200 shadow-sm p-6 sm:p-10 space-y-8">
        {/* Error Alert */}
        {errorMessage && (
          <div className="p-4 rounded-2xl bg-rose-50 border border-rose-200 text-rose-700 text-sm flex items-center gap-3">
            <AlertCircle className="w-5 h-5 shrink-0 text-rose-600" />
            <p className="font-medium">{errorMessage}</p>
          </div>
        )}

        {/* Success Alert */}
        {uploadSuccess && (
          <div className="p-4 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-sm flex items-center gap-3 animate-in fade-in">
            <CheckCircle2 className="w-5 h-5 shrink-0 text-emerald-600" />
            <div>
              <p className="font-bold">{t('upload.success')}</p>
              <p className="text-xs text-emerald-700">নথিপত্র তালিকায় স্থানান্তরিত করা হচ্ছে...</p>
            </div>
          </div>
        )}

        <form onSubmit={handleUpload} className="space-y-6">
          {/* Document Type Selector */}
          <div>
            <label className="block text-sm font-bold text-slate-800 mb-2.5">
              {t('upload.doc_type')}
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              {[
                { type: 'khatian', label: t('upload.khatian'), desc: 'সি.এস, এস.এ, আর.এস ও বি.এস' },
                { type: 'porcha', label: t('upload.porcha'), desc: 'জরিপ পরবর্তী রেকর্ড' },
                { type: 'deed', label: t('upload.deed'), desc: 'সাব-রেজিস্ট্রি ক্রয়-বিক্রয় দলিল' },
              ].map((item) => (
                <button
                  key={item.type}
                  type="button"
                  onClick={() => setDocType(item.type as DocType)}
                  className={`p-4 rounded-2xl border text-left transition-all ${
                    docType === item.type
                      ? 'border-emerald-600 bg-emerald-50/70 ring-2 ring-emerald-600/30'
                      : 'border-slate-200 hover:border-slate-300 bg-white'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-bold text-slate-900 text-sm">{item.label}</span>
                    <DocumentBadge type={item.type} size="sm" />
                  </div>
                  <span className="text-xs text-slate-500 block truncate">{item.desc}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Drag & Drop Zone */}
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed rounded-3xl p-8 sm:p-12 text-center cursor-pointer transition-all duration-200 ${
              isDragging
                ? 'border-emerald-600 bg-emerald-50/60 scale-[1.01]'
                : selectedFile
                ? 'border-emerald-400 bg-emerald-50/20'
                : 'border-slate-300 hover:border-emerald-500 hover:bg-slate-50/50'
            }`}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".jpg,.jpeg,.png,.pdf"
              onChange={handleFileChange}
              className="hidden"
            />

            <div className="flex flex-col items-center justify-center space-y-3">
              <div
                className={`w-16 h-16 rounded-2xl flex items-center justify-center transition-transform ${
                  selectedFile
                    ? 'bg-emerald-100 text-emerald-700'
                    : 'bg-emerald-50 text-emerald-700'
                }`}
              >
                {selectedFile ? (
                  <FileCheck className="w-8 h-8" />
                ) : (
                  <UploadIcon className="w-8 h-8 animate-bounce-short" />
                )}
              </div>

              {selectedFile ? (
                <div className="space-y-1">
                  <p className="font-bold text-slate-900 text-base max-w-md mx-auto truncate">
                    {selectedFile.name}
                  </p>
                  <p className="text-xs text-slate-500 font-mono">
                    {formatFileSize(selectedFile.size)} &bull; {selectedFile.type || 'Document'}
                  </p>
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      setSelectedFile(null);
                      if (fileInputRef.current) fileInputRef.current.value = '';
                    }}
                    className="inline-flex items-center gap-1 text-xs text-rose-600 hover:text-rose-700 font-medium pt-1"
                  >
                    <X className="w-3.5 h-3.5" />
                    <span>{t('upload.remove_file') || 'বাতিল করুন'}</span>
                  </button>
                </div>
              ) : (
                <div className="space-y-1">
                  <p className="text-base font-semibold text-slate-800">
                    {t('upload.drag_drop')}
                  </p>
                  <p className="text-xs text-slate-500">
                    {t('upload.supported')}
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Submit Button */}
          <div className="flex justify-end pt-2">
            <button
              type="submit"
              disabled={isUploading || !selectedFile}
              className={`w-full sm:w-auto px-8 py-3.5 rounded-xl font-bold text-sm md:text-base text-white transition-all shadow-md flex items-center justify-center gap-2 ${
                isUploading || !selectedFile
                  ? 'bg-slate-300 cursor-not-allowed text-slate-500 shadow-none'
                  : 'bg-emerald-700 hover:bg-emerald-800 active:scale-95 shadow-emerald-700/20'
              }`}
            >
              {isUploading ? (
                <>
                  <LoadingSpinner size="sm" message="" />
                  <span>{t('upload.processing')}</span>
                </>
              ) : (
                <>
                  <UploadIcon className="w-5 h-5" />
                  <span>{t('upload.upload_btn')}</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Demo Documents Section */}
      <section className="bg-slate-100/70 rounded-3xl border border-slate-200 p-6 sm:p-8 space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-amber-500" />
              <h2 className="text-lg sm:text-xl font-bold text-slate-900">
                {t('upload.demo_title')}
              </h2>
            </div>
            <p className="text-xs sm:text-sm text-slate-600">
              {t('upload.demo_desc')}
            </p>
          </div>

          {/* Upload All Demo Docs button */}
          <button
            type="button"
            onClick={handleUploadAllDemo}
            disabled={isUploadingAllDemo}
            className="inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl bg-emerald-700 hover:bg-emerald-800 text-white font-semibold text-xs sm:text-sm shadow-sm transition-all active:scale-95 disabled:bg-slate-300 disabled:cursor-not-allowed shrink-0"
          >
            {isUploadingAllDemo ? (
              <>
                <LoadingSpinner size="sm" message="" />
                <span>{t('upload.uploading_all')}</span>
              </>
            ) : (
              <>
                <Layers className="w-4 h-4" />
                <span>{t('upload.demo_upload_all')}</span>
              </>
            )}
          </button>
        </div>

        {demoSuccessMsg && (
          <div className="p-3.5 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-sm flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            <span className="font-semibold">{demoSuccessMsg}</span>
          </div>
        )}

        {/* Demo Documents Cards */}
        {loadingDemoDocs ? (
          <LoadingSpinner />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {demoDocs.map((demo) => (
              <div
                key={demo.id}
                className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs hover:shadow-sm transition-all flex flex-col justify-between"
              >
                <div className="space-y-3">
                  <div className="flex items-center justify-between gap-2">
                    <DocumentBadge type={demo.doc_type} size="sm" />
                    {demo.size && (
                      <span className="text-[11px] font-mono text-slate-400">
                        {demo.size}
                      </span>
                    )}
                  </div>
                  <div>
                    <h4 className="font-bold text-slate-900 text-sm tracking-tight line-clamp-1">
                      {demo.name}
                    </h4>
                    <p className="text-xs text-slate-500 mt-1 line-clamp-2">
                      {demo.description || demo.file_name}
                    </p>
                  </div>
                </div>

                <div className="pt-4 mt-3 border-t border-slate-100 flex items-center justify-between">
                  <span className="text-[11px] text-slate-400 font-mono truncate max-w-[120px]">
                    {demo.file_name}
                  </span>
                  <button
                    type="button"
                    onClick={() => handleDownloadDemo(demo)}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-emerald-50 text-slate-700 hover:text-emerald-700 text-xs font-semibold transition-colors"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>{t('upload.download')}</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
};
