"""第 57 章的数字工厂界面截图（第 13 轮十三）：截图由 textbook/tools/factory_shots.py（--only 57）在本机起数字工厂，学生提交 SH-101 的
全套工艺规程（std/SH-101_process.yaml）两次，老师批准其中一份成为生效版本，下达任务单 TS-57-1 后截取，
存在 textbook/mfgtech/shots/（清单.yaml 记下页面、账号和数据来源）；这里把截图包成书中的图。界面改了，重新运行 factory_shots.py。"""
from pathlib import Path

from PIL import Image

import _mfg as M

R = M.r3d()
SHOTS = Path(__file__).resolve().parents[2] / "shots"
FIGS = {"fig57_9_3": "shot57_1", "fig57_9_4": "shot57_2", "fig57_9_5": "shot57_3"}
for fig, shot in FIGS.items():
    p = SHOTS / f"{shot}.png"
    w, h = Image.open(p).size
    R.save_figure(fig, p.read_bytes(), w // 2, h // 2)
