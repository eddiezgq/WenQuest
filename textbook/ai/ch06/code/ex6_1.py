"""算例 6.1.1、6.1.2：传输与计算的重叠。检测相机一帧 3840×2160 的彩色图像传到 GPU、处理、把灰度结果传回，A10 插在 PCIe 4.0 ×16 上。
（1）按 PCIe 理论带宽估计每帧的三段时间；（2）F 帧串行与流水线（三段各用一个硬件引擎、互相重叠）的总时间模型：
    串行 F(t_h + t_k + t_d)；流水线 ≈ t_h + t_k + t_d + (F − 1)·max(t_h, t_k, t_d)。
程序 6.1.1（streams.cu）把处理的计算量调到与上传相当（t_k ≈ t_h），这里取同样的假设。"""
from _ch6 import A10, FRAME_GRAY, FRAME_RGB
from bookout import out

bw = A10["pcie"]
t_h = FRAME_RGB / bw * 1e3                  # ms
t_d = FRAME_GRAY / bw * 1e3
t_k = t_h                                   # 与程序 6.1.1 相同：计算量调到与上传相当
F = 12
serial = F * (t_h + t_k + t_d)
pipe = t_h + t_k + t_d + (F - 1) * max(t_h, t_k, t_d)
fps_serial = 1e3 / (t_h + t_k + t_d)
fps_pipe = 1e3 / max(t_h, t_k, t_d)
out(pcie_GBs=bw / 1e9, rgb_MB=FRAME_RGB / 1e6, gray_MB=FRAME_GRAY / 1e6, t_h=t_h, t_d=t_d, t_k=t_k, F=F, serial=serial, pipe=pipe,
    speedup=serial / pipe, limit=(t_h + t_k + t_d) / max(t_h, t_k, t_d), fps_serial=fps_serial, fps_pipe=fps_pipe)
