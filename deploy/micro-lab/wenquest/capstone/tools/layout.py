"""贯通项目版图工具（学生和教师共用）：Magic 器件生成、读取单元几何、放置与非门的四个管子、DRC/提取/LVS 检查。"""
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

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



def place_nand2(out: Path, wn: float = 0.42, wp: float = 0.97, cell: str = "nand2") -> dict:
    """Generate the four transistors (each with its own guard ring) and place them: NMOS N1 (gate A), N2 (gate B)
    in the bottom row, PMOS P1 (A), P2 (B) above. Writes out/<cell>.mag with the devices only, no wiring.
    Returns positions, terminal boxes and ring segments (internal units) for scripts that wire it."""
    out.mkdir(parents=True, exist_ok=True)
    if (out / f"{cell}.mag").exists() and os.environ.get("WQ_OVERWRITE") != "1":
        raise SystemExit(f"{out / (cell + '.mag')} already exists: choose a new folder (or set WQ_OVERWRITE=1 to replace it)")
    for f in out.glob("*.mag"):
        f.unlink()
    dev = {"n1": ("nfet", wn, "topc 1 botc 0"), "n2": ("nfet", wn, "topc 1 botc 0"),
           "p1": ("pfet", wp, "topc 0 botc 1"), "p2": ("pfet", wp, "topc 0 botc 1")}
    gen = "\n".join(f"box 0 {um(8) * i} 0 {um(8) * i}\nmagic::gencell sky130::sky130_fd_pr__{t}_01v8 {name} w {w} l 0.15 nf 1 m 1 guard 1 {c} full_metal 1"
                    for i, (name, (t, w, c)) in enumerate(dev.items()))
    run_magic(out, f"load {cell} -silent\nsnap internal\n{gen}\nwriteall force\n", "place1")
    inst = instances(out / f"{cell}.mag")
    geo = {k: read_cell(out / f"{inst[k][0]}.mag") for k in dev}
    n_li, p_li, p_nw = geo["n1"][0]["locali"], geo["p1"][0]["locali"], geo["p1"][0]["nwell"]
    n_top = max(r[3] for r in n_li)
    p_bot = min(r[1] for r in p_li)
    p_nw_half = (max(r[2] for r in p_nw) - min(r[0] for r in p_nw)) // 2
    # Two separate n-wells (one per PMOS) must not partly overlap between subcells: keep them 1.4 μm apart
    # (n-well spacing ≥ 1.27 μm). A standard cell instead puts both PMOS in one well.
    xB = 2 * p_nw_half + um(1.40)
    yP = n_top + um(1.60) - p_bot                         # 1.6 μm between the rings for gate pads and pins
    pos = {"n1": (0, 0), "n2": (xB, 0), "p1": (0, yP), "p2": (xB, yP)}
    moves = "\n".join(f"select cell {k}\nmove to {pos[k][0] + inst[k][3][0]} {pos[k][1] + inst[k][3][1]}\nselect clear" for k in dev)
    # Save only the top cell: the generated device cells must stay as place1 wrote them. (Magic rewrites a saved
    # device cell in lambda units, and a fresh session then reads it at half size — so never "writeall" the devices.)
    run_magic(out, f"load {cell} -silent\nsnap internal\n{moves}\nselect top cell\nwriteall force {cell}\n", "place2")
    T = {k: {t: term(*geo[k], t, *pos[k]) for t in ("D", "S", "G")} for k in dev}
    rings = {k: ring_seg(geo[k][0], *pos[k], "bottom" if k[0] == "n" else "top") for k in dev}
    meta = {"pos": pos, "T": T, "rings": rings, "xB": xB, "yP": yP, "n_top": n_top, "p_bot": p_bot}
    (out / "placement.json").write_text(json.dumps({"unit_um": U, **meta}, indent=1))
    return meta


def check(out: Path, cell: str, schematic: Path) -> dict:
    """DRC (full rule deck), extraction, LVS against the schematic netlist, GDS — for any layout out/<cell>.mag."""
    script = f"""
load {cell} -silent
select top cell
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
ext2spice -p extfiles -o {cell}_layout.spice
gds write {cell}.gds
"""
    log = run_magic(out, script, "check")
    drc = int(re.search(r"WQ_DRC_COUNT (\d+)", log).group(1)) if "WQ_DRC_COUNT" in log else -1
    why = re.findall(r"WQ_DRC_WHY (.*)", log)
    m = re.search(r"WQ_BBOX (-?\d+) (-?\d+) (-?\d+) (-?\d+)", log)
    bb = [int(x) for x in m.groups()] if m else [0] * 4
    sch = out / f"{cell}_schematic.spice"
    if Path(schematic).resolve() != sch.resolve():
        shutil.copy(schematic, sch)
    lvs = subprocess.run([NETGEN, "-batch", "lvs", f"{cell}_layout.spice {cell}", f"{sch.name} {cell}",
                          os.environ["NETGEN_SETUP"], "lvs.out"], cwd=out, capture_output=True, text=True, timeout=600)
    (out / "netgen.log").write_text(lvs.stdout + lvs.stderr, encoding="utf-8")
    report = (out / "lvs.out").read_text(errors="replace") if (out / "lvs.out").exists() else ""
    props_ok = "Property errors were found" not in report and "There were property errors" not in report
    match = "Circuits match uniquely" in report and "Netlists do not match" not in report and props_ok
    return {"drc_errors": drc, "drc_why": why, "lvs_match": match, "lvs_properties_ok": props_ok,
            "width_um": round((bb[2] - bb[0]) * U, 2), "height_um": round((bb[3] - bb[1]) * U, 2),
            "area_um2": round((bb[2] - bb[0]) * (bb[3] - bb[1]) * U * U, 2), "gds": str(out / f"{cell}.gds")}
