"""第 55 章的数字工厂界面截图（第 13 轮 11.4（5））：截图由 textbook/tools/factory_shots.py（--only 55）在本机起数字工厂、用仿真车间的误差模型
灌一批 SH-301 的测量数据（正常 30 件 → 老师注入“砂轮修整不锋利” → 30 件），并提交一份把工序 60 的磨削切深改大、取消光磨的工艺规程后截取，
存在 textbook/mfgtech/shots/（清单.yaml 记下页面、账号和数据来源）；这里把截图包成书中的图。界面改了，重新运行 factory_shots.py。"""
from pathlib import Path

from PIL import Image

import _mfg as M

R = M.r3d()
SHOTS = Path(__file__).resolve().parents[2] / "shots"
FIGS = {"fig55_2_9": "shot55_1", "fig55_5_10": "shot55_2", "fig55_7_7": "shot55_3"}
for fig, shot in FIGS.items():
    p = SHOTS / f"{shot}.png"
    w, h = Image.open(p).size
    R.save_figure(fig, p.read_bytes(), w // 2, h // 2)
