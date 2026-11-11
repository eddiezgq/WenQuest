"""第 138 轮 G5.1 第 4、5、6 步：尺寸链、夹具、精度预算（用数字工厂 hub/tolerance.py、hub/fixture.py、hub/accuracy.py）。

    python3 tools/wqls/g5_precision.py [<输出目录>]  → 精度分析.json，并打印结论

一、两件分开以后最关键的一环——针杆（上件）对旋梭、针板（下件）的位置。比较两种做法：
  方案 I（细则原定）：两件分别加工，装配时靠两个 Ø10 圆柱定位销对上，两件可以互换；
  方案 III（采用）：两件仍分别加工，各自的孔系都在一次装夹里完成；装配时用找正检具把上件找正到下件上
         （检棒插进针杆孔，对准下件的针板孔基准），拧紧螺钉后合箱配钻、配铰两个锥销孔（GB/T 117，1:50），打入锥销。
         两件配对使用，打同一编号。这是机床、减速器上“找正后配作销孔”的常用做法。
  （曾考虑方案 II：合箱后在同一次装夹里镗全部孔。不可行：针杆孔要从机头下面加工，合箱后机头下面只有 45 mm 高的空间，
   放不进直角铣头；机座底面贴在弯板上时，又挡住了从下面进刀的路。）
二、上件卧加夹具 FX-HSG-U-20 的定位与夹紧。
三、上件一次装夹加工的精度预算：两轴承孔同轴度 Ø0.02（精镗用镗杆加导向套同轴镗，第一版用转台掉头分别镗，合计 85%，AI 工艺评审员提示裕量不足，改了）、针杆孔对 B 位置度 Ø0.05、上轴中心高 200 ± 0.03（对接合面 C）。
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(ROOT / "factory" / "digital"), str(ROOT / "factory")]
from hub import accuracy as AC  # noqa: E402
from hub import fixture as FX  # noqa: E402
from hub import tolerance as TL  # noqa: E402

ARCSEC = math.pi / 180 / 3600
# 几何（mm，整机坐标）：针杆轴线 x = 0、y = 0；定位销（G4.4 的 joint()）；上轴两孔
PINS = [(315.8, 7.0), (380.2, 47.0)]          # G4.4 定稿模型（g45 stats.json joint.pins）
PIN_L = math.dist(*PINS)
NEEDLE = (0.0, 0.0)
X_6202, X_6201 = 31.0, 375.0
HOLE = (10.0, 0.015, 0.0)          # Ø10 H7
PIN_ASM = (10.0, 0.0, -0.009)      # 装配定位销 Ø10 h6
PIN_FIX = (10.0, -0.005, -0.011)   # 夹具圆柱销 Ø10 g5


def dist_point_to_pins(p):
    """点到第一个销的距离（转角误差的力臂）"""
    return math.dist(p, PINS[0])


def scheme_I():
    """方案 I：针杆孔（上件）对旋梭（下件）的位置，在两销连线的垂直方向上的极值与概率合成（单边 ±）。"""
    R = dist_point_to_pins(NEEDLE)
    # 上件工序 50：夹具一面两销定位（圆柱销 g5 + 削边销），针杆孔相对上件销孔的位置误差 = 定位误差 + 机床定位
    X1f = TL.pin_clearance(HOLE, PIN_FIX)
    dp = TL.diamond_pin((10.0, 0.015, 0.0), b=4.0, dLK=0.01, dLJ=0.003, T_pin=0.006)
    X2f = dp["X2max"]
    th_f = (X1f + X2f) / PIN_L                         # 最大转角（两孔间隙偏向相反）
    fix_needle = X1f / 2 + R * th_f / 2                 # 针杆孔处单边
    machine = 0.008                                     # 卧加 X/Y 定位精度单边（含直角铣头分度 ±5″ 在 150 mm 上 0.004）
    # 装配：两个 Ø10 h6 定位销压在下件、插进上件 H7 孔
    Xa = TL.pin_clearance(HOLE, PIN_ASM)
    th_a = 2 * Xa / PIN_L
    asm_needle = Xa / 2 + R * th_a / 2
    hook = fix_needle + machine                         # 下件旋梭孔对下件销孔：同样的夹具和机床，按同样估
    links = [TL.Link("针杆孔对上件销孔：夹具定位", 0, fix_needle, -fix_needle), TL.Link("针杆孔对上件销孔：机床", 0, machine, -machine),
             TL.Link("装配：定位销间隙（含转角）", 0, asm_needle, -asm_needle), TL.Link("旋梭轴孔对下件销孔", 0, hook, -hook)]
    ex, st = TL.extreme(links), TL.statistical(links)
    return dict(R_mm=round(R, 1), pin_L_mm=round(PIN_L, 1), X1_fixture=round(X1f, 4), X2_fixture=round(X2f, 4),
                rot_fixture_rad=th_f, X_assembly=round(Xa, 4),
                links=[dict(name=l.name, half=round(l.es, 4)) for l in links],
                extreme_half=round(ex.es, 4), statistical_half=round(st.es, 4), required_half=0.05,
                ok_extreme=ex.es <= 0.05, ok_statistical=st.es <= 0.05)



def scheme_III():
    """方案 III：装配找正后配铰锥销。针杆孔对下件基准的位置只取决于找正检具和配铰"""
    gauge = (0.018 + 0.008) / 2          # 检棒 Ø12 h5 在针杆孔 Ø12 H7 里的间隙，单边
    ref = 0.010                          # 下件上检具的基准（针板孔定位面）的制造误差
    adj = 0.005                          # 调整分辨率（顶丝微调）
    pin = 0.005                          # 打入锥销时的拉动
    links = [TL.Link("找正检棒在针杆孔里的间隙", 0, gauge, -gauge), TL.Link("下件检具基准", 0, ref, -ref),
             TL.Link("调整分辨率", 0, adj, -adj), TL.Link("配铰、打锥销的拉动", 0, pin, -pin)]
    ex, st = TL.extreme(links), TL.statistical(links)
    return dict(links=[dict(name=l.name, half=round(l.es, 4)) for l in links], extreme_half=round(ex.es, 4),
                statistical_half=round(st.es, 4), required_half=0.05, ok_extreme=ex.es <= 0.05)


# ---------------------------------------------------------------- 二、上件卧加夹具 FX-HSG-U-20
def fixture_upper():
    """上件立在卧加托盘上：接合面 C 朝下贴在夹具的立柱垫块上（垫高 160 mm，机头下面留出直角铣头的空间），
    两个工艺孔 Ø9 H7 套液压涨销（圆柱涨销＋削边涨销，零间隙），4 个液压缸正对垫块压在立柱脚凸台上（压在支承正上方，不产生弯矩）。
    切削力都在水平面内（平行于 C），靠摩擦抵抗；工件重力垂直于 C，帮助压紧。"""
    kc = lambda h: 1160 * h ** -0.26                   # noqa: E731  HT250 单位切削力 N/mm²
    Fc_edge = kc(0.125) * 2.0 * 0.125                   # 粗镗：单边 ap 2，双刃每刃 0.125
    Ff_bore = 0.4 * 2 * Fc_edge
    T_bore = Fc_edge * 17 * 2 / 1000
    Fc_face = 2.04 * 60e3 / 160                         # 粗铣面板口端面
    G = 16.1 * 9.81
    K = FX.safety_factor(K1="粗加工", K2="铣削", K3="断续", K4="机动", K6="接触面积大")["K"]
    F_par = max(Ff_bore, Fc_face)
    W_slide = max(0.0, FX.friction_clamp_required(F_par, K, mu1=0.16, mu2=0.16) - G)
    # 镗孔扭矩绕上轴（水平），使工件绕 C 面边缘翻转；压紧力的力臂取两排凸台间距的一半 67 mm（y −39.9 与 93.9）
    W_tip = K * T_bore / 0.067
    W = max(W_slide, W_tip)
    cyl = FX.cylinder_bore(W / 4, p=4.0, eta=0.85, pull=True)
    expand = dict(X1=0.003, X2=0.004, note="液压涨销定位，间隙按 0.003–0.004 计（产品样本量级）")
    th = (expand["X1"] + expand["X2"]) / PIN_L
    return dict(Fc_bore_edge_N=round(Fc_edge), Ff_bore_N=round(Ff_bore), torque_bore_Nm=round(T_bore, 1), Fc_face_N=round(Fc_face),
                weight_N=round(G), K=round(K, 2), W_slide_N=round(W_slide), W_tip_N=round(W_tip), W_required_N=round(W),
                cylinders=dict(n=4, p_mpa=4.0, D_min=round(cyl["D_min"], 1), D=cyl["D"], Q_each=round(cyl["Q"]) if cyl["Q"] else None),
                locating=dict(expand, rot_rad=th, at_needle_mm=round(dist_point_to_pins(NEEDLE) * th, 4)),
                note="上件的孔系都在这一次装夹里加工，相互位置与定位误差无关；工艺孔不是装配基准（装配靠找正后配铰的锥销）")


# ---------------------------------------------------------------- 三、精度预算（hub/accuracy.budget：系统误差相加，随机误差平方和开方）
def budgets():
    L_half = 172.0                                      # 两轴承孔离转台中心各约 172 mm（零件在托盘上居中）
    coax = [   # 同轴度 Ø0.02：精镗用“镗模式”同轴镗——一根镗杆从机头一端伸进去，前端 Ø35、后端 Ø32 两把精镗刀相距 344 mm，
               # 镗杆尾部 Ø17 导向柱穿过电机座的 Ø20 轴过孔，插进夹具支架上的旋转导向套，两孔一刀完成，不靠转台掉头。
               # （后轴承孔在电机座里面，外侧只有 Ø20 过孔，本来也只能从机头一端镗。）
               # 公差带是直径，误差项按“轴线偏移 × 2”计
        dict(name="旋转导向套（预紧轴承，零间隙）轴线对主轴轴线：夹具装上后在机用检棒调到 0.002", range=2 * 0.002, kind="sys"),
        dict(name="旋转导向套径向跳动 0.002", range=2 * 0.002, kind="rand"),
        dict(name="主轴径向跳动（精镗区 0.002）", range=2 * 0.002, kind="rand"),
        dict(name="镗杆弯曲（两端支承：主轴与导向套，前后两刀处之差；尾部导向柱 Ø17 较细，按 0.0015 计）", range=2 * 0.0015, kind="sys"),
        dict(name="精镗前松开、以精镗用的小夹紧力重夹，夹紧变形残余（估 0.001）", range=2 * 0.001, kind="sys"),
    ]
    needle = [   # 针杆孔对 B 的位置度 Ø0.05：直角铣头从机头下方铰孔
        dict(name="直角铣头输出轴倾斜：装好后用检棒在机标定，超过 ±3″ 就重装（铰孔长 150）", range=2 * 2 * 3 * ARCSEC * 150, kind="sys"),
        dict(name="直角铣头偏置标定（测头，±0.002）", range=2 * 2 * 0.002, kind="rand"),
        dict(name="转台分度 ±3″（针杆孔与轴承孔相差 90°，离转台中心约 180）", range=2 * 2 * 3 * ARCSEC * 180, kind="rand"),
        dict(name="X/Y 定位重复性 ±0.002", range=2 * 2 * 0.002, kind="rand"),
        dict(name="热漂移", range=2 * 0.002, kind="sys"),
    ]
    height = [   # 上轴中心到接合面 C：200 ± 0.03（T = 0.06）
        dict(name="夹具垫块顶面（C 的支承面）对托盘的高度，标定后 0.005", range=0.005, kind="sys"),
        dict(name="Y 轴定位精度 ±0.004", range=0.008, kind="rand"),
        dict(name="C 面平面度 0.02 与垫块贴合", range=0.01, kind="rand"),
        dict(name="热漂移 Y 向", range=0.004, kind="sys"),
    ]
    out = {}
    for name, items, T in (("两轴承孔同轴度 Ø0.02", coax, 0.02), ("针杆孔对 B 位置度 Ø0.05", needle, 0.05), ("上轴中心高 200 ± 0.03（对 C）", height, 0.06)):
        r = AC.budget(items, T)
        out[name] = dict(items=[dict(name=i["name"], kind=i["kind"], range=round(i["range"], 4)) for i in items],
                         sys=round(r["sys"], 4), rand=round(r["rand"], 4), total=round(r["total"], 4), T=T,
                         share=round(r["total"] / T, 2), ok=r["ok"], tight=r["tight"])
    return out


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "docs" / "设计" / "WQ-LS" / "G5"
    res = dict(scheme_I=scheme_I(), scheme_III=scheme_III(), fixture_upper=fixture_upper(), budgets=budgets())
    (out / "精度分析.json").write_text(json.dumps(res, ensure_ascii=False, indent=1))
    I, II = res["scheme_I"], res["scheme_III"]
    print(f"方案 I（分开加工、互换）：针杆—旋梭 极值 ±{I['extreme_half']}，概率 ±{I['statistical_half']}，要求 ±0.05")
    for l in I["links"]:
        print("    ", l)
    print(f"方案 III（找正后配铰锥销）：极值 ±{II['extreme_half']}，概率 ±{II['statistical_half']}")
    print("夹具", res["fixture_upper"])
    for k, v in res["budgets"].items():
        print(k, "合计", v["total"], "/", v["T"], f"{v['share']:.0%}", "OK" if v["ok"] else "超差", "裕量不足" if v["tight"] else "")


if __name__ == "__main__":
    main()
