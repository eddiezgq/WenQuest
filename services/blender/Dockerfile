# 三维仿真视频的“关键画面”渲染（第 38 轮第 1 步）：Blender（bpy 4.2）+ 渲染器 tools/blender + 平缝机虚拟样机网页。
# 和动画渲染容器一样：没有密钥、不能上网、一次只出一个；整段视频不在这里出（租 Lambda，见网关 video3d.py），
# 这里还把渲染器打成一个包（GET /bundle）交给租来的机器用。
# 构建上下文是仓库根目录（只带 Dockerfile.dockerignore 放行的文件）：docker build -f services/blender/Dockerfile .
FROM python:3.11-slim-bookworm
WORKDIR /srv
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PLAYWRIGHT_BROWSERS_PATH=/ms-playwright HOME=/tmp
RUN apt-get update \
 && apt-get install -y --no-install-recommends ffmpeg fonts-noto-cjk \
      libegl1 libgl1 libxkbcommon0 libsm6 libxi6 libxxf86vm1 libxfixes3 libxrender1 libxext6 libx11-6 \
 && rm -rf /var/lib/apt/lists/*
COPY services/blender/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
 && python -m playwright install --with-deps chromium \
 && rm -rf /var/lib/apt/lists/*
# 渲染器与它要读的文件，保持仓库里的相对位置（weblab.py 按仓库根目录找文件）
COPY tools/blender /srv/wq/tools/blender
COPY tools/site_cases/assets/three.min.js /srv/wq/tools/site_cases/assets/three.min.js
COPY textbook/web-editions/sewing/src/zh/labs/proto-lockstitch.html /srv/wq/textbook/web-editions/sewing/src/zh/labs/proto-lockstitch.html
COPY textbook/web-editions/sewing/src/lib/lockstitch-kit.js textbook/web-editions/sewing/src/lib/proto-lockstitch-mesh.js /srv/wq/textbook/web-editions/sewing/src/lib/
# 缝纫机设计软件的计算核心（第 56 轮 gen:sewdesign：按企业自己的设计尺寸摆零件；纯 Python，只用 math）
COPY services/gateway/app/sewcore/*.py /srv/wq/services/gateway/app/sewcore/
COPY video3d /srv/wq/video3d
COPY services/blender/app.py services/blender/run.sh ./
RUN useradd -r -u 10005 -m b3d && rm -rf /srv/wq/tools/blender/__pycache__
USER b3d
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=4)" || exit 1
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
