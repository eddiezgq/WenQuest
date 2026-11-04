# 问渠轴承 WenQuest Bearing (round 64): the browser app (apps/bearing, built here) served with the bearingkit API.
# Build from the repository root:  docker build -f services/bearing/Dockerfile .
# No secrets, no outside calls: everything is computed by bearingkit in this container.
FROM node:22-alpine AS web
WORKDIR /app
COPY apps/bearing/package.json apps/bearing/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY apps/bearing/ ./
RUN npm run build

FROM python:3.12-slim-bookworm
WORKDIR /srv
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 BEARING_WEB_DIR=/srv/web
COPY services/bearing/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY services/bearing/bearingkit ./bearingkit
COPY services/bearing/examples ./examples
COPY services/bearing/app.py services/bearing/projects_api.py ./
COPY services/bearing/freecad/*.py ./freecad/
COPY factory/digital/freecad/Mod/WenQuest/InitGui.py factory/digital/freecad/Mod/WenQuest/wq_workbench.py ./freecad/workbench/
COPY --from=web /app/dist ./web
RUN useradd -r -u 10007 bearing
USER bearing
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=4)" || exit 1
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
