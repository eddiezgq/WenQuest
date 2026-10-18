# 问渠凸轮 WenQuest Cam (round 39): the browser app (apps/cam, built here) served with the camkit API.
# Build from the repository root:  docker build -f services/cam/Dockerfile .
# No secrets, no outside calls: everything is computed by camkit in this container.
FROM node:22-alpine AS web
WORKDIR /app
COPY apps/cam/package.json apps/cam/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY apps/cam/ ./
RUN npm run build

FROM python:3.12-slim-bookworm
WORKDIR /srv
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 CAM_WEB_DIR=/srv/web
COPY services/cam/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY services/cam/camkit ./camkit
COPY services/cam/examples ./examples
COPY services/cam/app.py ./
COPY --from=web /app/dist ./web
RUN useradd -r -u 10006 cam
USER cam
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=4)" || exit 1
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
