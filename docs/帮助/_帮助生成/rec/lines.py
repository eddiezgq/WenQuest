# -*- coding: utf-8 -*-
"""录屏配音第一步（第 90 轮）：从录屏脚本里找出 say('…') 的每一句，用开源 Kokoro 中文声音合成（tools/video/voice.py，
离线，不调外部服务），写 durations.json（句子 → 秒数、WAV 路径）。录屏脚本按这个时长等配音读完再做下一步。

  WQ_TTS_MODELS=<模型目录> python3 lines.py <输出目录> 脚本1.js 脚本2.js …

字幕照原文显示；配音读法里的数字、单位由 voice.zh_numbers 转成口语（0.94 → 零点九四）。
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "tools" / "video"))
import voice as V  # noqa: E402

SAY = re.compile(r"""say\(\s*(['"`])(.+?)\1""")
SPOKEN = {"FreeCAD": "free cad", "WenQuest": "问渠", "DXF": "D X F", "CAE": "C A E", "PDF": "P D F", "SPC": "统计过程控制", "µm": "微米", "N·m": "牛米", "r/min": "转每分", "MPa": "兆帕", "mm": "毫米", "rad/s²": "弧度每二次方秒", "µrad": "微弧度",
          "N/µm": "牛每微米", "N·m/mrad": "牛米每毫弧度", "°C": "摄氏度", "kN": "千牛", "Hz": "赫兹", "%": "百分之"}


def spoken(text: str) -> str:
    s = text
    for k, v in SPOKEN.items():
        if k == "%":
            s = re.sub(r"(\d+(?:\.\d+)?)\s*%", lambda m: "百分之" + m.group(1), s)
        else:
            s = s.replace(k, v)
    s = s.replace("—", "，").replace("→", "到").replace("/", "或").replace("×", "乘").replace("±", "正负")
    return V.zh_numbers(s)


def main():
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    texts = []
    for f in sys.argv[2:]:
        for m in SAY.finditer(Path(f).read_text(encoding="utf-8")):
            if m.group(2) not in texts:
                texts.append(m.group(2))
    v = V.Voice("kokoro", "zh", out / "cache")
    d = {}
    for t in texts:
        p, sec = v.say(spoken(t))
        d[t] = {"sec": round(sec, 3), "wav": str(p)}
    (out / "durations.json").write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    print(len(d), "lines,", round(sum(x["sec"] for x in d.values()), 1), "s of speech")


if __name__ == "__main__":
    main()
