# -*- coding: utf-8 -*-
"""缝纫机企业解决方案演示稿（第 44 轮）引用的数字：全部由缝纫机设计软件的计算核心（services/gateway/app/sewcore）算出。
单独运行打印出来核对；设了 WQ_BOOK_OUT 时交给演示稿和介绍视频（{{sol_enterprise.键:格式}}）。"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT / "services" / "gateway"))

from app import sewcore  # noqa: E402
from app.sewcore import cover as C  # noqa: E402
from app.sewcore import design as D  # noqa: E402
from app.sewcore import embroid as E  # noqa: E402
from app.sewcore import pattern as P  # noqa: E402

# 五种机型、各自的校核项数
checks = {k: len(sewcore.get(k).analyze({})["checks"]) for k in sewcore.ORDER}
greens = all(sewcore.get(k).analyze({})["ok"] for k in sewcore.ORDER)

# 平缝机：转速 5000 → 6000，哪几项变红；针杆组件减轻、机壳加筋后全绿
FIX = {"n": 6000, "mr": 0.10, "fn": 240}
r6 = D.analyze({"n": 6000})
red6 = [c for c in r6["checks"] if c["state"] != "ok"]
needle6 = next(c for c in r6["checks"] if c["key"] == "needle_force")
rfix = D.analyze(FIX)
fixed_ok = all(c["state"] == "ok" for c in rfix["checks"])
p0 = D.clean({})

# 绷缝机：一单 T 恤下摆的用线和线团
cv = C.analyze({})
cvp = C.clean({})
plan = cv["tables"][0]["rows"][-1]

# 花样机：针距 3 mm 的转速上限；X 轴电机带轮半径 15 → 10 mm
W = P.window(1.5)[2]
nmax3 = P.n_max(W, P.t_axis(3, 50, 1))
nmax6 = P.n_max(W, P.t_axis(6, 50, 1))
duty = W / 360
m15 = P.axis_motor(3, 50, 15, 0.3, 1.27, 3.8, 0.05, 1, 3000, duty)
m10 = P.axis_motor(3, 50, 10, 0.3, 1.27, 3.8, 0.05, 1, 3000, duty)

# 刺绣机：8 头、7 mm 缎纹、800 r/min；头数与效率
a7 = E.a_req(7, 800)
am8 = E.a_max(8)
n8_7 = E.n_max(7, am8)
ep = E.clean({"n": 800})
eff = {h: E.production(ep, h, 800) for h in (4, 8, 15, 20)}

# 花样模板（圆，槽宽 5、板厚 3）
try:
    from app.sewcore import template as T
    tg = T.geom({"pat": "circle"}, 5, 3)
    tpl = dict(tpl_w=tg["plate"][0], tpl_h=tg["plate"][1], tpl_b=tg["bridges"])
except ImportError:              # 没装 shapely
    tpl = {}

# 人才培养：教材讲数、网页版教材里的虚拟实验与三维模型页数
import yaml  # noqa: E402
BOOK = Path(__file__).resolve().parents[2]
lessons = len(yaml.safe_load((BOOK / "course" / "course.yaml").read_text(encoding="utf-8"))["lessons"])
labs = len(list((BOOK / "src" / "zh" / "labs").glob("*.html")))

V = dict(lessons=lessons, labs=labs, red6_bad=sum(c["state"] == "bad" for c in red6), red6_warn=sum(c["state"] == "warn" for c in red6),
         machines=len(sewcore.ORDER), checks_all=sum(checks.values()), ck_ls=checks["lockstitch"], ck_ol=checks["overlock"],
         ck_cv=checks["cover"], ck_pt=checks["pattern"], ck_em=checks["embroid"],
         n6=6000, red6=len(red6), F6=float(needle6["value"]["zh"].split()[0]), Flim=p0["F_lim"],
         mr0=p0["mr"] * 1000, mr1=FIX["mr"] * 1000, fn0=p0["fn"], fn1=FIX["fn"], fixed_ok=int(fixed_ok),
         cv_q=cvp["Q"], cv_len=cvp["Lcm"], cv_m=float(plan[2].replace(",", "")), cv_cones=int(plan[3]),
         nmax3=nmax3, nmax6=nmax6, rms15=m15["Trms"], rms10=m10["Trms"], rated=1.27,
         a7=a7, am8=am8, n8_7=n8_7, **{f"eff{h}": eff[h]["eff"] * 100 for h in eff}, **{f"pph{h}": eff[h]["pph"] for h in eff}, **tpl)

if __name__ == "__main__":
    for k, v in V.items():
        print(k, v)
    print("red at 6000:", [c["name"]["zh"] for c in red6], "defaults all green:", greens)
    if os.environ.get("WQ_BOOK_OUT"):
        from bookout import out
        out(**V)
