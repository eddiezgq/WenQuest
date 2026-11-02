"""算例 57.9.1：一份初学者的 SH-101 工序设计草稿交 AI 工艺评审员预检。草稿在 std/SH-101_process.yaml 上改出六处常见错误：
① 半精车轴承位只留 Ø25.2（磨削余量太小）；② 粗车尺寸标成 Ø26.5（+0.1/−0.1），不是入体；③ 粗车想少走几刀：ap 6、f 0.4；
④ 铣键槽的单件工时只写 4 min（工步时间合计都不够）；⑤ 槽底尺寸 H 取 16.5（直接抄图纸的 d − t₁，没有换算）；
⑥ 齿轮左端面从左端面编程、公差 ±0.1（8 ± 0.1 保证不了）。画图 57.9.2（评审员的意见）。"""
import copy

import _mfg as M
from bookout import T, out, style

P = M.plan101()
d = copy.deepcopy(P)
ops = {o["seq"]: o for o in d["operations"]}
next(f for f in ops[30]["features"] if f["name"] == "轴承位")["size_mm"] = 25.2              # ①
r = next(f for f in ops[20]["features"] if f["name"] == "轴承位")
r["es_mm"], r["ei_mm"] = 0.1, -0.1                                                          # ②
ops[20]["cut"].update(ap_mm=6.0, f_mm_r=0.4)                                                # ③
ops[50]["minutes"] = 4                                                                      # ④
d["chains"][0]["links"][0].update(nominal=16.5)                                             # ⑤
c = next(c for c in d["tolerance_chart"]["cuts"] if c["seq"] == 30.24)
c.update(ref="L", nominal=81, es=0.1, ei=-0.1, label="工序 30 从左端面编程车齿轮左端面")                                            # ⑥
f = M.review(d)
sel = [x for x in f if x["level"] in ("error", "warning")]
err = [x for x in sel if x["level"] == "error"]
warn = [x for x in sel if x["level"] == "warning"]
plt = style()
LV = {"error": T("必须改", "must fix"), "warning": T("建议", "advice")}
rows = [[LV[x["level"]], x["rule"], str(x["seq"] or "—"), x["text"]] for x in sel]
cols = {(i, 0): (M.RED if x["level"] == "error" else M.WARM) for i, x in enumerate(sel)}
M.table_fig(plt, [T("级别", "level"), T("规则", "rule"), T("工序", "op"), T("意见", "comment")], rows, [0.09, 0.1, 0.07, 0.74], "fig57_9_2", cols, fontsize=6.6)
rules = sorted({x["rule"] for x in sel})
out(n=len(sel), n_err=len(err), n_warn=len(warn), score=M.proc().suggested_score(f), rules="、".join(rules), n_rules=len(rules),
    score_ref=M.proc().suggested_score(M.review(P)))
