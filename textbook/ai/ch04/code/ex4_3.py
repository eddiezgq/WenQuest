"""算例 4.3.1：一帧图像经 PCIe 传到 GPU 要多久，与核函数本身相比如何（阿姆达尔定律，3.2 节）。"""
from bookout import out
from gpus import GPUS, PCIE

px = 3840 * 2160
frame_in = 3 * px                    # RGB
result_out = px                      # 只取回掩码
kernel_bytes = 5 * px                # 核函数读 3、写 2 字节/像素
for_gen = {g: (frame_in + result_out) / PCIE[g] for g in (4, 5)}
t_kernel_a10 = kernel_bytes / GPUS["a10"]["bw"]
t_kernel_h100 = kernel_bytes / GPUS["h100"]["bw"]
frac4 = for_gen[4] / (for_gen[4] + t_kernel_a10)
fps_limit4 = 1 / (for_gen[4] + t_kernel_a10)
out(frame_MB=frame_in / 1e6, mask_MB=result_out / 1e6, pcie4=PCIE[4] / 1e9, pcie5=PCIE[5] / 1e9, t4_ms=for_gen[4] * 1e3,
    t5_ms=for_gen[5] * 1e3, tk_a10_us=t_kernel_a10 * 1e6, tk_h100_us=t_kernel_h100 * 1e6, ratio4=for_gen[4] / t_kernel_a10,
    frac4_pct=frac4 * 100, fps4=fps_limit4)
