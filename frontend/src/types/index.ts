export type DocType = 'khatian' | 'porcha' | 'deed';

export type DocumentStatus = 'done' | 'completed' | 'processing' | 'failed' | 'pending';

export interface ExtractedFields {
  owner?: string;
  district?: string;
  upazila?: string;
  mouza?: string;
  plot?: string;
  area?: string;
  khatian_no?: string;
  deed_no?: string;
  seller?: string;
  buyer?: string;
  amount?: string;
  reg_date?: string;
  [key: string]: any;
}

export interface DocumentItem {
  id: string;
  file_name: string;
  original_filename?: string;
  doc_type: DocType;
  file_url?: string;
  file_path?: string;
  status: DocumentStatus;
  confidence?: number;
  ocr_text?: string;
  extracted_fields?: ExtractedFields;
  created_at?: string;
  updated_at?: string;
  file_size?: number;
  mime_type?: string;
}

export interface DemoDoc {
  id: string;
  name: string;
  doc_type: DocType;
  file_name: string;
  description?: string;
  download_url?: string;
  file_path?: string;
  size?: string;
}

export interface DocumentStats {
  total: number;
  khatian: number;
  porcha: number;
  deed: number;
}
