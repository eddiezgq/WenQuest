"""51.8 节：算例 51.8.1——SH-301 铣键槽的三种定位方案比较（V 形块、两顶尖、卡盘加顶尖），对照槽底尺寸 H 和对称度的公差，按“定位误差不超过公差的三分之一”评价。"""
import _mfg as M
from bookout import T, out

TL = M.tol()
p = M.plan()
fin = next(f for f in M.op(p, 40)["features"] if f["name"] == "齿轮位")
Td = fin["es_mm"] - fin["ei_mm"]
H = p["chains"][0]["links"][0]
TH = H["es"] - H["ei"]
Tsym = 0.02                                         # 图纸 C6：键槽对称度 0.02
# 键槽对称度的基准是齿轮位轴线；齿轮位在铣键槽之后还要磨削（工序 60），磨后的轴线就是两中心孔连线。
# 工序 40 两顶尖精车，齿轮位外圆对中心孔连线的径向跳动按 ≤ 0.006 控制（工艺规程工序 40 的检验项），偏心 e_t = 0.006/2。
tir_t = next(i for i in M.op(p, 40)["inspect"] if "齿轮位跳动" in i["char"])["tir"]
e_t = tir_t / 2
tir_chuck = 0.03                                    # 三爪卡盘的定心精度（径向跳动读数，教学取值；常见 0.02–0.08 mm）
schemes = {
    # A：V 形块定位在精车外圆上，H 的工序基准是该外圆的下母线；V 形块对中，直径误差不影响对称度，
    #    但精车外圆的轴线相对中心孔连线（磨后的齿轮位轴线）有偏心，一批工件偏向各方向，对称度上占 2e_t
    "A": {"name": T("V 形块 + 轴向挡销", "V-blocks + axial stop"), "H": TL.v_block(Td, 90, "bottom"), "sym": TL.offset_to_zone(e_t)},
    # B：两顶尖，定位基准是中心孔连线；H 从精车外圆下母线量起：半径公差 Td/2 加外圆偏心在竖直方向的变动 2e_t
    "B": {"name": T("两顶尖", "between centres"),
          "H": TL.datum_mismatch([TL.Link("半径", 20.15, 0, -Td / 2), TL.Link("外圆偏心", 0, e_t, -e_t)]), "sym": 0.0},
    # C：三爪卡盘夹左轴端、后顶尖顶右端：卡盘的偏心 e = TIR/2，一批工件偏向各方向，轴线位置的变动范围 2e = TIR（按卡盘端估计，偏于安全）
    "C": {"name": T("三爪卡盘 + 后顶尖", "chuck + tail centre"), "H": Td / 2 + TL.chuck_runout_error(tir_chuck),
          "sym": TL.chuck_runout_error(tir_chuck)},
}
v = {"TH": TH, "TH3": TH / 3, "Tsym": Tsym, "Tsym3": Tsym / 3, "tir_chuck": tir_chuck, "e_chuck": tir_chuck / 2,
     "tir_t": tir_t, "e_t": e_t, "Td": Td, "hyd": 0.005, "hyd_ok": T("满足", "met") if TL.ok_against(Tsym, 0.005) else T("不满足", "not met")}
for k, s in schemes.items():
    okH, okS = TL.ok_against(TH, s["H"]), TL.ok_against(Tsym, s["sym"])
    v[k + "_H"], v[k + "_sym"] = s["H"], s["sym"]
    v[k + "_ok"] = T("可用", "acceptable") if okH and okS else T("不可用", "not acceptable")
out(**v)
