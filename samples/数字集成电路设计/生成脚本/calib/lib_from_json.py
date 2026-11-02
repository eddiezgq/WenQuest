"""把 skywater-pdk-libs-sky130_fd_sc_hd 仓库里按单元拆开的 *.lib.json 拼成一个只含组合单元的简化 liberty 文件（本地开发用）。

镜像里有完整的 PDK（$PDK_ROOT/sky130A/libs.ref/sky130_fd_sc_hd/lib/sky130_fd_sc_hd__tt_025C_1v80.lib），镜像验收直接用它；
本地没有 PDK 时，稀疏克隆该仓库的 timing/*common*、timing/*tt_025C_1v80* 与 cells/*/*__tt_025C_1v80.lib.json，再运行：
  python lib_from_json.py <仓库目录> <输出.lib>
只保留综合与时序估算需要的内容：面积、引脚方向与逻辑函数、输入电容、时序表（cell_rise/fall、rise/fall_transition）。
"""
import json
import sys
from pathlib import Path

repo, out = Path(sys.argv[1]), Path(sys.argv[2])
common = json.loads((repo / "timing/sky130_fd_sc_hd__common.lib.json").read_text())


def fmt_list(v):
    return ", ".join(str(x) for x in v)


def table(name, t):
    s = f"        {name} {{\n"
    if "index_1" in t:
        s += f'          index_1 ("{fmt_list(t["index_1"])}");\n'
    if "index_2" in t:
        s += f'          index_2 ("{fmt_list(t["index_2"])}");\n'
    vals = t["values"]
    if not isinstance(vals, list):
        vals = [vals]
    if vals and isinstance(vals[0], list):
        s += "          values (" + ", ".join(f'"{fmt_list(r)}"' for r in vals) + ");\n"
    else:
        s += f'          values ("{fmt_list(vals)}");\n'
    return s + "        }\n"


lines = ["library (sky130_fd_sc_hd__tt_025C_1v80_comb) {",
         '  delay_model : "table_lookup";', '  time_unit : "1ns";', '  voltage_unit : "1V";', '  current_unit : "1mA";',
         '  leakage_power_unit : "1nW";', "  capacitive_load_unit (1, pf);",
         "  input_threshold_pct_rise : 50; input_threshold_pct_fall : 50; output_threshold_pct_rise : 50; output_threshold_pct_fall : 50;",
         "  slew_lower_threshold_pct_rise : 20; slew_lower_threshold_pct_fall : 20; slew_upper_threshold_pct_rise : 80; slew_upper_threshold_pct_fall : 80;",
         "  nom_process : 1; nom_temperature : 25; nom_voltage : 1.8;"]
for k, v in common.items():
    if k.startswith("lu_table_template,del_"):
        name = k.split(",", 1)[1]
        lines.append(f"  lu_table_template ({name}) {{")
        for a in ("variable_1", "variable_2"):
            if a in v:
                lines.append(f"    {a} : {v[a]};")
        for a in ("index_1", "index_2"):
            if a in v:
                lines.append(f'    {a} ("{fmt_list(v[a])}");')
        lines.append("  }")
n = 0
for f in sorted(repo.glob("cells/*/*__tt_025C_1v80.lib.json")):
    d = json.loads(f.read_text())
    if any(k.startswith(("ff,", "latch,", "statetable", "ff_bank")) for k in d):
        continue
    pins = {k.split(",", 1)[1]: v for k, v in d.items() if k.startswith("pin,")}
    outs = [p for p, v in pins.items() if v.get("direction") == "output"]
    if not outs or not all("function" in pins[p] for p in outs):
        continue
    if any(v.get("direction") not in ("input", "output") for v in pins.values()):
        continue
    name = f.name.split("__tt_")[0]
    s = [f"  cell ({name}) {{", f"    area : {d['area']};"]
    for p, v in pins.items():
        s.append(f"    pin ({p}) {{")
        s.append(f"      direction : {v['direction']};")
        if v["direction"] == "input":
            s.append(f"      capacitance : {v.get('capacitance', 0.0)};")
        else:
            s.append(f'      function : "{v["function"]}";')
            tl = v.get("timing", [])
            for t in (tl if isinstance(tl, list) else [tl]):
                s.append("      timing () {")
                s.append(f'        related_pin : "{t["related_pin"]}";')
                if "timing_sense" in t:
                    s.append(f"        timing_sense : {t['timing_sense']};")
                for key, tv in t.items():
                    if isinstance(tv, dict) and key.split(",")[0] in ("cell_rise", "cell_fall", "rise_transition", "fall_transition"):
                        s.append(table(f"{key.split(',')[0]} ({key.split(',')[1]})", tv).rstrip("\n"))
                s.append("      }")
        s.append("    }")
    s.append("  }")
    lines += s
    n += 1
lines.append("}")
out.write_text("\n".join(lines) + "\n")
print(f"写出 {out}：{n} 个组合单元")
