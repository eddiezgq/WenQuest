"""贯通项目步骤二参考解：SKY130 二输入与非门（NAND2）的版图、DRC、提取与 LVS（第 17 轮附二 5a）。

四个管子由 tools/layout.py 的 place_nand2() 生成并放好（学生的起始版图也是它生成的），本脚本只做连线：
  下排 NMOS 串联：N1（栅 A）、N2（栅 B）；VSS — N1 — X — N2 — OUT
  上排 PMOS 并联：P1（栅 A）、P2（栅 B）；两管都接在 VDD 与 OUT 之间
  metal1：两条栅极竖条（A、B）及向外的引脚；N1 与 N2 之间的 X；VSS、VDD 电源轨及到各管源/漏的短线；
  metal2：OUT。OUT 要把 P1、P2（并联）和 N2 连在一起，单用 metal1 会和栅极竖条交叉，所以走第二层金属，
          经 via1 落到三个管子的端子上——这正是标准单元里“多一层布线”的由来。
每个管子各自带衬底保护环（分立器件），面积比 SKY130 标准单元 sky130_fd_sc_hd__nand2_1 大得多：
标准单元让串联的两个 NMOS 共用一块扩散区、两个 PMOS 共用一个 n 阱、不带各自的保护环。步骤二报告要比较这一点。

用法：python3 build_nand2.py [--wn 0.42] [--wp 0.97] [--schematic 网表] [--out 目录]
环境：MAGICRC、NETGEN_SETUP 同第 1 章（wqlab nand2 会自动设置）。
"""
import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tools"))
from layout import U, check, place_nand2, run_magic, um  # noqa: E402


def build(wn: float, wp: float, out: Path, schematic: Path | None = None) -> dict:
    g = place_nand2(out, wn, wp)
    T, rings, xB, yP, n_top, p_bot = g["T"], g["rings"], g["xB"], g["yP"], g["n_top"], g["p_bot"]
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
    n_rings = [rings["n1"], rings["n2"]]
    p_rings = [rings["p1"], rings["p2"]]
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
    script = f"""
load nand2 -silent
snap internal
{paint}
{lab}
select top cell
writeall force nand2
"""
    run_magic(out, script, "wire")
    if schematic is None:
        sch = (HERE / "nand2.spice").read_text(encoding="utf-8")
        sch = re.sub(r"(XMN\d .*?W=)[\d.]+", lambda m: f"{m.group(1)}{wn}", sch)
        sch = re.sub(r"(XMP\d .*?W=)[\d.]+", lambda m: f"{m.group(1)}{wp}", sch)
        schematic = out / "nand2_schematic.spice"
        schematic.write_text(sch, encoding="utf-8")
    res = {"wn_um": wn, "wp_um": wp, **check(out, "nand2", schematic)}
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
