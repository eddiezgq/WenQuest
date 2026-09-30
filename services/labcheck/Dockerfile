# WenQuest lab checker: opens AI-written virtual labs in headless Chromium and runs their tasks.
# No secrets, no internet (internal network only, see docker-compose.yml); the lab page itself also
# forbids every network request (Content-Security-Policy) and the checker aborts any that is tried.
# Debian 12 (bookworm): a distribution Playwright installs Chromium's system libraries for.
FROM python:3.12-slim-bookworm
WORKDIR /srv
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
 && playwright install --with-deps --only-shell chromium \
 && apt-get update && apt-get install -y --no-install-recommends fonts-noto-cjk \
 && rm -rf /var/lib/apt/lists/*
COPY app.py ./
RUN useradd -r -u 10003 -m lab
USER lab
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=4)" || exit 1
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
