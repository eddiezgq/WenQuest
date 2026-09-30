# WenQuest voice service: speech synthesis (Kokoro, Chinese + English) and speech recognition (SenseVoice + VAD),
# open-source models run on this server. No secrets, no internet at run time (internal network only, see
# docker-compose.yml); the models are downloaded once, when the image is built.
FROM python:3.12-slim-bookworm
WORKDIR /srv
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 VOICE_MODELS=/models
RUN apt-get update && apt-get install -y --no-install-recommends curl bzip2 ca-certificates && rm -rf /var/lib/apt/lists/*
COPY fetch_models.sh .
RUN ./fetch_models.sh /models
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py ./
RUN useradd -r -u 10004 -m voice
USER voice
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=4)" || exit 1
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
