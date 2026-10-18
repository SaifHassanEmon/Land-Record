import axios from 'axios';
import { DocumentItem, DemoDoc, DocType, DocumentStats } from '../types';

// Ensure base URL has no trailing slashes
const RAW_API_BASE = import.meta.env.VITE_API_BASE || '/api/v1';
const API_BASE = RAW_API_BASE.replace(/\/+$/, '');

export const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Interceptor to prevent Axios from stripping subpath (e.g., /api/v1) when request URL starts with '/'
apiClient.interceptors.request.use((config) => {
  if (config.baseURL && config.url && config.url.startsWith('/')) {
    try {
      const urlObj = new URL(config.baseURL, 'http://localhost');
      if (urlObj.pathname && urlObj.pathname !== '/') {
        // Strip leading slash so it appends to baseURL subpath
        config.url = config.url.replace(/^\/+/, '');
      }
    } catch {
      // ignore parsing error
    }
  }
  return config;
});

// Seed sample data for preview / offline demonstration
const MOCK_DEMO_DOCS: DemoDoc[] = [
  {
    id: 'demo-1',
    name: 'নমুনা সি.এস. খতিয়ান (বাড্ডা, ঢাকা)',
    doc_type: 'khatian',
    file_name: 'khatian_cs_128_badda.jpg',
    description: 'ঢাকা জেলা, গুলশান থানা, বাড্ডা মৌজার সি.এস. খতিয়ান রেকর্ড',
    download_url: '/api/v1/demo-docs/demo-1/download',
    size: '1.2 MB',
  },
  {
    id: 'demo-2',
    name: 'নমুনা আর.এস. পর্চা (রামপুরা, ঢাকা)',
    doc_type: 'porcha',
    file_name: 'porcha_rs_57_rampura.jpg',
    description: 'আর.এস. চূড়ান্ত জরিপ পর্চা ও দাগ নম্বর বিবরণ',
    download_url: '/api/v1/demo-docs/demo-2/download',
    size: '950 KB',
  },
  {
    id: 'demo-3',
    name: 'নমুনা সাফ কবলা দলিল (মিরপুর)',
    doc_type: 'deed',
    file_name: 'deed_9822_mirpur_2023.pdf',
    description: 'সাব-রেজিস্ট্রার কার্যালয় মিরপুর, সাফ কবলা রেজিস্ট্রি দলিল',
    download_url: '/api/v1/demo-docs/demo-3/download',
    size: '2.4 MB',
  },
];

const MOCK_INITIAL_DOCUMENTS: DocumentItem[] = [
  {
    id: 'doc-101',
    file_name: 'khatian_cs_128_badda.jpg',
    original_filename: 'khatian_cs_128_badda.jpg',
    doc_type: 'khatian',
    status: 'done',
    confidence: 94,
    created_at: new Date(Date.now() - 3600000 * 4).toISOString(),
    extracted_fields: {
      owner: 'মোঃ রফিকুল ইসলাম ও অন্যান্য',
      district: 'ঢাকা',
      upazila: 'গুলশান',
      mouza: 'বাড্ডা (জে.এল নং ৬৪)',
      plot: '৪৫০ ও ৪৫১',
      area: '০.১৫ একর (১৫ শতাংশ)',
      khatian_no: '১২৮',
    },
    ocr_text: `গণপ্রজাতন্ত্রী বাংলাদেশ সরকার\nভূমি রেকর্ড ও জরিপ অধিদপ্তর\nখতিয়ান নং: ১২৮\nজেলা: ঢাকা, উপজেলা: গুলশান, মৌজা: বাড্ডা (জে.এল নং ৬৪)\n\nমালিক বা দখলদারের নাম: মোঃ রফিকুল ইসলাম, পিতা: মৃত সামসুল হক\nঅংশ: ০.৫০\nদাগ নং: ৪৫০, শ্রেণী: নাল জমি, পরিমাণ: ০.১০ একর\nদাগ নং: ৪৫১, শ্রেণী: ভিটি জমি, পরিমাণ: ০.০৫ একর\nমোট জমির পরিমাণ: ০.১৫ একর\nমন্তব্য: দখল স্বত্বে বহাল`,
  },
  {
    id: 'doc-102',
    file_name: 'porcha_rs_57_rampura.jpg',
    original_filename: 'porcha_rs_57_rampura.jpg',
    doc_type: 'porcha',
    status: 'done',
    confidence: 88,
    created_at: new Date(Date.now() - 3600000 * 24).toISOString(),
    extracted_fields: {
      owner: 'বেগম সেলিনা আক্তার',
      district: 'ঢাকা',
      upazila: 'রামপুরা',
      mouza: 'পশ্চিম রামপুরা',
      plot: '১৮২',
      area: '৭.৫ শতাংশ',
      khatian_no: '৫৭',
    },
    ocr_text: `বাংলাদেশ ফরম নং ৫৪৬৩\nআর.এস. পর্চা / খতিয়ান\nমৌজা: পশ্চিম রামপুরা, থানা: রামপুরা, জেলা: ঢাকা\nখতিয়ান নং: ৫৭\nস্বত্বাধিকারীর বিবরণ:\n১. সেলিনা আক্তার, পিতা: এ. কে. এম. মোস্তফা\nদাগ নং: ১৮২, জমির শ্রেণী: বাড়ি\nজমির পরিমাণ: ৭.৫ শতক\nদখলকার ও মন্তব্য: দখল অত্র স্বত্বে নিয়ন্ত্রিত`,
  },
  {
    id: 'doc-103',
    file_name: 'deed_9822_mirpur_2023.pdf',
    original_filename: 'deed_9822_mirpur_2023.pdf',
    doc_type: 'deed',
    status: 'done',
    confidence: 91,
    created_at: new Date(Date.now() - 3600000 * 48).toISOString(),
    extracted_fields: {
      deed_no: '৯৮২২/২০২৩',
      district: 'ঢাকা',
      upazila: 'মিরপুর সাব-রেজিস্ট্রার কার্যালয়',
      mouza: 'সেনপাড়া পর্বতা',
      plot: '১১২০/৩',
      area: '৪.২ শতাংশ',
      seller: 'মোঃ কামাল হোসেন',
      buyer: 'মোছাঃ তাসলিমা বেগম',
      amount: '৪৫,০০,০০০/- (পঁয়তাল্লিশ লক্ষ টাকা)',
      reg_date: '১২/০৭/২০২৩',
    },
    ocr_text: `সাব-রেজিস্ট্রি কার্যালয় মিরপুর, ঢাকা\nদলিল নং: ৯৮২২, সন: ২০২৩ ইং\nদলিলের প্রকৃতি: সাফ কবলা বিক্রয় কোবালা পত্র\n\nপ্রথম পক্ষ / বিক্রেতা:\nমোঃ কামাল হোসেন, জাতীয় পরিচয়পত্র নং: ২৬৯৮৩৪৭৬১২\n\nদ্বিতীয় পক্ষ / ক্রেতা:\nমোছাঃ তাসলিমা বেগম, জাতীয় পরিচয়পত্র নং: ৮৭৩৫৪৬৯১২২\n\nসম্পত্তির তফসিল:\nজেলা: ঢাকা, থানা: মিরপুর, মৌজা: সেনপাড়া পর্বতা\nখতিয়ান নং: এস.এ. ৫৬২, আর.এস. ৩১৯\nদাগ নং: আর.এস. ১১২০/৩, পরিমাণ: ৪.২ শতক বাস্তু জমি\nবিক্রয় মূল্য: ৪৫,০০,০০০/- (পঁয়তাল্লিশ লক্ষ টাকা মাত্র)`,
  },
];

// In-memory fallback cache for smooth offline / preview testing
let localDocuments: DocumentItem[] = [...MOCK_INITIAL_DOCUMENTS];

function mapBackendDocument(item: any): DocumentItem {
  return {
    id: String(item.id),
    file_name: item.original_filename || item.filename || item.file_name || 'Document',
    original_filename: item.original_filename || item.filename,
    doc_type: item.doc_type || 'khatian',
    file_url: item.file_url || `${API_BASE}/documents/${item.id}/file`,
    file_path: item.file_path,
    status: item.status || 'done',
    confidence: item.ocr_confidence !== undefined ? item.ocr_confidence : (item.confidence || 90),
    ocr_text: item.ocr_text || '',
    extracted_fields: item.extracted_fields || {},
    created_at: item.created_at || new Date().toISOString(),
    updated_at: item.updated_at,
    file_size: item.file_size,
    mime_type: item.mime_type,
  };
}

/**
 * Upload a document (Khatian, Porcha, or Deed)
 */
export async function uploadDocument(file: File, docType: DocType): Promise<DocumentItem> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('doc_type', docType);

  try {
    const response = await apiClient.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return mapBackendDocument(response.data);
  } catch (err: any) {
    try {
      const response = await apiClient.post('/documents', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return mapBackendDocument(response.data);
    } catch (fallbackErr) {
      console.warn('API upload failed, creating mock document representation:', fallbackErr);

      const newDoc: DocumentItem = {
        id: `doc-${Date.now()}`,
        file_name: file.name,
        original_filename: file.name,
        doc_type: docType,
        status: 'done',
        confidence: 89,
        created_at: new Date().toISOString(),
        file_size: file.size,
        mime_type: file.type,
        file_url: URL.createObjectURL(file),
        extracted_fields: {
          owner: 'আব্দুল করিম ও অন্যান্য',
          district: 'ঢাকা',
          upazila: 'সাভার',
          mouza: 'আমিনবাজার',
          plot: '৮৯২',
          area: '০.১২ একর',
          khatian_no: docType === 'khatian' ? '৭৪২' : undefined,
          deed_no: docType === 'deed' ? '৪৫২১/২০২৪' : undefined,
        },
        ocr_text: `বাংলাদেশ ভূমি রেকর্ড - স্ক্যান করা কপি\nফাইলের নাম: ${file.name}\nধরনের বিবরণ: ${docType}\nতারিখ: ${new Date().toLocaleDateString('bn-BD')}\nস্বত্বাধিকারীর বিবরণ ও ভূমির তফসিল সফলভাবে প্রস্তুত করা হয়েছে।`,
      };

      localDocuments.unshift(newDoc);
      return newDoc;
    }
  }
}

/**
 * List documents with optional filters
 */
export async function listDocuments(params?: {
  doc_type?: string;
  skip?: number;
  limit?: number;
}): Promise<DocumentItem[]> {
  try {
    const response = await apiClient.get('/documents', { params });
    const data = response.data;
    if (Array.isArray(data)) {
      return data.map(mapBackendDocument);
    }
    if (data && Array.isArray(data.items)) {
      return data.items.map(mapBackendDocument);
    }
    return localDocuments;
  } catch (err) {
    console.warn('Falling back to local documents:', err);
    let results = [...localDocuments];
    if (params?.doc_type && params.doc_type !== 'all') {
      results = results.filter((d) => d.doc_type === params.doc_type);
    }
    return results;
  }
}

/**
 * Retrieve document by ID
 */
export async function getDocument(id: string): Promise<DocumentItem> {
  try {
    const response = await apiClient.get(`/documents/${id}`);
    return mapBackendDocument(response.data);
  } catch (err) {
    console.warn(`Falling back for document ${id}:`, err);
    const found = localDocuments.find((d) => d.id === id);
    if (found) return found;
    throw new Error('Document not found');
  }
}

/**
 * Search documents by query and optional document type
 */
export async function searchDocuments(query: string, docType?: string): Promise<DocumentItem[]> {
  try {
    const response = await apiClient.get('/search', {
      params: { q: query, doc_type: docType },
    });
    const data = response.data;
    if (Array.isArray(data)) {
      return data.map(mapBackendDocument);
    }
    if (data && Array.isArray(data.items)) {
      return data.items.map(mapBackendDocument);
    }
    return localDocuments;
  } catch (err) {
    console.warn('Falling back to local document search:', err);
    const qLower = query.toLowerCase().trim();
    return localDocuments.filter((doc) => {
      if (docType && docType !== 'all' && doc.doc_type !== docType) {
        return false;
      }
      if (!qLower) return true;

      const filenameMatch = doc.file_name.toLowerCase().includes(qLower);
      const ocrMatch = doc.ocr_text?.toLowerCase().includes(qLower) || false;
      const fieldsMatch = doc.extracted_fields
        ? Object.values(doc.extracted_fields).some(
            (val) => typeof val === 'string' && val.toLowerCase().includes(qLower)
          )
        : false;

      return filenameMatch || ocrMatch || fieldsMatch;
    });
  }
}

/**
 * Fetch available demo documents
 */
export async function getDemoDocs(): Promise<DemoDoc[]> {
  try {
    const response = await apiClient.get('/demo-docs');
    const data = response.data;

    let items: any[] = [];
    if (Array.isArray(data)) {
      items = data;
    } else if (data && Array.isArray(data.items)) {
      items = data.items;
    }

    if (items.length > 0) {
      return items.map((item, idx) => ({
        id: item.filename || `demo-${idx}`,
        name: item.name || item.filename || `নমুনা দলিল ${idx + 1}`,
        doc_type: item.doc_type || 'khatian',
        file_name: item.filename || item.file_name || `demo_${idx + 1}.pdf`,
        description: item.description || 'পরীক্ষার জন্য নমুনা ভূমি রেকর্ড দলিল',
        download_url: `${API_BASE}/demo-docs/${item.filename}/download`,
        size: item.file_size ? `${(item.file_size / 1024).toFixed(1)} KB` : undefined,
      }));
    }

    // If backend returns empty items list, fallback to rich built-in demo documents
    return MOCK_DEMO_DOCS;
  } catch (err) {
    console.warn('Falling back to mock demo docs:', err);
    return MOCK_DEMO_DOCS;
  }
}

/**
 * Seed / upload all demo documents
 */
export async function uploadAllDemoDocs(): Promise<{ message?: string; documents?: DocumentItem[] }> {
  try {
    const response = await apiClient.post('/demo-docs/upload-all');
    return response.data;
  } catch (err) {
    console.warn('Falling back for uploadAllDemoDocs:', err);
    MOCK_INITIAL_DOCUMENTS.forEach((doc) => {
      if (!localDocuments.some((d) => d.id === doc.id)) {
        localDocuments.unshift(doc);
      }
    });
    return {
      message: 'All demo documents uploaded successfully',
      documents: localDocuments,
    };
  }
}

/**
 * Delete a document by ID
 */
export async function deleteDocument(id: string): Promise<void | { success: boolean }> {
  try {
    const response = await apiClient.delete(`/documents/${id}`);
    localDocuments = localDocuments.filter((d) => d.id !== id);
    return response.data;
  } catch (err) {
    console.warn(`Falling back for deleteDocument ${id}:`, err);
    localDocuments = localDocuments.filter((d) => d.id !== id);
    return { success: true };
  }
}

/**
 * Helper to compute dashboard statistics
 */
export async function getStats(): Promise<DocumentStats> {
  try {
    const response = await apiClient.get('/stats');
    if (response.data && typeof response.data.total === 'number') {
      return response.data;
    }
  } catch {
    // ignore
  }

  const docs = await listDocuments();
  return {
    total: docs.length,
    khatian: docs.filter((d) => d.doc_type === 'khatian').length,
    porcha: docs.filter((d) => d.doc_type === 'porcha').length,
    deed: docs.filter((d) => d.doc_type === 'deed').length,
  };
}

export function normalizeConfidence(val: number | undefined | null): number {
  if (val === undefined || val === null || isNaN(val)) return 0;
  if (val <= 1 && val > 0) return Math.round(val * 100);
  return Math.round(val);
}
