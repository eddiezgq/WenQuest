"""第 17 轮附三 6c：从 SKY130 的 Magic 工艺文件读出第 4 章用的导线参数，写进 labs/micro/kit/models/params.json 的 wires 一节。

来源：open_pdks 生成的 sky130A.tech（$PDK_ROOT/sky130A/libs.tech/magic/sky130A.tech），提取样式 ngspice 的典型值：
  resist      方块电阻，毫欧/方 → 存为 Ω/□
  contact     每个通孔的电阻，毫欧 → 存为 Ω
  defaultareacap    对衬底（场区）的面积电容，aF/μm²
  defaultperimeter  对衬底的边缘电容，aF/μm（每条边）
  defaultsidewall   同层相邻导线的侧壁耦合：每微米长度 C = k /(s + s0)，k 单位 aF，s、s0 单位 μm
  width / spacing   设计规则的最小线宽与间距（tech 文件里单位为 nm）
  height      层的底面高度与厚度，μm
运行：python wires.py [tech 文件]；默认读环境变量 SKY130_TECH。--check 只比较，不写文件（镜像验收用）。
"""
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PARAMS = HERE.parents[3] / "labs/micro/kit/models/params.json"
LAYERS = {"li1": ("allli", "locali", "*li", "li"), "met1": ("allm1", "metal1", "*m1", "m1"), "met2": ("allm2", "metal2", "allm2", "m2"),
          "met3": ("allm3", "metal3", "allm3", "m3"), "met4": ("allm4", "metal4", "allm4", "m4"), "met5": ("allm5", "metal5", "allm5", "m5")}
VIAS = {"mcon": "li1-met1", "m2c": "met1-met2", "m3c": "met2-met3", "via3": "met3-met4", "via4": "met4-met5"}


def parse(text: str) -> dict:
    ext = text[text.index("\nextract"):]
    ext = ext[: ext.index("\nend", 1)]
    first_style = ext[: ext.index("variants (fast)") if "variants (fast)" in ext else len(ext)]
    out = {}
    for name, (types, plane, wtype, short) in LAYERS.items():
        q = re.escape(types)
        res = float(re.search(rf"^\s*resist\s+\({q}\)/{plane}\s+([\d.]+)", ext, re.M).group(1)) / 1000
        area = float(re.search(rf"^\s*defaultareacap\s+{q}\s+{plane}\s+([\d.]+)\s*$", ext, re.M).group(1))
        peri = float(re.search(rf"^\s*defaultperimeter\s+{q}\s+{plane}\s+([\d.]+)\s*$", ext, re.M).group(1))
        sw = re.search(rf"^\s*defaultsidewall\s+{q}\s+{plane}\s+([\d.]+)\s+([\d.]+)", ext, re.M)
        h = re.search(rf"^\s*height\s+{q}\s+([\d.]+)\s+([\d.]+)", ext, re.M)
        w = re.search(rf"^\s*width\s+[^\s]*{re.escape(wtype)}[^\s]*\s+(\d+)", text, re.M)
        s = re.search(rf"^\s*spacing\s+[^\s]*{re.escape(types)}[^\s]*\s+[^\s]+\s+(\d+)", text, re.M)
        out[name] = {"Rsq": res, "Carea": area, "Cfringe": peri, "Kside": float(sw.group(1)), "s0": float(sw.group(2)),
                     "z": float(h.group(1)), "t": float(h.group(2)), "wmin": int(w.group(1)) / 1000,
                     "smin": int(s.group(1)) / 1000 if s else None}
    if out["li1"]["smin"] is None:
        out["li1"]["smin"] = 0.17                    # li.3（tech 文件里 li 的间距写在别的规则行）
    vias = {}
    for v, between in VIAS.items():
        m = re.search(rf"^\s*contact\s+{v}\s+([\d.]+)", ext, re.M)
        vias[between] = float(m.group(1)) / 1000
    return {"_note": "SKY130 导线参数（典型值），由 samples/数字集成电路设计/生成脚本/calib/wires.py 从 open_pdks 的 sky130A.tech 读出："
                     "Rsq Ω/□；Carea aF/μm²（对衬底）；Cfringe aF/μm（每条边，对衬底）；同层耦合每微米 Kside/(s+s0) aF；"
                     "z、t 层底高度与厚度 μm；wmin、smin 最小线宽、间距 μm；via 每个通孔 Ω",
            "layers": out, "via": vias}


def main():
    src = next((a for a in sys.argv[1:] if not a.startswith("--")), None) or os.environ.get("SKY130_TECH")
    if not src:
        sys.exit("给出 sky130A.tech 的路径或设 SKY130_TECH")
    w = parse(Path(src).read_text(encoding="utf-8", errors="replace"))
    params = json.loads(PARAMS.read_text(encoding="utf-8"))
    if "--check" in sys.argv:
        old = params.get("wires", {}).get("layers", {})
        bad = [f"{l}.{k}: {old.get(l, {}).get(k)} → {v}" for l, d in w["layers"].items() for k, v in d.items()
               if v is not None and abs((old.get(l, {}).get(k) or 0) - v) > 0.05 * abs(v) + 1e-9]
        print("导线参数与仓库一致" if not bad else "导线参数不一致：" + "；".join(bad))
        sys.exit(1 if bad else 0)
    params["wires"] = w
    PARAMS.write_text(json.dumps(params, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for l, d in w["layers"].items():
        print(f"{l}: {d['Rsq']:.3f} Ω/□, {d['Carea']} aF/μm², fringe {d['Cfringe']} aF/μm, side {d['Kside']}/(s+{d['s0']}), "
              f"w {d['wmin']} s {d['smin']} μm, t {d['t']} μm")
    print("via:", w["via"])


if __name__ == "__main__":
    main()
