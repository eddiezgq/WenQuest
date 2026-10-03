"""50.9 节：一份工艺数据驱动三个系统——核对 SH-301 的工艺规程与 ERPNext 工艺路线、质量系统检验模板、仿真车间的测量项目是否一致，
并让 AI 工艺评审员和卡片生成器各检查一遍。"""
import _mfg as M
from bookout import T, out
from hub import process
from sim import errors as ERR

p = M.plan()
F = M.F
route = F.ROUTINGS[F.BOMS["SH-301"][0]]
erp_ok = [(o["operation"], o["minutes"]) for o in p["operations"]] == list(route)
tmpl = F.inspection_templates()["零件检验-输出轴"]
names = [t["parameter"] for t in tmpl]
qms_chars = [c for c in p["characteristics"] if c.get("qms")]
qms_ok = all(c["qms"] in names for c in qms_chars)
measured = [c[0] for c in ERR.CHARS]
findings = process.review(p)
problems = M.cards.check(p)
not_in_erp = len(p["characteristics"]) - len(qms_chars)
ok = T("一致", "consistent")
bad = T("不一致", "inconsistent")
out(erp_ok=erp_ok, qms_ok=qms_ok, erp_txt=ok if erp_ok else bad, qms_txt=ok if qms_ok else bad, n_tmpl=len(names), n_qms_chars=len(qms_chars), n_measured=len(measured), not_in_erp=not_in_erp,
    n_findings=len(findings), n_problems=len(problems), n_chars=len(p["characteristics"]))
