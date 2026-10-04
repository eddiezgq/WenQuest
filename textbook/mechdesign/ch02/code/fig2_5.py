"""图 2.5.1 V 模型：左边从需求一级级分解到零件，右边从零件一级级验证到整机；以 WQR-105 为例。"""
import _ch2 as H
from bookout import T, figure, style

L = [(T("客户需求\n输出转矩、寿命、价格", "customer needs\ntorque, life, price"), T("用户验收\n客户现场运行", "acceptance\nat the customer's site")),
     (T("整机指标\n传动比 10.5、额定 350 N·m", "system specs\ni = 10.5, 350 N·m rated"), T("整机试验\n跑合试验台、出厂检验", "system test\nrun-in bench, final inspection")),
     (T("部件设计\n输出轴组件、箱体", "subsystem design\noutput-shaft assembly, housing"), T("部件验证\n装配检查、空载跑合", "subsystem check\nassembly, idle run")),
     (T("零件设计\nSH-301：直径、圆角、材料", "part design\nSH-301: diameters, fillets, material"), T("零件验证\n有限元、疲劳、三坐标", "part check\nFE, fatigue, CMM"))]
plt = style()
fig, ax = plt.subplots(figsize=(6.9, 3.6))
n = len(L)
w, h, W = 2.1, 0.62, 8.8
for k, (left, right) in enumerate(L):
    y = (n - 1 - k) * 0.85 + 0.6
    xl, xr = k * 0.6, W - k * 0.6 - w
    H.box(ax, xl, y, w, h, left, H.PALE["blue"], 7.2)
    H.box(ax, xr, y, w, h, right, H.PALE["green"], 7.2)
    ax.annotate("", (xr, y + h / 2), (xl + w, y + h / 2), arrowprops=dict(arrowstyle="<->", color=H.MUTED, lw=0.7, ls="--"))
    if k < n - 1:
        H.arrow(ax, (xl + w * 0.35, y), (xl + 0.6 + w * 0.35, y - 0.85 + h))
        H.arrow(ax, (xr - 0.6 + w * 0.65, y - 0.85 + h), (xr + w * 0.65, y))
H.box(ax, W / 2 - 1.1, 0.0, 2.2, 0.42, T("制造（数控、装配）", "manufacture (CNC, assembly)"), H.PALE["orange"], 7.2)
H.arrow(ax, (1.8 + w * 0.5, 0.6), (W / 2 - 0.6, 0.42))
H.arrow(ax, (W / 2 + 0.6, 0.42), (W - 1.8 - w * 0.5, 0.6))
ax.text(0.2, n * 0.85 + 0.65, T("分解：从需求到零件", "decompose: from needs to parts"), fontsize=8, color="#2c6fbb")
ax.text(W - 0.2, n * 0.85 + 0.65, T("验证：从零件到整机", "verify: from parts to the machine"), fontsize=8, color="#2ca02c", ha="right")
ax.text(W / 2, 2.15, T("虚线：每一级的验证\n对照同一级的要求", "dashed: each check is against\nthe requirement at its own level"), ha="center", fontsize=7, color=H.MUTED)
ax.set_xlim(-0.1, W + 0.1)
ax.set_ylim(-0.1, n * 0.85 + 0.9)
ax.axis("off")
fig.tight_layout()
figure(fig, "fig2_5_1")
