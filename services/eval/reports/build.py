"""第 83 轮：用评价流水线（r5/pipeline.py）的结果，生成三份评估报告（网页 + Word）和两个演示页。

    python3 services/eval/reports/build.py [--out site]

问渠出课程层：  eval/课程目标达成情况评价报告、eval/课程教学质量报告，演示页 eval/index.html（学生、教师、学校三端）
校情中枢出专业层：xq/毕业要求达成情况评价报告，演示页 xq/index.html（学校 → 学院 → 专业看板、规则亮灯、改进任务）
数字全部取自流水线输出和 r4/mapping.json；毕业要求里“示例：”开头的课程、其余专业的数值是模拟的，页面和报告里都写明。
改进措施由规则生成，标“待教师确认”（正式版由 AI 起草、教师确认，AI 不下结论）。
"""
from __future__ import annotations

import argparse
import html
import json
import random
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[1]
R5 = HERE / "r5"
THR = 0.70


def load():
    run = json.loads((R5 / "pipeline_run.json").read_text(encoding="utf-8"))
    push = json.loads((R5 / "pipeline_push.json").read_text(encoding="utf-8"))
    stu = json.loads((R5 / "pipeline_students.json").read_text(encoding="utf-8"))
    mapping = json.loads((HERE / "r4" / "mapping.json").read_text(encoding="utf-8"))
    return run, push, stu, mapping


def course_data(run, push, stu, mapping):
    rec = {r["kind"]: r for r in push["records"] if r["kind"] != "student_risk"}
    coa = rec["course_objective_attainment"]
    objs = {}
    for o in coa["objectives"]:
        r = run["课程目标达成度"][o["co_id"]]
        objs[o["co_id"]] = {"name": o["name"], "direct": r["直接"], "indirect": r["间接"], "pass_rate": r["个人达成比例"],
                            "achieved": r["达成"], "components": o["components"]}
    support = {}
    for gp, rows in mapping["SUPPORT"].items():
        for course, co, w in rows:
            if co:
                support.setdefault(co, []).append((gp, w))
    risks = [r for r in push["records"] if r["kind"] == "student_risk"]
    return {"offering": coa["offering"], "n": coa["n_students"], "threshold": coa["threshold"], "pass_line": coa["student_pass_line"],
            "objectives": objs, "support": support, "grades": run["成绩分布"], "mean": run["总评平均"], "pillars": run["三根支柱平均"],
            "gain": rec["learning_gain"], "weak": run["期末最弱的两个知识点（平均掌握概率）"], "eval": run["评教"],
            "themes": rec["feedback_themes"]["themes"], "review": run["终审队列"], "risks": len(risks),
            "s006": run["样例学生 S006（照抄型）"], "checks": run["检查"], "checks_ok": run["检查通过"],
            "students": stu, "snapshot": coa["provenance"]["snapshot_id"]}


def suggestions(c):
    out = []
    for co, o in c["objectives"].items():
        if o["achieved"]:
            continue
        worst = min(o["components"], key=lambda x: x["rate"])
        out.append(f"{co}（{o['name']}）直接评价 {o['direct']:.3f}，低于阈值 {c['threshold']:.2f}；"
                   f"考核项中“{worst['name']}”得分率最低（{worst['rate']:.3f}）。建议：加强该环节的指导与练习，"
                   f"针对最弱知识点（{'、'.join(c['weak'])}）增加讲解和练习，下学期复核。")
    lo = c["eval"]["最低两题"]
    out.append(f"评教最低两题为 {lo[0][0]}（{lo[0][1]}）、{lo[1][0]}（{lo[1][1]}），均与“反馈”有关：建议作业、实验报告的反馈写明具体错误和改进方法。")
    return out


def graduation(c, mapping):
    """毕业要求指标点达成（校情中枢）：本课程用流水线算出的课程目标达成度，其他课程为示例值"""
    pts = []
    for gp, rows in mapping["SUPPORT"].items():
        sup = []
        for course, co, w in rows:
            v = c["objectives"][co]["direct"] if co else mapping["OTHER"][course]
            sup.append({"course": "大学物理（上）" if course == "本课程" else course.replace("示例：", ""), "co": co, "w": w, "v": round(v, 3), "example": co is None})
        ws = round(sum(s["w"] * s["v"] for s in sup), 3)
        mn = round(min(s["v"] for s in sup), 3)
        pts.append({"id": gp, "weighted": ws, "min": mn, "achieved": ws >= THR, "support": sup})
    return pts


def school(c, pts):
    """校情中枢 V0 的模拟学校：机器人工程专业用真算的指标点，其余专业为模拟值（固定随机种子）"""
    rnd = random.Random(83)
    colleges = [("机械与机器人学院", ["机器人工程", "机械设计制造及其自动化"]), ("电子信息学院", ["电子信息工程", "微电子科学与工程"]),
                ("计算机学院", ["计算机科学与技术", "人工智能"])]
    gps = ["1.2 工程知识", "2.1 问题分析", "3.1 设计/开发解决方案", "4.2 研究", "5.1 使用现代工具", "10.1 沟通"]
    out = []
    for col, progs in colleges:
        ps = []
        for p in progs:
            if p == "机器人工程":
                points = [{"id": x["id"], "v": x["weighted"], "real": True} for x in pts]
            else:
                points = [{"id": g, "v": round(rnd.uniform(0.66, 0.86), 3), "real": False} for g in gps]
            low = [x for x in points if x["v"] < THR]
            ps.append({"name": p, "points": points, "low": len(low), "min": min(x["v"] for x in points),
                       "risk": c["risks"] if p == "机器人工程" else rnd.randint(4, 18), "real": p == "机器人工程"})
        out.append({"name": col, "programs": ps})
    tasks = []
    for co, o in c["objectives"].items():
        if not o["achieved"]:
            gp = next((g for g, _ in c["support"].get(co, [])), "")
            tasks.append({"id": "T-2027-001", "to": "大学物理（上）课程负责人", "target": f"{co} / {gp}",
                          "reason": f"{co} 直接评价 {o['direct']:.3f}，低于阈值 {THR:.2f}", "due": "2027-06-30", "status": "已下达"})
    k = 2
    for col in out:
        for p in col["programs"]:
            for x in p["points"]:
                if x["v"] < THR and not x["real"]:
                    tasks.append({"id": f"T-2027-{k:03d}", "to": f"{p['name']}专业负责人", "target": x["id"],
                                  "reason": f"指标点达成 {x['v']:.3f}，低于 {THR:.2f}（模拟）", "due": "2027-06-30", "status": "待下达"})
                    k += 1
    return {"colleges": out, "tasks": tasks}


# ---------------------------------------------------------------- 报告：结构写一次，同时出网页和 Word
def report_course(c, F):
    o = c["offering"]
    S = [("h", f"《{o['course_name']}》课程目标达成情况评价报告"),
         ("p", f"课程代码 {o['course_code']}　学期 {o['term']}　开课班 {o['offering_id']}　学生 {c['n']} 人　数据快照 {c['snapshot']}"),
         ("note", "演示样稿：学生数据为模拟数据（30 人模拟班），数字全部由评价流水线计算得出。"),
         ("kpis", [("课程目标", f"{sum(v['achieved'] for v in c['objectives'].values())} / {len(c['objectives'])} 达成", "#0d9488"),
                   ("最低达成度", f"{min(v['direct'] for v in c['objectives'].values()):.3f}", "#e11d48"),
                   ("学生", f"{c['n']} 人", "#2563eb"), ("规则检查", c["checks_ok"], "#7c3aed")]),
         ("h2", "一、课程目标与毕业要求指标点"),
         ("table", ["课程目标", "内容", "支撑的毕业要求指标点（权重）"],
          [[co, v["name"], "；".join(f"{g}（{w}）" for g, w in c["support"].get(co, []))] for co, v in c["objectives"].items()]),
         ("h2", "二、考核方式与评价依据"),
         ("table", ["课程目标", "考核环节", "权重", "得分率"],
          [[co, comp["name"], f"{comp['weight']:.1f}", f"{comp['rate']:.3f}"] for co, v in c["objectives"].items() for comp in v["components"]]),
         ("img", F["components"], "图 1　各考核环节得分率：红色环节拖了课程目标的后腿"),
         ("h2", "三、计算方法"),
         ("ul", [f"直接评价：课程目标达成度 = Σ（考核环节权重 × 该环节得分率），达成阈值 {c['threshold']:.2f}。",
                 f"个人达成比例：个人达成度不低于 {c['pass_line']:.2f} 的学生所占比例。",
                 "间接评价：期末学生自评问卷，与直接评价分开列出，不合并。"]),
         ("h2", "四、达成情况"),
         ("table", ["课程目标", "直接评价", "间接评价（自评）", "个人达成比例", "结论"],
          [[co, f"{v['direct']:.3f}", f"{v['indirect']:.3f}", f"{v['pass_rate']:.0%}", "达成" if v["achieved"] else "未达成"]
           for co, v in c["objectives"].items()]),
         ("img", F["co"], "图 2　课程目标达成度：直接评价（红 = 未达成）与学生自评对照"),
         ("img", F["kp"], "图 3　期末各知识点掌握结构：卡点一眼可见"),
         ("h2", "五、分析与改进措施（待教师确认；演示稿由规则生成，正式版由 AI 起草）")]
    S += [("ul", suggestions(c))]
    S += [("h2", "六、数据来源"),
          ("ul", ["期初诊断、练习、虚拟实验过程与报告、章节自适应考试、AI 答辩组合议、教师终审：问渠学习平台记录。",
                  "每项分数都能追到证据（作答、实验记录、答辩记录）；有未结终审案例的学生，成绩单暂缓发布。"])]
    return S


def report_quality(c, F):
    o = c["offering"]
    g = c["gain"]
    S = [("h", f"《{o['course_name']}》课程教学质量报告"),
         ("p", f"学期 {o['term']}　开课班 {o['offering_id']}　学生 {c['n']} 人"),
         ("note", "演示样稿：数据为模拟数据，数字由评价流水线计算得出。"),
         ("kpis", [("总评平均", f"{c['mean']}", "#2563eb"), ("掌握概率增值", f"+{g['gain']:.2f}", "#7c3aed"),
                   ("学业预警", f"{c['risks']} 人", "#f59e0b"), ("终审案例", f"{c['review']['总数']} 例", "#e11d48")]),
         ("h2", "一、学业结果"),
         ("table", ["项目", "结果"],
          [["总评平均", f"{c['mean']}"], ["成绩分布", "，".join(f"{k} {v}" for k, v in c["grades"].items())],
           ["三根支柱平均", f"知识 {c['pillars']['A']}，实践 {c['pillars']['B']}，综合 {c['pillars']['C']}"]]),
         ("img", F["grades"], "图 1　成绩分布"),
         ("img", F["radar"], "图 2　三个学生的能力画像（照抄型 S006、最高分、最低分）"),
         ("h2", "二、学习增值"),
         ("p", f"平均掌握概率由期初 {g['pre_mean']:.3f} 提高到期末 {g['post_mean']:.3f}，增值 {g['gain']:.3f}（{g['n_students']} 人）。"
               f"期末最弱的知识点：{'、'.join(c['weak'])}。"),
         ("img", F["gain"], "图 3　学习增值；AI 学习路径比随机练习在两个卡点上的提升高出近一倍"),
         ("h2", "三、学业预警与终审"),
         ("p", f"学业预警 {c['risks']} 人（已推送任课教师、辅导员）。终审队列 {c['review']['总数']} 个案例："
               + "，".join(f"{k} {v}" for k, v in c["review"]["按原因"].items() if v)
               + f"；暂缓发布成绩单 {len(c['review']['暂缓发布成绩单'])} 人，等口试结果。"),
         ("img", F["scatter"], "图 4　知识 vs 实践：闭卷高、实践低的红圈学生被过程考核和答辩拦下"),
         ("h2", "四、学生评教"),
         ("p", f"回收 {c['eval']['回答份数']} 份；得分最低两题：" + "、".join(f"{q}（{s}）" for q, s in c["eval"]["最低两题"]) + "。"),
         ("table", ["学生反馈主题", "人次", "倾向"], [[t["theme"], str(t["count"]), t["tone"]] for t in c["themes"]]),
         ("img", F["review"], "图 5　终审队列构成与学生反馈主题"),
         ("h2", "五、持续改进（待教师确认；演示稿由规则生成，正式版由 AI 起草）"), ("ul", suggestions(c))]
    return S


def report_grad(c, pts, F):
    S = [("h", "机器人工程专业毕业要求达成情况评价报告（样稿）"),
         ("p", "评价学年 2026–2027　评价方法：加权和法为主，最小值法对照　达成阈值 0.70"),
         ("note", "演示样稿：《大学物理（上）》一门课的数值由问渠评价流水线真算（模拟学生数据）；标“示例”的课程是示例数值。由校情中枢汇总各课程推送生成。"),
         ("kpis", [("指标点", f"{sum(p['achieved'] for p in pts)} / {len(pts)} 达成", "#0d9488"),
                   ("最低", f"{min(p['weighted'] for p in pts):.3f}", "#e11d48"), ("改进任务", f"{sum(not v['achieved'] for v in c['objectives'].values())} 项", "#f59e0b")]),
         ("h2", "一、各指标点达成情况"),
         ("table", ["毕业要求指标点", "加权和法", "最小值法", "结论"],
          [[p["id"], f"{p['weighted']:.3f}", f"{p['min']:.3f}", "达成" if p["achieved"] else "未达成"] for p in pts]),
         ("img", F["radar"], "图 1　机器人工程毕业要求指标点（红虚线为阈值 0.70）"),
         ("h2", "二、支撑课程明细"),
         ("table", ["指标点", "支撑课程", "课程目标", "支撑权重", "课程目标达成度"],
          [[p["id"], s["course"] + ("（示例）" if s["example"] else ""), s["co"] or "—", f"{s['w']:.1f}", f"{s['v']:.3f}"]
           for p in pts for s in p["support"]]),
         ("img", F["support"], "图 2　各指标点由哪些课程撑起来"),
         ("img", F["heat"], "图 3　全校毕业要求达成热力图（其他专业为模拟值）"),
         ("h2", "三、分析"),
         ("ul", [f"{p['id']}：加权和 {p['weighted']:.3f}，最低的支撑课程是 "
                 f"{min(p['support'], key=lambda s: s['v'])['course']}（{min(s['v'] for s in p['support']):.3f}）。"
                 for p in pts if p["min"] < THR + 0.02] or ["各指标点均达成，且最小值不低于阈值附近。"]),
         ("h2", "四、改进任务（校情中枢 → 课程负责人）"),
         ("ul", [f"{co} 未达成：已向《大学物理（上）》课程负责人下达改进任务，下学期复核（评价—反馈—改进闭环）。"
                 for co, v in c["objectives"].items() if not v["achieved"]])]
    return S


def to_html(S, title):
    e = html.escape
    body = []
    for item in S:
        k = item[0]
        if k == "h":
            body.append(f"<h1>{e(item[1])}</h1>")
        elif k == "h2":
            body.append(f"<h2>{e(item[1])}</h2>")
        elif k == "p":
            body.append(f"<p>{e(item[1])}</p>")
        elif k == "note":
            body.append(f'<p class="note">{e(item[1])}</p>')
        elif k == "ul":
            body.append("<ul>" + "".join(f"<li>{e(x)}</li>" for x in item[1]) + "</ul>")
        elif k == "img":
            body.append(f'<figure><img src="{e(item[1])}" alt="{e(item[2])}"><figcaption>{e(item[2])}</figcaption></figure>')
        elif k == "kpis":
            body.append('<div class="kpis">' + "".join(f'<div class="kpi" style="--c:{col}"><b>{e(v)}</b><span>{e(l)}</span></div>' for l, v, col in item[1]) + "</div>")
        elif k == "table":
            body.append("<table><thead><tr>" + "".join(f"<th>{e(h)}</th>" for h in item[1]) + "</tr></thead><tbody>"
                        + "".join("<tr>" + "".join(f"<td>{e(str(x))}</td>" for x in r) + "</tr>" for r in item[2]) + "</tbody></table>")
    return f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title><style>
:root{{--ink:#121c21;--muted:#56656b;--line:#d6d2c6;--paper:#fbfaf6;--accent:#7a5a00;color-scheme:light}}
@media (prefers-color-scheme:dark){{:root{{--ink:#e6ecee;--muted:#93a3a9;--line:#2a3a41;--paper:#0f181c;--accent:#f2c94c;color-scheme:dark}}}}
body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.75 "Noto Sans SC","PingFang SC","Microsoft YaHei",system-ui,sans-serif}}
main{{max-width:900px;margin:0 auto;padding:28px 16px 64px}} h1{{font:700 26px/1.3 "Noto Serif SC",serif}} h2{{font:600 19px/1.4 "Noto Serif SC",serif;margin-top:28px}}
.note{{color:var(--muted);font-size:14px;border-left:3px solid var(--accent);padding-left:10px}}
table{{border-collapse:collapse;width:100%;font-size:14.5px;margin:8px 0}} th,td{{border:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}}
.top{{display:flex;gap:16px;font-size:14px}} .top a{{color:var(--accent)}}
h1{{background:linear-gradient(90deg,#2563eb,#7c3aed,#db2777);-webkit-background-clip:text;background-clip:text;color:transparent}}
h2{{border-left:5px solid #2563eb;padding-left:10px}} th{{background:color-mix(in srgb,#2563eb 10%,transparent)}}
figure{{margin:18px 0;background:#fff;border:1px solid var(--line);border-radius:10px;padding:10px}} figure img{{width:100%;display:block}}
figcaption{{font-size:13.5px;color:#475569;margin-top:6px}}
.kpis{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:16px 0}}
.kpi{{border-radius:10px;padding:12px 14px;background:color-mix(in srgb,var(--c) 12%,transparent);border:1px solid color-mix(in srgb,var(--c) 40%,transparent)}}
.kpi b{{display:block;font:700 24px/1.2 ui-monospace,monospace;color:var(--c)}} .kpi span{{font-size:13px;color:var(--muted)}}
@media print{{.top{{display:none}}}}
</style></head><body><main><div class="top"><a href="./">← 返回演示</a><a href="{e(title)}.docx">下载 Word</a></div>
{''.join(body)}</main></body></html>"""


def to_docx(S, path):
    from docx import Document
    from docx.oxml.ns import qn
    from docx.shared import Cm, Pt, RGBColor
    d = Document()
    st = d.styles["Normal"]
    st.font.name = "Microsoft YaHei"
    st.element.rPr.rFonts.set(qn("w:eastAsia"), "Microsoft YaHei")
    st.font.size = Pt(10.5)
    for item in S:
        k = item[0]
        if k == "h":
            d.add_heading(item[1], 0)
        elif k == "h2":
            d.add_heading(item[1], 1)
        elif k in ("p", "note"):
            p = d.add_paragraph(item[1])
            if k == "note":
                p.runs[0].italic = True
        elif k == "ul":
            for x in item[1]:
                d.add_paragraph(x, style="List Bullet")
        elif k == "img":
            d.add_picture(str(path.parent / item[1]), width=Cm(15.5))
            cap = d.add_paragraph(item[2])
            cap.runs[0].font.size = Pt(9)
            cap.runs[0].font.color.rgb = RGBColor(0x47, 0x55, 0x69)
        elif k == "kpis":
            t = d.add_table(rows=2, cols=len(item[1]))
            t.style = "Table Grid"
            for i, (l, v, col) in enumerate(item[1]):
                r = t.rows[0].cells[i].paragraphs[0].add_run(v)
                r.bold = True
                r.font.size = Pt(16)
                r.font.color.rgb = RGBColor.from_string(col.lstrip("#").upper())
                t.rows[1].cells[i].text = l
        elif k == "table":
            t = d.add_table(rows=1, cols=len(item[1]))
            t.style = "Table Grid"
            for i, h in enumerate(item[1]):
                t.rows[0].cells[i].text = h
            for r in item[2]:
                cells = t.add_row().cells
                for i, x in enumerate(r):
                    cells[i].text = str(x)
    d.save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "site"))
    a = ap.parse_args()
    out = Path(a.out)
    run, push, stu, mapping = load()
    c = course_data(run, push, stu, mapping)
    pts = graduation(c, mapping)
    sch = school(c, pts)
    ev, xq = out / "eval", out / "xq"
    ev.mkdir(parents=True, exist_ok=True)
    xq.mkdir(parents=True, exist_ok=True)
    import charts
    lp = json.loads((R5 / "learning_path_results.json").read_text(encoding="utf-8"))
    Fc = charts.course_charts(c, lp, stu, charts.kp_names(), ev)
    Fs = charts.school_charts(pts, sch, xq, THR)
    reports = [(ev, "课程目标达成情况评价报告", report_course(c, Fc)), (ev, "课程教学质量报告", report_quality(c, Fc)),
               (xq, "毕业要求达成情况评价报告", report_grad(c, pts, Fs))]
    for d, name, S in reports:
        (d / f"{name}.html").write_text(to_html(S, name), encoding="utf-8")
        to_docx(S, d / f"{name}.docx")
    s006 = next(s for s in stu if s["id"] == "S006")
    data_ev = {"figs": Fc, "course": {**{k: v for k, v in c.items() if k not in ("students", "support")}, "suggestions": suggestions(c)},
               "sample_students": [s006, max(stu, key=lambda s: s["total"]), min(stu, key=lambda s: s["total"])]}
    (ev / "data.json").write_text(json.dumps(data_ev, ensure_ascii=False, indent=1), encoding="utf-8")
    (xq / "data.json").write_text(json.dumps({"figs": Fs, "points": pts, **sch, "threshold": THR}, ensure_ascii=False, indent=1), encoding="utf-8")
    tpl = Path(__file__).resolve().parent
    for d, f in ((ev, "eval.html"), (xq, "xq.html")):
        (d / "index.html").write_text((tpl / f).read_text(encoding="utf-8"), encoding="utf-8")
    print("生成：", ev, xq)


if __name__ == "__main__":
    main()
