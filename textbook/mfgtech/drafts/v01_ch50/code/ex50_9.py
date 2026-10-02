"""50.9 节：计算机辅助工艺规划与 AI 工艺评审员（算例 50.9.1）——一份初学者的 SH-301 工艺规程草稿，评审员提了哪些意见、建议分多少。"""
import copy

import _mfg as M
from bookout import out
from hub import process

p = M.plan()
d = copy.deepcopy(p)
ops = d["operations"]
for f in ops[3]["features"]:          # ① 想省掉磨削：精车直接做到 IT6
    f["ei_mm"] = -0.016
ops[1]["cut"].update(ap_mm=4.0, f_mm_r=0.5, vc_m_min=150)      # ② 粗车想一刀切完
ops[4], ops[5] = ops[5], ops[4]        # ③ 键槽放到磨削之后
for k, o in enumerate(ops):
    o["seq"] = 10 * (k + 1)
d["attachments"] = []                  # ④ 没附计算书
f = process.review(d)
err = [x for x in f if x["level"] == "error"]
warn = [x for x in f if x["level"] == "warning"]
P, Fc, _ = process.cutting_power_kw("45", ops[1]["cut"])
out(n=len(f), n_err=len(err), n_warn=len(warn), score=process.suggested_score(f), P=P, Fc=Fc, P_in=P / 0.8,
    **{f"f{i + 1}": f"〔{x['rule']}·{'必须改' if x['level'] == 'error' else '建议'}〕" + (f"工序 {x['seq']}：" if x["seq"] else "") + x["text"]
       for i, x in enumerate(f)})
