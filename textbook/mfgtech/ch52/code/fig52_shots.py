"""第 52 章的数字工厂界面截图（第 13 轮 8.8，R5）：截图由 textbook/tools/factory_shots.py 在本机起数字工厂、灌测试数据后截取，
存在 textbook/mfgtech/shots/（清单.yaml 记下页面、账号和数据来源）；这里把截图包成书中的图。界面改了，重新运行 factory_shots.py。"""
from pathlib import Path

from PIL import Image

import copy

import _mfg as M
from bookout import out

R = M.r3d()
SHOTS = Path(__file__).resolve().parents[2] / "shots"
FIGS = {"fig52_9_9": "shot52_1", "fig52_9_10": "shot52_2"}
for fig, shot in FIGS.items():
    p = SHOTS / f"{shot}.png"
    w, h = Image.open(p).size
    R.save_figure(fig, p.read_bytes(), w // 2, h // 2)

# 图 52.9.9 的数：夹具数据 hand_force 改为 10 N（扭矩 1 N·m）后，评审员核算的夹紧力（与评审员同一个函数 hub/fixture.py analyse）
FX = M.fx()
weak = copy.deepcopy(M.fixture_data())
weak["clamping"]["hand_force"] = 10
r = FX.analyse(weak)
out(W_weak=r["W_have"], W_need=r["need"]["W"], torque_weak=weak["clamping"]["hand_force"] * weak["clamping"]["wrench"] / 1000)
