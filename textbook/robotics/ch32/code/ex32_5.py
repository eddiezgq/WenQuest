"""32.5 节的计算：丝杠——SCARA（零件库 B-SCA-WQ4）的竖直轴。

算例 32.5.1：竖直轴要举起 3 kg（2 kg 负载 + 1 kg 花键轴与夹爪，示例值），行程取零件库 B-SCA-WQ4 的默认值。比较两种丝杠：
  梯形丝杠 Tr16×4（零件库 C-SCN-LEAD 的默认尺寸，中径约 d − P/2，牙型半角 15°，钢—青铜摩擦系数取 0.1，示例值）；
  滚珠丝杠 16×10（滚动摩擦，当量摩擦系数取 0.005，示例值；升角按钢球中心圆，约为公称直径）。
  螺旋升角 λ = atan(P / (π d₂))，当量摩擦角 φ′ = atan(μ / cos β)，效率 η = tan λ / tan(λ + φ′)，λ ≤ φ′ 时自锁；
  电机力矩 T = F P / (2π η)；电机 3000 r/min 时的升降速度 v = n P；走完行程的时间。
"""
import math

import yaml

from _ch32 import G0, ROOT
from bookout import out

sca = yaml.safe_load((ROOT / "library" / "catalog" / "B" / "B-SCA-WQ4" / "entry.yaml").read_text(encoding="utf-8"))
lead = yaml.safe_load((ROOT / "library" / "catalog" / "C" / "C-SCN-LEAD" / "entry.yaml").read_text(encoding="utf-8"))
stroke = float(sca["defaults"]["stroke_m"])
d_tr, P_tr = float(lead["defaults"]["diameter_mm"]), float(lead["defaults"]["lead_mm"])
F = 3.0 * G0
n = 3000.0


def screw(d, P, mu, beta_deg, d2=None):
    d2 = d - P / 2 if d2 is None else d2
    lam = math.atan(P / (math.pi * d2))
    phi = math.atan(mu / math.cos(math.radians(beta_deg)))
    eta = math.tan(lam) / math.tan(lam + phi)
    T = F * P / 1000 / (2 * math.pi * eta)
    v = n / 60 * P / 1000
    return {"lam": math.degrees(lam), "phi": math.degrees(phi), "eta": eta, "lock": lam <= phi, "T": T, "v": v, "t": stroke / v}


tr = screw(d_tr, P_tr, 0.10, 15.0)
ball = screw(16.0, 10.0, 0.005, 0.0, d2=16.0)          # 滚珠丝杠按钢球中心圆直径（约等于公称直径）
assert tr["lock"] and not ball["lock"] and ball["eta"] > 2 * tr["eta"]
out(stroke=stroke, F=F, d_tr=d_tr, P_tr=P_tr, **{f"tr_{k}": v for k, v in tr.items() if k != "lock"}, **{f"b_{k}": v for k, v in ball.items() if k != "lock"})
