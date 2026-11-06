"""生成官网首页 site/index.html（第 27 轮“三之二”）。

    python3 tools/site_home/build.py

模板 template.html；数字条和课程地图里的章数由仓库自动统计（textbook/*/book.yaml、progress.yaml、
anim/*.py、lab/*.js、factory/digital/实验*.md），课程清单在下面 TIERS（与第 28 轮细则课程目录一致，状态照实写）。
"""
import datetime as dt
import glob
import pathlib

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
HERE = pathlib.Path(__file__).resolve().parent
TB = ROOT / "textbook"
BOOKS = ["robotics", "physics", "linalg", "calculus", "mechdesign", "mfgtech", "ai", "plc", "dic"]


def book_stats(b):
    plan = yaml.safe_load((TB / b / "book.yaml").read_text(encoding="utf-8")).get("chapters") or []
    prog = yaml.safe_load((TB / b / "progress.yaml").read_text(encoding="utf-8")) or {}
    ch = prog.get("chapters", prog)
    written = len(ch) if isinstance(ch, (dict, list)) else 0
    return {"plan": len(plan) if isinstance(plan, list) else int(plan or 0), "written": written,
            "anim": len(glob.glob(str(TB / b / "ch*" / "anim" / "*.py"))),
            "lab": len(glob.glob(str(TB / b / "ch*" / "lab" / "*.js"))),
            "en": len({pathlib.Path(p).parent for p in glob.glob(str(TB / b / "ch*" / "*.en.md"))})}


def T(zh, en):
    return f"<span data-zh>{zh}</span><span data-en>{en}</span>"


ST = {"on": ("已上线", "Online", "st now"), "wip": ("编写中", "In progress", "st"), "plan": ("规划中", "Planned", "st plan")}


def tiers(S):
    def bk(b, zh_extra="", en_extra=""):
        s = S[b]
        return T(f"教材已写 {s['written']} / {s['plan']} 章，动画 {s['anim']} 段，实验 {s['lab']} 个{zh_extra}",
                 f"{s['written']} of {s['plan']} chapters written, {s['anim']} animations, {s['lab']} labs{en_extra}")
    G = [
        (("人工智能导论", "Introduction to AI"), ("各专业", "All"), T("取自《人工智能》教材", "Drawn from the <i>AI</i> textbook"), "wip"),
        (("写作与表达", "Writing and Speaking"), ("各专业", "All"), T("—", "—"), "plan"),
        (("科技与工业史", "History of Science and Industry"), ("各专业", "All"), T("—", "—"), "plan"),
        (("微观经济学 · 心理学", "Microeconomics · Psychology"), ("各专业", "All"), T("—", "—"), "plan"),
        (("限选：宏观经济学、人类学、精算与风险", "Electives: macroeconomics, anthropology, actuarial risk"), ("各专业", "All"), T("—", "—"), "plan"),
    ]
    B = [
        (("微积分", "Calculus"), ("各专业", "All"), bk("calculus"), "wip"),
        (("线性代数", "Linear Algebra"), ("各专业", "All"), bk("linalg", "；公开课视频样片 1 讲", "; one sample public lecture video"), "wip"),
        (("大学物理", "University Physics"), ("各专业", "All"), bk("physics", "；第 1 章课程已上线", "; Chapter 1 course online"), "wip"),
        (("程序设计（AI 结对编程起步）", "Programming (pairing with AI)"), ("各专业", "All"), T("—", "—"), "plan"),
        (("概率统计 · 工程制图与 CAD · 电路原理", "Probability · Engineering drawing &amp; CAD · Circuits"), ("各专业", "All"), T("—", "—"), "plan"),
    ]
    M = [
        (("机器人学", "Robotics"), ("机器人", "Robotics"), bk("robotics", f"；{S['robotics']['en']} 章有英文版", f"; {S['robotics']['en']} chapters in English"), "wip"),
        (("控制与运动学", "Control and Kinematics"), ("机器人", "Robotics"), T("内容取自《机器人学》运动学与控制各章", "Built from the kinematics and control chapters of <i>Robotics</i>"), "plan"),
        (("机械设计", "Machine Design"), ("机器人 · 智能制造", "Robotics · Mfg"), bk("mechdesign"), "wip"),
        (("机械制造技术", "Manufacturing Technology"), ("智能制造", "Mfg"), bk("mfgtech"), "wip"),
        (("PLC 原理及实践", "PLC Principles and Practice"), ("机器人 · 智能制造", "Robotics · Mfg"), bk("plc", "；另有 PLC 实验台", "; plus a PLC lab bench"), "wip"),
        (("数字集成电路设计", "Digital IC Design"), ("电子信息与微电子", "Electronics"), bk("dic"), "wip"),
        (("人工智能（AI 与 CUDA）", "Artificial Intelligence (AI and CUDA)"), ("计算机", "CS"), bk("ai", "；云端 GPU 实验", "; cloud GPU labs"), "wip"),
        (("ERP 原理与实践 · 制造执行系统 MES", "ERP · MES"), ("智能制造", "Mfg"), T("实验台在数字工厂里现成", "Lab bench ready in the digital factory"), "plan"),
        (("电路、模电数电、信号与系统等微电子各课", "Circuits, electronics, signals and the rest of the microelectronics line"), ("电子信息与微电子", "Electronics"), T("21 门课的方案已定", "21-course plan settled"), "plan"),
        (("数据结构、操作系统、计算机网络", "Data structures, operating systems, networks"), ("计算机", "CS"), T("—", "—"), "plan"),
    ]
    F = [
        (("缝纫机设计与制造", "Sewing Machine Design and Manufacturing"), ("智能制造", "Mfg"), T("31 讲、42 个动画与虚拟实验、网页互动课件、作业测验与考试；免费", "31 lessons, 42 animations and labs, web slides, homework, quizzes and exams; free"), "on"),
        (("微电子贯通项目（RTL → GDS）", "Microelectronics capstone (RTL → GDS)"), ("电子信息与微电子", "Electronics"), T("试点已走通，优秀作品可流片", "Pilot run complete; the best designs can be taped out"), "wip"),
        (("GPU 云实验与 CUDA", "Cloud GPU labs and CUDA"), ("计算机", "CS"), T("云端 GPU 实验环境已建", "Cloud GPU lab environment built"), "wip"),
        (("移动机器人 · 机械臂与智能制造 · 人形机器人与具身智能", "Mobile robots · manipulators &amp; manufacturing · humanoids"), ("机器人", "Robotics"), T("—", "—"), "plan"),
        (("智能装备与绿色制造（13 门）", "Smart equipment and green manufacturing (13 courses)"), ("智能制造", "Mfg"), T("凸轮、伺服、关节模组、数字孪生、碳足迹、电池回收等", "Cams, servo drives, joint modules, digital twins, carbon footprint, battery recycling…"), "plan"),
        (("工厂运营与工业软件（10 门）", "Factory operations and industrial software (10 courses)"), ("智能制造 · 计算机", "Mfg · CS"), T("ERP、MES、仓储、供应链、排程、质量、设备、精益等", "ERP, MES, warehousing, supply chain, scheduling, quality, maintenance, lean…"), "plan"),
        (("机器人软件与 ROS 2", "Robot software and ROS 2"), ("计算机 · 机器人", "CS · Robotics"), T("—", "—"), "plan"),
    ]
    out = []
    for key, rows, on in (("gen", G, False), ("base", B, True), ("major", M, False), ("feat", F, False)):
        trs = "".join(
            f'<tr><td>{T(*n)}</td><td>{T(*m)}</td><td>{c}</td><td class="{ST[s][2]}">{T(ST[s][0], ST[s][1])}</td></tr>'
            for n, m, c, s in rows)
        out.append(f'<div class="tier{" on" if on else ""}" data-t="{key}"><div class="tbl"><table class="courses">'
                   f'<thead><tr><th>{T("课程", "Course")}</th><th>{T("专业", "Program")}</th><th>{T("现有内容", "What exists")}</th><th>{T("状态", "Status")}</th></tr></thead>'
                   f"<tbody>{trs}</tbody></table></div></div>")
    return "\n".join(out)


# ---------------------------------------------------------------- 第 80 轮：问渠全貌总图、看视频认识问渠
NOT_FILES = ("/cam/", "/bearing/")          # 由各自的服务提供，不是 site/ 里的文件


def check_link(url, problems):
    if not url.startswith("/") or url.startswith(NOT_FILES):
        return
    path = ROOT / "site" / url.lstrip("/")
    if not (path.is_file() or (path / "index.html").is_file() or path.with_suffix(".html").is_file()):
        problems.append(url)


def atlas(cat, vals):
    problems, cols = [], []
    for k, g in enumerate(cat["groups"], 1):
        cards = []
        for it in g["items"]:
            check_link(it["url"], problems)
            dz, de = it["dz"], it["de"]
            for a, b in vals.items():
                dz, de = dz.replace(a, b), de.replace(a, b)
            ext = it["url"].startswith("http")
            lock = (f'<span class="lock">{T("需登录", "Sign-in")}</span>' if it.get("login") else "")
            card = (f'<a class="ac" href="{it["url"]}"{" rel=noopener" if ext else ""}><b>{T(it["zh"], it["en"])}{lock}</b>'
                    f'<span>{T(dz, de)}</span></a>')
            iv = (cat.get("intro") or {}).get(it.get("intro") or "") or {}
            yt = iv.get("yt")
            if yt:                                   # 第 86 轮：有视频简介的卡加“▶ 视频”（英文版，YouTube；有中文版时中文界面放 yt_zh）
                zh_attr = f' data-yt-zh="{iv["yt_zh"]}"' if iv.get("yt_zh") else ""
                card = f'<div class="acw">{card}<button type="button" class="vb" data-yt="{yt}"{zh_attr}>▶ {T("视频", "Video")}</button></div>'
            cards.append(card)
        cols.append(f'<div class="ag{" wide" if g.get("wide") else ""}" id="atlas-{g["key"]}"><h3><span class="n">{k:02d}</span>{T(g["zh"], g["en"])}</h3>'
                    f'<div class="acs">{"".join(cards)}</div></div>')
    if problems:
        raise SystemExit(f"总图里的站内链接找不到文件：{problems}")
    return "\n".join(cols)


def video_cfg(cat):
    import json
    v = cat["videos"]
    return json.dumps({"pinned": v.get("sewing_pinned", [])}, ensure_ascii=False)


def main():
    S = {b: book_stats(b) for b in BOOKS}
    flab = len(glob.glob(str(ROOT / "factory" / "digital" / "实验*.md")))
    tpl = (HERE / "template.html").read_text(encoding="utf-8")
    vals = {
        "__CH__": str(sum(s["written"] for s in S.values())),
        "__PLAN__": str(sum(s["plan"] for s in S.values())),
        "__ANIM__": str(sum(s["anim"] for s in S.values())),
        "__LAB__": str(sum(s["lab"] for s in S.values())),
        "__FLAB__": str(flab),
        "__ASOF__": dt.date.today().isoformat(),
        "__TIERS__": tiers(S),
    }
    cat = yaml.safe_load((HERE / "catalog.yaml").read_text(encoding="utf-8"))
    vals["__ATLAS__"] = atlas(cat, {k: vals[k] for k in ("__LAB__", "__FLAB__")})
    top = ((cat.get("intro") or {}).get("overview") or {}).get("yt")   # 第 86 轮：总图上方“▶ 两分钟看懂问渠”
    vals["__INTRO__"] = (f'<p class="aintro"><button type="button" class="vb big" data-yt="{top}">▶ {T("两分钟看懂问渠", "WenQuest in two minutes")}</button></p>'
                         if top else "")
    vals["__VCFG__"] = video_cfg(cat)
    for k, v in vals.items():
        tpl = tpl.replace(k, v)
    (ROOT / "site" / "index.html").write_text(tpl, encoding="utf-8")
    vp = (HERE / "videos.tpl.html").read_text(encoding="utf-8").replace("__VCFG__", vals["__VCFG__"])
    (ROOT / "site" / "videos.html").write_text(vp, encoding="utf-8")
    print({k: v for k, v in vals.items() if k not in ("__TIERS__", "__ATLAS__", "__VCFG__")})


if __name__ == "__main__":
    main()
