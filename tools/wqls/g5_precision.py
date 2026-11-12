"""第 138 轮 G5.1 第 4、5、6 步、G5.2：尺寸链、夹具、精度预算（用数字工厂 hub/tolerance.py、hub/fixture.py、hub/accuracy.py）。

G5.2（2026-11-11）改为“先做精基准、合箱，再整体精镗”：两件各自粗加工、时效、精铣接合面后合箱，打锥销，
合件以下件底面 A 和两个工艺孔 Ø10 H7 定位，在卧加上一次装夹精加工两件上的全部孔系（工序 70，夹具 FX-HSG-P-70）。
现在用的是 pair_budgets()（合件精加工的精度预算）和 fixture_pair()（FX-HSG-P-70 的夹紧）；
下面的方案 I、方案 III 和上件单独精加工的 budgets_upper_g51() 留作 G5.1 的记录。

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

KC11, MC = 1160.0, 0.26

ARCSEC = math.pi / 180 / 3600
# 几何（mm，整机坐标）：针杆轴线 x = 0、y = 0；定位销（G4.4 的 joint()）；上轴两孔
PINS = [(315.8, 7.0), (380.2, 66.0)]          # G5.2：第二个销由 y 47 移到 66（锥销孔要从机座底下钻）
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
    两个工艺孔 Ø9 H7 套液压涨销（圆柱涨销＋削边涨销，零间隙）。立柱脚的 4 个凸台在立柱里面，外面压不到，所以用 4 个液压拉缸：
    拉杆拧进凸台上的 M10 螺孔（工序 10 就攻好），把工件拉紧在正下方的 4 个支承钉上（拉力作用线过支承钉，不产生弯矩）。
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
    # 辅助支承（G5.1 补充）：机头悬伸，粗估机头一端的刚度 k ≈ m·(2πf)²（有效质量约 5 kg，前后 221 Hz、上下 229 Hz）
    k_lat = 5.0 * (2 * math.pi * 221) ** 2 / 1e6        # N/μm
    k_ver = 5.0 * (2 * math.pi * 229) ** 2 / 1e6
    # 直角铣头从下往上钻针杆孔 Ø11.5、f 0.15：Ff ≈ 0.5·kc·(D/2)·f·sinκ（Sandvik 公式），kc = kc1·h^−mc，h = f/2·sinκ
    kap = math.radians(59)
    h = 0.15 / 2 * math.sin(kap)
    Ff_drill = 0.5 * (1160 * h ** -0.26) * (11.5 / 2) * 0.15 * math.sin(kap)
    k_sup = 60.0                                        # 液压浮动支承锁紧后的刚度（柱塞 Ø16，产品样本量级 50–80 N/μm）
    k_top = 1 / (1 / k_sup + 1 / 40.0)                  # 顶部支承顶在 4.5 mm 顶壁上，顶壁局部刚度按 40 N/μm 串联
    aux = dict(supports=[dict(where="机头底面，往上撑", at=(-25, 52, 46)), dict(where="机头底面，往上撑", at=(25, 52, 46)),
                         dict(where="机头后侧面，往前撑", at=(-20, 70, 190)), dict(where="机头顶面，往下撑（后立柱的回转臂上）", at=(-20, -28, 258))],
               k_head_lat_N_um=round(k_lat, 1), k_head_ver_N_um=round(k_ver, 1), k_support_N_um=k_sup, k_top_eff_N_um=round(k_top, 1),
               face_mill_N=round(Fc_face), drill_thrust_up_N=round(Ff_drill),
               deflect_face_um=dict(without=round(Fc_face / k_lat), with_=round(Fc_face / (k_lat + k_sup), 1)),
               deflect_drill_um=dict(without=round(Ff_drill / k_ver), with_=round(Ff_drill / (k_ver + k_top), 1)),
               f_head_Hz=dict(lat=round(221 * math.sqrt((k_lat + k_sup) / k_lat)), ver=round(229 * math.sqrt((k_ver + 2 * k_sup) / k_ver))),
               load_max_N=round(1.5 * max(Fc_face, Ff_drill)), rated_N=4000, spring_N=10,
               preload_deflect_um=round(10 / k_ver, 2),
               clear_angle_head_mm=round(min(math.hypot(x, y) for x, y in ((-25, 52), (25, 52))) - 8 - 28, 1),
               note="支承只能往一个方向撑：底面两个管往下的力，后侧面管往后的力，顶面那个管直角铣头从下往上钻孔的轴向力。"
                    "弹簧推出后液压锁紧，只撑不定位；精镗两轴承孔前全部松开缩回，同轴度不受影响")
    expand = dict(X1=0.003, X2=0.004, note="液压涨销定位，间隙按 0.003–0.004 计（产品样本量级）")
    th = (expand["X1"] + expand["X2"]) / PIN_L
    return dict(Fc_bore_edge_N=round(Fc_edge), Ff_bore_N=round(Ff_bore), torque_bore_Nm=round(T_bore, 1), Fc_face_N=round(Fc_face),
                weight_N=round(G), K=round(K, 2), W_slide_N=round(W_slide), W_tip_N=round(W_tip), W_required_N=round(W),
                cylinders=dict(n=4, p_mpa=4.0, D_min=round(cyl["D_min"], 1), D=cyl["D"], Q_each=round(cyl["Q"]) if cyl["Q"] else None),
                locating=dict(expand, rot_rad=th, at_needle_mm=round(dist_point_to_pins(NEEDLE) * th, 4)), aux_supports=aux,
                note="上件的孔系都在这一次装夹里加工，相互位置与定位误差无关；工艺孔不是装配基准（装配靠找正后配铰的锥销）")


# ---------------------------------------------------------------- 三、精度预算（hub/accuracy.budget：系统误差相加，随机误差平方和开方）
def budgets_upper_g51():
    """G5.1 记录：上件单独在卧加上精加工时的预算（G5.2 起不用）"""
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
        dict(name="辅助支承弹簧推力（≤ 10 N）引起的机头附加变形，锁紧后保持（G5.1 补充）", range=2 * 0.001, kind="sys"),
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


# ---------------------------------------------------------------- G5.2：合件精加工（工序 70）
LOWER_PINS = ((-94.4, -30.0), (401.4, 80.0))      # 下件底边法兰上的两个工艺孔 Ø10 H7（housing.py BED_PROC_HOLES）
X_TABLE = 153.0                                   # 合件在转台上居中：转台中心 x 153、y 27
X_LOW = (96.0, 371.0)                             # 下轴两孔中点 x（88…104、364…378）


def pair_budgets():
    """合件一次装夹（下件 A ＋ 两工艺孔）精加工的精度预算。公差带是直径或全宽，误差项按全宽（偏移 × 2）计。"""
    s3 = 3 * ARCSEC
    # 针杆孔对旋梭轴孔轴线的位置度 Ø0.05（只看 y 向：x 向的梭尖间隙靠旋梭在轴上的轴向位置调）。
    # 针杆孔在上件工序 50 已精铰（合箱后进不去刀，见细则 G5.2 偏差 1）。工序 70 开头在针杆上、下两孔里各插一个液压涨紧塞规 Ø12，
    # 测头在 B 0° 测两个塞规伸出来的测量段：下塞规在机座和机头之间的空当里（z 30），上塞规经面板口（z 190），各 3 点定圆心。
    # 两个圆心连成针杆轴线，外推到旋梭轴高度 z −21.5、上轴高度 z 200，作为旋梭轴孔和上轴两孔的 y 坐标。
    # 测量和镗孔都在 B 0°，零件 y 向都由机床 X 轴定，不经过转台分度。
    zl, zu = 30.0, 190.0

    def amp(z):                                          # 两个圆心的误差外推到 z 的放大系数
        k = (z - zl) / (zu - zl)
        return math.hypot(1 - k, k)
    a_h, a_b = amp(-21.5), amp(200.0)
    needle_hook = [
        dict(name="两个涨紧塞规在针杆孔里的定心（液压涨紧，零间隙）各 ±0.002，外推到 z −21.5（放大 {:.2f}）".format(a_h), range=2 * 0.002 * a_h, kind="rand"),
        dict(name="测头：每个塞规 3 点定圆心 ±0.0015（单点重复性 1 μm，含测针偏置标定），外推后", range=2 * 0.0015 * a_h, kind="rand"),
        dict(name="镗旋梭轴孔时 X 轴定位重复性 ±0.002", range=2 * 0.002, kind="rand"),
        dict(name="阶梯镗杆（Ø18 杆、Ø12 颈，伸出 175）：切削力随刀转动，主要让孔变小（按实测孔径补偿），轴线偏移按 ±0.002", range=2 * 0.002, kind="rand"),
        dict(name="热漂移（测量到镗完约 10 min）", range=2 * 0.002, kind="sys"),
        dict(name="夹紧变形：压板压在支承正上方，只有局部压缩", range=2 * 0.001, kind="sys"),
    ]
    needle_b = [   # 针杆孔对上轴两孔公共轴线 B 的位置度 Ø0.05（y 向）：上轴两孔的 y 也取测出的针杆轴线（外推到 z 200）
        dict(name="两个塞规定心各 ±0.002，外推到 z 200（放大 {:.2f}）".format(a_b), range=2 * 0.002 * a_b, kind="rand"),
        dict(name="测头定圆心 ±0.0015，外推后", range=2 * 0.0015 * a_b, kind="rand"),
        dict(name="同轴镗杆定位：X 轴重复性 ±0.002、导向套对主轴 0.002", range=2 * math.hypot(0.002, 0.002), kind="rand"),
        dict(name="热漂移", range=2 * 0.002, kind="sys"),
    ]
    coax_up = [   # 上轴两孔同轴度 Ø0.02：同 G5.1（镗杆从机头端伸进去，尾部导向柱 Ø17 穿过电机端 Ø20 过孔进旋转导向套）
        dict(name="旋转导向套（预紧轴承，零间隙）轴线对主轴轴线：夹具装上后在机用检棒调到 0.002", range=2 * 0.002, kind="sys"),
        dict(name="旋转导向套径向跳动 0.002", range=2 * 0.002, kind="rand"),
        dict(name="主轴径向跳动（精镗区 0.002）", range=2 * 0.002, kind="rand"),
        dict(name="镗杆弯曲（两端支承；尾部导向柱 Ø17，按 0.0015 计）", range=2 * 0.0015, kind="sys"),
        dict(name="精镗前夹紧力降到 40%，夹紧变形残余（估 0.001）", range=2 * 0.001, kind="sys"),
    ]
    coax_low = [   # 下轴两孔同轴度 Ø0.02：镗杆 Ø26 从右端壁 Ø34 孔进，经横筋 Ø34 孔，尾部导向柱 Ø17 穿过左端壁 Ø20 孔进旋转导向套（左支架）
        dict(name="旋转导向套轴线对主轴轴线：在机用检棒调到 0.002", range=2 * 0.002, kind="sys"),
        dict(name="旋转导向套径向跳动 0.002", range=2 * 0.002, kind="rand"),
        dict(name="主轴径向跳动 0.002", range=2 * 0.002, kind="rand"),
        dict(name="镗杆弯曲（杆身 Ø26，两刀相距 276，按 0.001 计）", range=2 * 0.001, kind="sys"),
        dict(name="夹紧变形残余（估 0.001）", range=2 * 0.001, kind="sys"),
    ]
    centre = [   # 齿轮中心距 31.058 ± 0.015（T 0.03）：旋梭轴孔在 B 0° 镗，下轴两孔在 B 180° 镗
        dict(name="转台分度 180° ±3″：下轴孔离转台中心最远 218（x 371）", range=2 * s3 * (X_LOW[1] - X_TABLE), kind="rand"),
        dict(name="X、Y 轴定位精度 ±0.004（两个孔各一次，投影到中心连线上）", range=2 * math.sqrt(2) * 0.004, kind="rand"),
        dict(name="两次对刀（镗杆偏心标定）±0.002", range=2 * math.sqrt(2) * 0.002, kind="rand"),
        dict(name="热漂移", range=0.004, kind="sys"),
    ]
    height = [   # 上轴中心到底面 A：262 ± 0.05（T 0.1）
        dict(name="夹具支承钉顶面对托盘的高度，标定后 0.005", range=0.005, kind="sys"),
        dict(name="Y 轴定位精度 ±0.004", range=0.008, kind="rand"),
        dict(name="底面 A 平面度 0.05 与支承钉贴合（4 点，取 0.02）", range=0.02, kind="rand"),
        dict(name="热漂移 Y 向", range=0.006, kind="sys"),
    ]
    par = [   # 上轴对下轴的平行度 0.03（在 300 长度上，同步带两轮对齐、齿轮不受影响）
        dict(name="上轴两孔在 B 0° 镗、下轴两孔在 B 180° 镗：分度 ±3″ 在 300 长度上", range=2 * s3 * 300, kind="rand"),
        dict(name="两根镗杆各自的导向套对主轴 0.002", range=2 * math.sqrt(2) * 0.002, kind="rand"),
        dict(name="两根镗杆弯曲之差", range=0.002, kind="sys"),
    ]
    out = {}
    for name, items, T in (("针杆孔对旋梭轴孔 位置度 Ø0.05", needle_hook, 0.05), ("针杆孔对上轴孔 B 位置度 Ø0.05", needle_b, 0.05),
                           ("上轴两孔同轴度 Ø0.02", coax_up, 0.02),
                           ("下轴两孔同轴度 Ø0.02", coax_low, 0.02), ("齿轮中心距 31.058 ± 0.015", centre, 0.03),
                           ("上轴中心高 262 ± 0.05（对 A）", height, 0.10), ("上轴对下轴平行度 0.03/300", par, 0.03)):
        r = AC.budget(items, T)
        out[name] = dict(items=[dict(name=i["name"], kind=i["kind"], range=round(i["range"], 4)) for i in items],
                         sys=round(r["sys"], 4), rand=round(r["rand"], 4), total=round(r["total"], 4), T=T,
                         share=round(r["total"] / T, 2), ok=r["ok"], tight=r["tight"])
    return out


budgets = pair_budgets


def fixture_pair():
    """合件卧加夹具 FX-HSG-P-70：底面 A 放在 4 个支承钉上，两个工艺孔 Ø10 H7 套液压圆柱涨销、削边涨销（零间隙）；
    4 个液压回转压板压在机座顶面的四角，正对下面的支承钉。夹具是框架，支承钉在两条纵梁上，中间空着：
    锥销孔要从机座底下往上钻（机座底面敞开），直角铣头就放在框里。工序 L30 下件单独粗镗也用这个夹具。"""
    kc = lambda h: KC11 * h ** -MC                      # noqa: E731
    h = 0.15 / 2 * math.sin(math.radians(59))
    Ff_drill = 0.5 * kc(h) * (8.5 / 2) * 0.15 * math.sin(math.radians(59))     # 钻锥销底孔 Ø8.5、f 0.15，往上的轴向力
    hm = 0.08 * math.sqrt(47.25 / 63)
    Fc_face = KC11 * hm ** (-MC) * 0.5 * hm * 5 * 47.25 / (math.pi * 63)      # 精铣面板口端面 ap 0.5（最大的横向力）
    G = 24.3 * 9.81
    K = FX.safety_factor(K1="粗加工", K2="钻削", K3="连续", K4="机动")["K"]
    W_lift = max(0.0, K * Ff_drill - G)                  # 钻孔把合件往上顶，靠压板压住
    Kf = FX.safety_factor(K1="精加工", K2="铣削", K3="断续", K4="机动")["K"]
    W_slide = max(0.0, FX.friction_clamp_required(Fc_face, Kf, mu1=0.16, mu2=0.16) - G)
    W = max(W_lift, W_slide)
    cyl = FX.cylinder_bore(W / 4, p=4.0, eta=0.85, pull=True)
    expand = dict(X1=0.003, X2=0.004, note="液压涨销定位，间隙按 0.003–0.004 计")
    L = math.dist(*LOWER_PINS)
    return dict(drill_thrust_up_N=round(Ff_drill), Fc_face_N=round(Fc_face), weight_N=round(G), K_drill=round(K, 2), K_face=round(Kf, 2),
                W_lift_N=round(W_lift), W_slide_N=round(W_slide), W_required_N=round(W),
                clamps=dict(n=4, p_mpa=4.0, D_min=round(cyl["D_min"], 1), D=cyl["D"], Q_each=round(cyl["Q"]) if cyl["Q"] else None),
                pins_L_mm=round(L, 1), locating=dict(expand, rot_rad=(expand["X1"] + expand["X2"]) / L),
                head_support="不加：精加工最大的横向力是精铣面板口端面约 {:.0f} N，机头让刀约 {:.0f} μm，只影响这个端面（平面度 0.1）".format(Fc_face, Fc_face / 10.0),
                note="所有孔都在这一次装夹里加工，相互位置与定位误差无关；定位误差只影响孔系对 A 和工艺孔的位置（中心高 262 ± 0.05）")


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "docs" / "设计" / "WQ-LS" / "G5"
    res = dict(budgets=pair_budgets(), fixture_pair=fixture_pair(), fixture_upper_rough=fixture_upper(),
               g51_record=dict(scheme_I=scheme_I(), scheme_III=scheme_III(), budgets_upper=budgets_upper_g51()))
    (out / "精度分析.json").write_text(json.dumps(res, ensure_ascii=False, indent=1))
    I, II = res["g51_record"]["scheme_I"], res["g51_record"]["scheme_III"]
    print(f"方案 I（分开加工、互换）：针杆—旋梭 极值 ±{I['extreme_half']}，概率 ±{I['statistical_half']}，要求 ±0.05")
    for l in I["links"]:
        print("    ", l)
    print(f"方案 III（找正后配铰锥销）：极值 ±{II['extreme_half']}，概率 ±{II['statistical_half']}")
    print("合件夹具 P-70", res["fixture_pair"])
    for k, v in res["budgets"].items():
        print(k, "合计", v["total"], "/", v["T"], f"{v['share']:.0%}", "OK" if v["ok"] else "超差", "裕量不足" if v["tight"] else "")


if __name__ == "__main__":
    main()
