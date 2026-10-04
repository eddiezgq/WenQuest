"""贯通项目步骤二参考解：SKY130 二输入与非门（NAND2）的版图、DRC、提取与 LVS（第 17 轮附二 5a）。

做法与第 1 章反相器相同（Magic 的 SKY130 器件生成器 + 脚本连线），只是四个管子：
  下排 NMOS 串联：N1（栅 A）、N2（栅 B）；VSS — N1 — X — N2 — OUT
  上排 PMOS 并联：P1（栅 A）、P2（栅 B）；两管都接在 VDD 与 OUT 之间
连线：
  metal1：两条栅极竖条（A、B）及向外的引脚；N1 与 N2 之间的 X；VSS、VDD 电源轨及到各管源/漏的短线；
  metal2：OUT。OUT 要把 P1、P2（并联）和 N2 连在一起，单用 metal1 会和栅极竖条交叉，所以走第二层金属，
          经 via1 落到三个管子的端子上——这正是标准单元里“多一层布线”的由来。
每个管子各自带衬底保护环（分立器件），面积比 SKY130 标准单元 sky130_fd_sc_hd__nand2_1 大得多：
标准单元让串联的两个 NMOS 共用一块扩散区、不带各自的保护环。步骤二报告要比较这一点。

用法：python3 build_nand2.py [--wn 0.42] [--wp 0.97] [--schematic 网表] [--out 目录]
环境：MAGICRC、NETGEN_SETUP 同第 1 章（wqlab nand2 会自动设置）。
输出 result.json：{"drc_errors", "lvs_match", "area_um2", ...}
"""
import argparse
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
U = 0.005                                    # μm per internal unit in the top cell (magscale 1 2)
MAGIC = os.environ.get("MAGIC", "magic")
NETGEN = os.environ.get("NETGEN", "netgen")


def um(x: float) -> int:
    return int(round(x / U))


def run_magic(workdir: Path, script: str, name: str) -> str:
    (workdir / f"{name}.tcl").write_text(script + "\nquit -noprompt\n", encoding="utf-8")
    p = subprocess.run([MAGIC, "-dnull", "-noconsole", "-rcfile", os.environ["MAGICRC"], f"{name}.tcl"],
                       cwd=workdir, capture_output=True, text=True, timeout=600)
    (workdir / f"{name}.log").write_text(p.stdout + p.stderr, encoding="utf-8")
    return p.stdout + p.stderr


def read_cell(path: Path):
    """Layers → rects and port labels → (layer, x, y), in top-cell internal units.
    A cell file without a "magscale 1 2" line is in lambda (0.01 μm) and is scaled ×2 (Magic writes the device cells that way when it saves them again)."""
    text = path.read_text()
    k = 1 if re.search(r"^magscale 1 2", text, re.M) else 2
    layers, labels, cur = {}, {}, None
    for ln in text.splitlines():
        m = re.match(r"<< (\S+) >>", ln)
        if m:
            cur = m.group(1); continue
        if ln.startswith("rect ") and cur:
            layers.setdefault(cur, []).append(tuple(int(v) * k for v in ln.split()[1:5]))
        m = re.match(r"rlabel (\S+) (-?\d+) (-?\d+) (-?\d+) (-?\d+) \d+ (\S+)", ln)
        if m:
            labels[m.group(6)] = (m.group(1), int(m.group(2)) * k, int(m.group(3)) * k)
    return layers, labels


def instances(path: Path) -> dict:
    out, cell, inst, t = {}, None, None, None
    for ln in path.read_text().splitlines():
        m = re.match(r"use (\S+)\s+(\S+)", ln)
        if m:
            cell, inst = m.group(1), m.group(2)
        m = re.match(r"transform 1 0 (-?\d+) 0 1 (-?\d+)", ln)
        if m:
            t = (int(m.group(1)), int(m.group(2)))
        m = re.match(r"box (-?\d+) (-?\d+) -?\d+ -?\d+", ln)
        if m and inst and t:
            out[inst] = (cell, t[0], t[1], (int(m.group(1)), int(m.group(2)))); inst = t = None
    return out


def term(layers, labels, name, dx, dy):
    """The metal1 rectangle group of terminal D, S or G (bounding box), shifted to (dx, dy)."""
    _, lx, ly = labels[name]
    m1 = layers.get("metal1", [])
    if name == "G":
        grp = [r for r in m1 if r[0] <= lx <= r[2] or abs((r[0] + r[2]) / 2 - lx) < um(0.2)]
        grp = [r for r in grp if abs((r[1] + r[3]) / 2 - ly) < um(0.25)]
    else:
        grp = [r for r in m1 if (r[0] + r[2]) / 2 * lx > 0 and abs((r[0] + r[2]) / 2 - lx) < um(0.4)
               and abs((r[1] + r[3]) / 2 - ly) < um(1.6)]
        gy = labels["G"][2]
        grp = [r for r in grp if abs((r[1] + r[3]) / 2 - gy) > um(0.3)]        # not the gate pad
    x0, y0 = min(r[0] for r in grp), min(r[1] for r in grp)
    x1, y1 = max(r[2] for r in grp), max(r[3] for r in grp)
    return (x0 + dx, y0 + dy, x1 + dx, y1 + dy)


def ring_seg(layers, dx, dy, side):
    """The guard ring's widest horizontal locali segment on the bottom or top side."""
    li = layers["locali"]
    edge = min(r[1] for r in li) if side == "bottom" else max(r[3] for r in li)
    band = [r for r in li if (r[1] <= edge + um(0.2) if side == "bottom" else r[3] >= edge - um(0.2))]
    s = max(band, key=lambda r: (r[2] - r[0]) * (r[3] - r[1]))
    return (s[0] + dx, s[1] + dy, s[2] + dx, s[3] + dy)


def build(wn: float, wp: float, out: Path, schematic: Path | None = None) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    for f in out.glob("*.mag"):
        f.unlink()
    dev = {"n1": ("nfet", wn, "topc 1 botc 0"), "n2": ("nfet", wn, "topc 1 botc 0"),
           "p1": ("pfet", wp, "topc 0 botc 1"), "p2": ("pfet", wp, "topc 0 botc 1")}
    gen = "\n".join(f"box 0 {um(8) * i} 0 {um(8) * i}\nmagic::gencell sky130::sky130_fd_pr__{t}_01v8 {name} w {w} l 0.15 nf 1 m 1 guard 1 {c} full_metal 1"
                    for i, (name, (t, w, c)) in enumerate(dev.items()))
    run_magic(out, f"load nand2 -silent\nsnap internal\n{gen}\nwriteall force\n", "pass1")
    inst = instances(out / "nand2.mag")
    geo = {k: read_cell(out / f"{inst[k][0]}.mag") for k in dev}

    # ---- placement (device origins, internal units)
    n_li, p_li, p_nw = geo["n1"][0]["locali"], geo["p1"][0]["locali"], geo["p1"][0]["nwell"]
    n_top = max(r[3] for r in n_li)
    p_bot = min(r[1] for r in p_li)
    p_nw_half = (max(r[2] for r in p_nw) - min(r[0] for r in p_nw)) // 2
    # Two separate n-wells (one per PMOS) must not partly overlap between subcells: keep them 1.4 μm apart
    # (n-well spacing ≥ 1.27 μm). A standard cell instead puts both PMOS in one well.
    xB = 2 * p_nw_half + um(1.40)
    yP = n_top + um(1.60) - p_bot                         # 1.6 μm between the rings for gate pads and pins
    pos = {"n1": (0, 0), "n2": (xB, 0), "p1": (0, yP), "p2": (xB, yP)}
    T = {k: {t: term(*geo[k], t, *pos[k]) for t in ("D", "S", "G")} for k in dev}
    W = um(0.30)
    rects = []                                           # (layer, rect)
    # gates: vertical strips from the NMOS gate pad to the PMOS gate pad, pins A (left) and B (right)
    pin_y = (n_top + (yP + p_bot)) // 2
    for nk, pk, sign, nm in (("n1", "p1", -1, "A"), ("n2", "p2", 1, "B")):
        g_n, g_p = T[nk]["G"], T[pk]["G"]
        cx = (g_n[0] + g_n[2]) // 2
        rects.append(("metal1", (cx - W // 2, g_n[1], cx + W // 2, g_p[3])))
        x_end = cx + sign * um(2.2)
        rects.append(("metal1", (min(cx, x_end), pin_y - W // 2, max(cx, x_end), pin_y + W // 2)))
    # X: N1.S → N2.D, across the two rings, at the middle of the source/drain columns
    s1, d2 = T["n1"]["S"], T["n2"]["D"]
    ym = (s1[1] + s1[3]) // 2
    rects.append(("metal1", (s1[0], ym - W // 2, d2[2], ym + W // 2)))
    # rails over the bottom (NMOS) and top (PMOS) ring segments, with an mcon on each ring
    n_rings = [ring_seg(geo[k][0], *pos[k], "bottom") for k in ("n1", "n2")]
    p_rings = [ring_seg(geo[k][0], *pos[k], "top") for k in ("p1", "p2")]
    left, right = -um(2.6), xB + um(2.6)
    vss = (left, n_rings[0][1] - um(0.10), right, n_rings[0][3] + um(0.10))
    vdd = (left, p_rings[0][1] - um(0.10), right, p_rings[0][3] + um(0.10))
    rects += [("metal1", vss), ("metal1", vdd)]
    h = um(0.17) // 2
    for s in n_rings + p_rings:
        cx, cy = (s[0] + s[2]) // 2, (s[1] + s[3]) // 2
        rects.append(("viali", (cx - h, cy - h, cx + h, cy + h)))
    # N1.D down to VSS; P1.D and P2.S up to VDD
    d1 = T["n1"]["D"]
    rects.append(("metal1", (d1[0], vss[3] - um(0.05), d1[2], d1[1] + W)))
    for k, t in (("p1", "D"), ("p2", "S")):
        c = T[k][t]
        rects.append(("metal1", (c[0], c[3] - W, c[2], vdd[1] + um(0.05))))
    # OUT on metal2: via1 on P1.S, P2.D and N2.S; a horizontal run at the PMOS middle and a vertical run down to N2.S
    # via1 contact 0.26 μm square (cut 0.15 + 0.055 on each side); metal1 and metal2 extend a further 0.06 μm
    # in one direction (via.5a, met2.5): metal1 vertically (it must stay inside narrow source/drain columns), metal2 both ways
    v, e = um(0.26) // 2, um(0.06)
    def via(c, y=None):
        cx, cy = (c[0] + c[2]) // 2, (c[1] + c[3]) // 2 if y is None else y
        return cx, cy, [("metal1", (cx - v, cy - v - e, cx + v, cy + v + e)), ("metal2", (cx - v - e, cy - v - e, cx + v + e, cy + v + e)),
                        ("via1", (cx - v, cy - v, cx + v, cy + v))]
    p1s, p2d, n2s = T["p1"]["S"], T["p2"]["D"], T["n2"]["S"]
    yo = (p1s[1] + p1s[3]) // 2
    xa, _, va = via(p1s, yo)
    xb_, _, vb = via(p2d, yo)
    xc, yc, vc = via(n2s)
    M2 = 2 * (v + e)                                       # metal2 runs as wide as the via pads: no notches
    rects += va + vb + vc + [
              ("metal2", (xa - M2 // 2, yo - M2 // 2, xc + M2 // 2, yo + M2 // 2)),
              ("metal2", (xc - M2 // 2, yc - M2 // 2, xc + M2 // 2, yo + M2 // 2))]
    rects.sort(key=lambda lr: lr[0] == "via1")                  # paint the contacts last
    paint = "\n".join(f"box {r[0]} {r[1]} {r[2]} {r[3]}\npaint {layer}" for layer, r in rects)
    gA = (T["n1"]["G"][0] + T["n1"]["G"][2]) // 2 - um(2.0)
    gB = (T["n2"]["G"][0] + T["n2"]["G"][2]) // 2 + um(2.0)
    labels = [("A", gA, pin_y, "metal1"), ("B", gB, pin_y, "metal1"), ("OUT", xc, (yc + yo) // 2, "metal2"),
              ("VDD", left + um(0.3), (vdd[1] + vdd[3]) // 2, "metal1"), ("VSS", left + um(0.3), (vss[1] + vss[3]) // 2, "metal1")]
    lab = "\n".join(f"box {x} {y} {x} {y}\nlabel {t} c {layer}\nport make" for t, x, y, layer in labels)
    moves = "\n".join(f"select cell {k}\nmove to {pos[k][0] + inst[k][3][0]} {pos[k][1] + inst[k][3][1]}\nselect clear" for k in dev)
    script = f"""
load nand2 -silent
snap internal
{moves}
{paint}
{lab}
select top cell
writeall force
drc style drc(full)
drc check
drc catchup
puts "WQ_DRC_COUNT [drc list count total]"
foreach {{why boxes}} [drc listall why] {{ puts "WQ_DRC_WHY $why ([llength $boxes])" }}
select top cell
puts "WQ_BBOX [box values]"
extract path extfiles
extract all
ext2spice lvs
ext2spice -p extfiles -o nand2_layout.spice
gds write nand2.gds
"""
    log = run_magic(out, script, "pass2")
    drc = int(re.search(r"WQ_DRC_COUNT (\d+)", log).group(1)) if "WQ_DRC_COUNT" in log else -1
    why = re.findall(r"WQ_DRC_WHY (.*)", log)
    bb = [int(x) for x in re.search(r"WQ_BBOX (-?\d+) (-?\d+) (-?\d+) (-?\d+)", log).groups()] if "WQ_BBOX" in log else [0] * 4
    if schematic:
        shutil.copy(schematic, out / "nand2.spice")
    else:
        ref = (HERE / "nand2.spice").read_text(encoding="utf-8")
        ref = re.sub(r"(XMN\d .*?W=)[\d.]+", lambda m: f"{m.group(1)}{wn}", ref)
        ref = re.sub(r"(XMP\d .*?W=)[\d.]+", lambda m: f"{m.group(1)}{wp}", ref)
        (out / "nand2.spice").write_text(ref, encoding="utf-8")
    lvs = subprocess.run([NETGEN, "-batch", "lvs", "nand2_layout.spice nand2", "nand2.spice nand2",
                          os.environ["NETGEN_SETUP"], "lvs.out"], cwd=out, capture_output=True, text=True, timeout=600)
    (out / "netgen.log").write_text(lvs.stdout + lvs.stderr, encoding="utf-8")
    report = (out / "lvs.out").read_text(errors="replace") if (out / "lvs.out").exists() else ""
    props_ok = "Property errors were found" not in report and "There were property errors" not in report
    match = "Circuits match uniquely" in report and "Netlists do not match" not in report and props_ok
    res = {"wn_um": wn, "wp_um": wp, "drc_errors": drc, "drc_why": why, "lvs_match": match, "lvs_properties_ok": props_ok,
           "width_um": round((bb[2] - bb[0]) * U, 2), "height_um": round((bb[3] - bb[1]) * U, 2),
           "area_um2": round((bb[2] - bb[0]) * (bb[3] - bb[1]) * U * U, 2), "gds": str(out / "nand2.gds")}
    (out / "result.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--wn", type=float, default=0.42)
    ap.add_argument("--wp", type=float, default=0.97)
    ap.add_argument("--out", default="nand2_build")
    ap.add_argument("--schematic")
    a = ap.parse_args()
    r = build(a.wn, a.wp, Path(a.out).resolve(), Path(a.schematic).resolve() if a.schematic else None)
    print(json.dumps(r, ensure_ascii=False))
    raise SystemExit(0 if r["drc_errors"] == 0 and r["lvs_match"] else 1)
