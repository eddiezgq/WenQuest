"""52.5 节：夹紧动力装置。算例 52.5.1——JJ-301-50 改为机器人上下料时的气动方案：
机动夹紧安全系数 K4 = 1.0 重算需要的夹紧力；(a) 气缸代替螺柱、在压板中部下拉（经杠杆比）与 (b) 直接压工件的转角缸，
两者都是活塞杆拉回夹紧，按有杆腔面积选缸径；液压方案；手动定扭矩夹紧与气动夹紧的夹紧力分散比较。"""
import _mfg as M
from bookout import out

FX = M.fx()
fx = M.fixture_data()
cl = fx["clamping"]
pn = fx["pneumatic"]
an = FX.analyse(fx)
need_p = an["need_pneumatic"]["W"]
K_man, K_pn = an["K"]["K"], FX.safety_factor(**(fx["safety"] | {"K4": "机动", "K5": "方便"}))["K"]
need_each = need_p / cl["count"]                         # 每个夹紧点需要的夹紧力（机动）
ratio = cl["l_heel"] / (cl["l_work"] + cl["l_heel"]) * 0.95
strap = FX.cylinder_bore(need_each / ratio, pn["p_min"], pn["eta"], pull=True)     # (a) 拉杆式压板
swing = FX.cylinder_bore(need_each / 0.95, pn["p_min"], pn["eta"], pull=True)      # (b) 转角缸，回程拉紧
assert strap["D"] == an["cyl"]["D"]
hyd = FX.cylinder_bore(need_each / 0.95, 5.0, 0.9, series=(12, 16, 20, 25, 32, 40), pull=True)   # 液压转角缸，5 MPa
# 夹紧力的分散：手动定扭矩时，螺纹和支承面的摩擦系数在 0.10–0.20 之间变化
lo = FX.screw_clamp(cl["hand_force"], cl["wrench"], cl["thread_d"], cl["thread_P"], 0.20, 0.20, cl["r_end"])["W"]
hi = FX.screw_clamp(cl["hand_force"], cl["wrench"], cl["thread_d"], cl["thread_P"], 0.10, 0.10, cl["r_end"])["W"]
# 气动：气压在 0.4–0.6 MPa 之间波动（车间管网），用减压阀稳定在 0.5 ± 0.02 MPa
D, rod = swing["D"], swing["rod"]
q_lo, q_hi = FX.cylinder(D, 0.4, pn["eta"], rod, False), FX.cylinder(D, 0.6, pn["eta"], rod, False)
q_reg_lo, q_reg_hi = FX.cylinder(D, 0.48, pn["eta"], rod, False), FX.cylinder(D, 0.52, pn["eta"], rod, False)
push50 = FX.cylinder(D, pn["p_min"], pn["eta"])
out(K_man=K_man, K_pn=K_pn, need_p=need_p, need_man=an["need"]["W"], need_each=need_each, ratio=ratio,
    D_strap=strap["D"], rod_strap=strap["rod"], Q_strap=strap["Q"], D_swing=swing["D"], rod_swing=swing["rod"], Q_swing=swing["Q"],
    push_swing=push50, D_hyd=hyd["D"], rod_hyd=hyd["rod"], p_min=pn["p_min"],
    man_lo=lo, man_hi=hi, man_ratio=hi / lo, pn_lo=q_lo, pn_hi=q_hi, pn_ratio=q_hi / q_lo, reg_ratio=q_reg_hi / q_reg_lo)
