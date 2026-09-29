"""The lesson page students read in WenQuest, built from the lesson spec in the benchmark order:
goal · robot problem · concept (+ lecture notes) · worked example · animation · virtual lab ·
back to the problem (five steps) · everyday example · summary · check yourself."""
from __future__ import annotations

import html

LABELS = {
    "zh": {"goal": "本节目标", "problem": "机器人问题", "given": "已知", "concept": "概念", "example": "例题", "solution": "解",
           "animation": "动画", "anim_note": "看本节的动画，注意画面里的问题：", "lab": "虚拟实验",
           "lab_note": "在本章“虚拟实验”里完成下面的任务，课后按实验指导书写实验报告。", "robot": "机器人场景", "life": "生活场景",
           "model": "回到实际问题：建模求解", "steps": ["① 问题", "② 建模", "③ 求解", "④ 检验", "⑤ 修正"],
           "everyday": "生活中的例子", "answer": "答案", "summary": "小结", "check": "想一想"},
    "en": {"goal": "Goal", "problem": "Robot problem", "given": "Given", "concept": "Concept", "example": "Worked example", "solution": "Solution",
           "animation": "Animation", "anim_note": "Watch this lesson’s animation and think about its question:", "lab": "Virtual lab",
           "lab_note": "Do these tasks in the chapter’s virtual lab, then write the lab report with the lab guide.", "robot": "Robot scene",
           "life": "Everyday scene", "model": "Back to the problem: modelling", "steps": ["① Problem", "② Model", "③ Solve", "④ Check", "⑤ Improve"],
           "everyday": "Everyday example", "answer": "Answer", "summary": "Summary", "check": "Check yourself"},
}


def _e(s: str) -> str:
    return html.escape(s or "")


def build(spec: dict, lang: str) -> str:
    i = 0 if lang == "zh" else 1
    L = LABELS["zh" if i == 0 else "en"]
    s = spec
    ul = lambda items: "<ul>" + "".join(f"<li>{_e(x[i])}</li>" for x in items if x[i]) + "</ul>"  # noqa: E731
    ol = lambda items: "<ol>" + "".join(f"<li>{_e(x[i])}</li>" for x in items if x[i]) + "</ol>"  # noqa: E731
    p = s["problem"]
    out = [f"<blockquote><p><strong>{L['goal']}</strong>：{_e(s['goal'][i])}</p></blockquote>" if i == 0 else
           f"<blockquote><p><strong>{L['goal']}:</strong> {_e(s['goal'][i])}</p></blockquote>"]
    out.append(f"<h3>{L['problem']}：{_e(p['title'][i])}</h3>" if i == 0 else f"<h3>{L['problem']}: {_e(p['title'][i])}</h3>")
    out.append(f"<p>{_e(p['text'][i])}</p>")
    if p["given"]:
        out.append(f"<p><strong>{L['given']}</strong></p>" + ul(p["given"]))
    c = s["concept"]
    out.append(f"<h3>{L['concept']}：{_e(c['title'][i])}</h3>" if i == 0 else f"<h3>{L['concept']}: {_e(c['title'][i])}</h3>")
    out.append(ul(c["points"]))
    if c["formula"][i]:
        out.append(f"<blockquote><p><strong>{_e(c['formula'][i])}</strong></p></blockquote>")
    for n in s["notes"]:
        out.append(f"<h4>{_e(n['heading'][i])}</h4>")
        out.append(n["zh"] if i == 0 else n["en"])
    e = s["example"]
    if e["question"][i]:
        out.append(f"<h3>{L['example']}</h3><p>{_e(e['question'][i])}</p><p><strong>{L['solution']}</strong></p>" + ol(e["steps"]))
        if e["answer"][i]:
            out.append(f"<p><strong>{_e(e['answer'][i])}</strong></p>")
    a = s["animation"]
    out.append(f"<h3>{L['animation']}：{_e(a['title'][i])}</h3>" if i == 0 else f"<h3>{L['animation']}: {_e(a['title'][i])}</h3>")
    out.append(f"<p>{L['anim_note']}<strong>{_e(a['question'][i])}</strong></p>")
    lb = s["lab"]
    out.append(f"<h3>{L['lab']}：{_e(lb['title'][i])}</h3>" if i == 0 else f"<h3>{L['lab']}: {_e(lb['title'][i])}</h3>")
    out.append(f"<p>{L['lab_note']}</p>")
    out.append(f"<ul><li><strong>{L['robot']}</strong>：{_e(lb['robot_scene'][i])}</li><li><strong>{L['life']}</strong>：{_e(lb['life_scene'][i])}</li></ul>"
               if i == 0 else
               f"<ul><li><strong>{L['robot']}:</strong> {_e(lb['robot_scene'][i])}</li><li><strong>{L['life']}:</strong> {_e(lb['life_scene'][i])}</li></ul>")
    out.append(ol(lb["tasks"]))
    m = s["model"]
    rows = [p["text"], m["assume"], m["solve"], m["check"], m["improve"]]
    out.append(f"<h3>{L['model']}</h3><table>" + "".join(f"<tr><th>{L['steps'][k]}</th><td>{_e(r[i])}</td></tr>" for k, r in enumerate(rows)) + "</table>")
    ev = s["everyday"]
    if ev["text"][i]:
        out.append(f"<h3>{L['everyday']}</h3><p>{_e(ev['text'][i])}</p>")
        if ev["answer"][i]:
            out.append(f"<p><em>{L['answer']}：{_e(ev['answer'][i])}</em></p>" if i == 0 else f"<p><em>{L['answer']}: {_e(ev['answer'][i])}</em></p>")
    if s["summary"]:
        out.append(f"<h3>{L['summary']}</h3>" + ul(s["summary"]))
    if s["self_check"]:
        out.append(f"<h3>{L['check']}</h3>" + ol(s["self_check"]))
    return "\n".join(out)
