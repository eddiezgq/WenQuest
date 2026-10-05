"""第 51 章的数字工厂界面截图（第 13 轮 8.8，R5）：截图由 textbook/tools/factory_shots.py 在本机起数字工厂、灌测试数据后截取，
存在 textbook/mfgtech/shots/（清单.yaml 记下页面、账号和数据来源）；这里把截图包成书中的图。界面改了，重新运行 factory_shots.py。"""
from pathlib import Path

from PIL import Image

import _mfg as M
from bookout import out

R = M.r3d()
SHOTS = Path(__file__).resolve().parents[2] / "shots"
FIGS = {"fig51_8_2": "shot51_1", "fig51_9_3": "shot51_2"}
for fig, shot in FIGS.items():
    p = SHOTS / f"{shot}.png"
    w, h = Image.open(p).size
    R.save_figure(fig, p.read_bytes(), w // 2, h // 2)

# 图 51.8.2 的数：工序 50 的 locate_check（V 形块、从下母线量），Td 改为 0.3 与 0.25 时 H 的定位误差（与评审员同一个函数）
TL = M.tol()
lc = M.op(M.plan(), 50)["locate_check"]
e = {td: TL.v_block(td, lc["alpha"], lc["measure"]) for td in (lc["Td"], 0.3, 0.25)}
out(e0=e[lc["Td"]], e30=e[0.3], e25=e[0.25], tol=lc["tol"], third=lc["tol"] / 3, td0=lc["Td"])
