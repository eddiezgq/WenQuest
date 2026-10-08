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
    for k, v in vals.items():
        tpl = tpl.replace(k, v)
    (ROOT / "site" / "index.html").write_text(tpl, encoding="utf-8")
    print({k: v for k, v in vals.items() if k != "__TIERS__"})


if __name__ == "__main__":
    main()
