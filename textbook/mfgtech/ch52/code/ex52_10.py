"""52.10 节：算例 52.10.1——V 形块磨损多少就该换？由接触几何（第 51 章 v_block_contact）求一个工作面磨损与键槽对称度的关系，
结合仿真车间的对称度分布（sim/errors.py），定出更换界限和检查周期；并说明问题情景“键槽夹具定位元件磨损”相当于磨损多少。"""
import math
import sys

import _mfg as M
from bookout import out

TL = M.tol()
sys.path.insert(0, str(M.REPO / "factory" / "digital"))
from sim import errors as SE  # noqa: E402

# 一个工作面磨损 w：轴心水平偏移 cx(w)，对称度公差带占用 2·cx
w0 = 0.01
cx, _ = TL.v_block_contact(None, 90, wear_left=w0, radius=40.3 / 2)
k = TL.offset_to_zone(abs(cx)) / w0                     # 每 1 mm 磨损占用的对称度
# 仿真车间里正常的对称度：均值 0.006、标准差 0.002（sim/errors.py 的模型参数，代表对刀、铣刀偏摆等其他误差）
src = (M.REPO / "factory" / "digital" / "sim" / "errors.py").read_text(encoding="utf-8")
assert "sym_mean, sym_sd = 0.006, 0.002" in src
mu, sd, T_sym = 0.006, 0.002, 0.02
w_limit = (T_sym - (mu + 3 * sd)) / k                   # 均值 + 3σ 碰到公差时的磨损量
cpk_new = (T_sym - mu) / (3 * sd)                        # 对称度只有上限
# 问题情景注入的对称度均值增量相当于多大磨损
inj = SE.PROBLEMS["locator_worn"]["default"]
w_inj = inj / k
# 磨损速度（教学假设）：20Cr 渗碳淬火的 V 形块，每装卸 1000 件磨损约 0.5 µm
rate = 0.0005 / 1000
life = w_limit / rate
check_every = 500
out(w0=w0, cx=abs(cx), k=k, mu=mu, sd=sd, w_limit=w_limit, w_limit_um=w_limit * 1000, cpk_new=cpk_new, inj=inj, w_inj=w_inj * 1000,
    rate_um=rate * 1000 * 1000, life=life, check_every=check_every, checks=life / check_every)
