"""三维动画 53.7.1（配图 53.7.1）：SH-301 的轴向加工一刀一刀进行——每一刀以哪个面为基准（蓝点）、加工哪个面（红色）、工序尺寸多少，
都取自数字工厂工艺规程的 tolerance_chart；轴的形状随之变化（直径按工序 20、40 的尺寸，示意）。最后列出图纸尺寸由哪几刀间接得到。
模型：factory/digital/models3d（工件轮廓由回转生成），逐帧渲染（render3d.Video）。"""
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[4]
for p in (REPO / "factory" / "digital", REPO / "textbook" / "tools"):
    sys.path.insert(0, str(p))

import render3d as R  # noqa: E402
from models3d import core as C, shapes as S  # noqa: E402

plan = yaml.safe_load((REPO / "factory" / "digital" / "std" / "SH-301_process.yaml").read_text(encoding="utf-8"))
tc = plan["tolerance_chart"]
cuts = tc["cuts"]
pos = {"L": -7.0, "R": 175.0}                              # 毛坯：左端面在 −7，总长 182（终件左端面在 0 附近）
D = {"blank": 50.0}
ROUGH = {("L", "S1"): 31.5, ("S1", "S2"): 36.5, ("S2", "S3"): 41.5, ("S3", "S4"): 36.5, ("S4", "R"): 31.5}
FIN = {("L", "S1"): 30.0, ("S1", "S2"): 35.3, ("S2", "S3"): 40.3, ("S3", "S4"): 35.3, ("S4", "R"): 30.0}
ORDER = ["L", "S1", "S2", "S3", "S4", "R"]
seg_d = {k: 50.0 for k in ROUGH}


def profile():
    faces = [f for f in ORDER if f in pos]
    pts = []
    for a_, b_ in zip(faces, faces[1:]):
        d = 50.0
        for (s0, s1), dd in seg_d.items():
            if ORDER.index(s0) >= ORDER.index(a_) and ORDER.index(s1) <= ORDER.index(b_):
                d = min(d, dd) if (a_, b_) == (s0, s1) else d
        d = seg_d.get((a_, b_), 50.0)
        pts.append((pos[a_], pos[b_], d))
    return pts


def shaft():
    s = None
    for x0, x1, d in profile():
        c = S.cyl("x", (0, 0), d / 2, x0, x1)
        s = c if s is None else s + c
    return s


def apply(c):
    pos[c["surf"]] = pos[c["ref"]] + c["nominal"]
    seq = c["seq"]
    # 直径随工序变化（示意）：工序 20 的粗车轴肩、工序 40 的精车轴肩完成相邻轴段的外圆
    if seq < 40:
        if c["surf"] == "S3":
            seg_d[("S3", "S4")] = ROUGH[("S3", "S4")]; seg_d[("S4", "R")] = ROUGH[("S3", "S4")]
        if c["surf"] == "S4":
            seg_d[("S4", "R")] = ROUGH[("S4", "R")]
        if c["surf"] == "S2":
            seg_d[("S2", "S3")] = ROUGH[("S2", "S3")]; seg_d[("L", "S1")] = ROUGH[("S1", "S2")]; seg_d[("S1", "S2")] = ROUGH[("S1", "S2")]
        if c["surf"] == "S1":
            seg_d[("L", "S1")] = ROUGH[("L", "S1")]
    else:
        if c["surf"] == "S3":
            seg_d[("S3", "S4")] = FIN[("S3", "S4")]; seg_d[("S4", "R")] = FIN[("S3", "S4")]
        if c["surf"] == "S4":
            seg_d[("S4", "R")] = FIN[("S4", "R")]
        if c["surf"] == "S2":
            seg_d[("S2", "S3")] = FIN[("S2", "S3")]; seg_d[("S1", "S2")] = FIN[("S1", "S2")]; seg_d[("L", "S1")] = FIN[("S1", "S2")]
        if c["surf"] == "S1":
            seg_d[("L", "S1")] = FIN[("L", "S1")]


# 先把各刀后的形状算好（每个状态一个零件，按需显示）
a = C.Assembly("跟踪图")
states = [(dict(pos), dict(seg_d), None)]
a.add(C.Part("状态0", shaft(), "work"))
for i, c in enumerate(cuts):
    apply(c)
    a.add(C.Part(f"状态{i + 1}", shaft(), "work"))
    states.append((dict(pos), dict(seg_d), c))
CAM = {"dir": [0, -1, 0.0], "fit": [[-12, 0, -75], [182, 0, 60]]}
v = R.Video(a, width=1280, height=720, fps=20)
N = len(states)


def frame(k, cap, extra_dims=(), show_cut=True):
    p_, _, c = states[k]
    c = c if show_cut else None
    parts = {f"状态{j}": {"visible": j == k} for j in range(N)}
    pts, dims, texts = [], list(extra_dims), []
    if c:
        xr, xs = p_[c["ref"]], p_[c["surf"]]
        pts = [{"at": (xr, -30, 0), "r": 7, "color": "#4f7fb8", "text": f"基准 {c['ref']}", "dx": -30, "dy": 30},
               {"at": (xs, -30, 0), "r": 7, "color": "#c0504d", "text": f"加工 {c['surf']}", "dx": -30, "dy": -18}]
        tol = f"±{c['es']:g}" if abs(c["es"] + c["ei"]) < 1e-9 else f"({c['es']:+g}/{c['ei']:+g})"
        dims.append({"a": (xr, -30, -27), "b": (xs, -30, -27), "off": (0, 0, -10), "text": f"{abs(c['nominal']):g} {tol}", "color": "#c0504d"})
    for j, cc in enumerate(cuts[:12]):
        done = j < k
        texts.append({"pos": [0.06 + 0.31 * (j // 4), 0.8 + 0.045 * (j % 4)], "text": f"{cc['seq']:g}  {cc['ref']}→{cc['surf']}  {abs(cc['nominal']):g}",
                      "fontSize": 17, "bold": j == k - 1, "color": "#c0504d" if j == k - 1 else ("#1d2327" if done else "#9aa3ab")})
    return {"parts": parts, "camera": CAM, "points": pts, "dims": dims,
            "texts": [{"pos": [0.03, 0.08], "text": cap[0], "fontSize": 24, "bold": True},
                      {"pos": [0.03, 0.13], "text": cap[1], "fontSize": 17, "color": "#5b6770"}] + texts}


v.add(frame(0, ("毛坯 Ø50 × 182：轴向一共 12 刀", "Blank Ø50 × 182: twelve axial cuts")), hold=1.5)
for k in range(1, N):
    c = states[k][2]
    v.add(frame(k, (c["label"], f"cut {c['seq']:g}: datum {c['ref']}, machined face {c['surf']}")), hold=1.4)
p_ = states[-1][0]
fin = [{"a": (p_["S2"], 25, 22), "b": (p_["S3"], 25, 22), "off": (0, 0, 14), "text": "60 ± 0.3：经过 40.3、40.31、40.21 三刀", "color": "#5a9e6f"}]
v.add(frame(N - 1, ("齿轮位长度 60 没有一刀直接车出：它是封闭环", "The 60 mm gear seat is never cut directly: it is a closing link"), fin, show_cut=False), hold=3.0)
v.save("v53_7_1")
