"""第 53 章的数字工厂界面截图（第 13 轮 8.8，R5）：截图由 textbook/tools/factory_shots.py 在本机起数字工厂、灌测试数据后截取，
存在 textbook/mfgtech/shots/（清单.yaml 记下页面、账号和数据来源）；这里把截图包成书中的图。界面改了，重新运行 factory_shots.py。"""
from pathlib import Path

from PIL import Image

import _mfg as M

R = M.r3d()
SHOTS = Path(__file__).resolve().parents[2] / "shots"
FIGS = {"fig53_9_1": "shot53_1", "fig53_9_2": "shot53_2"}
for fig, shot in FIGS.items():
    p = SHOTS / f"{shot}.png"
    w, h = Image.open(p).size
    R.save_figure(fig, p.read_bytes(), w // 2, h // 2)
