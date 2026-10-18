FROM python:3.11-slim

# Install system dependencies: Tesseract with Bengali pack and poppler for PDF conversion
# In Debian 12 (Bookworm), libgl1 and libglib2.0-0 replace the deprecated libgl1-mesa-glx
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-ben \
    poppler-utils \
    libglib2.0-0 \
    libgl1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install lightweight CPU-only PyTorch first (drastically reduces image size & prevents out-of-memory on Render)
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Generate demo documents during build so demo files are always ready
RUN python generate_demo_docs.py || true

# Dynamic PORT support: Render injects $PORT (usually 10000)
ENV PORT=8000
EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
