"""算例 6.7.1：检测工位整条流水线的时间预算（A10，按理论带宽估计）。每帧：上传彩色图像 → 灰度化 → 3×3 平滑 → 直方图 →
暗像素的流压缩（前缀和）→ 传回暗像素坐标列表。各核函数受带宽限制，按“读写的字节 ÷ 显存带宽”估计；每次启动另加 5 μs。
相机每秒 60 帧，每帧的预算 16.7 ms。"""
from _ch6 import A10, FRAME_GRAY, FRAME_RGB
from bookout import out

bw, pcie = A10["bw"], A10["pcie"]
dark = 11277                                     # 测试图的暗像素数（程序 5.3.2）
stages = {
    "h2d": FRAME_RGB / pcie,
    "gray": (FRAME_RGB + FRAME_GRAY) / bw,
    "smooth": 2 * FRAME_GRAY / bw,
    "hist": FRAME_GRAY / bw,
    "compact": (FRAME_GRAY + 2 * FRAME_GRAY * 4 + dark * 4) / bw,   # 读灰度、写读前缀和（32 位）、写坐标
    "d2h": dark * 4 / pcie,
}
launch = 5e-6 * 5
gpu = sum(v for k, v in stages.items() if k not in ("h2d", "d2h")) + launch
total = sum(stages.values()) + launch
budget = 1 / 60
cams = budget / max(stages["h2d"], gpu)          # 传输与计算重叠时，每帧的间隔由最长的一段决定
# 阿姆达尔：把全部核函数再加快 10 倍，串行时每帧的总时间只减少多少
faster = total - gpu + gpu / 10
out(**{f"{k}_us": v * 1e6 for k, v in stages.items()}, launch_us=launch * 1e6, gpu_us=gpu * 1e6, total_us=total * 1e6,
    budget_ms=budget * 1e3, cams=cams, h2d_frac=100 * stages["h2d"] / total, faster_us=faster * 1e6, gain=100 * (1 - faster / total))
