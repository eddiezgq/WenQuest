# -*- coding: utf-8 -*-
"""零件库“电子元件”大类第一批（第 88 轮，电子 E4）：关节驱动板 DRV-JOINT 用到的元器件。

每族一个条目（A-ELE-*），规格表一行一个规格；外形取 KiCad 官方三维模型库 7.0.11 的 STEP（仓库 factory/designs/3dmodels，
CC-BY-SA 4.0 附例外，见那里的 LICENSE.md），造型程序 generators/f_kicad.py 原样读入。
电气参数只写设计用到的数值（阻值、容值、耐压），芯片只写封装和示例选型名，其余“见器件手册”，不编。

    python3 tools/import_kicad_ele.py      # 重新生成 catalog/A/A-ELE-*（逐字一致，测试核对）
"""
import csv
import io
import os
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(os.environ.get("WQLIB_SPECS_OUT") or (ROOT / "catalog"))
M3D = "factory/designs/3dmodels"
CHECKED = {"by": "Claude", "on": "2026-11-05",
           "note": "Debian 软件包 kicad-footprints / kicad-packages3d 7.0.11 的 copyright 文件：CC-BY-SA 4.0 附例外（设计与由其生成的文件不受相同方式共享约束）"}
SOURCE = {"origin": "kicad", "repo": "https://gitlab.com/kicad/libraries/kicad-packages3D", "commit": "7.0.11",
          "license": "CC-BY-SA-4.0", "attribution": "外形：KiCad 官方三维模型库 7.0.11（© KiCad Libraries Team，CC-BY-SA 4.0 附例外）；"
                                                     "条目与规格表：问渠零件库", "checked": CHECKED}

FAMILIES = [
    {"id": "A-ELE-R0402", "zh": "贴片电阻 0402", "en": "Chip resistor 0402", "tags": ["电阻", "0402"],
     "params": [("r_ohm", "阻值", "Resistance", "key", "Ω"), ("tol_pct", "精度", "Tolerance", "perf", "%")],
     "rows": [("10R", 10, 1), ("120R", 120, 1), ("1K", 1000, 1), ("6K8", 6800, 1), ("10K", 10000, 1), ("51K", 51000, 1),
              ("100K", 100000, 1), ("147K", 147000, 1)],
     "step": "Resistor_SMD.3dshapes/R_0402_1005Metric.step", "fp": "Resistor_SMD:R_0402_1005Metric", "spice": "R",
     "principle": "厚膜电阻：陶瓷基片上印电阻浆料，两端电极焊在焊盘上。0402 即 1.0 × 0.5 mm（公制 1005），贴片机一次能贴几万只。",
     "uses": ["驱动板的分压、上下拉、滤波", "栅极电阻"]},
    {"id": "A-ELE-C0402", "zh": "贴片陶瓷电容 0402", "en": "Ceramic capacitor 0402", "tags": ["电容", "MLCC", "0402"],
     "params": [("c_f", "容值", "Capacitance", "key", "F"), ("v_rated", "耐压", "Rated voltage", "perf", "V")],
     "rows": [("10P", 10e-12, 50), ("220P", 220e-12, 50), ("1N", 1e-9, 50), ("10N", 10e-9, 50), ("100N", 100e-9, 16),
              ("1U", 1e-6, 25), ("4U7", 4.7e-6, 6.3)],
     "step": "Capacitor_SMD.3dshapes/C_0402_1005Metric.step", "fp": "Capacitor_SMD:C_0402_1005Metric", "spice": "C",
     "principle": "多层陶瓷电容（MLCC）：几十到几百层陶瓷介质与电极交错叠压烧结。容值随直流偏压下降，选型时看器件手册的偏压曲线。",
     "uses": ["芯片电源去耦", "滤波", "晶振负载电容"]},
    {"id": "A-ELE-C1206", "zh": "贴片陶瓷电容 1206", "en": "Ceramic capacitor 1206", "tags": ["电容", "MLCC", "1206"],
     "params": [("c_f", "容值", "Capacitance", "key", "F"), ("v_rated", "耐压", "Rated voltage", "perf", "V")],
     "rows": [("2U2-100V", 2.2e-6, 100), ("10U-25V", 10e-6, 25), ("22U-25V", 22e-6, 25)],
     "step": "Capacitor_SMD.3dshapes/C_1206_3216Metric.step", "fp": "Capacitor_SMD:C_1206_3216Metric", "spice": "C",
     "principle": "尺寸大的 MLCC 耐压高、容值大；放在半桥旁边就近吸收开关电流，回路越小，开关尖峰越小。",
     "uses": ["半桥吸收电容", "稳压器输入输出电容"]},
    {"id": "A-ELE-CPEL", "zh": "贴片铝电解电容", "en": "SMD aluminium electrolytic capacitor", "tags": ["电容", "电解"],
     "params": [("c_f", "容值", "Capacitance", "key", "F"), ("v_rated", "耐压", "Rated voltage", "perf", "V"), ("d_mm", "直径", "Diameter", "dim", "mm"),
                ("h_mm", "高度", "Height", "dim", "mm")],
     "rows": [("470U-63V", 470e-6, 63, 16, 17.5)],
     "step": "Capacitor_SMD.3dshapes/CP_Elec_16x17.5.step", "fp": "Capacitor_SMD:CP_Elec_16x17.5", "spice": "C",
     "principle": "铝电解电容容量大、体积小，适合做母线储能；有极性，等效串联电阻（ESR）和纹波电流决定发热和寿命。",
     "uses": ["48 V 母线电容（电路分析例题 3）"]},
    {"id": "A-ELE-SHUNT", "zh": "采样电阻 2512", "en": "Current shunt 2512", "tags": ["电阻", "采样", "2512"],
     "params": [("r_ohm", "阻值", "Resistance", "key", "Ω"), ("tol_pct", "精度", "Tolerance", "perf", "%")],
     "rows": [("2M", 0.002, 1)],
     "step": "Resistor_SMD.3dshapes/R_2512_6332Metric.step", "fp": "Resistor_SMD:R_2512_6332Metric", "spice": "R",
     "principle": "毫欧级合金电阻串在相线上，电流流过产生几十毫伏压降，由电流采样放大器放大后进 ADC；两端用开尔文引线，焊锡和走线的电阻不进读数。",
     "uses": ["关节驱动板三相电流采样（电路分析例题 1）"]},
    {"id": "A-ELE-LPWR", "zh": "贴片功率电感", "en": "SMD power inductor", "tags": ["电感"],
     "params": [("l_h", "电感量", "Inductance", "key", "H")],
     "rows": [("22U", 22e-6)],
     "step": "Inductor_SMD.3dshapes/L_Bourns_SRN6045TA.step", "fp": "Inductor_SMD:L_Bourns_SRN6045TA", "spice": "L",
     "principle": "降压电源的储能电感：开关导通时储能、关断时向负载放能；电感量由输入输出电压、开关频率和允许的纹波电流算。",
     "uses": ["48 V → 12 V 降压电源"]},
    {"id": "A-ELE-DSCH", "zh": "贴片肖特基二极管", "en": "SMD Schottky diode", "tags": ["二极管", "肖特基"],
     "params": [("v_rated", "反向耐压", "Reverse voltage", "key", "V"), ("pkg", "封装", "Package", "info", "")],
     "rows": [("SMA-60V", 60, "SMA"), ("SOD123-100V", 100, "SOD-123")],
     "step": {"SMA-60V": "Diode_SMD.3dshapes/D_SMA.step", "SOD123-100V": "Diode_SMD.3dshapes/D_SOD-123.step"},
     "fp": "Diode_SMD:D_SMA", "spice": "D",
     "principle": "金属–半导体结，正向压降低、恢复快；用作降压电源的续流二极管和半桥驱动的自举二极管。",
     "uses": ["续流二极管", "自举二极管"]},
    {"id": "A-ELE-MOSTDSON", "zh": "功率 MOSFET（TDSON-8）", "en": "Power MOSFET (TDSON-8)", "tags": ["MOSFET", "功率器件"],
     "params": [("part", "示例选型", "Example part", "key", ""), ("pkg", "封装", "Package", "info", "")],
     "rows": [("BSC040N08NS5", "BSC040N08NS5", "TDSON-8")],
     "step": "Package_TO_SOT_SMD.3dshapes/TDSON-8-1.step", "fp": "Package_TO_SOT_SMD:TDSON-8-1", "spice": "wqfet（通用示例模型，见 cae/circuit.py）",
     "principle": "N 沟道功率 MOSFET：栅极充电到阈值以上导通。三相桥每相上下两只；导通电阻、栅电荷、耐压等参数见器件手册（示例选型，未经硬件验证）。",
     "uses": ["三相逆变桥（电路分析例题 2）"]},
    {"id": "A-ELE-SOIC8", "zh": "SOIC-8 芯片", "en": "SOIC-8 ICs", "tags": ["芯片", "SOIC-8"],
     "params": [("part", "示例选型", "Example part", "key", ""), ("func", "功能", "Function", "info", "")],
     "rows": [("IR2101S", "IR2101S", "半桥栅极驱动"), ("INA240A1D", "INA240A1D", "电流采样放大（20 倍）"),
              ("MCP2562-E-SN", "MCP2562-E/SN", "CAN 收发器"), ("MAX3485", "MAX3485", "RS-485 收发器")],
     "step": "Package_SO.3dshapes/SOIC-8_3.9x4.9mm_P1.27mm.step", "fp": "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", "spice": "",
     "principle": "小外形封装 8 脚、脚距 1.27 mm。驱动板上的栅极驱动、电流采样放大、通信收发都是这个封装（示例选型，引脚取自 KiCad 官方符号库）。",
     "uses": ["栅极驱动", "电流采样", "CAN、RS-485"]},
    {"id": "A-ELE-LQFP48", "zh": "LQFP-48 微控制器", "en": "LQFP-48 microcontroller", "tags": ["芯片", "MCU"],
     "params": [("part", "示例选型", "Example part", "key", ""), ("pkg", "封装", "Package", "info", "")],
     "rows": [("STM32G431CBT6", "STM32G431CBT6", "LQFP-48 7×7")],
     "step": "Package_QFP.3dshapes/LQFP-48_7x7mm_P0.5mm.step", "fp": "Package_QFP:LQFP-48_7x7mm_P0.5mm", "spice": "",
     "principle": "电机控制 MCU：定时器出三相互补 PWM、ADC 同步采电流、编码器接口、CAN；脚距 0.5 mm，贴片和 AOI 要求高（示例选型）。",
     "uses": ["关节驱动板主控"]},
    {"id": "A-ELE-SOT", "zh": "SOT 封装稳压芯片", "en": "SOT regulators", "tags": ["芯片", "电源"],
     "params": [("part", "示例选型", "Example part", "key", ""), ("pkg", "封装", "Package", "info", "")],
     "rows": [("LMR16006YQ", "LMR16006YQ", "SOT-23-6"), ("AMS1117-5.0", "AMS1117-5.0", "SOT-223"), ("AMS1117-3.3", "AMS1117-3.3", "SOT-223")],
     "step": {"LMR16006YQ": "Package_TO_SOT_SMD.3dshapes/SOT-23-6.step", "AMS1117-5.0": "Package_TO_SOT_SMD.3dshapes/SOT-223.step",
              "AMS1117-3.3": "Package_TO_SOT_SMD.3dshapes/SOT-223.step"},
     "fp": "Package_TO_SOT_SMD:SOT-23-6", "spice": "",
     "principle": "降压芯片（开关电源，效率高）把 48 V 降到 12 V；线性稳压（简单、安静、效率低）再出 5 V 和 3.3 V（示例选型）。",
     "uses": ["驱动板辅助电源"]},
    {"id": "A-ELE-XTAL", "zh": "贴片晶振 3225", "en": "Crystal 3225", "tags": ["晶振"],
     "params": [("f_hz", "频率", "Frequency", "key", "Hz")],
     "rows": [("8MHZ", 8e6)],
     "step": "Crystal.3dshapes/Crystal_SMD_3225-4Pin_3.2x2.5mm.step", "fp": "Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm", "spice": "",
     "principle": "石英晶体谐振器给 MCU 提供准确时钟（CAN 通信要求时钟准）；两只负载电容接地。",
     "uses": ["MCU 外部时钟"]},
    {"id": "A-ELE-TB", "zh": "接线端子（5.0 mm）", "en": "Terminal block 5.0 mm", "tags": ["连接器", "端子"],
     "params": [("n_pin", "位数", "Positions", "key", ""), ("pitch_mm", "间距", "Pitch", "dim", "mm")],
     "rows": [("2P", 2, 5.0), ("3P", 3, 5.0)],
     "step": {"2P": "TerminalBlock_Phoenix.3dshapes/TerminalBlock_Phoenix_MKDS-1,5-2_1x02_P5.00mm_Horizontal.step",
              "3P": "TerminalBlock_Phoenix.3dshapes/TerminalBlock_Phoenix_MKDS-1,5-3_1x03_P5.00mm_Horizontal.step"},
     "fp": "TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-2_1x02_P5.00mm_Horizontal", "spice": "",
     "principle": "螺钉压线端子，通孔插件，在后段选择焊上焊；接 48 V 电源和电机三相。",
     "uses": ["母线输入", "电机输出"]},
    {"id": "A-ELE-XH", "zh": "线对板连接器（2.5 mm）", "en": "Wire-to-board connector 2.5 mm", "tags": ["连接器"],
     "params": [("n_pin", "针数", "Pins", "key", ""), ("pitch_mm", "间距", "Pitch", "dim", "mm")],
     "rows": [("4P", 4, 2.5), ("5P", 5, 2.5), ("6P", 6, 2.5)],
     "step": {"4P": "Connector_JST.3dshapes/JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical.step",
              "5P": "Connector_JST.3dshapes/JST_XH_B5B-XH-A_1x05_P2.50mm_Vertical.step",
              "6P": "Connector_JST.3dshapes/JST_XH_B6B-XH-A_1x06_P2.50mm_Vertical.step"},
     "fp": "Connector_JST:JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical", "spice": "",
     "principle": "2.5 mm 间距线对板连接器，通孔插件；接编码器和 CAN 总线。",
     "uses": ["编码器", "CAN"]},
]


def build():
    files = {}
    for f in FAMILIES:
        keys = [p[0] for p in f["params"]]
        buf = io.StringIO()
        w = csv.writer(buf, lineterminator="\n")
        w.writerow(["size"] + keys + ["step"])
        for r in f["rows"]:
            step = f["step"][r[0]] if isinstance(f["step"], dict) else f["step"]
            w.writerow([r[0]] + ["{:g}".format(x) if isinstance(x, float) else x for x in r[1:]] + [step])
        e = {"schema": 1, "id": f["id"], "kind": "family", "name": {"zh": f["zh"], "en": f["en"]}, "category": "ELE", "tags": f["tags"],
             "params": [{"key": k, "zh": zh + ("（{}）".format(u) if u else ""), "en": en, "role": role} for k, zh, en, role, u in f["params"]]
             + [{"key": "step", "zh": "外形文件", "en": "Shape file", "role": "info"}],
             "specs": "specs.csv", "default": f["rows"][0][0],
             "model": {"engine": "kicad:" + M3D, "formats": ["step", "glb"], "origin": "KiCad 封装原点（焊盘中心），Z 向上",
                       "note": "外形原样取自 KiCad 官方三维模型库；封装（焊盘）{}；SPICE 模型：{}".format(f["fp"], f["spice"] or "无（芯片看器件手册）")},
             "source": SOURCE, "teaching": {"principle": f["principle"], "uses": f["uses"], "courses": [{"course": "电子技术基础"}]},
             }
        head = "# {} · {}（电子元件第一批，第 88 轮；由 tools/import_kicad_ele.py 生成）\n".format(f["id"], f["zh"])
        files[(f["id"], "entry.yaml")] = head + yaml.safe_dump(e, allow_unicode=True, sort_keys=False, width=200)
        files[(f["id"], "specs.csv")] = buf.getvalue()
    return files


def main():
    for (eid, fn), text in build().items():
        d = OUT / "A" / eid
        d.mkdir(parents=True, exist_ok=True)
        (d / fn).write_text(text, encoding="utf-8")
    print("写了 {} 个条目".format(len(FAMILIES)))


if __name__ == "__main__":
    main()
