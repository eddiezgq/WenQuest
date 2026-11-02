"""第 56 章的数字工厂界面截图（第 13 轮十二）：截图由 textbook/tools/factory_shots.py（--only 56）在本机起数字工厂，学生提交 SH-101 的
两份路线（本章的参照路线 std/SH-101_route.yaml，和把铣键槽挪到渗碳淬火、磨削之后的一份），下达任务单 TS-56-1 后截取，
存在 textbook/mfgtech/shots/（清单.yaml 记下页面、账号和数据来源）；这里把截图包成书中的图。界面改了，重新运行 factory_shots.py。"""
from pathlib import Path

from PIL import Image

import _mfg as M

R = M.r3d()
SHOTS = Path(__file__).resolve().parents[2] / "shots"
FIGS = {"fig56_9_6": "shot56_1", "fig56_10_4": "shot56_2", "fig56_10_5": "shot56_3"}
for fig, shot in FIGS.items():
    p = SHOTS / f"{shot}.png"
    w, h = Image.open(p).size
    R.save_figure(fig, p.read_bytes(), w // 2, h // 2)
