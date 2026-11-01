"""第 54 章的数字工厂界面截图（第 13 轮 9.4（3））：截图由 textbook/tools/factory_shots.py 在本机起数字工厂、用仿真车间的误差模型
灌一个班次的测量数据（正常 30 件 → 老师注入“磨床尾座偏移” → 22 件 → 学生开 8D、老师批准“校正尾座” → 20 件）后截取，
存在 textbook/mfgtech/shots/（清单.yaml 记下页面、账号和数据来源）；这里把截图包成书中的图。界面改了，重新运行 factory_shots.py。"""
from pathlib import Path

from PIL import Image

import _mfg as M

R = M.r3d()
SHOTS = Path(__file__).resolve().parents[2] / "shots"
FIGS = {"fig54_7_6": "shot54_0", "fig54_8_5": "shot54_1", "fig54_8_6": "shot54_2", "fig54_9_5": "shot54_3"}
for fig, shot in FIGS.items():
    p = SHOTS / f"{shot}.png"
    w, h = Image.open(p).size
    R.save_figure(fig, p.read_bytes(), w // 2, h // 2)
