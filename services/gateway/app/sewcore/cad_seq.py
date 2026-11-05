"""花样机、刺绣机、横机的三维零件（第 89 轮，只给三维讲解片用，不出 STEP）。

这三种机讲的是“一个花样 / 一片衣片怎么走完”，所以 phi 是**进度角**：
- 花样机、刺绣机：每 360° = 一针（主轴转一圈缝一针）；一针之内针杆按曲柄滑块上下，模板 / 绣框在离布窗口里移到下一针；
- 横机：每 360° = 一趟；一趟之内机头按这一趟的加速—匀速—减速走完行程（同 flatknit.profile），针按三角曲线起落。
针、趟的数据就是设计软件里样机用的那一串（analyze()['view']['cfg']，第 81 轮的 proto），和三维样机 15-1 / 16-1 / 17-1 同一套。
零件、尺寸照教材模型 model-pattern / model-embroid / model-flatknit（网页 three.js）——**尺寸是示意**，运动、针迹、趟次按这台设计。

页面坐标是 three.js 的 X 右、Y 上、Z 朝前；这里换成计算核心的 X 右、Y 朝后、Z 上：(x, y, z)页面 → (x, −z, y)。机器正面在 −Y。
"""
import base64
import json
import math
import zlib
from functools import lru_cache

from .common import thin

D2R = math.pi / 180
MACHINES = ("pattern", "embroid", "flatknit")
SEAM_MAX = 1200                 # 针迹管子最多这么多点（多了等间隔抽样，当前这一针总在末端）


def _c(h):
    return ((h >> 16 & 255) / 255, (h >> 8 & 255) / 255, (h & 255) / 255)


HOUSING, STEEL, DARK, ALU, TABLE = _c(0xe9e6dd), _c(0xc9d0d6), _c(0x2a3038), _c(0xb8c2cc), _c(0xcfc9ba)
BLUE, ORANGE, GREEN, GREY = _c(0x2f6fd6), _c(0xe0662f), _c(0x2e9e5b), _c(0x8a949e)
PAL = [_c(h) for h in (0x2d6fb3, 0x2e9e6a, 0xc77d1a, 0x7b4fb3, 0x1a9aa8, 0xb34f7b, 0x5a6b2e, 0x8a5a2e)]


def _P(q):
    """页面坐标 → 计算核心坐标"""
    return [q[0], -q[2], q[1]]


class _B:
    """按页面坐标写零件"""

    def __init__(self):
        self.out = []

    def box(self, name, zh, c, size, color):
        sx, sy, sz = size
        self.out.append(dict(type="box", name=name, zh=zh, size=[sx, sz, sy], base=[c[0] - sx / 2, -c[2] - sz / 2, c[1] - sy / 2], color=color))

    def cyl(self, name, zh, r, A, B, color):
        d = [B[i] - A[i] for i in range(3)]
        Ln = math.sqrt(sum(x * x for x in d)) or 1e-6
        self.out.append(dict(type="cyl", name=name, zh=zh, r=r, h=Ln, base=_P(A), dir=_P([x / Ln for x in d]), color=color))

    def disc(self, name, zh, r, th, c, ax, color):
        self.cyl(name, zh, r, [c[i] - ax[i] * th / 2 for i in range(3)], [c[i] + ax[i] * th / 2 for i in range(3)], color)

    def ball(self, name, zh, c, r, color):
        self.out.append(dict(type="sphere", name=name, zh=zh, c=_P(c), r=r, color=color))

    def tube(self, name, zh, pts, r, color):
        self.out.append(dict(type="tube", name=name, zh=zh, pts=[_P(q) for q in pts], r=r, color=color))

    def obox(self, name, zh, c, u, v, size, color, poly=None):
        """斜放的板：中心 c，板面两个方向 u、v（单位向量，页面坐标），尺寸 (a 沿 u, b 沿 v, t 厚)；poly 给出板面轮廓（u、v 坐标）就按它"""
        n = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]]
        a, b, t = size
        o = [c[i] - n[i] * t / 2 for i in range(3)]
        r = 0.6
        pts = poly or [(-a / 2, -b / 2), (a / 2, -b / 2), (a / 2, b / 2), (-a / 2, b / 2)]
        circles = [[x - math.copysign(r, x) if poly is None else x, y - math.copysign(r, y) if poly is None else y, r] for x, y in pts]
        self.out.append(dict(type="plate", name=name, zh=zh, circles=circles, t=t, holes=[], color=color,
                             frame=dict(o=_P(o), u=_P(u), v=_P(v), n=_P(n))))


def _key(machine, params):
    return machine, json.dumps(params or {}, sort_keys=True, ensure_ascii=False, default=str)


@lru_cache(maxsize=16)
def _cfg(machine, key):
    p = json.loads(key)
    if isinstance(p.get("_track"), str):                      # 讲解片场景里带的轨迹（压缩过的，见 video_track）：不用再算
        return unpack(p["_track"]), {k: v for k, v in p.items() if k != "_track"}
    from . import embroid, flatknit, pattern
    M = {"pattern": pattern, "embroid": embroid, "flatknit": flatknit}[machine]
    R = M.analyze(p)
    return R["view"]["cfg"], R["params"]


# ---------- 讲解片场景里带的轨迹 ----------
VIDEO_MAX = 800                 # 讲解片里最多这么多针 / 趟（多了等间隔抽样；出问题的那一针和它前一针一定留着，慢放时移动距离是真的）
FILE_KEYS = ("dst", "pts", "knit", "kpng")         # 上传的花样 / 意匠文件：不写进场景（太长），场景里带抽样后的轨迹
SERIES = {"pattern": ("idx", "pts", "sp", "cap", "mv"), "embroid": ("idx", "pts", "kind", "sp", "L", "acc", "col"),
          "flatknit": ("idx", "kind", "D", "v", "t", "row", "tacc")}
SPECIAL = {"pattern": ("worst", "far"), "embroid": ("worst", "over"), "flatknit": ("first_x", "widest")}


def video_track(machine, D, limit=VIDEO_MAX):
    """样机数据（proto）再抽样到 limit 以内，给讲解片用：出问题的那一针 / 那一趟和前一针都留着，下标改成抽样后的"""
    n = D["n"]
    ks = set()
    for k in SPECIAL[machine]:
        v = D.get(k)
        if v is not None:
            ks |= {v, max(0, v - 1)}
    keep = thin(n, limit, keep=tuple(sorted(ks)))
    out = {k: v for k, v in D.items() if k not in SERIES[machine] and k != "up" and k not in SPECIAL[machine]}
    for k in SERIES[machine]:
        v = D[k]
        out[k] = "".join(v[i] for i in keep) if isinstance(v, str) else [v[i] for i in keep]
    for k in SPECIAL[machine]:
        out[k] = keep.index(D[k]) if D.get(k) is not None else None
    if machine == "embroid":                                 # 抽样跳过了跳步、换色：这一段不画线（同 proto 的 up）
        up, prev = [], -1
        for i in keep:
            up.append(1 if (D["up"] and D["up"][i]) or any(D["kind"][q] != "s" for q in range(prev + 1, i)) else 0)
            prev = i
        out["up"] = up
    out["n"] = len(keep)
    return out


def pack(track):
    return base64.b64encode(zlib.compress(json.dumps(track, separators=(",", ":")).encode(), 9)).decode()


def unpack(s):
    return json.loads(zlib.decompress(base64.b64decode(s)))


def cfg_of(machine, params):
    """这台设计的样机数据（同三维样机）和整理后的参数"""
    return _cfg(*_key(machine, params))


def xN(f):
    """针杆曲柄滑块：离上止点下降量（mm，同 pattern.xN、模型 15-1 / 16-1）"""
    from .pattern import xN as _x
    return _x(f)


def _smooth(t):
    return 0.0 if t <= 0 else 1.0 if t >= 1 else t - math.sin(2 * math.pi * t) / (2 * math.pi)


def _trail(pts, keep, upto, at):
    """已缝的针迹：keep 里下标 ≤ upto 的点照原样，其余收到 at（当前针位）；末尾再加 at，抽样时针迹也正好接到针下。点数固定"""
    return [pts[k] if k <= upto else at for k in keep] + [at]


def parts_seq(params=None, phi=0.0, machine="pattern"):
    if machine == "pattern":
        return _parts_pattern(params, phi)
    if machine == "embroid":
        return _parts_embroid(params, phi)
    return _parts_flatknit(params, phi)


# ======================================================================== 花样机（模型 15-1）
def _parts_pattern(params=None, phi=0.0):
    D, p = cfg_of("pattern", params)
    n = D["n"]
    xs_, ys_ = [q[0] for q in D["pts"]], [q[1] for q in D["pts"]]
    cx, cy = (max(xs_) + min(xs_)) / 2, (max(ys_) + min(ys_)) / 2
    PTS = [(q[0] - cx, q[1] - cy) for q in D["pts"]]
    bw, bh = max(xs_) - min(xs_), max(ys_) - min(ys_)
    FW, FD = max(300.0, bw + 90), max(230.0, bh + 90)
    ENTER, LEAVE, MG = D["f1"], D["f2"], D["mg"]
    f = phi % 360
    base = max(0, min(n - 1, int(math.floor(phi / 360))))
    # 每圈一针：机针在布中（入布—出布）模板不动；出布后从 出布角 + 余量 起，用这一针的移动转角 mv 走到下一针（同模型 15-1）
    if f >= LEAVE:
        i0, i1, u = base, min(base + 1, n - 1), f - LEAVE - MG
    elif f < ENTER and base > 0:
        i0, i1, u = base - 1, base, f + 360 - LEAVE - MG
    else:
        i0 = i1 = base
        u = 1e9
    mv = max(1.0, D["mv"][i1])
    tau = max(0.0, min(1.0, u / mv))
    s = _smooth(tau)
    px, py = PTS[i0][0] + (PTS[i1][0] - PTS[i0][0]) * s, PTS[i0][1] + (PTS[i1][1] - PTS[i0][1]) * s
    X, Z = -px, py
    b = _B()
    # 台板、控制箱、底板、针板、旋梭
    b.box("PT_Table", "台板", [120, -80, 40], [1000, 30, 760], TABLE)
    b.box("PT_Control", "控制箱", [420, -195, 120], [260, 200, 200], DARK)
    b.box("PT_Bed", "底板", [200, -42, -10], [560, 46, 170], HOUSING)
    b.box("PT_Plate", "针板", [0, -18, 0], [60, 3, 60], STEEL)
    b.disc("PT_Hook", "旋梭", 26, 10, [0, -40, 0], [0, 0, 1], STEEL)
    # Y 轴：导轨、横梁（带 X 轴前后走）、电机、同步带
    for k, x in enumerate((-340, 340)):
        b.box(f"PT_YRail{k + 1}", "直线导轨", [x, -57, 60], [24, 16, 560], GREY)
        b.box(f"PT_YCar{k + 1}", "导轨滑块", [x, -53, 260 + Z], [46, 20, 60], _c(0x5d6670))
    b.box("PT_Beam", "Y 横梁", [0, -36, 260 + Z], [720, 26, 46], ALU)
    b.box("PT_YMotor", "Y 轴伺服电机", [390, -20, 380], [70, 70, 90], DARK)
    b.cyl("PT_YShaft", "Y 轴电机轴", 14, [320, -30, 380], [360, -30, 380], _c(0x9aa4ad))
    b.box("PT_YBelt", "Y 轴同步带", [312, -44, 60], [8, 4, 560], _c(0x22262b))
    # X 轴：电机、同步带、滑座（在横梁上，跟着 Y 走）
    b.box("PT_XMotor", "X 轴伺服电机", [-400, -30, 260 + Z], [70, 70, 80], DARK)
    b.cyl("PT_XShaft", "X 轴电机轴", 14, [-370, -30, 260 + Z], [-330, -30, 260 + Z], _c(0x9aa4ad))
    b.box("PT_XBelt", "X 轴同步带", [0, -20, 288 + Z], [700, 4, 10], _c(0x22262b))
    b.box("PT_XSlide", "X 滑座", [X, -12, 260 + Z], [110, 30, 70], ORANGE)
    # 压框、模板、布（跟着滑座走），气缸
    FR = _c(0x5d6670)
    b.box("PT_FrameF", "压框", [X, 6, Z + FD / 2], [FW, 10, 16], FR)
    b.box("PT_FrameB", "压框", [X, 6, Z - FD / 2], [FW, 10, 16], FR)
    b.box("PT_FrameR", "压框", [X + FW / 2, 6, Z], [16, 10, FD], FR)
    b.box("PT_FrameL", "压框", [X - FW / 2, 6, Z], [16, 10, FD], FR)
    b.box("PT_FrameArm", "压框连臂", [X, 6, Z + FD / 2 + 85], [40, 10, 170], FR)
    b.box("PT_TplLow", "下模板", [X, -1, Z], [FW - 30, 2, FD - 30], _c(0x9fcbe3))
    b.box("PT_Fabric", "布", [X, 0.6, Z], [FW - 60, 0.8, FD - 60], _c(0xe3cf9f))
    b.box("PT_TplUp", "上模板", [X, 2.2, Z], [FW - 30, 2, FD - 30], _c(0x9fcbe3))
    for k, x in enumerate((-110, 110)):
        b.cyl(f"PT_Cyl{k + 1}", "气缸", 12, [X + x, 10, Z - FD / 2 - 14], [X + x, 70, Z - FD / 2 - 14], _c(0xd6dbe0))
        b.cyl(f"PT_CylRod{k + 1}", "气缸杆", 4, [X + x, 70, Z - FD / 2 - 14], [X + x, 97, Z - FD / 2 - 14], STEEL)
    # 模板上的槽（花样路径，静止跟着模板）、已缝的针迹（一针一针长出来）
    ks = thin(n, 600)
    b.tube("PT_Slot", "模板槽", [[X + PTS[k][0], 3.3, Z - PTS[k][1]] for k in ks], 1.4, _c(0x2c4a6e))
    kt = thin(n, SEAM_MAX)
    at = PTS[base]
    b.tube("PT_Seam", "针迹", [[X + q[0], 3.9, Z - q[1]] for q in _trail(PTS, kt, base, at)], 0.7, _c(0x1d4c9e))
    # 机头（立柱、横臂、机头、主轴电机、操作面板）
    b.box("PT_Pillar", "立柱", [470, 120, -10], [110, 330, 120], HOUSING)
    b.box("PT_Arm", "横臂", [220, 240, -10], [560, 90, 110], HOUSING)
    b.box("PT_HeadFront", "机头", [-10, 160, -10], [120, 170, 120], HOUSING)
    b.cyl("PT_MainMotor", "主轴伺服电机", 48, [525, 240, -10], [635, 240, -10], DARK)
    b.box("PT_Panel", "操作面板", [240, 250, 52], [120, 80, 12], DARK)
    # 针杆、机针、中压脚（曲柄滑块，同第 3 章；针尖离针板 18 − xN）
    tipY = 18 - xN(f)
    b.cyl("PT_Needle", "机针", 0.9, [0, tipY, 0], [0, tipY + 38, 0], STEEL)
    b.cyl("PT_NeedleBar", "针杆", 6, [0, tipY + 38, 0], [0, tipY + 208, 0], BLUE)
    mpY = max(4.5, tipY + 6)
    b.disc("PT_Foot", "中压脚", 7, 3, [0, mpY, 0], [0, 1, 0], BLUE)
    b.cyl("PT_FootBar", "中压脚杆", 4, [8, mpY + 2, 0], [8, mpY + 122, 0], BLUE)
    inF = ENTER < f < LEAVE
    return dict(parts=b.out, phi=phi, params=p, idx=D["idx"][i1] + 1, i=i1, N=D["N"], n=n, sp=D["sp"][i1], cap=D["cap"][i1],
                needle=tipY, inF=inF, late=inF and tau < 1, px=px, py=py)


# ======================================================================== 刺绣机（模型 16-1）
EMB_HEADS = 4                   # 讲解片最多画 4 个机头（第 89 轮 Q3）


def _emb_runs(D):
    """针迹分段：同一颜色、中间没有跳步 / 换色 / 抽样跳过的连续针（同模型 16-1 的画线规则）"""
    runs, cur = [], None
    for i in range(1, D["n"]):
        if D["kind"][i] == "s" and D["kind"][i - 1] == "s" and not (D["up"] and D["up"][i]):
            c = D["col"][i] % len(PAL)
            if cur and cur[1] == i - 1 and cur[2] == c:
                cur[1] = i
            else:
                cur = [i - 1, i, c]
                runs.append(cur)
    return runs


def _parts_embroid(params=None, phi=0.0):
    D, p = cfg_of("embroid", params)
    n = D["n"]
    PTS = [tuple(q) for q in D["pts"]]
    HV = max(1, min(EMB_HEADS, int(D["H"]) or 1))
    PITCH = 420
    span = (HV - 1) * PITCH
    Lb = span + 700
    xs = [i * PITCH - span / 2 for i in range(HV)]
    hw = max(150.0, min(400.0, max(D["w"], D["h"]) + 80))
    FL, FD = span + hw + 200, hw + 140
    W = D["W"] or 204
    ws = 360 - W / 2
    f = phi % 360
    base = max(0, min(n - 1, int(math.floor(phi / 360))))
    # 窗口从 360 − W/2 开始，跨过上止点；走这一针要的转角 = W × √(所需 / 可用加速度)，比值 > 1 时针扎下后绷架还在动（同模型 16-1）
    if f >= ws:
        i0, i1, u = base, min(base + 1, n - 1), f - ws
    else:
        i0, i1, u = max(base - 1, 0), base, f + 360 - ws
    need = W * math.sqrt(max(1.0, D["acc"][i1] or 0))
    tau = max(0.0, min(1.0, u / need))
    s = _smooth(tau)
    px, py = PTS[i0][0] + (PTS[i1][0] - PTS[i0][0]) * s, PTS[i0][1] + (PTS[i1][1] - PTS[i0][1]) * s
    jump = D["kind"][i1] in "jc"
    tipY = 18 if jump else 18 - xN(f)
    b = _B()
    b.box("EM_Table", "台板", [0, -40, 60], [Lb + 500, 40, 900], TABLE)
    b.cyl("EM_LowerShaft", "下轴", 9, [-Lb / 2, -70, -20], [Lb / 2, -70, -20], _c(0xaeb7c0))
    b.box("EM_Beam", "横梁", [0, 430, -150], [Lb, 120, 160], HOUSING)
    b.cyl("EM_MainMotor", "主轴电机", 60, [Lb / 2 + 10, 430, -150], [Lb / 2 + 150, 430, -150], DARK)
    for h, x in enumerate(xs, 1):
        b.box(f"EM_Head{h}", f"机头 {h}", [x, 300, -10], [150, 260, 190], HOUSING)
        b.box(f"EM_Case{h}", f"针杆箱 {h}", [x, 250, 95], [170, 120, 70], HOUSING)
        for k in range(6):
            b.cyl(f"EM_IdleBar{h}_{k + 1}", "针杆（不用的）", 3, [x - 50 + k * 20, 205, 132], [x - 50 + k * 20, 295, 132], STEEL)
            b.cyl(f"EM_Cone{h}_{k + 1}", "线团", 11, [x - 62 + k * 25, 473, -20], [x - 62 + k * 25, 519, -20], PAL[k % len(PAL)])
        b.box(f"EM_Stand{h}", "线架", [x, 470, -20], [150, 6, 60], DARK)
        nx = x + 10
        b.cyl(f"EM_Needle{h}", f"机针 {h}", 0.9, [nx, tipY, 132], [nx, tipY + 36, 132], STEEL)
        b.cyl(f"EM_Bar{h}", f"针杆 {h}", 4.5, [nx, tipY + 36, 132], [nx, tipY + 186, 132], BLUE)
        b.disc(f"EM_Foot{h}", f"压脚 {h}", 7, 3, [nx, max(4, tipY + 5), 132], [0, 1, 0], BLUE)
        b.disc(f"EM_Hook{h}", f"旋梭 {h}", 24, 10, [nx, -20, 132], [0, 0, 1], STEEL)
    # 绷架（两根长梁、两根横梁，每头一个绣框和一块布），跟着 X、Y 走：框上的点 (px, py) 到针下
    X, Z = -px, py
    FR = _c(0x5d6670)
    b.box("EM_FrameF", "绷架", [X, 0, Z + 132 + FD / 2], [FL, 24, 30], FR)
    b.box("EM_FrameB", "绷架", [X, 0, Z + 132 - FD / 2], [FL, 24, 30], FR)
    b.box("EM_FrameR", "绷架", [X + FL / 2, 0, Z + 132], [30, 24, FD], FR)
    b.box("EM_FrameL", "绷架", [X - FL / 2, 0, Z + 132], [30, 24, FD], FR)
    runs = _emb_runs(D)
    # 每段的点数：总共不超过 SEAM_MAX / 头数
    budget = max(40, SEAM_MAX // HV)
    tot = sum(r[1] - r[0] + 1 for r in runs) or 1
    for h, x in enumerate(xs, 1):
        cx_, cz = X + x + 10, Z + 132
        ring = [[cx_ + hw / 2 * math.cos(2 * math.pi * k / 48), 8, cz + hw / 2 * math.sin(2 * math.pi * k / 48)] for k in range(49)]
        b.tube(f"EM_Hoop{h}", f"绣框 {h}", ring, 6, _c(0xd8c7a0))
        b.disc(f"EM_Cloth{h}", f"绣布 {h}", hw / 2 - 2, 1, [cx_, 6, cz], [0, 1, 0], _c(0xf3efe6))
        for r, (a, z_, c) in enumerate(runs, 1):
            idx = list(range(a, z_ + 1))
            lim = max(6, round(budget * len(idx) / tot))
            kk = [idx[j] for j in thin(len(idx), lim)]
            at = PTS[min(max(base, a), z_)]
            b.tube(f"EM_Seam{h}_{r}", f"针迹 {h}（第 {c + 1} 色）", [[cx_ + q[0], 7.4, cz - q[1]] for q in _trail(PTS, kk, base, at)], 0.6, PAL[c])
    for k, x in enumerate((-FL / 2 - 60, FL / 2 + 60)):
        b.box(f"EM_Rail{k + 1}", "导轨", [x, -30, 132], [26, 16, FD + 500], GREY)
    b.box("EM_XMotor", "X 轴电机", [-FL / 2 - 120, 40, 132], [80, 80, 90], DARK)
    b.box("EM_XBelt", "X 轴同步带", [-60, 20, 72 - FD / 2], [FL, 4, 10], _c(0x22262b))
    b.box("EM_YMotor", "Y 轴电机", [FL / 2 + 160, 40, 0], [80, 80, 90], DARK)
    b.box("EM_YBelt", "Y 轴同步带", [FL / 2 + 160, 20, 0], [8, 4, 600], _c(0x22262b))
    inF = (not jump) and W / 2 < f < 360 - W / 2
    return dict(parts=b.out, phi=phi, params=p, idx=D["idx"][i1] + 1, i=i1, N=D["N"], n=n, sp=D["sp"][i1], col=D["col"][i1] + 1,
                acc=D["acc"][i1], need=round((D["acc"][i1] or 0) * D["am"], 2), am=D["am"], needle=tipY, inF=inF, late=inF and tau < 1,
                heads=HV, H=int(D["H"]), px=px, py=py, jump=jump)


# ======================================================================== 横机（模型 17-1）
FK_N, FK_PV, FK_S0, FK_CW = 40, 12.0, 10.0, 170.0
FK_ANG = 40 * D2R


def _bed(side, x, y, z):
    """针床局部坐标 → 页面坐标：x 沿针床、z 从针床口往下坡、y 高出针床面；side = +1 前床、−1 后床（同模型 17-1 的 bedFrame）"""
    ca, sa = math.cos(FK_ANG), math.sin(FK_ANG)
    Y, Z = y * ca - z * sa, y * sa + z * ca
    return [x, Y, Z] if side > 0 else [-x, Y, -Z]


def _bed_axes(side):
    u = [1.0, 0.0, 0.0] if side > 0 else [-1.0, 0.0, 0.0]
    return u, _bed(side, 0, 0, 1), _bed(side, 0, 1, 0)           # 沿针床、下坡、法向


def _sm(a, b, u):
    t = min(1.0, max(0.0, (u - a) / (b - a)))
    return t * t * (3 - 2 * t)


def _profile(u, lvl):
    """机头中心经过时针往针床口伸出多少（mm）：lvl 0 不动、1 集圈、2 编织（同模型 17-1）"""
    if not lvl:
        return 0.0
    top = 36 if lvl == 2 else 20
    return top * _sm(-70, -15, u) * (1 - _sm(15, 45, u)) - 10 * _sm(20, 45, u) * (1 - _sm(55, 75, u))


def pass_pos(D, j, tt):
    """第 j 趟开始后 tt 秒：机头离起点多远（mm）、速度（m/s）——加速、匀速、减速（同 flatknit.profile、模型 17-1）"""
    Dm, v, a = D["D"][j] / 1000, D["v"][j], D["a"]
    vp = min(v, math.sqrt(a * Dm))
    ta = vp / a
    tc = max(0.0, (Dm - vp * vp / a) / vp) if vp > 0 else 0.0
    tm = 2 * ta + tc
    if tt <= 0:
        return 0.0, 0.0
    if tt >= tm:
        return D["D"][j], 0.0
    if tt < ta:
        return 0.5 * a * tt * tt * 1000, a * tt
    if tt < ta + tc:
        return (0.5 * a * ta * ta + vp * (tt - ta)) * 1000, vp
    u = tm - tt
    return D["D"][j] - 0.5 * a * u * u * 1000, a * u


def pass_top(D, j):
    """这一趟实际达到的最高速度（m/s）：行程短时加速不到设定速度"""
    return min(D["v"][j], math.sqrt(D["a"] * D["D"][j] / 1000))


def _parts_flatknit(params=None, phi=0.0):
    D, p = cfg_of("flatknit", params)
    n = D["n"]
    N, PV, S0, CW = FK_N, FK_PV, FK_S0, FK_CW
    L = N * PV + 80
    kx = L / (D["B"] or L)                                       # 针床有效宽 B（mm）↔ 画面上的针床长 L
    j = max(0, min(n - 1, int(math.floor(phi / 360))))
    fr = (phi % 360) / 360
    kw = D["kw"] or 1
    tj = D["t"][j] / kw                                          # 一趟的真实用时（全成型的倍数只算总时间）
    tt = fr * tj
    dirj = -1 if j % 2 else 1
    s_, v_ = pass_pos(D, j, tt)
    Dv = D["D"][j] * kx
    xc = dirj * (-Dv / 2 + s_ * kx)
    k = D["kind"][j]
    rack = max(0, min(4, D["rack"] or 0)) if k == "x" else 0
    rackT = rack * _sm(0.0, 0.12, fr) * (1 - _sm(0.88, 1.0, fr))
    nsys = max(1, min(4, round(D["sys"] or 1)))
    b = _B()
    # 针床（前、后，斜 40°）、针
    for side, nm, zh in ((1, "F", "前针床"), (-1, "B", "后针床")):
        u, dn, nr = _bed_axes(side)
        sh = rackT * PV if side < 0 else 0.0                     # 摇床：后针床横移
        c = _bed(side, 0, -20, S0 + 100)
        c[0] += sh
        b.obox(f"FK_Bed{nm}", zh, [c[0], c[1], c[2]], u, dn, (L, 200, 40), _c(0xb8c0c8))
        for i in range(N):
            xi = (i - (N - 1) / 2) * PV                         # 世界 x（后床的局部 x 反向，_bed 里再反回来）
            uu = dirj * (xi + sh - xc)
            lv = 0 if k == "e" else ((1 if side > 0 else 0) if k == "x" else (2 if (i % 2 == 0) == (side > 0) else 0))
            ext = _profile(uu, lv)
            A = _bed(side, side * xi, 2, S0 - ext)
            B_ = _bed(side, side * xi, 2, S0 + 120 - ext)
            A[0] += sh
            B_[0] += sh
            b.cyl(f"FK_Needle{nm}{i + 1}", f"{zh}针 {i + 1}", 1.5, A, B_, _c(0xe3e7ea))
            bt = _bed(side, side * xi, 3, S0 + 80 - ext)
            bt2 = _bed(side, side * xi, 14, S0 + 80 - ext)
            bt[0] += sh
            bt2[0] += sh
            b.cyl(f"FK_Butt{nm}{i + 1}", "针踵", 1.5, bt, bt2, GREY)
    # 机头：几个系统就几套三角（同模型 17-1），跟着机头走
    for side, nm in ((1, "F"), (-1, "B")):
        u, dn, nr = _bed_axes(side)
        for s in range(nsys):
            ox = xc + (s - (nsys - 1) / 2) * CW
            lx = (ox if side > 0 else -ox)                       # 后床的局部 x 反向
            c = _bed(side, lx, 40, S0 + 95)
            b.obox(f"FK_CamPlate{nm}{s + 1}", "三角座", c, u, dn, (CW, 190, 14), _c(0x4b5560))
            c = _bed(side, lx, 58, S0 + 200)
            b.obox(f"FK_Rib{nm}{s + 1}", "三角座外沿", c, u, dn, (CW - 20, 30, 22), _c(0x4b5560))
            c = _bed(side, lx, 28, S0 + 105)
            b.obox(f"FK_Cam{nm}{s + 1}", "起针三角", c, u, dn, (0, 0, 10), _c(0x2a3038), poly=[(48, 0), (0, -49.5), (-16, -49.5), (-24, 0)])
            c = _bed(side, lx - 20 * side, 60, S0 + 168)
            b.obox(f"FK_Sel{nm}{s + 1}", "电磁选针器", c, u, dn, (70, 30, 26), _c(0x1d2228))
    b.box("FK_Bridge", "机头桥架", [xc, 150, 0], [(CW + 10) * nsys, 24, 40], _c(0x4b5560))
    b.box("FK_Web", "机头立板", [xc, 95, 0], [CW + 10, 110, 20], _c(0x4b5560))
    # 纱嘴导轨、纱嘴、纱线
    b.box("FK_RailA", "纱嘴导轨", [0, 190, -22], [L + 120, 10, 14], GREY)
    b.box("FK_RailB", "纱嘴导轨", [0, 190, 22], [L + 120, 10, 14], GREY)
    cx_ = xc - dirj * 40
    b.box("FK_Carrier", "纱嘴", [cx_, 175, 0], [26, 26, 22], ORANGE)
    b.cyl("FK_CarrierRod", "纱嘴杆", 2.2, [cx_, 15, 0], [cx_, 165, 0], ORANGE)
    lo_ = max(-N * PV / 2, min(N * PV / 2, xc - dirj * 90))
    b.tube("FK_Yarn", "纱线", [[cx_, 250, 0], [cx_, 170, 0], [cx_, 16, 0], [lo_, 2, 0]], 0.9, BLUE)
    # 织物（往下长：已织趟数 / 总趟数）、牵拉辊
    done = (D["tacc"][j] - D["t"][j] * (1 - fr)) / max(1e-9, D["tacc"][-1])
    fw = max(40.0, min(N * PV, (D["W"] or 0) * kx))
    fh = 40 + 260 * max(0.0, min(1.0, done))
    b.box("FK_Fabric", "织物", [0, -12 - fh / 2, 0], [fw, fh, 2], _c(0xe7d3a0))
    for k_, z in enumerate((-22, 22)):
        b.cyl(f"FK_Roller{k_ + 1}", "牵拉辊", 18, [-L / 2 - 20, -330, z], [L / 2 + 20, -330, z], _c(0xb0b8c0))
    # 机头驱动：电机、同步带、带夹
    b.cyl("FK_Motor", "机头电机", 36, [-L / 2 - 120, 170, -195], [-L / 2 - 120, 170, -105], _c(0x2a3038))
    b.box("FK_Belt", "同步带", [0, 175, -110], [L + 200, 4, 12], _c(0x22262b))
    b.box("FK_Clamp", "带夹", [xc, 170, -90], [30, 20, 40], _c(0x6b7682))
    for s_side in (-1, 1):
        b.box(f"FK_Wall{'LR'[(s_side + 1) // 2]}", "机架侧板", [s_side * (L / 2 + 160), -170, 0], [30, 260, 460], _c(0xd9d6cd))
    return dict(parts=b.out, phi=phi, params=p, idx=D["idx"][j] + 1, i=j, N=D["N"], n=n, kind=k, v=v_, top=pass_top(D, j),
                x=s_ if dirj > 0 else D["D"][j] - s_, tacc=D["tacc"][j] - D["t"][j] + min(fr * D["t"][j], D["t"][j]), rack=rack,
                sys=nsys, kw=kw)


# 零件名前缀 → 机构（三维讲解片透视、慢放用；cad.group_of 也查这张表）
PREFIX = (
    ("PT_Hook", "hook"), ("PT_YRail", "y"), ("PT_YCar", "y"), ("PT_Beam", "y"), ("PT_YMotor", "y"), ("PT_YShaft", "y"), ("PT_YBelt", "y"),
    ("PT_X", "x"), ("PT_Frame", "tpl"), ("PT_Tpl", "tpl"), ("PT_Fabric", "tpl"), ("PT_Cyl", "tpl"), ("PT_Slot", "tpl"), ("PT_Seam", "stitch"),
    ("PT_Pillar", "head"), ("PT_Arm", "head"), ("PT_HeadFront", "head"), ("PT_MainMotor", "head"), ("PT_Panel", "head"),
    ("PT_Needle", "needle"), ("PT_Foot", "needle"),
    ("EM_Beam", "head"), ("EM_MainMotor", "head"), ("EM_Head", "head"), ("EM_Case", "head"), ("EM_IdleBar", "head"), ("EM_Cone", "head"),
    ("EM_Stand", "head"), ("EM_Needle", "needle"), ("EM_Bar", "needle"), ("EM_Foot", "needle"), ("EM_Hook", "hook"),
    ("EM_Frame", "hoop"), ("EM_Hoop", "hoop"), ("EM_Cloth", "hoop"), ("EM_Seam", "stitch"), ("EM_X", "x"), ("EM_Y", "y"),
    ("FK_Bed", "bed"), ("FK_Needle", "needles"), ("FK_Butt", "needles"), ("FK_CamPlate", "carriage"), ("FK_Rib", "carriage"),
    ("FK_Cam", "carriage"), ("FK_Sel", "carriage"), ("FK_Bridge", "carriage"), ("FK_Web", "carriage"), ("FK_Rail", "yarn"),
    ("FK_Carrier", "yarn"), ("FK_Yarn", "yarn"), ("FK_Fabric", "fabric"), ("FK_Roller", "fabric"), ("FK_Motor", "drive"),
    ("FK_Belt", "drive"), ("FK_Clamp", "drive"),
)
