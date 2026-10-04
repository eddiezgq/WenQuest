# WenQuest Verilog synthesis service (第 17 轮附 3.3): Yosys for the phone version of the Verilog lab.
# No secrets, no internet (internal network only, see docker-compose.yml); read-only, 1 CPU, 1 GB.
# Ubuntu 24.04: Yosys 0.33, the same version the browser page's tests and the gateway tests use.
FROM ubuntu:24.04
WORKDIR /srv
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_BREAK_SYSTEM_PACKAGES=1
RUN apt-get update && apt-get install -y --no-install-recommends yosys python3 python3-pip && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
COPY app.py ./
RUN useradd -r -u 10005 -m synth
USER synth
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python3 -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=4)" || exit 1
CMD ["python3", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
