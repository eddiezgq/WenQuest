# 问渠 GPU 实验镜像（《人工智能》第 14 轮附，方案 C：学校自有 GPU 服务器；其他支持自定义镜像的平台也可用）。
# AutoDL 与 Lambda 用平台的基础镜像，由问渠在开机后放入实验文件（细则 4.3 节），不需要本镜像。
# 构建：docker build -t wenquest/cuda-lab:0.1 deploy/gpu-lab
# 运行：docker run --gpus all --cap-add SYS_ADMIN -p 8888:8888 -e JUPYTER_TOKEN=<令牌> wenquest/cuda-lab:0.1
#       （--cap-add SYS_ADMIN 让 Nsight Compute 能读性能计数器，宿主机驱动还需允许非管理员读计数器，见帮助文件）
FROM nvidia/cuda:12.8.1-devel-ubuntu24.04
ENV DEBIAN_FRONTEND=noninteractive PIP_NO_CACHE_DIR=1 PIP_BREAK_SYSTEM_PACKAGES=1
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-pip git curl \
    && rm -rf /var/lib/apt/lists/*
RUN pip3 install --index-url https://download.pytorch.org/whl/cu128 torch \
    && pip3 install triton jupyterlab numpy matplotlib pyyaml
WORKDIR /workspace
COPY wqgpu.py /workspace/wq/wqgpu.py
EXPOSE 8888
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--ServerApp.root_dir=/workspace"]
