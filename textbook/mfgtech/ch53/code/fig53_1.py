"""53.1 节的三维图：键槽深度尺寸链落在 SH-301 上（图 53.1.2，过键槽中部剖开）、齿轮位长度 60 的轴向尺寸链（图 53.1.3）。
模型：factory/digital/models3d（SH-301 各工序状态取自工艺规程）。磨削余量在 (b) 中放大画出。"""
import _mfg as M
from bookout import out

C, W, J, E, TY, MA, S = M.m3d()
R = M.r3d()
A, P = C.Assembly, C.Part
blue, red, green = "#4f7fb8", "#c0504d", "#5a9e6f"
k = W.plan()["part"]["keyway"]
xk = 52.0 + float(k["offset_mm"]) + float(k["L"]) / 2          # 键槽中部
b, z_bot = float(k["b"]), 20.0 - float(k["t"])                  # 槽宽、槽底离轴线（15）
cam = {"dir": [-1, 0, 0], "fit": [[xk, -30, -26], [xk, 30, 26]]}
sec = ((xk, 0, 0), (1, 0, 0))


def slot_section(r_pre, r_post=None):
    q = A("键槽截面")
    body = S.cyl("x", (0, 0), r_pre, xk - 15, xk + 15) - S.box(xk - 16, xk + 16, -b / 2, b / 2, z_bot, 30)
    if r_post is None:
        q.add(P("工件（铣键槽后，磨削前）", body, "work"))
    else:
        core = body & S.cyl("x", (0, 0), r_post, xk - 16, xk + 16)
        q.add(P("工件（磨削后）", core, "work"))
        q.add(P("磨去的一层（放大画出）", body - S.cyl("x", (0, 0), r_post, xk - 16, xk + 16), red, opacity=0.5))
    return q


r1, r2 = 20.15, 20.0
H = z_bot + r1
pa = R.render_png(slot_section(r1), 640, 600, camera=cam, section=sec, fontSize=19,
                  dims=[{"a": (xk, 4, -r1), "b": (xk, 4, z_bot), "off": (0, 0, 0), "text": f"H = {H:g}"},
                        {"a": (xk, -8, -r1), "b": (xk, -8, 0), "off": (0, 0, 0), "text": f"r₁ = {r1:g}"}],
                  points=[{"at": (xk, 0, 0), "r": 4, "color": "#1d2327"}, {"at": (xk, 0, -r1), "r": 5, "color": blue, "text": "精车外圆下母线（工序基准）", "dx": 10, "dy": 22}])
# (b) 磨削后：余量放大到 2 mm（r₁ 画成 22），槽底不动
r1x = 22.0
pb = R.render_png(slot_section(r1x, r2), 640, 600, camera={"dir": [-1, 0, 0], "fit": [[xk, -30, -28], [xk, 30, 28]]}, section=sec, fontSize=19,
                  dims=[{"a": (xk, 4, -r2), "b": (xk, 4, z_bot), "off": (0, 0, 0), "text": f"A₀ = d − t₁ = {z_bot + r2:g}", "color": red},
                        {"a": (xk, -8, -r2), "b": (xk, -8, 0), "off": (0, 0, 0), "text": f"r₂ = {r2:g}"}],
                  points=[{"at": (xk, 0, -r2), "r": 5, "color": red, "text": "磨后外圆下母线", "dx": 10, "dy": 22},
                          {"at": (xk, 0, -r1x), "r": 4, "color": blue, "text": "磨前的下母线", "dx": -150, "dy": 26}])
R.compose("fig53_1_2", [pa, pb], 2, titles=["(a) 工序 50 铣键槽：直接控制 H（从精车外圆下母线量起）", "(b) 工序 60 磨齿轮位后：d − t1 是间接得到的封闭环（磨削余量放大画出）"])

# ---- 图 53.1.3：齿轮位长度 60 的轴向尺寸链：167（增环）、52、55（减环）、60（封闭环）
w = W.sh301("op40")
q = A("轴向尺寸链")
q.add(w)
L = 167.0
y0 = -26.0
dims = [{"a": (0, y0, 0), "b": (L, y0, 0), "off": (0, -34, 0), "text": "167 ± 0.2（增环：工序 40 调头车左端面）", "color": blue},
        {"a": (0, y0, 0), "b": (52, y0, 0), "off": (0, -12, 0), "text": "52（减环）", "color": green},
        {"a": (112, y0, 0), "b": (L, y0, 0), "off": (0, -12, 0), "text": "55（减环）", "color": green},
        {"a": (52, 20.15, 0), "b": (112, 20.15, 0), "off": (0, 14, 0), "text": "A₀ = 60（封闭环，间接得到）", "color": red}]
R.figure3d("fig53_1_3", q, 1400, 650, camera={"dir": [0, -0.35, 1], "up": [0, 1, 0], "fit": [[-5, -75, 0], [L + 5, 45, 0]]}, dims=dims, fontSize=17,
           points=[{"at": (0, 0, 16), "r": 5, "color": blue, "text": "左端面 L", "dx": -30, "dy": -10}, {"at": (L, 0, 16), "r": 5, "color": blue, "text": "右端面 R", "dx": -20, "dy": -10},
                   {"at": (52, 0, 21), "r": 5, "color": red, "text": "S2", "dx": -8, "dy": -10}, {"at": (112, 0, 21), "r": 5, "color": red, "text": "S3", "dx": -8, "dy": -10}])
out(n_fig3d=2, H=H)
