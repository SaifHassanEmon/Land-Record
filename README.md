# ভূমি রেকর্ড ডিজিটাইজেশন সিস্টেম
## Bangladesh Land Records Digitization System

> A digital archiving solution for the Bangladesh Land Ministry to convert scanned Khatian (খতিয়ান), Porcha (পর্চা), and Legal Deeds (দলিল) into searchable digital records using Bengali OCR.

---

## 🚀 Quick Start

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- **OR** Python 3.11+ and Node.js 20+ for local development

---

### Option A — Docker (Recommended)

```bash
# 1. Clone / open the project
cd Land-Record

# 2. Copy environment file
copy .env.example .env

# 3. Start all services
docker-compose up --build

# Frontend → http://localhost:5173
# Backend API → http://localhost:8000
# API Docs → http://localhost:8000/docs
```

---

### Option B — Local Development

#### Backend
```bash
cd backend

# Install Tesseract with Bengali language pack (Windows)
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# Make sure to select "Bengali" language during installation

# Install Python dependencies
pip install -r requirements.txt

# Generate demo documents
python generate_demo_docs.py

# Start the API server
uvicorn app.main:app --reload --port 8000
```

#### Frontend
```bash
cd frontend

# Install Node dependencies
npm install

# Start the dev server
npm run dev

# Open http://localhost:5173
```

---

## 🧪 Testing with Demo Documents

Three realistic Bengali land record PDFs are included for testing:

| File | Type | Description |
|------|------|-------------|
| `backend/demo_docs/khatian_demo.pdf` | খতিয়ান | Khatian for Savar, Dhaka — Owner: মোঃ আবদুল করিম |
| `backend/demo_docs/porcha_demo.pdf` | পর্চা | Land tax receipt for Hathazari, Chittagong — Owner: ফাতেমা বেগম |
| `backend/demo_docs/deed_demo.pdf` | দলিল | Sale deed in Mirpur, Dhaka — ৩৫ লক্ষ টাকা |

### How to test

1. Open the app at **http://localhost:5173**
2. Go to the **আপলোড** (Upload) page
3. See the **ডেমো দলিলসমূহ** section at the bottom
4. Click **"সব ডেমো দলিল আপলোড করুন"** to process all 3 at once
5. Watch the OCR extract Bengali fields automatically
6. Go to **দলিলসমূহ** (Documents) to browse and search

Or regenerate demo docs manually:
```bash
cd backend
python generate_demo_docs.py
```

---

## 🏗️ Architecture

```
Land-Record/
├── backend/              # FastAPI Python backend
│   ├── app/
│   │   ├── api/          # REST endpoints (documents, search, demo)
│   │   ├── models/       # SQLAlchemy ORM models
│   │   ├── schemas/      # Pydantic request/response schemas
│   │   ├── ocr/          # OCR pipeline (EasyOCR + Tesseract + OpenCV)
│   │   └── utils/        # File handling utilities
│   ├── demo_docs/        # Sample Bengali land record PDFs
│   ├── uploads/          # Uploaded documents storage
│   ├── generate_demo_docs.py  # Demo PDF generator script
│   └── requirements.txt
├── frontend/             # React + TypeScript frontend
│   └── src/
│       ├── i18n/         # Bengali & English translations
│       ├── pages/        # Home, Upload, Documents, Detail
│       └── components/   # Reusable UI components
├── docker-compose.yml
└── .env.example
```

---

## 🌐 Language Support

The UI defaults to **বাংলা** and can be toggled to English using the language button in the top navigation bar. Language preference is saved in the browser.

---

## 📋 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/documents/upload` | Upload & OCR a document |
| `GET` | `/api/v1/documents/` | List all documents |
| `GET` | `/api/v1/documents/{id}` | Get document details |
| `GET` | `/api/v1/documents/{id}/file` | Download original file |
| `DELETE` | `/api/v1/documents/{id}` | Delete a document |
| `GET` | `/api/v1/search?q=...` | Full-text search |
| `GET` | `/api/v1/demo-docs` | List demo documents |
| `POST` | `/api/v1/demo-docs/upload-all` | Bulk-upload all demo docs |

Full interactive docs at **http://localhost:8000/docs**

---

## 🔧 Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, TypeScript, Vite, Tailwind CSS |
| i18n | react-i18next (Bengali default) |
| Backend | FastAPI, Python 3.11, SQLAlchemy |
| Database | SQLite (dev) |
| OCR | EasyOCR (Bengali model) + Tesseract |
| Image Processing | OpenCV, Pillow |
| Containerization | Docker, Docker Compose |

---

## 📞 Support

For issues with Bengali OCR accuracy, see `backend/app/ocr/README.md`.
