"""图 1.7.1 机械工程史上的几个节点（年代见 1.7 节正文与参考文献）。"""
import _ch1 as H
from bookout import T, figure, style

EVENTS = [  # (年份, 中文, 英文, 上 / 下)
    (-450, "《考工记》：车、弓的\n制作规范", "Kaogong Ji: rules for\ncarts and bows", 1),
    (1088, "苏颂、韩公廉\n水运仪象台", "Su Song's astronomical\nclock tower", -1),
    (1637, "宋应星\n《天工开物》", "Song Yingxing,\nTiangong Kaiwu", 1),
    (1769, "瓦特分离冷凝器\n专利", "Watt's separate\ncondenser patent", -1),
    (1841, "惠特沃斯\n螺纹标准", "Whitworth\nscrew thread", 1),
    (1870, "沃勒：疲劳\n极限", "Wöhler: fatigue\nlimit", -1),
    (1875, "勒洛\n《理论运动学》", "Reuleaux,\nKinematics", 1),
    (1886, "雷诺：润滑\n理论", "Reynolds:\nlubrication", -1),
    (1947, "国际标准化组织\nISO 成立", "ISO\nfounded", 1),
    (1956, "有限元法\n（特纳等）", "finite element\nmethod (Turner)", -1),
    (1963, "Sketchpad：\n计算机绘图", "Sketchpad:\ncomputer graphics", 1),
]


plt = style()
fig, ax = plt.subplots(figsize=(6.9, 3.0))
n = len(EVENTS)
ax.plot([-0.3, n - 0.7], [0, 0], color=H.INK, lw=1.2)
for k, (y, zh, en, side) in enumerate(EVENTS):
    yr = T("战国（约前 5—前 3 世纪）", "Warring States (c. 5th–3rd c. BC)") if y < 0 else str(y)
    ax.plot(k, 0, "o", color="#2c6fbb", ms=5)
    ax.plot([k, k], [0, side * 0.35], color=H.MUTED, lw=0.7)
    ax.text(k, side * 0.4, yr + "\n" + T(zh, en) if side > 0 else T(zh, en) + "\n" + yr, ha="center",
            va="bottom" if side > 0 else "top", fontsize=6.6)
ax.text(n - 0.7, -0.12, T("（不按比例）", "(not to scale)"), ha="right", va="top", fontsize=6.5, color=H.MUTED)
ax.set_xlim(-0.8, n - 0.2)
ax.set_ylim(-1.3, 1.3)
ax.axis("off")
fig.tight_layout()
figure(fig, "fig1_7_1")
