import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  Upload as UploadIcon,
  FileCheck,
  CheckCircle2,
  AlertCircle,
  Sparkles,
  X,
  FileText,
  ScrollText,
  Image as ImageIcon,
} from 'lucide-react';
import { DocType } from '../types';
import { uploadDocument, fetchDemoFile } from '../api/client';
import { DocumentBadge } from '../components/DocumentBadge';
import { LoadingSpinner } from '../components/LoadingSpinner';

export const Upload: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [filePreviewUrl, setFilePreviewUrl] = useState<string | null>(null);
  const [docType, setDocType] = useState<DocType>('khatian');
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [isLoadingDemo, setIsLoadingDemo] = useState<boolean>(false);
  const [uploadSuccess, setUploadSuccess] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

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
      setNewFile(file);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setNewFile(e.target.files[0]);
    }
  };

  const setNewFile = (file: File) => {
    setSelectedFile(file);
    setErrorMessage(null);
    if (file.type.startsWith('image/')) {
      const url = URL.createObjectURL(file);
      setFilePreviewUrl(url);
    } else {
      setFilePreviewUrl(null);
    }
  };

  const clearSelectedFile = () => {
    if (filePreviewUrl) {
      URL.revokeObjectURL(filePreviewUrl);
    }
    setSelectedFile(null);
    setFilePreviewUrl(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  /**
   * Loads the authentic user-provided demo image matching the selected or requested docType
   */
  const handleUseDemo = async (targetType: 'khatian' | 'porcha') => {
    try {
      setIsLoadingDemo(true);
      setErrorMessage(null);
      setDocType(targetType);
      const file = await fetchDemoFile(targetType);
      setNewFile(file);
    } catch (err: any) {
      console.error('Failed to load demo file:', err);
      setErrorMessage(err.message || 'নমুনা ফাইল লোড করতে সমস্যা হয়েছে।');
    } finally {
      setIsLoadingDemo(false);
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
      }, 1000);
    } catch (err: any) {
      console.error('Upload failed:', err);
      setErrorMessage(err.message || t('common.error'));
    } finally {
      setIsUploading(false);
    }
  };

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return '';
    const kb = bytes / 1024;
    if (kb < 1024) return `${kb.toFixed(1)} KB`;
    return `${(kb / 1024).toFixed(1)} MB`;
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      {/* Header */}
      <div className="text-center max-w-2xl mx-auto space-y-2">
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
          {t('upload.title')}
        </h1>
        <p className="text-slate-600 text-sm sm:text-base">
          {t('home.description')}
        </p>
      </div>

      {/* Main Upload Container */}
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

        {/* Quick Demo Document Option Banner */}
        <div className="bg-gradient-to-r from-emerald-50 via-teal-50 to-slate-50 border border-emerald-200/80 rounded-2xl p-5 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-emerald-600" />
              <span className="font-bold text-slate-900 text-sm sm:text-base">
                {t('upload.or_use_demo')}
              </span>
            </div>
            {isLoadingDemo && (
              <span className="text-xs font-semibold text-emerald-700 flex items-center gap-1.5">
                <LoadingSpinner size="sm" message="" />
                <span>লোড হচ্ছে...</span>
              </span>
            )}
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
            {/* Demo Khatian Button */}
            <button
              type="button"
              onClick={() => handleUseDemo('khatian')}
              disabled={isLoadingDemo || isUploading}
              className={`p-3.5 rounded-xl border text-left transition-all flex items-center gap-3.5 ${
                docType === 'khatian' && selectedFile?.name.includes('khatian')
                  ? 'border-emerald-600 bg-white ring-2 ring-emerald-500 shadow-sm'
                  : 'border-emerald-200 hover:border-emerald-400 bg-white/90 hover:bg-white'
              }`}
            >
              <div className="w-12 h-12 rounded-lg bg-emerald-100 flex items-center justify-center shrink-0 overflow-hidden border border-emerald-200">
                <img
                  src="/demo/khatian_demo.png"
                  alt="নমুনা খতিয়ান"
                  className="w-full h-full object-cover"
                />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-1.5">
                  <ScrollText className="w-4 h-4 text-emerald-700 shrink-0" />
                  <span className="font-bold text-slate-900 text-sm truncate">
                    {t('upload.use_demo_khatian')}
                  </span>
                </div>
                <p className="text-xs text-slate-500 truncate mt-0.5">
                  {t('upload.demo_khatian_sub')}
                </p>
              </div>
            </button>

            {/* Demo Porcha Button */}
            <button
              type="button"
              onClick={() => handleUseDemo('porcha')}
              disabled={isLoadingDemo || isUploading}
              className={`p-3.5 rounded-xl border text-left transition-all flex items-center gap-3.5 ${
                docType === 'porcha' && selectedFile?.name.includes('porcha')
                  ? 'border-emerald-600 bg-white ring-2 ring-emerald-500 shadow-sm'
                  : 'border-emerald-200 hover:border-emerald-400 bg-white/90 hover:bg-white'
              }`}
            >
              <div className="w-12 h-12 rounded-lg bg-blue-100 flex items-center justify-center shrink-0 overflow-hidden border border-blue-200">
                <img
                  src="/demo/porcha_demo.jpg"
                  alt="নমুনা পর্চা"
                  className="w-full h-full object-cover"
                />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-1.5">
                  <FileText className="w-4 h-4 text-blue-700 shrink-0" />
                  <span className="font-bold text-slate-900 text-sm truncate">
                    {t('upload.use_demo_porcha')}
                  </span>
                </div>
                <p className="text-xs text-slate-500 truncate mt-0.5">
                  {t('upload.demo_porcha_sub')}
                </p>
              </div>
            </button>
          </div>
        </div>

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
            className={`border-2 border-dashed rounded-3xl p-6 sm:p-10 text-center cursor-pointer transition-all duration-200 ${
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
              {filePreviewUrl ? (
                <div className="relative group">
                  <div className="w-24 h-28 sm:w-28 sm:h-32 rounded-xl border border-slate-200 shadow-sm overflow-hidden bg-white mx-auto">
                    <img
                      src={filePreviewUrl}
                      alt="Preview"
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <div className="absolute -top-2 -right-2 bg-emerald-600 text-white rounded-full p-1 shadow">
                    <FileCheck className="w-4 h-4" />
                  </div>
                </div>
              ) : (
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
              )}

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
                      clearSelectedFile();
                    }}
                    className="inline-flex items-center gap-1 text-xs text-rose-600 hover:text-rose-700 font-medium pt-1"
                  >
                    <X className="w-3.5 h-3.5" />
                    <span>{t('upload.remove_file')}</span>
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

          {/* Submit Button & Direct Demo Action */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-2">
            <div>
              {(!selectedFile && (docType === 'khatian' || docType === 'porcha')) && (
                <button
                  type="button"
                  onClick={() => handleUseDemo(docType as 'khatian' | 'porcha')}
                  className="inline-flex items-center gap-1.5 text-xs sm:text-sm font-semibold text-emerald-700 hover:text-emerald-800 bg-emerald-50 hover:bg-emerald-100 px-3.5 py-2 rounded-xl transition-colors"
                >
                  <Sparkles className="w-4 h-4 text-emerald-600" />
                  <span>
                    {docType === 'khatian'
                      ? 'নমুনা খতিয়ান ফাইল লোড করুন'
                      : 'নমুনা পর্চা ফাইল লোড করুন'}
                  </span>
                </button>
              )}
            </div>

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
                  <span>{t('upload.upload_and_process')}</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
