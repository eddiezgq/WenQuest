"""第 138 轮 G4.8：8 种变型的选配件清单 → docs/设计/WQ-LS/G4/选配件清单.json

    python3 tools/wqls/g4_opt_bom.py <带 T,E 的零件目录>      （零件目录里的 parts.json 有每个零件的质量）

T、E 的零件来自 cad/opt.py；D 只是旋梭镀 DLC 膜（不改形状，工艺卡加一道镀膜工序）。带 E 的去掉 G4.7 的机械针距件。
"""
import itertools
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "设计" / "WQ-LS" / "G4" / "选配件清单.json"
T_PARTS = {"moving_knife": "动刀", "knife_shaft": "动刀轴（含曲柄）", "fixed_knife": "定刀", "trim_base": "动刀轴座",
           "trim_cam": "剪线凸轮", "trim_lever": "剪线摆杆", "trim_roller": "滚子 Ø8", "trim_rock": "剪线摆轴（含曲柄）",
           "trim_link": "球头拉杆", "trim_brackets": "摆轴座（两个，右边托电磁铁）", "trim_solenoid": "剪线电磁铁 24 V Ø22",
           "wiper": "拨线钩（钢丝 Ø0.8、轴、小曲柄）", "wiper_solenoid": "拨线电磁铁 24 V Ø16",
           "release_arm_t": "立轴拨杆加的臂", "release_solenoid": "松线电磁铁 24 V Ø16（含支架）"}
E_PARTS = {"estep_motor": "42 步进电机 48 mm（带磁编码器）", "estep_bracket": "电机板", "estep_pulley_m": "电机带轮 12 齿",
           "estep_pulley_r": "调节器带轮 24 齿", "estep_belt": "同步带 HTD 3M 宽 9", "reverse_button": "倒缝按钮"}
E_REMOVE = {"pull_rod": "针距拉杆", "stitch_dial": "针距旋钮（槽轮）", "reverse_lever": "倒缝扳手", "reverse_spring": "拉簧"}


def main():
    pj = json.loads((Path(sys.argv[1]) / "parts.json").read_text())["parts"]
    g = {k: v.get("mass_g") for k, v in pj.items()}
    rows = []
    for t, e, d in itertools.product((0, 1), repeat=3):
        name = "WQ-LS" + ("-" + "".join(c for c, f in zip("TED", (t, e, d)) if f) if (t or e or d) else "")
        add = {**(T_PARTS if t else {}), **(E_PARTS if e else {})}
        rows.append(dict(model=name, T=bool(t), E=bool(e), D=bool(d), add=sorted(add), remove=sorted(E_REMOVE) if e else [],
                         mass_add_g=round(sum(g.get(k) or 0 for k in add), 1),
                         mass_remove_g=(round(sum(g[k] for k in E_REMOVE), 1) if all(g.get(k) for k in E_REMOVE) else "unknown") if e else 0.0,
                         process_extra=(["旋梭（梭床、梭尖）镀 DLC 膜，膜厚 2–3 µm"] if d else [])
                         + (["合件工序 80 第 9 步：选 T 的孔"] if t else []) + (["合件工序 80 第 9 步：选 E 的孔；立柱旋钮、倒缝扳手孔不加工，装盖板"] if e else [])))
    out = dict(note="8 种变型；质量按三维零件（钢 7.85、铝 2.75、塑料 1.2、电磁铁和电机按铜 8.9 g/cm³ 粗算）", names={**T_PARTS, **E_PARTS},
               removed_by_E=E_REMOVE, variants=rows)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1))
    for r in rows:
        print(r["model"], len(r["add"]), r["mass_add_g"], "-", r["mass_remove_g"])


if __name__ == "__main__":
    main()
