FROM python:3.12-slim
WORKDIR /srv
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
# LibreOffice turns teachers' PowerPoint files into web presentations; Noto CJK renders Chinese slides;
# Tesseract reads scanned textbooks (text recognition runs on this server, no outside service).
RUN apt-get update \
 && (apt-get install -y --no-install-recommends libreoffice-impress-nogui \
     || apt-get install -y --no-install-recommends libreoffice-impress) \
 && apt-get install -y --no-install-recommends fonts-noto-cjk fonts-dejavu-core \
 && apt-get install -y --no-install-recommends tesseract-ocr tesseract-ocr-chi-sim tesseract-ocr-eng \
 && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
RUN useradd -r -u 10001 -m wq && mkdir -p /data && chown wq /data
USER wq
ENV WQ_DATA_DIR=/data WQ_IMPORT_DIR=/data/imports
VOLUME /data
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import urllib.request,sys; urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=4)" || exit 1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips", "*"]
