import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  HelpCircle,
  X,
  FileText,
  ScrollText,
  Sparkles,
  Edit3,
  Save,
  CheckCircle2,
  Search,
  Upload,
  ArrowRight,
  ShieldCheck,
  Check,
  Play,
  FileCheck,
} from 'lucide-react';
import { DocType } from '../types';

interface OptionsDemoGuideProps {
  onSelectDocType?: (type: DocType) => void;
  onUseDemo?: (type: 'khatian' | 'porcha') => void;
}

export const OptionsDemoGuide: React.FC<OptionsDemoGuideProps> = ({
  onSelectDocType,
  onUseDemo,
}) => {
  const { t, i18n } = useTranslation();
  const isBengali = i18n.language?.startsWith('bn');
  const [isOpen, setIsOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<'types' | 'upload' | 'ocr' | 'verify' | 'search'>('types');

  const guideSections = [
    {
      id: 'types',
      title: isBengali ? '১. দলিলের ধরন' : '1. Document Types',
      subtitle: isBengali ? 'খতিয়ান, পর্চা ও দলিল' : 'Khatian, Porcha & Deed',
      icon: ScrollText,
      color: 'emerald',
    },
    {
      id: 'upload',
      title: isBengali ? '২. আপলোড পদ্ধতি' : '2. Upload Methods',
      subtitle: isBengali ? 'নমুনা ফাইল ও নিজস্ব স্ক্যান' : 'Demo vs Custom Upload',
      icon: Upload,
      color: 'blue',
    },
    {
      id: 'ocr',
      title: isBengali ? '৩. বাংলা OCR ও সেভ' : '3. OCR & Auto-Save',
      subtitle: isBengali ? 'লেখা উদ্ধার ও সংরক্ষণ' : 'Text Extraction & Storage',
      icon: Sparkles,
      color: 'purple',
    },
    {
      id: 'verify',
      title: isBengali ? '৪. যাচাই ও সম্পাদনা' : '4. Verify & Save',
      subtitle: isBengali ? 'হাতে লেখা তথ্য পরিবর্তন' : 'Review & Correct Fields',
      icon: Edit3,
      color: 'amber',
    },
    {
      id: 'search',
      title: isBengali ? '৫. দলিলসমূহ ও খোঁজ' : '5. Documents & Search',
      subtitle: isBengali ? 'অনুসন্ধান ও ফিল্টারিং' : 'Full-Text Search',
      icon: Search,
      color: 'teal',
    },
  ];

  return (
    <>
      {/* Trigger Button */}
      <button
        type="button"
        onClick={() => setIsOpen(true)}
        className="inline-flex items-center gap-2 px-4 py-2 rounded-2xl bg-gradient-to-r from-emerald-50 to-teal-50 hover:from-emerald-100 hover:to-teal-100 border border-emerald-300 text-emerald-800 text-xs sm:text-sm font-bold shadow-xs transition-all active:scale-95"
      >
        <HelpCircle className="w-4 h-4 text-emerald-700 shrink-0" />
        <span>
          {isBengali
            ? '💡 কোন অপশনটি কী কাজ করে? (অপশন গাইড ও ডেমো)'
            : '💡 Options Guide & Feature Walkthrough'}
        </span>
      </button>

      {/* Modal Dialog */}
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs animate-in fade-in duration-200">
          <div className="relative w-full max-w-4xl bg-white rounded-3xl shadow-2xl border border-slate-200 overflow-hidden max-h-[92vh] flex flex-col">
            {/* Modal Header */}
            <div className="px-6 py-5 bg-gradient-to-r from-emerald-800 to-teal-900 text-white flex items-center justify-between shrink-0">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-white/10 flex items-center justify-center">
                  <HelpCircle className="w-6 h-6 text-emerald-300" />
                </div>
                <div>
                  <h3 className="text-lg sm:text-xl font-black">
                    {isBengali
                      ? 'বাংলাদেশ ভূমি রেকর্ড ডিজিটাইজেশন — অপশন পরিচিতি ও ডেমো'
                      : 'Land Records System — Options & Features Guide'}
                  </h3>
                  <p className="text-xs sm:text-sm text-emerald-200">
                    {isBengali
                      ? 'প্রতিটি অপশনের কাজ ও ব্যবহারের নিয়ম বিস্তারিতভাবে জেনে নিন'
                      : 'Detailed explanation of each option and how to use it'}
                  </p>
                </div>
              </div>

              <button
                type="button"
                onClick={() => setIsOpen(false)}
                className="w-9 h-9 rounded-full bg-white/10 hover:bg-white/20 flex items-center justify-center text-white transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Navigation Tabs */}
            <div className="flex border-b border-slate-200 bg-slate-50 overflow-x-auto shrink-0 p-2 gap-1.5 scrollbar-thin">
              {guideSections.map((sec) => {
                const Icon = sec.icon;
                const isActive = activeTab === sec.id;
                return (
                  <button
                    key={sec.id}
                    type="button"
                    onClick={() => setActiveTab(sec.id as any)}
                    className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs sm:text-sm font-bold whitespace-nowrap transition-all ${
                      isActive
                        ? 'bg-emerald-700 text-white shadow-sm'
                        : 'bg-white hover:bg-slate-100 text-slate-700 border border-slate-200'
                    }`}
                  >
                    <Icon className="w-4 h-4 shrink-0" />
                    <span>{sec.title}</span>
                  </button>
                );
              })}
            </div>

            {/* Tab Contents */}
            <div className="p-6 sm:p-8 overflow-y-auto flex-1 space-y-6">
              {/* TAB 1: DOCUMENT TYPES */}
              {activeTab === 'types' && (
                <div className="space-y-6 animate-in fade-in duration-200">
                  <div className="border-b border-slate-100 pb-3">
                    <h4 className="text-base sm:text-lg font-bold text-slate-900">
                      {isBengali
                        ? 'দলিলের ধরন নির্বাচন (Choose Document Type)'
                        : 'Choose Document Type'}
                    </h4>
                    <p className="text-xs sm:text-sm text-slate-500 mt-0.5">
                      {isBengali
                        ? 'সিস্টেমটি বাংলাদেশ ভূমি মন্ত্রণালয়ের প্রধান তিন ধরনের দলিল আলাদা এআই মডেলে প্রসেস করে:'
                        : 'The system uses specialized extractors for the 3 official document types:'}
                    </p>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {/* Khatian Card */}
                    <div className="p-5 rounded-2xl border-2 border-emerald-500/80 bg-emerald-50/50 space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="font-extrabold text-emerald-950 text-base">
                          {isBengali ? '১. খতিয়ান (Khatian)' : '1. Khatian'}
                        </span>
                        <span className="px-2.5 py-1 rounded-lg text-xs font-bold bg-emerald-700 text-white">
                          রেকর্ড অব রাইটস
                        </span>
                      </div>
                      <p className="text-xs text-slate-700 leading-relaxed">
                        {isBengali
                          ? 'সি.এস, এস.এ, আর.এস ও বি.এস সরকারি জমাবন্দি খতিয়ান। সরকার কর্তৃক তৈরি জমির চূড়ান্ত মালিকানা স্বত্ব দলিল।'
                          : 'C.S, S.A, R.S, and B.S Record of Rights (RoR). Official survey record of land ownership.'}
                      </p>
                      <div className="bg-white p-3 rounded-xl border border-emerald-200 text-xs space-y-1">
                        <span className="font-bold text-emerald-900 block">
                          {isBengali ? 'স্বয়ংক্রিয় উদ্ধারকৃত ফিল্ডসমূহ:' : 'Extracted Fields:'}
                        </span>
                        <ul className="list-disc list-inside text-slate-600 space-y-0.5">
                          <li>খতিয়ান নং ও সাবেক খতিয়ান নং</li>
                          <li>জেলা, উপজেলা ও ইউনিয়ন</li>
                          <li>মৌজা ও জে.এল. নম্বর</li>
                          <li>মালিকের নাম ও পিতার নাম</li>
                          <li>দাগ নং ও জমির পরিমাণ (একর/বিঘা)</li>
                        </ul>
                      </div>
                      {onSelectDocType && (
                        <button
                          type="button"
                          onClick={() => {
                            onSelectDocType('khatian');
                            setIsOpen(false);
                          }}
                          className="w-full py-2 rounded-xl bg-emerald-700 hover:bg-emerald-800 text-white font-bold text-xs flex items-center justify-center gap-1.5 transition-all shadow-xs"
                        >
                          <Check className="w-3.5 h-3.5" />
                          <span>{isBengali ? 'খতিয়ান নির্বাচন করুন' : 'Select Khatian'}</span>
                        </button>
                      )}
                    </div>

                    {/* Porcha Card */}
                    <div className="p-5 rounded-2xl border-2 border-blue-400/80 bg-blue-50/50 space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="font-extrabold text-blue-950 text-base">
                          {isBengali ? '২. পর্চা (Porcha)' : '2. Porcha'}
                        </span>
                        <span className="px-2.5 py-1 rounded-lg text-xs font-bold bg-blue-700 text-white">
                          ভূমি উন্নয়ন কর/পর্চা
                        </span>
                      </div>
                      <p className="text-xs text-slate-700 leading-relaxed">
                        {isBengali
                          ? 'জরিপ পরবর্তী বা তহসিল অফিস থেকে ইস্যুকৃত পর্চা বা রেকর্ড কপি। এতে দাগওয়ারি অংশীদারদের পূর্ণ বিবরণ থাকে।'
                          : 'Survey extract or land development tax receipt. Contains tenant schedules and plot distributions.'}
                      </p>
                      <div className="bg-white p-3 rounded-xl border border-blue-200 text-xs space-y-1">
                        <span className="font-bold text-blue-900 block">
                          {isBengali ? 'স্বয়ংক্রিয় উদ্ধারকৃত ফিল্ডসমূহ:' : 'Extracted Fields:'}
                        </span>
                        <ul className="list-disc list-inside text-slate-600 space-y-0.5">
                          <li>পর্চা নং, আর.এস/বি.এস খতিয়ান</li>
                          <li>জেলা, উপজেলা, মৌজা ও গ্রাম</li>
                          <li>বহু-অংশীদার মালিকদের তালিকা</li>
                          <li>দাগ নম্বর ও জমির শ্রেণি (আবাদি/ভিটা)</li>
                          <li>ইস্যুর তারিখ ও রেজিস্টার নম্বর</li>
                        </ul>
                      </div>
                      {onSelectDocType && (
                        <button
                          type="button"
                          onClick={() => {
                            onSelectDocType('porcha');
                            setIsOpen(false);
                          }}
                          className="w-full py-2 rounded-xl bg-blue-700 hover:bg-blue-800 text-white font-bold text-xs flex items-center justify-center gap-1.5 transition-all shadow-xs"
                        >
                          <Check className="w-3.5 h-3.5" />
                          <span>{isBengali ? 'পর্চা নির্বাচন করুন' : 'Select Porcha'}</span>
                        </button>
                      )}
                    </div>

                    {/* Deed Card */}
                    <div className="p-5 rounded-2xl border-2 border-purple-400/80 bg-purple-50/50 space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="font-extrabold text-purple-950 text-base">
                          {isBengali ? '৩. দলিল (Deed)' : '3. Legal Deed'}
                        </span>
                        <span className="px-2.5 py-1 rounded-lg text-xs font-bold bg-purple-700 text-white">
                          সাব-রেজিস্ট্রি দলিল
                        </span>
                      </div>
                      <p className="text-xs text-slate-700 leading-relaxed">
                        {isBengali
                          ? 'সাব-রেজিস্ট্রি অফিস থেকে সম্পাদিত সাফ কবলা, হেবা বিল এওয়াজ, দানপত্র বা বণ্টননামা রেজিস্ট্রি দলিল।'
                          : 'Sub-registry legal transfer deeds (Sale deed, Gift/Heba, Partition deed).'}
                      </p>
                      <div className="bg-white p-3 rounded-xl border border-purple-200 text-xs space-y-1">
                        <span className="font-bold text-purple-900 block">
                          {isBengali ? 'স্বয়ংক্রিয় উদ্ধারকৃত ফিল্ডসমূহ:' : 'Extracted Fields:'}
                        </span>
                        <ul className="list-disc list-inside text-slate-600 space-y-0.5">
                          <li>দলিল নম্বর ও দলিলের শ্রেণি/প্রকৃতি</li>
                          <li>১ম পক্ষ: দাতা / বিক্রেতার নাম</li>
                          <li>২য় পক্ষ: গ্রহীতা / ক্রেতার নাম</li>
                          <li>পণমূল্য / বিক্রয় মূল্য (টাকা)</li>
                          <li>নিবন্ধন তারিখ ও সাব-রেজিস্ট্রি অফিস</li>
                        </ul>
                      </div>
                      {onSelectDocType && (
                        <button
                          type="button"
                          onClick={() => {
                            onSelectDocType('deed');
                            setIsOpen(false);
                          }}
                          className="w-full py-2 rounded-xl bg-purple-700 hover:bg-purple-800 text-white font-bold text-xs flex items-center justify-center gap-1.5 transition-all shadow-xs"
                        >
                          <Check className="w-3.5 h-3.5" />
                          <span>{isBengali ? 'দলিল নির্বাচন করুন' : 'Select Deed'}</span>
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* TAB 2: UPLOAD METHODS */}
              {activeTab === 'upload' && (
                <div className="space-y-6 animate-in fade-in duration-200">
                  <div className="border-b border-slate-100 pb-3">
                    <h4 className="text-base sm:text-lg font-bold text-slate-900">
                      {isBengali ? 'আপলোড পদ্ধতি নির্বাচন' : 'Choose Upload Method'}
                    </h4>
                    <p className="text-xs sm:text-sm text-slate-500 mt-0.5">
                      {isBengali
                        ? 'আপনার কাছে টেস্ট ফাইল না থাকলেও আপনি সিস্টেমটি পুরোপুরি পরখ করতে পারবেন:'
                        : 'Easily test with authentic pre-loaded government records or upload your own:'}
                    </p>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                    {/* Demo Files Option */}
                    <div className="p-6 rounded-2xl border-2 border-emerald-500 bg-emerald-50/40 space-y-4">
                      <div className="flex items-center gap-3">
                        <div className="w-12 h-12 rounded-xl bg-emerald-600 text-white flex items-center justify-center">
                          <Sparkles className="w-6 h-6" />
                        </div>
                        <div>
                          <h5 className="font-extrabold text-slate-900 text-base">
                            {isBengali ? 'অপশন ক: নমুনা ফাইল ব্যবহার করুন' : 'Option A: Use Demo File'}
                          </h5>
                          <span className="text-xs text-emerald-800 font-semibold">
                            {isBengali ? '১-ক্লিকে টেস্টিং (কোনো ফাইল প্রয়োজন নেই)' : '1-Click Instant Testing'}
                          </span>
                        </div>
                      </div>

                      <p className="text-xs text-slate-600 leading-relaxed">
                        {isBengali
                          ? 'ভূমি মন্ত্রণালয়ের আসল স্ক্যান করা নরসিংদীর খতিয়ান ও ঢাকার পর্চা সিস্টেমে প্রি-লোডেড করা আছে। বোতামে চাপ দিলে তৎক্ষণাৎ ফাইলটি আপলোড হয়ে প্রসেসিং শুরু হবে।'
                          : 'Official authentic government records are pre-loaded. Click to load either the Narsingdi Khatian or Dhaka Porcha without searching for test files.'}
                      </p>

                      <div className="space-y-2 pt-2">
                        {onUseDemo && (
                          <div className="grid grid-cols-2 gap-2">
                            <button
                              type="button"
                              onClick={() => {
                                onUseDemo('khatian');
                                setIsOpen(false);
                              }}
                              className="px-3 py-2.5 rounded-xl bg-emerald-700 hover:bg-emerald-800 text-white font-bold text-xs flex items-center justify-center gap-1.5 shadow-xs"
                            >
                              <Play className="w-3.5 h-3.5" />
                              <span>নমুনা খতিয়ান চালান</span>
                            </button>
                            <button
                              type="button"
                              onClick={() => {
                                onUseDemo('porcha');
                                setIsOpen(false);
                              }}
                              className="px-3 py-2.5 rounded-xl bg-blue-700 hover:bg-blue-800 text-white font-bold text-xs flex items-center justify-center gap-1.5 shadow-xs"
                            >
                              <Play className="w-3.5 h-3.5" />
                              <span>নমুনা পর্চা চালান</span>
                            </button>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Custom File Upload Option */}
                    <div className="p-6 rounded-2xl border-2 border-slate-300 bg-white space-y-4">
                      <div className="flex items-center gap-3">
                        <div className="w-12 h-12 rounded-xl bg-slate-800 text-white flex items-center justify-center">
                          <Upload className="w-6 h-6" />
                        </div>
                        <div>
                          <h5 className="font-extrabold text-slate-900 text-base">
                            {isBengali ? 'অপশন খ: নিজস্ব ফাইল আপলোড' : 'Option B: Custom File Upload'}
                          </h5>
                          <span className="text-xs text-slate-500 font-semibold">
                            JPG, PNG, PDF (সর্বোচ্চ ২৫ মেগাবাইট)
                          </span>
                        </div>
                      </div>

                      <p className="text-xs text-slate-600 leading-relaxed">
                        {isBengali
                          ? 'আপনার মোবাইল ক্যামেরা দিয়ে তোলা বা স্ক্যানার দিয়ে স্ক্যান করা যেকোনো ভূমি রেকর্ড টেনে এনে ছেড়ে দিন (Drag & Drop) অথবা ক্লিক করে ফাইল সিলেক্ট করুন।'
                          : 'Drag and drop any scanned land document or legal deed from your computer or phone. Supports high-resolution scans and multi-page PDFs.'}
                      </p>

                      <div className="bg-slate-50 p-3 rounded-xl border border-slate-200 text-xs space-y-1">
                        <span className="font-bold text-slate-800 block">টিপস:</span>
                        <p className="text-slate-600 text-xs">
                          {isBengali
                            ? 'সোজা আলোতে তোলা পরিষ্কার ছবি দিলে OCR-এর নির্ভুলতা ৯০% এর বেশি হয়।'
                            : 'Good lighting and flat document positioning ensure >90% OCR accuracy.'}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* TAB 3: OCR & AUTO-SAVE */}
              {activeTab === 'ocr' && (
                <div className="space-y-6 animate-in fade-in duration-200">
                  <div className="border-b border-slate-100 pb-3">
                    <h4 className="text-base sm:text-lg font-bold text-slate-900">
                      {isBengali
                        ? 'বাংলা OCR ও স্বয়ংক্রিয় ডাটাবেজ সংরক্ষণ'
                        : 'Bengali OCR Pipeline & Automatic Database Storage'}
                    </h4>
                    <p className="text-xs sm:text-sm text-slate-500 mt-0.5">
                      {isBengali
                        ? '"আপলোড ও প্রসেস করুন" বোতামে চাপ দিলে সিস্টেম যা যা করে:'
                        : 'What happens when you click "Upload & Process":'}
                    </p>
                  </div>

                  <div className="space-y-3">
                    <div className="flex items-start gap-4 p-4 rounded-2xl border border-slate-200 bg-white shadow-xs">
                      <div className="w-8 h-8 rounded-full bg-emerald-600 text-white font-black text-sm flex items-center justify-center shrink-0">
                        ১
                      </div>
                      <div className="space-y-1">
                        <span className="font-bold text-slate-900 text-sm">
                          {isBengali ? 'ইমেজ প্রি-প্রসেসিং ও ডেস্কেউ (Deskew)' : 'Image Preprocessing & Deskew'}
                        </span>
                        <p className="text-xs text-slate-600">
                          {isBengali
                            ? 'OpenCV দিয়ে স্ক্যানটির কোণ পরিমাপ করে বাঁকা থাকলে স্বয়ংক্রিয়ভাবে সোজা করা হয় এবং গোলমাল ফিল্টার করা হয়।'
                            : 'OpenCV detects document angle using Hough transform and rotates it straight.'}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-start gap-4 p-4 rounded-2xl border border-slate-200 bg-white shadow-xs">
                      <div className="w-8 h-8 rounded-full bg-emerald-600 text-white font-black text-sm flex items-center justify-center shrink-0">
                        ২
                      </div>
                      <div className="space-y-1">
                        <span className="font-bold text-slate-900 text-sm">
                          {isBengali ? 'বাংলা নিউরাল নেটওয়ার্ক OCR' : 'Bengali Neural OCR'}
                        </span>
                        <p className="text-xs text-slate-600">
                          {isBengali
                            ? 'Tesseract LSTM ও Gemini Vision মডেল দিয়ে বাংলা হস্তলিপি ও মুদ্রণের প্রতিটি বর্ণ ও সংখ্যা নিখুঁতভাবে উদ্ধার করা হয়।'
                            : 'Tesseract LSTM neural network and Gemini Vision extract all Bengali characters and numerals.'}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-start gap-4 p-4 rounded-2xl border border-slate-200 bg-white shadow-xs">
                      <div className="w-8 h-8 rounded-full bg-emerald-600 text-white font-black text-sm flex items-center justify-center shrink-0">
                        ৩
                      </div>
                      <div className="space-y-1">
                        <span className="font-bold text-slate-900 text-sm">
                          {isBengali ? 'কাঠামোবদ্ধ ফিল্ড নিষ্কাশন' : 'Structured Field Extraction'}
                        </span>
                        <p className="text-xs text-slate-600">
                          {isBengali
                            ? 'রেগুলার এক্সপ্রেশন ও প্যাটার্ন অ্যানালাইসিসের মাধ্যমে মালিকের নাম, দাগ নম্বর, খতিয়ান নং ও জমির পরিমাণ আলাদা করা হয়।'
                            : 'Field extractor identifies owner, plot numbers, khatian number, and total land area.'}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-start gap-4 p-4 rounded-2xl border-2 border-emerald-500 bg-emerald-50/50 shadow-xs">
                      <div className="w-8 h-8 rounded-full bg-emerald-700 text-white font-black text-sm flex items-center justify-center shrink-0">
                        ৪
                      </div>
                      <div className="space-y-1">
                        <span className="font-bold text-emerald-950 text-sm">
                          {isBengali
                            ? '✓ ডাটাবেজে তাৎক্ষণিক স্বয়ংক্রিয় সংরক্ষণ (Automatic Permanent Save)'
                            : '✓ Instant Permanent Database Storage'}
                        </span>
                        <p className="text-xs text-emerald-900">
                          {isBengali
                            ? 'প্রক্রিয়াকরণ সম্পন্ন হওয়ামাত্রই রেকর্ডটি ডাটাবেজে পার্মানেন্টভাবে সংরক্ষিত হয় এবং "দলিলসমূহ" তালিকায় যুক্ত হয়ে যায়। কোনো তথ্য হারিয়ে যায় না।'
                            : 'As soon as processing finishes, the record is immediately committed to SQLite database and appears on the Documents list.'}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* TAB 4: VERIFY & EDIT */}
              {activeTab === 'verify' && (
                <div className="space-y-6 animate-in fade-in duration-200">
                  <div className="border-b border-slate-100 pb-3">
                    <h4 className="text-base sm:text-lg font-bold text-slate-900">
                      {isBengali ? 'তথ্য যাচাই ও সম্পাদনা (Verify & Save)' : 'Verify & Edit Options'}
                    </h4>
                    <p className="text-xs sm:text-sm text-slate-500 mt-0.5">
                      {isBengali
                        ? 'প্রক্রিয়াকরণ শেষে প্রদর্শিত স্ক্রিনের বোতাম ও অপশনগুলোর কাজ:'
                        : 'What each post-processing button and field allows you to do:'}
                    </p>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="p-4 rounded-2xl border border-slate-200 bg-white space-y-2">
                      <div className="flex items-center gap-2 text-emerald-700 font-bold text-sm">
                        <Edit3 className="w-4 h-4" />
                        <span>{isBengali ? 'সম্পাদনাযোগ্য ইনপুট ফিল্ড' : 'Editable Field Inputs'}</span>
                      </div>
                      <p className="text-xs text-slate-600 leading-relaxed">
                        {isBengali
                          ? 'পুরনো বা ক্ষতিগ্রস্ত দলিলের ক্ষেত্রে যদি কোনো অক্ষরের বানান পরিবর্তন প্রয়োজন হয়, সরাসরি ফিল্ডে ক্লিক করে লিখে ঠিক করতে পারেন।'
                          : 'Click any input box to edit misspelled names, corrected plot numbers, or land areas.'}
                      </p>
                    </div>

                    <div className="p-4 rounded-2xl border border-slate-200 bg-white space-y-2">
                      <div className="flex items-center gap-2 text-emerald-700 font-bold text-sm">
                        <FileText className="w-4 h-4" />
                        <span>{isBengali ? 'মূল স্ক্যান ও প্রিভিউ' : 'Original Scan Side-by-Side'}</span>
                      </div>
                      <p className="text-xs text-slate-600 leading-relaxed">
                        {isBengali
                          ? 'বামপাশে মূল স্ক্যান করা কাগজের দলিলটি দেখা যায়। "বড় করে দেখুন" চাপলে পূর্ণ রেজোলিউশনে মিলিয়ে দেখা যায়।'
                          : 'View the original scanned paper on the left to verify numbers against the actual handwritten record.'}
                      </p>
                    </div>

                    <div className="p-4 rounded-2xl border border-emerald-300 bg-emerald-50/60 space-y-2">
                      <div className="flex items-center gap-2 text-emerald-900 font-bold text-sm">
                        <Save className="w-4 h-4 text-emerald-700" />
                        <span>{isBengali ? '"যাচাই সংরক্ষণ ও বিস্তারিত দেখুন"' : '"Save Verified & View Details"'}</span>
                      </div>
                      <p className="text-xs text-emerald-800 leading-relaxed">
                        {isBengali
                          ? 'আপনার সম্পাদিত ফিল্ডগুলো ডাটাবেজে আপডেট করে এবং সরাসরি দলিলের বিস্তারিত পাতায় নিয়ে যায়।'
                          : 'Saves your modifications via PUT request and opens the full document detail page.'}
                      </p>
                    </div>

                    <div className="p-4 rounded-2xl border border-teal-300 bg-teal-50/60 space-y-2">
                      <div className="flex items-center gap-2 text-teal-900 font-bold text-sm">
                        <ArrowRight className="w-4 h-4 text-teal-700" />
                        <span>{isBengali ? '"দলিলসমূহ তালিকায় দেখুন"' : '"View in Documents List"'}</span>
                      </div>
                      <p className="text-xs text-teal-800 leading-relaxed">
                        {isBengali
                          ? 'সরাসরি সকল ডিজিটাল দলিলের তালিকায় চলে যায়, যেখানে এই নতুন সংরক্ষিত দলিলটি সবার উপরে দেখতে পাবেন।'
                          : 'Goes to the Documents repository where all digitized records can be browsed and filtered.'}
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* TAB 5: DOCUMENTS & SEARCH */}
              {activeTab === 'search' && (
                <div className="space-y-6 animate-in fade-in duration-200">
                  <div className="border-b border-slate-100 pb-3">
                    <h4 className="text-base sm:text-lg font-bold text-slate-900">
                      {isBengali
                        ? 'দলিলসমূহ ও ফুল-টেক্সট অনুসন্ধান'
                        : 'Documents Repository & Full-Text Search'}
                    </h4>
                    <p className="text-xs sm:text-sm text-slate-500 mt-0.5">
                      {isBengali
                        ? 'সংরক্ষিত দলিলগুলো খুঁজে বের করার শক্তিশালী অনুসন্ধান ব্যবস্থা:'
                        : 'How to search and retrieve any digitized land document in seconds:'}
                    </p>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 space-y-2">
                      <div className="flex items-center gap-2 text-slate-900 font-bold text-sm">
                        <Search className="w-4 h-4 text-emerald-700" />
                        <span>মালিকের নামে খোঁজ</span>
                      </div>
                      <p className="text-xs text-slate-600">
                        মালিকের নাম (যেমন: "আব্দুল করিম", "রহিমা বেগম") লিখে সার্চ করলে সংশ্লিষ্ট সকল খতিয়ান পাওয়া যায়।
                      </p>
                    </div>

                    <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 space-y-2">
                      <div className="flex items-center gap-2 text-slate-900 font-bold text-sm">
                        <FileCheck className="w-4 h-4 text-emerald-700" />
                        <span>খতিয়ান বা দাগ নম্বর</span>
                      </div>
                      <p className="text-xs text-slate-600">
                        খতিয়ান নম্বর (যেমন: ১২৩৪) অথবা দাগ নম্বর (যেমন: ১২৩) দিয়ে অনুসন্ধান করলে তৎক্ষণাৎ রেজাল্ট আসে।
                      </p>
                    </div>

                    <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 space-y-2">
                      <div className="flex items-center gap-2 text-slate-900 font-bold text-sm">
                        <ShieldCheck className="w-4 h-4 text-emerald-700" />
                        <span>ফিল্টার ট্যাব</span>
                      </div>
                      <p className="text-xs text-slate-600">
                        "সকল", "খতিয়ান", "পর্চা", "দলিল" ট্যাবে ক্লিক করে এক ক্লিকে যেকোনো নির্দিষ্ট ক্যাটাগরির দলিল দেখুন।
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Modal Footer */}
            <div className="px-6 py-4 bg-slate-100 border-t border-slate-200 flex items-center justify-between shrink-0">
              <span className="text-xs text-slate-500">
                {isBengali
                  ? 'বাংলাদেশ ভূমি রেকর্ড ডিজিটাইজেশন সিস্টেম • ভূমি মন্ত্রণালয়'
                  : 'Bangladesh Land Records Digitization System'}
              </span>
              <button
                type="button"
                onClick={() => setIsOpen(false)}
                className="px-6 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-900 text-white font-bold text-xs sm:text-sm transition-all"
              >
                {isBengali ? 'বুঝেছি / বন্ধ করুন' : 'Got it / Close'}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
