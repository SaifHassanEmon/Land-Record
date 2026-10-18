import React, { useState } from 'react';
import { NavLink, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { LanguageToggle } from './LanguageToggle';
import {
  FileText,
  Upload,
  Home,
  Menu,
  X,
  PhoneCall,
  ShieldCheck,
  Building2,
  ExternalLink,
} from 'lucide-react';

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { t } = useTranslation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navLinks = [
    { to: '/', label: t('nav.home'), icon: Home },
    { to: '/documents', label: t('nav.documents'), icon: FileText },
    { to: '/upload', label: t('nav.upload'), icon: Upload },
  ];

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-800">
      {/* Top Ministry Notification Bar */}
      <div className="bg-[#00533d] text-emerald-100 text-xs py-1.5 px-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-[#F42A41] animate-pulse" />
            <span className="font-medium tracking-wide">
              {t('home.subtitle')} &bull; Digital Land Record Archive
            </span>
          </div>
          <div className="hidden sm:flex items-center gap-4 text-emerald-200">
            <span className="flex items-center gap-1">
              <PhoneCall className="w-3 h-3 text-[#F42A41]" />
              হটলাইন: <strong className="text-white">১৬১২২</strong>
            </span>
            <span>|</span>
            <span className="flex items-center gap-1">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-300" />
              স্মার্ট ভূমি সেবা
            </span>
          </div>
        </div>
      </div>

      {/* Main Navbar */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-40 shadow-xs backdrop-blur-md bg-white/95">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-20 items-center">
            {/* Logo and Brand */}
            <Link to="/" className="flex items-center gap-3.5 group">
              {/* Bangladesh Emblem / Seal representation */}
              <div className="w-12 h-12 rounded-full bg-[#006A4E] border-2 border-emerald-600 flex items-center justify-center shadow-md shrink-0 relative overflow-hidden group-hover:scale-105 transition-transform">
                <div className="w-6 h-6 rounded-full bg-[#F42A41] flex items-center justify-center">
                  <Building2 className="w-3.5 h-3.5 text-white" />
                </div>
              </div>

              <div>
                <h1 className="text-lg md:text-xl font-bold text-slate-900 tracking-tight leading-snug group-hover:text-emerald-700 transition-colors">
                  {t('home.title')}
                </h1>
                <p className="text-xs text-emerald-700 font-semibold flex items-center gap-1">
                  <span>{t('home.subtitle')}</span>
                </p>
              </div>
            </Link>

            {/* Desktop Navigation */}
            <nav className="hidden md:flex items-center gap-1.5">
              {navLinks.map((link) => {
                const Icon = link.icon;
                return (
                  <NavLink
                    key={link.to}
                    to={link.to}
                    className={({ isActive }) =>
                      `flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold transition-all ${
                        isActive
                          ? 'bg-emerald-700 text-white shadow-sm shadow-emerald-700/20'
                          : 'text-slate-600 hover:text-emerald-700 hover:bg-emerald-50'
                      }`
                    }
                  >
                    <Icon className="w-4 h-4" />
                    <span>{link.label}</span>
                  </NavLink>
                );
              })}
            </nav>

            {/* Right actions: Language Toggle & Mobile menu toggle */}
            <div className="flex items-center gap-3">
              <LanguageToggle />

              {/* Mobile hamburger button */}
              <button
                type="button"
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="md:hidden p-2 rounded-xl text-slate-600 hover:text-emerald-700 hover:bg-emerald-50 focus:outline-none"
                aria-label="Toggle navigation menu"
              >
                {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Navigation Dropdown */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t border-slate-200 bg-white px-4 pt-3 pb-5 space-y-1 shadow-lg animate-in slide-in-from-top duration-200">
            {navLinks.map((link) => {
              const Icon = link.icon;
              return (
                <NavLink
                  key={link.to}
                  to={link.to}
                  onClick={() => setMobileMenuOpen(false)}
                  className={({ isActive }) =>
                    `flex items-center gap-3 px-4 py-3 rounded-xl text-base font-semibold transition-colors ${
                      isActive
                        ? 'bg-emerald-700 text-white'
                        : 'text-slate-700 hover:bg-emerald-50 hover:text-emerald-700'
                    }`
                  }
                >
                  <Icon className="w-5 h-5" />
                  <span>{link.label}</span>
                </NavLink>
              );
            })}
          </div>
        )}
      </header>

      {/* Main Content Area */}
      <main className="flex-1">{children}</main>

      {/* Footer */}
      <footer className="bg-slate-900 text-slate-300 mt-16 border-t border-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            {/* Ministry Info */}
            <div className="md:col-span-2 space-y-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-[#006A4E] flex items-center justify-center">
                  <div className="w-5 h-5 rounded-full bg-[#F42A41]" />
                </div>
                <div>
                  <h3 className="text-white font-bold text-base">{t('home.title')}</h3>
                  <p className="text-emerald-400 text-xs">{t('home.subtitle')}</p>
                </div>
              </div>
              <p className="text-slate-400 text-sm max-w-md leading-relaxed">
                {t('home.description')}. ভূমি ব্যবস্থাপনায় স্বচ্ছতা, গতি ও নিরাপত্তা নিশ্চিতকরণে আধুনিক ডিজিটাল প্রযুক্তি।
              </p>
            </div>

            {/* Quick Links */}
            <div>
              <h4 className="text-white font-semibold text-sm mb-4 uppercase tracking-wider">
                মেনু
              </h4>
              <ul className="space-y-2 text-sm text-slate-400">
                <li>
                  <Link to="/" className="hover:text-emerald-400 transition-colors">
                    {t('nav.home')}
                  </Link>
                </li>
                <li>
                  <Link to="/documents" className="hover:text-emerald-400 transition-colors">
                    {t('nav.documents')}
                  </Link>
                </li>
                <li>
                  <Link to="/upload" className="hover:text-emerald-400 transition-colors">
                    {t('nav.upload')}
                  </Link>
                </li>
              </ul>
            </div>

            {/* Support & Hotline */}
            <div>
              <h4 className="text-white font-semibold text-sm mb-4 uppercase tracking-wider">
                সহায়তা ও যোগাযোগ
              </h4>
              <div className="space-y-3 text-sm text-slate-400">
                <div className="flex items-start gap-2">
                  <PhoneCall className="w-4 h-4 text-emerald-400 mt-1 shrink-0" />
                  <div>
                    <p className="text-xs text-slate-400">ভূমি সেবা হটলাইন</p>
                    <p className="text-lg font-bold text-white tracking-wide">১৬১২২</p>
                  </div>
                </div>
                <div className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-white pt-2">
                  <ExternalLink className="w-3.5 h-3.5 text-emerald-400" />
                  <span>minland.gov.bd</span>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-12 pt-6 border-t border-slate-800 text-center text-xs text-slate-500 flex flex-col sm:flex-row items-center justify-between gap-4">
            <p>
              &copy; {new Date().getFullYear()} {t('home.subtitle')} | সর্বস্বত্ব সংরক্ষিত
            </p>
            <p className="text-slate-500">
              Bangladesh Land Records Digitization System &bull; Version 1.0.0
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};
