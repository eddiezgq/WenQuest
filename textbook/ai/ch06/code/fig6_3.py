"""6.3 节的示意图（数据同程序 6.3.2，conventions/gpus.py）。

图 6.3.1：（a）一台 8 卡服务器：每块 GPU 的多条 NVLink 连到 NVSwitch 交换芯片，任意两块 GPU 之间都是满带宽；PCIe 连到主机与网卡；（b）各种互联每个方向的带宽（对数坐标）与传 1 GB 的时间。
"""
from bookout import COLORS, T, figure, style
from gpus import IB, NVLINK, PCIE

plt = style()
C = COLORS
fig, (a, b) = plt.subplots(1, 2, figsize=(12, 4.6), gridspec_kw={"width_ratios": [1.1, 1]})
for k in range(8):
    x = k * 0.62
    a.add_patch(plt.Rectangle((x, 3.2), 0.52, 0.6, fc=C["z"], alpha=0.5))
    a.text(x + 0.26, 3.5, str(k), ha="center", va="center", fontsize=9)
    for dx in (-0.1, 0.0, 0.1):                              # 每块 GPU 有多条 NVLink 连到交换芯片
        a.plot([x + 0.26 + dx, x + 0.26 + dx * 3], [3.2, 2.45], color=C["y"], lw=1.2, alpha=0.8)
    a.plot([x + 0.26, x + 0.26], [3.8, 4.4], color=C["muted"], lw=1, ls="--")
a.text(-0.1, 3.5, "GPU", ha="right", va="center", fontsize=9)
a.add_patch(plt.Rectangle((0.0, 1.95), 4.86, 0.5, fc=C["y"], alpha=0.5))
a.text(2.43, 2.2, T("NVSwitch：任意两块 GPU 之间满带宽", "NVSwitch: full bandwidth between any two GPUs"), ha="center", va="center", fontsize=9)
a.add_patch(plt.Rectangle((0.0, 4.4), 4.86, 0.5, fc=C["muted"], alpha=0.3))
a.text(2.43, 4.65, T("PCIe 交换机 / CPU（主机内存、网卡）", "PCIe switches / CPUs (host memory, NICs)"), ha="center", va="center", fontsize=9)
a.set_xlim(-0.6, 5.0)
a.set_ylim(1.6, 5.2)
a.invert_yaxis()
a.axis("off")
a.set_title(T("（a）8 卡服务器：NVLink 经 NVSwitch 全互联，PCIe 连主机", "(a) 8-GPU server: NVLink via NVSwitch, PCIe to the host"), fontsize=10)
items = [("PCIe 4.0 ×16", PCIE[4]), ("PCIe 5.0 ×16", PCIE[5]), ("NVLink V100", NVLINK["v100"]), ("NVLink A100", NVLINK["a100"]),
         ("NVLink H100", NVLINK["h100"]), ("NVLink B200", NVLINK["b200"]), ("InfiniBand HDR", IB["hdr"]), ("InfiniBand NDR", IB["ndr"])]
names = [n for n, _ in items]
vals = [v / 1e9 for _, v in items]
cols = [C["muted"] if "PCIe" in n else C["y"] if "NVLink" in n else C["x"] for n in names]
b.barh(range(len(items)), vals, color=cols, alpha=0.75)
for i, v in enumerate(vals):
    b.text(v * 1.08, i, T(f"{v:.0f} GB/s，1 GB 要 {1e3 / v:.1f} ms", f"{v:.0f} GB/s, 1 GB in {1e3 / v:.1f} ms"), va="center", fontsize=8)
b.set_yticks(range(len(items)))
b.set_yticklabels(names, fontsize=9)
b.set_xscale("log")
b.set_xlim(10, 20000)
b.invert_yaxis()
b.set_xlabel(T("每个方向的带宽（GB/s）", "bandwidth per direction (GB/s)"))
b.set_title(T("（b）互联带宽（每块 GPU 或每块网卡，每个方向）", "(b) Interconnect bandwidth (per GPU or NIC, per direction)"), fontsize=10)
fig.tight_layout()
figure(fig, "fig6_3_1")
plt.close(fig)
