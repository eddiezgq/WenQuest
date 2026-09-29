# WenQuest animation renderer: Manim + LaTeX + ffmpeg, no secrets, no internet (see docker-compose.yml).
FROM python:3.12-slim
WORKDIR /srv
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      ffmpeg fonts-noto-cjk fonts-dejavu-core \
      libcairo2 libpango-1.0-0 libpangocairo-1.0-0 \
      build-essential pkg-config libcairo2-dev libpango1.0-dev \
      dvisvgm texlive-latex-base texlive-latex-recommended texlive-fonts-recommended \
 && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
 && apt-get purge -y build-essential && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*
COPY app.py wq_anim.py ./
RUN useradd -r -u 10002 -m anim
USER anim
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=4)" || exit 1
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
