import React from 'react';
import { useTranslation } from 'react-i18next';
import { DocType, DocumentStatus } from '../types';
import { FileText, Award, ScrollText, CheckCircle2, Clock, AlertTriangle } from 'lucide-react';

interface DocumentBadgeProps {
  type?: DocType | string;
  status?: DocumentStatus | string;
  confidence?: number;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export const DocumentBadge: React.FC<DocumentBadgeProps> = ({
  type,
  status,
  confidence,
  size = 'md',
  className = '',
}) => {
  const { t } = useTranslation();

  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5 gap-1',
    md: 'text-xs md:text-sm px-2.5 py-1 gap-1.5',
    lg: 'text-sm px-3 py-1.5 gap-2 font-medium',
  };

  // If rendering doc_type badge
  if (type) {
    const normalizedType = type.toLowerCase();
    switch (normalizedType) {
      case 'khatian':
        return (
          <span
            className={`inline-flex items-center rounded-full font-medium border bg-emerald-100/90 text-emerald-800 border-emerald-300 ${sizeClasses[size]} ${className}`}
          >
            <ScrollText className="w-3.5 h-3.5 text-emerald-700" />
            <span>{t('upload.khatian')}</span>
          </span>
        );
      case 'porcha':
        return (
          <span
            className={`inline-flex items-center rounded-full font-medium border bg-blue-100/90 text-blue-800 border-blue-300 ${sizeClasses[size]} ${className}`}
          >
            <FileText className="w-3.5 h-3.5 text-blue-700" />
            <span>{t('upload.porcha')}</span>
          </span>
        );
      case 'deed':
        return (
          <span
            className={`inline-flex items-center rounded-full font-medium border bg-amber-100/90 text-amber-900 border-amber-300 ${sizeClasses[size]} ${className}`}
          >
            <Award className="w-3.5 h-3.5 text-amber-700" />
            <span>{t('upload.deed')}</span>
          </span>
        );
      default:
        return (
          <span
            className={`inline-flex items-center rounded-full font-medium border bg-slate-100 text-slate-700 border-slate-300 ${sizeClasses[size]} ${className}`}
          >
            <FileText className="w-3.5 h-3.5" />
            <span>{type}</span>
          </span>
        );
    }
  }

  // If rendering status badge
  if (status) {
    const normalizedStatus = status.toLowerCase();
    switch (normalizedStatus) {
      case 'done':
      case 'completed':
        return (
          <span
            className={`inline-flex items-center rounded-full font-medium border bg-emerald-50 text-emerald-700 border-emerald-200 ${sizeClasses[size]} ${className}`}
          >
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
            <span>{t('documents.status_done')}</span>
          </span>
        );
      case 'processing':
      case 'pending':
        return (
          <span
            className={`inline-flex items-center rounded-full font-medium border bg-amber-50 text-amber-700 border-amber-200 ${sizeClasses[size]} ${className}`}
          >
            <Clock className="w-3.5 h-3.5 text-amber-600 animate-spin" />
            <span>{t('documents.status_processing')}</span>
          </span>
        );
      case 'failed':
      default:
        return (
          <span
            className={`inline-flex items-center rounded-full font-medium border bg-rose-50 text-rose-700 border-rose-200 ${sizeClasses[size]} ${className}`}
          >
            <AlertTriangle className="w-3.5 h-3.5 text-rose-600" />
            <span>{t('documents.status_failed')}</span>
          </span>
        );
    }
  }

  // If rendering confidence badge
  if (confidence !== undefined) {
    const confVal = confidence <= 1 && confidence > 0 ? Math.round(confidence * 100) : Math.round(confidence);
    let colorClass = 'bg-rose-50 text-rose-700 border-rose-200';
    if (confVal >= 80) {
      colorClass = 'bg-emerald-50 text-emerald-800 border-emerald-200';
    } else if (confVal >= 60) {
      colorClass = 'bg-amber-50 text-amber-800 border-amber-200';
    }

    return (
      <span
        className={`inline-flex items-center rounded-full font-semibold border ${colorClass} ${sizeClasses[size]} ${className}`}
      >
        <span>{confVal}%</span>
      </span>
    );
  }

  return null;
};
