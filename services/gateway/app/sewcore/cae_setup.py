# -*- coding: utf-8 -*-
"""送 CAE 之前的准备（第 41 轮）：把一个设计里的关键零件变成数字工厂计算服务认得的任务。

- 有限元：零件单独生成 STEP（与导出的三维模型同一份几何），按孔的位置找到 STEP 里对应的圆柱面，
  轴孔加支承、销孔加力；力取本软件算出的一转内受力最大的时刻，一转的受力曲线作疲劳载荷谱（每转一个“块”）。
- 动力学：刺布 / 引针曲柄滑块用数字工厂零件库的曲柄滑块机构（C-LNK-SLIDER），针杆组件质量作滑块上的负载。
- 解析对照：本软件公式算出的同一个量（连杆力、主轴转矩），用来核对 CAE 的结果。
只用标准库和本包的其他模块；生成 STEP 要 build123d（网关镜像里有）。
"""
import math

from . import cad
from .machines import get

DEG = math.pi / 180
HOURS_PER_YEAR = 16 * 300        # 每天开机 16 小时、每年 300 天

PARTS = {
    "lockstitch": [("ConnectingRod", "针杆连杆", "Needle-bar connecting rod"), ("NeedleCrank", "针杆曲柄", "Needle-bar crank")],
    "overlock": [("OL_NeedleRod", "引针连杆", "Needle drive connecting rod"), ("OL_NeedleCrank", "引针曲柄", "Needle drive crank"),
                 ("LL_Rocker", "下弯针摆杆", "Lower looper rocker")],
    "cover": [],
}


def parts(machine):
    return [dict(key=k, zh=zh, en=en) for k, zh, en in PARTS.get(machine, [])]


# ---------- 刺布（引针）曲柄滑块：连杆轴向力 ----------
def _slider(p, f, n, mr):
    """连杆受拉为正（N）。x 自上止点向下为正；滑块需要的力 = mr·a（向下为正），连杆竖直分力向上为正。"""
    r, l = p["r"], p["l"]
    lam = r / l
    a = f * DEG
    w = 2 * math.pi * n / 60
    S = math.sqrt(1 - (lam * math.sin(a)) ** 2)
    acc = r / 1000 * w * w * (math.cos(a) - lam * (math.cos(2 * a) + lam ** 2 * math.sin(a) ** 4) / S ** 3)
    return -mr * acc / S


def _slider_vel(p, f, n):
    r, l = p["r"], p["l"]
    lam = r / l
    a = f * DEG
    w = 2 * math.pi * n / 60
    S = math.sqrt(1 - (lam * math.sin(a)) ** 2)
    return w * r / 1000 * math.sin(a) * (1 - lam * math.cos(a) / S)


def rod_series(p, n, mr):
    return [_slider(p, f, n, mr) for f in range(360)]


# ---------- 下弯针 RSSR：球头连杆力 ----------
def _rssr_link_series(p, n):
    from . import overlock as O
    R = O.rssr(p["ll_r"], p["ll_b"], p["ll_c"], O.LL, n)
    if R["fail"]:
        return None
    w = 2 * math.pi * n / 60
    th = R["th"]
    J = p["ll_J"] * 1e-7                                  # g·cm² → kg·m²
    out = []
    for f in range(360):
        d2 = (th[(f + 1) % 360] - 2 * th[f] + th[(f - 1) % 360])
        # 跨过 ±π 的展开在 rssr() 里已处理；首尾相接处再修一次
        while d2 > math.pi:
            d2 -= 2 * math.pi
        while d2 < -math.pi:
            d2 += 2 * math.pi
        thdd = d2 / (DEG * DEG) * w * w                    # rad/s²
        P = O.rssr_pose(p["ll_r"], p["ll_b"], p["ll_c"], O.LL, f)
        A, B, Q, e = P["A"], P["B"], P["Q"], P["e"]
        d = [A[i] - B[i] for i in range(3)]
        L = math.sqrt(sum(x * x for x in d))
        d = [x / L for x in d]
        rb = [(B[i] - Q[i]) / 1000 for i in range(3)]
        cr = (rb[1] * d[2] - rb[2] * d[1], rb[2] * d[0] - rb[0] * d[2], rb[0] * d[1] - rb[1] * d[0])
        arm = sum(cr[i] * e[i] for i in range(3))
        out.append(dict(force=(J * thdd / arm) if abs(arm) > 1e-9 else 0.0, dir=d, thdd=thdd))
    return out


def _desc(model, name):
    return next(d for d in model["parts"] if d["name"] == name)


def _holes3d(d):
    fr = cad._frame(d)
    return [dict(center=list(cad._P(fr, a, b, d["t"] / 2)), axis=list(fr[3]), r=r) for a, b, r in d["holes"]]


def fea_case(machine, params, part):
    """返回 None（这个机型没有这个零件）或任务说明：零件描述、支承孔、受力孔、力向量、一转的载荷谱"""
    if part not in [k for k, _, _ in PARTS.get(machine, [])]:
        return None
    M = get(machine)
    p = M.clean(params)
    n = p["n"]
    if part in ("ConnectingRod", "NeedleCrank", "OL_NeedleRod", "OL_NeedleCrank"):
        ser = rod_series(p, n, p["mr"])
        f0 = max(range(360), key=lambda f: abs(ser[f]))
        model = cad.parts3d(p, f0, machine)
        rod = _desc(model, "ConnectingRod" if machine == "lockstitch" else "OL_NeedleRod")
        pin, joint = _holes3d(rod)[:2]
        u = [joint["center"][i] - pin["center"][i] for i in range(3)]
        L = math.sqrt(sum(x * x for x in u))
        u = [x / L for x in u]
        T = ser[f0]
        if part in ("ConnectingRod", "OL_NeedleRod"):
            d = rod
            support, load = pin, joint
            vec = [T * x for x in u]                      # 受拉：销孔这一端被往外拉
        else:
            d = _desc(model, part)
            shaft, cpin = _holes3d(d)[:2]
            support, load = shaft, cpin
            vec = [T * x for x in u]                      # 连杆受拉时把曲柄销拉向针杆
        return dict(machine=machine, part=part, phi=f0, descriptor=d, support=support, load=load, vector_n=[round(v, 3) for v in vec],
                    ref_load=round(T, 3), series=[round(v, 3) for v in ser], block_seconds=60.0 / n, n=n,
                    analytic=dict(zh="连杆轴向力（本软件公式）", en="Rod axial force (this software's formula)", value=round(T, 1), unit="N"))
    if part == "LL_Rocker" and machine == "overlock":
        S = _rssr_link_series(p, n)
        if S is None:
            return None
        f0 = max(range(360), key=lambda f: abs(S[f]["force"]))
        model = cad.parts3d(p, f0, machine)
        d = _desc(model, "LL_Rocker")
        hub, ball = _holes3d(d)[:2]
        F = S[f0]["force"]
        vec = [F * x for x in S[f0]["dir"]]
        return dict(machine=machine, part=part, phi=f0, descriptor=d, support=hub, load=ball, vector_n=[round(v, 3) for v in vec],
                    ref_load=round(F, 3), series=[round(s["force"], 3) for s in S], block_seconds=60.0 / n, n=n,
                    analytic=dict(zh="球头连杆力（本软件公式）", en="Ball-link force (this software's formula)", value=round(F, 1), unit="N"))
    return None


def part_step(descriptor):
    """单个零件的 STEP（build123d）；没有 build123d 返回 None"""
    try:
        import build123d as bd
    except Exception:
        return None
    import os
    import tempfile
    s = cad._bd_solid(bd, descriptor)
    with tempfile.TemporaryDirectory() as t:
        path = os.path.join(t, "part.step")
        bd.export_step(s, path)
        with open(path, "rb") as f:
            return f.read()


def match_face(faces, hole, tol=0.35):
    """STEP 面清单里与这个孔对应的圆柱面编号"""
    out = []
    c, a = hole["center"], hole["axis"]
    for f in faces:
        if f.get("kind") != "cylinder" or "axis" not in f or "radius_mm" not in f:
            continue
        if abs(f["radius_mm"] - hole["r"]) > 0.15:
            continue
        ax = f["axis"]
        if abs(sum(ax[i] * a[i] for i in range(3))) < 0.98:
            continue
        o = f["axis_origin"]
        w = [c[i] - o[i] for i in range(3)]
        t = sum(w[i] * ax[i] for i in range(3))
        dist = math.sqrt(max(0.0, sum(x * x for x in w) - t * t))
        if dist < tol:
            out.append(f["id"])
    return out


def fea_setup(case, faces, material_id, mesh_mm=None):
    sf = match_face(faces, case["support"])
    lf = match_face(faces, case["load"])
    if not sf or not lf:
        raise ValueError("在零件模型里没找到轴孔或销孔")
    d = case["descriptor"]
    size = mesh_mm or max(0.8, min(2.5, d["t"] / 3))
    sup = case["support"]
    return {"material_id": material_id, "mesh": {"size_mm": round(size, 2)},
            "loads": [{"type": "cyl_support", "faces": sf, "dofs": ["radial", "tangential", "axial"],
                       "axis": {"origin": sup["center"], "dir": sup["axis"]}},
                      {"type": "force", "faces": lf, "vector_n": case["vector_n"]}]}


def frame_setup(faces):
    """机壳模态：底面（最低的水平平面）固定；顶面加 1 N（计算服务要求至少一个载荷，对固有频率没有影响）"""
    planes = [f for f in faces if f.get("kind") == "plane" and abs((f.get("normal") or [0, 0, 0])[2]) > 0.95]
    if not planes:
        raise ValueError("机壳模型里没有水平的底面")
    zmin = min(f["center"][2] for f in planes)
    zmax = max(f["center"][2] for f in planes)
    bottom = [f["id"] for f in planes if f["center"][2] < zmin + 0.5]
    top = [f["id"] for f in planes if f["center"][2] > zmax - 0.5 and f["id"] not in bottom]
    if not top:
        raise ValueError("机壳模型太扁，找不到顶面")
    return {"loads": [{"type": "fixed", "faces": bottom}, {"type": "force", "faces": top[:1], "vector_n": [0, 0, -1]}]}


# ---------- 动力学 ----------
N_SIM = 30.0     # r/min：计算服务每秒最多记 200 个点，高速时一转只有两三个点；按低速算、再按转速平方换算（纯惯性载荷、不计重力时精确成立）


def mbd_spec(machine, params, revs=3):
    M = get(machine)
    p = M.clean(params)
    if machine not in ("lockstitch", "overlock"):
        return None
    n = p["n"]
    w = 2 * math.pi * N_SIM / 60
    return {"model": {"source": "mech", "id": "C-LNK-SLIDER",
                      "params": {"crank_m": p["r"] / 1000, "rod_m": p["l"] / 1000, "offset_m": 0.0,
                                 "link_width_m": 0.002, "link_thickness_m": 0.001}},     # 杆件取得很轻：只核针杆组件的惯性
            "setup": {"duration_s": round(revs * 60 / N_SIM, 3), "gravity": False, "sample_hz": 200,
                      "drives": [{"joint": "crank", "kind": "speed", "value": round(w, 5)}],
                      "payloads": [{"body": "slider", "mass": p["mr"]}]},
            "scale": (n / N_SIM) ** 2, "n_sim": N_SIM,
            "analytic_torque_peak": analytic_torque_peak(p, n, p["mr"])}


def analytic_torque_peak(p, n, mr):
    """刺布机构所需的主轴转矩峰值（N·m）：T = F_滑块 · v / ω（只算针杆组件的惯性，忽略连杆和曲柄自身质量）"""
    w = 2 * math.pi * n / 60
    best = 0.0
    for f in range(360):
        r, l = p["r"], p["l"]
        lam = r / l
        a = f * DEG
        S = math.sqrt(1 - (lam * math.sin(a)) ** 2)
        acc = r / 1000 * w * w * (math.cos(a) - lam * (math.cos(2 * a) + lam ** 2 * math.sin(a) ** 4) / S ** 3)
        best = max(best, abs(mr * acc * _slider_vel(p, f, n) / w))
    return best


def spindle_torque(machine, params):
    """主轴转矩（N·m）一转的曲线：本软件各机构惯性力的虚功 + 缝纫阻力矩。平缝机算刺布、挑线、送布；包缝机算引针与两套弯针。"""
    M = get(machine)
    p = M.clean(params)
    n = p["n"]
    w = 2 * math.pi * n / 60
    out = []
    if machine == "lockstitch":
        mech = M.mech_of(p)
        Fd = mech.feed_model(fab=p["fab"], mode=p["mode"], s=p["s"], dT=p["dT"], dP=p["dP"], h=p["h"], P=p["P"])
        mt, mf = 0.025, 0.05                       # 挑线杆、送布牙组件质量（与教材第 8 讲整机惯性力同一组值）

        def pos(f):
            c = mech.link_com(f)                    # m
            return c, (Fd["X"](f) / 1000, Fd["Y"](f) / 1000)
        E = []
        h = 0.5
        for f in range(360):
            v = _slider_vel(p, f, n)
            (c0, d0), (c1, d1) = pos(f - h), pos(f + h)
            k = w / (2 * h * DEG)
            vt2 = ((c1[0] - c0[0]) * k) ** 2 + ((c1[1] - c0[1]) * k) ** 2
            vf2 = ((d1[0] - d0[0]) * k) ** 2 + ((d1[1] - d0[1]) * k) ** 2
            E.append(0.5 * p["mr"] * v * v + 0.5 * mt * vt2 + 0.5 * mf * vf2)
        for f in range(360):
            out.append((E[(f + 1) % 360] - E[(f - 1) % 360]) / (2 * DEG) + p["T_sew"])
    elif machine == "overlock":
        from . import overlock as O
        Ls = O.rssr(p["ll_r"], p["ll_b"], p["ll_c"], O.LL, n)
        J = p["ll_J"] * 1e-7
        E = []
        for f in range(360):
            v = _slider_vel(p, f, n)
            th_d = Ls["thd"][f] if not Ls["fail"] and Ls["thd"][f] is not None else 0.0
            E.append(0.5 * p["mr"] * v * v + 0.5 * J * th_d * th_d)
        for f in range(360):
            out.append((E[(f + 1) % 360] - E[(f - 1) % 360]) / (2 * DEG) + p["T_sew"])
    else:
        return None
    return out


def select_motor(T, n, motors, safety=1.2):
    """直驱主轴伺服：峰值转矩 × 安全系数 ≤ 电机峰值；均方根 × 安全系数 ≤ 额定；最高转速 ≥ 转速"""
    peak = max(abs(x) for x in T)
    rms = math.sqrt(sum(x * x for x in T) / len(T))
    rows = []
    for m in motors:
        ok = peak * safety <= m["peak_nm"] and rms * safety <= m["rated_nm"] and m["max_rpm"] >= n
        rows.append(dict(m, ok=ok, peak_use=peak / m["peak_nm"], rms_use=rms / m["rated_nm"]))
    pick = next((r for r in rows if r["ok"]), None)
    return dict(peak_nm=peak, rms_nm=rms, n=n, power_w=rms * 2 * math.pi * n / 60, pick=pick, rows=rows, safety=safety)


def life_years(summary):
    if summary.get("infinite"):
        return float("inf")
    h = summary.get("life_hours")
    return None if h is None else h / HOURS_PER_YEAR


# ---------- 拓扑优化（两孔平板）、数控编程（第 41 轮第二批） ----------
FLAT_FRAME = {"o": [0.0, 0.0, 0.0], "u": [1.0, 0.0, 0.0], "v": [0.0, 1.0, 0.0], "n": [0.0, 0.0, 1.0]}


def _center(d):
    """零件外形（几个圆的凸包）的外接矩形中心，平面坐标"""
    pts = cad.outline(d["circles"], seg=32)
    return ((min(x for x, _ in pts) + max(x for x, _ in pts)) / 2, (min(y for _, y in pts) + max(y for _, y in pts)) / 2)


def flat(d):
    """零件放平：平面坐标 (a, b) → (x − 中心, y − 中心)，厚度沿 z 从 −t 到 0——上表面在 Z0、外形中心在 X0 Y0（数控的工件零点；
    上表面不在 Z0 时试切报“快移撞到工件”，零件离原点远时报“超程”）。拓扑优化的结果也在这个坐标里"""
    cx, cy = _center(d)
    q = dict(d, frame=dict(FLAT_FRAME, o=[-cx, -cy, -float(d["t"])]))
    q.pop("y0", None)
    return q


def _local(fr, v):
    _, u, w, _ = fr
    return [sum(v[i] * u[i] for i in range(3)), sum(v[i] * w[i] for i in range(3))]


def topo_case(machine, params, part, volfrac=0.5):
    """同 fea_case 的零件和受力，换成平板坐标：设计区域 = 现在的外形（几个圆的凸包），圆（毂、平衡块）保留实心，
    第一个孔支承、第二个孔受力（与 fea_case 的支承孔、受力孔同一对）。拓扑优化是平面的，只用力在板面内的分量；
    有限元复核用完整的力（包缝机球头连杆的力有垂直于板面的分量）"""
    case = fea_case(machine, params, part)
    if not case:
        return None
    d = case["descriptor"]
    fr = cad._frame(d)
    cx, cy = _center(d)
    sh = lambda c: [float(c[0]) - cx, float(c[1]) - cy] + [float(v) for v in c[2:]]  # noqa: E731
    holes = [sh(h) for h in d["holes"]]
    f2 = _local(fr, case["vector_n"])
    dom = [sh(q) for q in cad.outline(d["circles"], seg=64)]
    area0 = _area(dom) - sum(math.pi * r * r for _, _, r in holes)
    plate = {"domain": dom, "solid": [sh(c) for c in d["circles"]], "holes": holes,
             "support": holes[0], "load": {"at": holes[1], "f": [round(f2[0], 3), round(f2[1], 3)]}, "thickness_mm": float(d["t"])}
    t = float(d["t"])
    fn = sum(case["vector_n"][i] * fr[3][i] for i in range(3))          # 垂直于板面的分量：平面拓扑优化管不到，有限元复核要算上
    fl = dict(case, descriptor=flat(d), vector_n=[round(f2[0], 3), round(f2[1], 3), round(fn, 3)],
              support=dict(center=[holes[0][0], holes[0][1], -t / 2], axis=[0.0, 0.0, 1.0], r=holes[0][2]),
              load=dict(center=[holes[1][0], holes[1][1], -t / 2], axis=[0.0, 0.0, 1.0], r=holes[1][2]))
    return {"spec": {"plate": plate, "volfrac": float(volfrac)}, "case": fl, "area0": area0}


def _area(pts):
    return abs(sum(pts[i][0] * pts[i - 1][1] - pts[i - 1][0] * pts[i][1] for i in range(len(pts)))) / 2


CAM_EN = {"NeedleCrank": "Needle crank", "ConnectingRod": "Needle-bar link", "TakeupCrank": "Take-up crank", "TakeupLever": "Take-up lever",
          "TakeupRocker": "Take-up rocker", "LiftEccentric": "Lift eccentric", "FeedEccentric": "Feed eccentric",
          "OL_NeedleCrank": "Needle crank", "OL_NeedleRod": "Needle link", "LL_Eccentric": "Lower-looper eccentric", "LL_Rocker": "Lower-looper rocker",
          "LL_Looper": "Lower looper", "UL_Eccentric": "Upper-looper eccentric", "UL_Rocker": "Upper-looper rocker",
          "FeedArmMain": "Main feed arm", "FeedArmDiff": "Differential feed arm"}


def cam_parts(machine):
    """可以出铣削程序的平板零件（本软件三维模型里的平板件；旋梭不是板件，不算；绷缝机没有三维零件）"""
    if machine not in ("lockstitch", "overlock"):
        return []
    model = cad.parts3d({}, 0.0, machine)
    return [dict(key=d["name"], zh=d["zh"], en=CAM_EN.get(d["name"], d["name"])) for d in model["parts"]
            if d["type"] == "plate" and d["name"] in CAM_EN]


def cam_desc(machine, params, part):
    if machine not in ("lockstitch", "overlock") or part not in CAM_EN:
        return None
    model = cad.parts3d(get(machine).clean(params), 0.0, machine)
    d = next((x for x in model["parts"] if x["type"] == "plate" and x["name"] == part), None)
    return flat(d) if d else None


def outline_dxf(outer, inner, holes, name, t):
    """拓扑优化后的零件轮廓 → DXF（R12，mm）：外轮廓、减重孔用多段线，安装孔用整圆"""
    ents = []

    def poly(pts):
        for (ax, ay), (bx, by) in zip(pts, pts[1:] + pts[:1]):
            ents.extend(["0", "LINE", "8", name, "10", f"{ax:.4f}", "20", f"{ay:.4f}", "11", f"{bx:.4f}", "21", f"{by:.4f}"])
    poly(outer)
    hc = [(x, y, r) for x, y, r in holes]
    for ring in inner:
        cx = sum(p[0] for p in ring) / len(ring)
        cy = sum(p[1] for p in ring) / len(ring)
        if any(math.hypot(cx - x, cy - y) < 0.3 * r for x, y, r in hc):
            continue                                            # 安装孔：下面画整圆
        poly(ring)
    for x, y, r in hc:
        ents.extend(["0", "CIRCLE", "8", name, "10", f"{x:.4f}", "20", f"{y:.4f}", "40", f"{r:.4f}"])
    ents.extend(["0", "TEXT", "8", name, "10", f"{min(p[0] for p in outer):.2f}", "20", f"{min(p[1] for p in outer) - 8:.2f}", "40", "3",
                 "1", f"{name} t={t:g}"])
    body = ["0", "SECTION", "2", "HEADER", "9", "$INSUNITS", "70", "4", "0", "ENDSEC", "0", "SECTION", "2", "ENTITIES"] + ents + ["0", "ENDSEC", "0", "EOF"]
    return ("\n".join(body) + "\n").encode("utf-8")
