"""第 1 章参考解：SKY130 CMOS 反相器的版图、DRC、提取与 LVS（第 17 轮附 4b）。

第一遍：Magic 的 SKY130 器件生成器放 NMOS（下）、PMOS（上），都带衬底保护环；
第二遍：读两个器件单元里的实际几何（metal1 端子、保护环的 locali），算出连线后用 metal1 画：
  栅极：两管栅极接触之间一条竖直 metal1，向右引出 IN；
  输出：两管漏极向左接到一条竖直 metal1，OUT；
  电源：底部 VSS 轨接 NMOS 源极和保护环，顶部 VDD 轨接 PMOS 源极和保护环（保护环经 mcon 接 metal1）。
然后：DRC（drc(full)）→ 提取 SPICE → Netgen 与原理图网表（inv.spice）做 LVS → 导出 GDS。

用法：python3 build_inv.py [--wn 0.42] [--wp 0.97] [--out 目录]
环境：MAGICRC 指向 sky130A.magicrc（IIC-OSIC-TOOLS 镜像中为 $PDK_ROOT/$PDK/libs.tech/magic/sky130A.magicrc），
      NETGEN_SETUP 指向 sky130A_setup.tcl（镜像中为 $PDK_ROOT/$PDK/libs.tech/netgen/sky130A_setup.tcl）。
输出 result.json：{"drc_errors", "lvs_match", "area_um2", "width_um", "height_um", ...}，供 wqlab 汇总。
"""
import argparse
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
U = 0.005                                   # μm per Magic internal unit (sky130A.magicrc sets scalegrid 1 2)


def um(x: float) -> int:
    """Microns → internal units, on the 0.005 μm grid."""
    return int(round(x / U))
MAGIC = os.environ.get("MAGIC", "magic")
NETGEN = os.environ.get("NETGEN", "netgen")


def run_magic(workdir: Path, script: str, name: str) -> str:
    (workdir / f"{name}.tcl").write_text(script + "\nquit -noprompt\n", encoding="utf-8")
    p = subprocess.run([MAGIC, "-dnull", "-noconsole", "-rcfile", os.environ["MAGICRC"], f"{name}.tcl"],
                       cwd=workdir, capture_output=True, text=True, timeout=600)
    (workdir / f"{name}.log").write_text(p.stdout + p.stderr, encoding="utf-8")
    return p.stdout + p.stderr


def read_mag(path: Path) -> tuple[dict, dict]:
    """Layers → list of rects, and port labels → (layer, x, y)."""
    layers, labels, cur = {}, {}, None
    for ln in path.read_text().splitlines():
        m = re.match(r"<< (\S+) >>", ln)
        if m:
            cur = m.group(1); continue
        if ln.startswith("rect ") and cur:
            layers.setdefault(cur, []).append(tuple(int(v) for v in ln.split()[1:5]))
        m = re.match(r"rlabel (\S+) (-?\d+) (-?\d+) (-?\d+) (-?\d+) \d+ (\S+)", ln)
        if m:
            labels[m.group(6)] = (m.group(1), int(m.group(2)), int(m.group(3)))
    return layers, labels


def instances(path: Path) -> dict:
    """use <cell> <inst> / transform 1 0 dx 0 1 dy / box x0 y0 x1 y1 → {inst: (cell, dx, dy, box_ll_local)}."""
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


def shift(r, dx, dy):
    return (r[0] + dx, r[1] + dy, r[2] + dx, r[3] + dy)


def contains(r, x, y):
    return r[0] <= x <= r[2] and r[1] <= y <= r[3]


def terminal_box(layers, labels, name, dx, dy):
    """Bounding box of the metal1 shapes that touch the terminal's contact column."""
    _, lx, ly = labels[name]
    m1 = [r for r in layers.get("metal1", []) if r[0] - 4 <= lx <= r[2] + 4]
    if name == "G":
        m1 = [r for r in m1 if abs((r[1] + r[3]) / 2 - ly) < 40]
    else:
        m1 = [r for r in m1 if not (r[0] < -16 and r[2] > 16)]       # not the gate pad
        m1 = [r for r in m1 if (r[0] + r[2]) / 2 * lx > 0 or abs((r[0] + r[2]) / 2 - lx) < 15]
    xs0, ys0 = min(r[0] for r in m1), min(r[1] for r in m1)
    xs1, ys1 = max(r[2] for r in m1), max(r[3] for r in m1)
    return shift((xs0, ys0, xs1, ys1), dx, dy)


def ring_li(layers, dx, dy, side):
    """The guard ring's horizontal locali segment on the given side: the largest-area rect in the outer band."""
    li = layers["locali"]
    edge = min(r[1] for r in li) if side == "bottom" else max(r[3] for r in li)
    band = [r for r in li if (r[1] <= edge + um(0.2) if side == "bottom" else r[3] >= edge - um(0.2))]
    seg = max(band, key=lambda r: (r[2] - r[0]) * (r[3] - r[1]))
    return shift(seg, dx, dy)


def build(wn: float, wp: float, out: Path, schematic: Path | None = None) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    for f in out.glob("*.mag"):
        f.unlink()
    # ---- pass 1: devices
    run_magic(out, f"""
load inv -silent
snap internal
box 0 0 0 0
magic::gencell sky130::sky130_fd_pr__nfet_01v8 xn w {wn} l 0.15 nf 1 m 1 guard 1 topc 1 botc 0 full_metal 1
box 0 {um(6)} 0 {um(6)}
magic::gencell sky130::sky130_fd_pr__pfet_01v8 xp w {wp} l 0.15 nf 1 m 1 guard 1 topc 0 botc 1 full_metal 1
writeall force
""", "pass1")
    inst = instances(out / "inv.mag")
    ncell, ndx, ndy, _ = inst["xn"]
    pcell, pdx, pdy, pll = inst["xp"]
    nl, nlab = read_mag(out / f"{ncell}.mag")
    pl, plab = read_mag(out / f"{pcell}.mag")
    # PMOS placed so that its guard ring sits 1.0 μm above the NMOS ring (room for the gate strip)
    n_top = max(r[3] for r in nl["locali"]) + ndy
    p_bot_local = min(r[1] for r in pl["locali"])
    pdy = n_top + um(1.0) - p_bot_local
    nD, nS, nG = (terminal_box(nl, nlab, k, ndx, ndy) for k in ("D", "S", "G"))
    pD, pS, pG = (terminal_box(pl, plab, k, pdx, pdy) for k in ("D", "S", "G"))
    n_ring, p_ring = ring_li(nl, ndx, ndy, "bottom"), ring_li(pl, pdx, pdy, "top")
    W = um(0.30)                                                    # wire width 0.30 μm (metal1 min 0.14)
    left = min(nD[0], pD[0]) - um(0.60)                             # OUT trunk left of both drains
    right = max(nS[2], pS[2]) + um(0.60)
    gx0 = (nG[0] + nG[2]) // 2 - W // 2                             # gate strip centred on the gate pads
    rects = []
    rects.append(("metal1", (gx0, nG[1], gx0 + W, pG[3])))           # gate strip
    rects.append(("metal1", (gx0, (nG[3] + pG[1]) // 2 - W // 2, right + um(0.6), (nG[3] + pG[1]) // 2 + W // 2)))  # IN to the right
    rects.append(("metal1", (left, nD[1], left + W, pD[3])))         # OUT trunk
    rects.append(("metal1", (left, nD[1], nD[2], nD[1] + W)))        # NMOS drain → trunk
    rects.append(("metal1", (left, pD[3] - W, pD[2], pD[3])))        # PMOS drain → trunk
    vss_y0, vss_y1 = n_ring[1] - um(0.10), n_ring[3] + um(0.10)      # VSS rail over the bottom ring segment
    vdd_y0, vdd_y1 = p_ring[1] - um(0.10), p_ring[3] + um(0.10)
    rects.append(("metal1", (left - um(0.6), vss_y0, right + um(0.6), vss_y1)))
    rects.append(("metal1", (left - um(0.6), vdd_y0, right + um(0.6), vdd_y1)))
    rects.append(("metal1", (nS[0], vss_y1 - um(0.05), nS[2], nS[1] + W)))  # NMOS source down to VSS
    rects.append(("metal1", (pS[0], pS[3] - W, pS[2], vdd_y0 + um(0.05))))  # PMOS source up to VDD
    # mcon (viali) on the ring segments, centred, 0.17 μm square
    def mcon(seg):
        cx, cy = (seg[0] + seg[2]) // 2, (seg[1] + seg[3]) // 2
        h = um(0.17) // 2
        return ("viali", (cx - h, cy - h, cx + h, cy + h))
    rects += [mcon(n_ring), mcon(p_ring)]
    paint = "\n".join(f"box {r[0]} {r[1]} {r[2]} {r[3]}\npaint {layer}" for layer, r in rects)
    iny = (nG[3] + pG[1]) // 2
    labels = [("IN", right + um(0.4), iny, "metal1"), ("OUT", left + W // 2, (nD[1] + pD[3]) // 2, "metal1"),
              ("VDD", left - um(0.4), (vdd_y0 + vdd_y1) // 2, "metal1"), ("VSS", left - um(0.4), (vss_y0 + vss_y1) // 2, "metal1")]
    lab = "\n".join(f"box {x} {y} {x} {y}\nlabel {t} c {layer}\nport make" for t, x, y, layer in labels)
    script = f"""
load inv -silent
snap internal
select cell xp
move to {pdx + pll[0]} {pdy + pll[1]}
select clear
{paint}
{lab}
select top cell
writeall force inv
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
ext2spice -p extfiles -o inv_layout.spice
gds write inv.gds
"""
    log = run_magic(out, script, "pass2")
    drc = int(re.search(r"WQ_DRC_COUNT (\d+)", log).group(1)) if "WQ_DRC_COUNT" in log else -1
    why = re.findall(r"WQ_DRC_WHY (.*)", log)
    bb = [int(v) for v in re.search(r"WQ_BBOX (-?\d+) (-?\d+) (-?\d+) (-?\d+)", log).groups()] if "WQ_BBOX" in log else [0, 0, 0, 0]
    # ---- LVS
    if schematic:                                                   # the student's own netlist (from Xschem)
        shutil.copy(schematic, out / "inv.spice")
    else:                                                           # the reference schematic at the chosen sizes
        ref = (HERE / "inv.spice").read_text(encoding="utf-8")
        ref = re.sub(r"(XMN .*?W=)[\d.]+", lambda m: f"{m.group(1)}{wn}", ref)
        ref = re.sub(r"(XMP .*?W=)[\d.]+", lambda m: f"{m.group(1)}{wp}", ref)
        (out / "inv.spice").write_text(ref, encoding="utf-8")
    lvs = subprocess.run([NETGEN, "-batch", "lvs", "inv_layout.spice inv", "inv.spice inv",
                          os.environ["NETGEN_SETUP"], "lvs.out"], cwd=out, capture_output=True, text=True, timeout=600)
    (out / "netgen.log").write_text(lvs.stdout + lvs.stderr, encoding="utf-8")
    report = (out / "lvs.out").read_text(errors="replace") if (out / "lvs.out").exists() else ""
    props_ok = "Property errors were found" not in report and "There were property errors" not in report
    match = "Circuits match uniquely" in report and "Netlists do not match" not in report and props_ok
    unit = U
    res = {"wn_um": wn, "wp_um": wp, "drc_errors": drc, "drc_why": why, "lvs_match": match, "lvs_properties_ok": props_ok,
           "width_um": round((bb[2] - bb[0]) * unit, 2), "height_um": round((bb[3] - bb[1]) * unit, 2),
           "area_um2": round((bb[2] - bb[0]) * (bb[3] - bb[1]) * unit * unit, 2),
           "gds": str(out / "inv.gds")}
    (out / "result.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--wn", type=float, default=0.42)
    ap.add_argument("--wp", type=float, default=0.97)
    ap.add_argument("--out", default="inv_build")
    ap.add_argument("--schematic", help="compare against this netlist instead of the reference schematic")
    a = ap.parse_args()
    r = build(a.wn, a.wp, Path(a.out).resolve(), Path(a.schematic).resolve() if a.schematic else None)
    print(json.dumps(r, ensure_ascii=False))
    raise SystemExit(0 if r["drc_errors"] == 0 and r["lvs_match"] else 1)
