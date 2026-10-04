# WenQuest Verilog synthesis service (第 17 轮附 3.3): Yosys for the phone version of the Verilog lab.
# No secrets, no internet (internal network only, see docker-compose.yml); read-only, 1 CPU, 1 GB.
FROM python:3.12-slim-bookworm
WORKDIR /srv
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y --no-install-recommends yosys && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py ./
RUN useradd -r -u 10005 -m synth
USER synth
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=4)" || exit 1
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
