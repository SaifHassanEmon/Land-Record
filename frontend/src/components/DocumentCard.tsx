import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Calendar, Eye, Trash2, MapPin, User, Hash } from 'lucide-react';
import { DocumentItem } from '../types';
import { DocumentBadge } from './DocumentBadge';
import { normalizeConfidence } from '../api/client';

interface DocumentCardProps {
  document: DocumentItem;
  onDelete?: (id: string) => void;
}

export const DocumentCard: React.FC<DocumentCardProps> = ({ document, onDelete }) => {
  const { t, i18n } = useTranslation();
  const isBengali = i18n.language?.startsWith('bn');

  const confVal = normalizeConfidence(document.confidence);

  // Confidence styling
  let confColor = 'text-rose-600 bg-rose-50 border-rose-200';
  let confProgressColor = 'bg-rose-500';
  if (confVal >= 80) {
    confColor = 'text-emerald-700 bg-emerald-50 border-emerald-200';
    confProgressColor = 'bg-emerald-600';
  } else if (confVal >= 60) {
    confColor = 'text-amber-700 bg-amber-50 border-amber-200';
    confProgressColor = 'bg-amber-500';
  }

  // Format date
  const formatDate = (dateStr?: string) => {
    if (!dateStr) return '';
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString(isBengali ? 'bn-BD' : 'en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      });
    } catch {
      return dateStr;
    }
  };

  const fields = document.extracted_fields || {};

  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition-all duration-300 flex flex-col justify-between overflow-hidden group">
      <div>
        {/* Card Header */}
        <div className="p-4 border-b border-slate-100 flex items-center justify-between gap-2 bg-slate-50/60">
          <DocumentBadge type={document.doc_type} size="sm" />
          <div className="flex items-center gap-2">
            <DocumentBadge status={document.status} size="sm" />
          </div>
        </div>

        {/* Card Body */}
        <div className="p-5">
          <Link
            to={`/documents/${document.id}`}
            className="block group-hover:text-emerald-700 transition-colors"
          >
            <h3 className="font-semibold text-slate-900 text-base md:text-lg truncate tracking-tight mb-1" title={document.file_name}>
              {document.file_name}
            </h3>
          </Link>

          {/* Date info */}
          <div className="flex items-center gap-1.5 text-xs text-slate-500 mb-4">
            <Calendar className="w-3.5 h-3.5" />
            <span>{formatDate(document.created_at)}</span>
          </div>

          {/* Extracted Fields Preview */}
          <div className="space-y-1.5 text-xs text-slate-600 bg-slate-50 p-3 rounded-xl border border-slate-100 mb-4">
            {fields.owner && (
              <div className="flex items-center gap-2 truncate">
                <User className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                <span className="font-medium text-slate-500">{t('detail.owner')}:</span>
                <span className="truncate text-slate-800">{fields.owner}</span>
              </div>
            )}
            {(fields.mouza || fields.district) && (
              <div className="flex items-center gap-2 truncate">
                <MapPin className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                <span className="font-medium text-slate-500">{t('detail.mouza')}:</span>
                <span className="truncate text-slate-800">
                  {[fields.mouza, fields.district].filter(Boolean).join(', ')}
                </span>
              </div>
            )}
            {(fields.plot || fields.khatian_no || fields.deed_no) && (
              <div className="flex items-center gap-2 truncate">
                <Hash className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                <span className="font-medium text-slate-500">
                  {fields.khatian_no ? t('detail.khatian_no') : (fields.deed_no ? t('detail.deed_no') : t('detail.plot'))}:
                </span>
                <span className="truncate text-slate-800 font-mono">
                  {fields.khatian_no || fields.deed_no || fields.plot}
                </span>
              </div>
            )}
            {!fields.owner && !fields.mouza && !fields.plot && (
              <div className="text-slate-400 italic py-1 text-center">
                {t('detail.extracted_fields')}
              </div>
            )}
          </div>

          {/* Confidence Score Bar */}
          <div className="mt-2">
            <div className="flex items-center justify-between text-xs mb-1">
              <span className="text-slate-500 font-medium">{t('detail.confidence')}</span>
              <span className={`px-2 py-0.5 rounded-full font-bold border text-[11px] ${confColor}`}>
                {confVal}%
              </span>
            </div>
            <div className="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-500 ${confProgressColor}`}
                style={{ width: `${confVal}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Card Footer Actions */}
      <div className="px-5 py-3.5 bg-slate-50/80 border-t border-slate-100 flex items-center justify-between">
        <Link
          to={`/documents/${document.id}`}
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-emerald-700 hover:text-emerald-800 transition-colors"
        >
          <Eye className="w-4 h-4" />
          <span>{t('common.view')}</span>
        </Link>

        {onDelete && (
          <button
            type="button"
            onClick={() => onDelete(document.id)}
            className="inline-flex items-center gap-1 text-xs font-medium text-slate-400 hover:text-rose-600 transition-colors p-1 rounded-md hover:bg-rose-50"
            title={t('common.delete')}
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span>{t('common.delete')}</span>
          </button>
        )}
      </div>
    </div>
  );
};
