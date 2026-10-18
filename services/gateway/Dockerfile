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
 && apt-get install -y --no-install-recommends graphviz librsvg2-bin fontconfig ffmpeg \
 && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# 缝纫机设计软件（第 39 轮）出 STEP 用 build123d（OpenCASCADE）；装不上时网页版仍可用，只是不出 STEP（改给 FreeCAD 宏）
RUN apt-get update && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 libxrender1 libx11-6 libxext6 \
 && rm -rf /var/lib/apt/lists/* \
 && (sed -e "s/\[[^]]*\]//" -e "/^-/d" requirements.txt > /tmp/pins.txt && pip install --no-cache-dir -c /tmp/pins.txt build123d==0.13.0 && python -c "import build123d" \
     || (echo "build123d unavailable: STEP export disabled" && pip uninstall -y build123d || true))
COPY app ./app
RUN useradd -r -u 10001 -m wq && mkdir -p /data && chown wq /data
USER wq
ENV WQ_DATA_DIR=/data WQ_IMPORT_DIR=/data/imports
VOLUME /data
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import urllib.request,sys; urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=4)" || exit 1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips", "*"]
