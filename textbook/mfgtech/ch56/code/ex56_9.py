"""算例 56.0.1、56.9.1、56.9.2：把工艺路线交给 AI 工艺评审员（与数字工厂“AI 预检”同一个函数 hub/process.review）。
56.0.1 工厂 ERP 里的现行工序（RT-齿轮轴，只有工序名和工时）补上毛坯后预检；
56.9.1 第 56 章拟定的路线（std/SH-101_route.yaml）预检；
56.9.2 几种排错的路线：铣键槽挪到渗碳淬火之后、滚齿挪到淬火之后、去掉热处理后的磨削、不修研中心孔、磨削余量只留 0.12。
画图 56.0.2（现行工序的意见）、56.9.5（各种排错的路线被找出的意见）。"""
import copy

import _mfg as M
from bookout import T, figure, out, style

proc = M.proc()
ref = M.route101()
fp = proc.factory_plan("SH-101")
fp["blank"] = {"kind": "热轧圆钢", "spec": "Ø60"}
f_fact = M.review(fp)
f_ref = M.review(ref)


def move(p, seq, before):
    o = next(x for x in p["operations"] if x["seq"] == seq)
    p["operations"].remove(o)
    i = next(k for k, x in enumerate(p["operations"]) if x["seq"] == before)
    p["operations"].insert(i, o)
    o["seq"] = before - 5                      # 挪过去的工序重新编号（否则还会多出一条“工序号要从小到大”的意见）


def variant(name):
    p = copy.deepcopy(ref)
    if name == "key":
        move(p, 50, 80)
    elif name == "hob":
        move(p, 40, 70)
    elif name == "nogrind":
        p["operations"] = [o for o in p["operations"] if o["seq"] != 70]
    elif name == "center":
        next(o for o in p["operations"] if o["seq"] == 70)["content"] = "两顶尖装夹，粗磨、精磨两处轴承位、密封轴颈和轴伸"
    elif name == "allow":
        for f in next(o for o in p["operations"] if o["seq"] == 30)["features"]:
            if f["name"] == "轴承位":
                f["size_mm"] = 25.12
    elif name == "skip":
        o = next(o for o in p["operations"] if o["seq"] == 30)
        o["features"] = [f for f in o["features"] if f["name"] != "轴承位"]
    return p


VAR = [("key", T("铣键槽挪到渗碳淬火之后", "keyway after carburizing")), ("hob", T("滚齿挪到渗碳淬火之后", "hobbing after carburizing")),
       ("nogrind", T("去掉热处理后的磨削", "no grinding after hardening")), ("center", T("磨削前不修研中心孔", "no centre-hole lapping")),
       ("allow", T("轴承位半精车只到 Ø25.12（磨量太小）", "semi-turned only to Ø25.12")), ("skip", T("轴承位粗车后直接磨", "bearing seat: rough-turned then ground"))]
res = {}
for k, name in VAR:
    f = [x for x in M.review(variant(k)) if x["rule"] == "路线" and x["level"] in ("error", "warning")]
    res[k] = f
score = {k: proc.suggested_score(M.review(variant(k))) for k, _ in VAR}

plt = style()


LV = {"error": T("必须改", "must fix"), "warning": T("建议", "advice"), "info": T("说明", "note")}


HEAD = [T("级别", "level"), T("规则", "rule"), T("工序", "op"), T("意见", "comment")]
sel = [f for f in f_fact if f["level"] in ("error", "warning")]
rows = [[LV[f["level"]], f["rule"], str(f["seq"] or "—"), f["text"]] for f in sel]
cols = {(i, 0): (M.RED if f["level"] == "error" else M.WARM) for i, f in enumerate(sel)}
M.table_fig(plt, HEAD, rows, [0.09, 0.08, 0.07, 0.76], "fig56_0_2", cols, fontsize=6.8)
rows, cols = [], {}
for k, name in VAR:
    for f in res[k][:1]:
        cols[(len(rows), 0)] = M.RED if f["level"] == "error" else M.WARM
        rows.append([LV[f["level"]], name, str(f["seq"] or "—"), f["text"]])
M.table_fig(plt, [T("级别", "level"), T("排错的路线", "faulty route"), T("工序", "op"), T("AI 评审员的意见", "reviewer's comment")],
            rows, [0.09, 0.2, 0.07, 0.64], "fig56_9_5", cols, fontsize=6.8)

ops_fact = [o["operation"].split(" ")[0] for o in fp["operations"]]
out(n_fact=len(fp["operations"]), ops_fact="、".join(ops_fact), n_err_fact=sum(f["level"] == "error" for f in f_fact),
    n_warn_fact=sum(f["level"] == "warning" for f in f_fact), score_fact=proc.suggested_score(f_fact),
    n_route_fact=sum(f["rule"] == "路线" for f in f_fact if f["level"] in ("error", "warning")),
    score_ref=proc.suggested_score(f_ref), n_ref_issues=sum(f["level"] in ("error", "warning") for f in f_ref),
    **{f"score_{k}": v for k, v in score.items()}, **{f"lvl_{k}": (res[k][0]["level"] if res[k] else "") for k, _ in VAR})
