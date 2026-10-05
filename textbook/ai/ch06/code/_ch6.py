"""第 6 章共用（以下划线开头，构建时不单独运行）：实测所用显卡 A10 的规格（取自 conventions/gpus.py，另加数据手册上的 TF32 峰值）、
检测相机一帧的大小。"""
from gpus import GPUS, PCIE

W, H = 3840, 2160
FRAME_RGB = W * H * 3            # 一帧彩色图像的字节数
FRAME_GRAY = W * H               # 灰度图的字节数

A10 = dict(GPUS["a10"])
A10["tf32t"] = 62.5e12
A10["pcie"] = PCIE[4]            # A10 插在 PCIe 4.0 ×16 上，每个方向的理论带宽
