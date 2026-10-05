"""图 1.3.1 工程师的工具链：CAD、CAE、PLM、ERP、MES、QMS 由一条数据线连起来；箭头上是数字工厂统一数据总线的消息类型。"""
import _ch1 as H
from bookout import T, figure, style

plt = style()
fig, ax = plt.subplots(figsize=(6.9, 3.4))
nodes = {
    "CAD": (0.0, 2.2, T("CAD 建模出图\nFreeCAD / build123d\n在线设计台", "CAD: model, drawing\nFreeCAD / build123d\nweb design desk"), H.PALE["green"]),
    "CAE": (0.0, 0.4, T("CAE 仿真与分析\n有限元、疲劳、\n多体动力学", "CAE: simulation\nFE, fatigue,\nmultibody"), H.PALE["orange"]),
    "PLM": (2.45, 1.3, T("PLM 设计发布\n与审批（版本）", "PLM: release &\napproval (revisions)"), H.PALE["purple"]),
    "ERP": (4.9, 2.2, T("ERP（ERPNext）\n物料、BOM、工艺、\n订单、成本", "ERP (ERPNext)\nitems, BOM, routing,\norders, cost"), H.PALE["blue"]),
    "MES": (4.9, 0.4, T("MES 车间\n工单、数控程序、\n设备状态", "MES: shop floor\nwork orders, CNC,\nmachine status"), H.PALE["teal"]),
    "QMS": (7.1, 1.3, T("QMS 质量\n检验、三坐标、\n不合格品", "QMS: quality\ninspection, CMM,\nnonconformance"), H.PALE["gray"]),
}
w, h = 1.85, 0.95
for k, (x, y, txt, col) in nodes.items():
    H.box(ax, x, y, w, h, txt, col, 7.2)


def link(a, b, label, dy=0.0, rad=0.0):
    xa, ya = nodes[a][0] + w / 2, nodes[a][1] + h / 2
    xb, yb = nodes[b][0] + w / 2, nodes[b][1] + h / 2
    if abs(xa - xb) < 1e-9:                                       # 上下相连：从框边到框边
        H.arrow(ax, (xa, ya - h / 2), (xb, yb + h / 2), rad=rad)
        xm = xa + 0.08
        ax.text(xm, (ya + yb) / 2, label, ha="left", va="center", fontsize=6.8, color="#2c6fbb",
                family="monospace" if label.isascii() else None)
        return
    H.arrow(ax, (xa + (w / 2 if xb > xa else -w / 2), ya), (xb - (w / 2 if xb > xa else -w / 2), yb), rad=rad)
    ax.text((xa + xb) / 2, (ya + yb) / 2 + dy, label, ha="center", fontsize=6.8, color="#2c6fbb",
            family="monospace" if label.isascii() else None)


link("CAD", "PLM", "design.submit", 0.18)
link("CAE", "PLM", T("分析报告", "report"), -0.25)
link("PLM", "ERP", "design.release", 0.2)
link("PLM", "MES", "design.gcode", -0.42)
link("ERP", "MES", "erp.doc", 0.0)
link("MES", "QMS", "quality.measurement", -0.5)
link("QMS", "ERP", "quality.ncr", 0.2)
ax.set_xlim(-0.1, 9.1)
ax.set_ylim(0.2, 3.3)
ax.axis("off")
fig.tight_layout()
figure(fig, "fig1_3_1")
