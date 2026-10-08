"""第 13 章共用的数据与算法（自然语言处理与大语言模型）。

本章不放任何企业真实文件，也不放模型权重。要用的东西全在这里按公式与模板生成：

- `manual()`：数字工厂的**质量手册**（条文编号、页码、版本，其中故意留下几处新旧版互相矛盾的条文——
  真实手册就是这样，这正是 13.9 节要处理的问题）；`questions()`：问答对与标准答案的出处（条文号）。
- `tokens()`：中文按**字二元组**切、英文与编号按词切（中文没有天然词边界，分词器一换检索结果就变，
  所以本章检索一律用字 n 元组，这件事在 13.1 节交代）。
- `chunks()`、`bm25()`、`embed()`：切片、词频检索与向量检索，都自己实现，不依赖外部库与联网模型。
- `skipgram()`：在程序生成的小语料上训一个词向量（NumPy，负采样），供 13.1 节的类比任务用。
- `bleu()`、`bradley_terry()`：13.2、13.5 节要用的两个指标与一个模型。

所有随机都从固定种子出发，书中每个数字都能复算。
"""
from __future__ import annotations

import hashlib
import math
import re

import numpy as np

# ---------------------------------------------------------------- 质量手册

CH_TITLES = {
    2: "通用要求",
    3: "量具与测量",
    4: "零件加工与检验",
    5: "不合格品控制",
    6: "记录与追溯",
    7: "人员与授权",
    8: "供应商与来料",
    9: "附录：历次修订",
}

PART = "SH-301 输出轴"
# 零件各有自己的公差与硬度——这正是检索容易出错的地方：问 SH-301 却取回 SH-302 的条文
PARTS = [(PART, 0.02, (28, 32), 0.8), ("SH-302 输入轴", 0.03, (30, 35), 1.6),
         ("GH-12 主动齿轮", 0.05, (45, 50), 0.4), ("GH-13 从动齿轮", 0.06, (45, 50), 0.4),
         ("XT-5 箱体", 0.10, (None, None), 3.2), ("ZC-7 支承座", 0.08, (None, None), 3.2)]
MACHINES = ["CK6150 数控车床", "YK3610 滚齿机", "TX6113 卧式镗床", "MK1320 外圆磨床", "ZKL-60 调质炉",
            "CK6136 数控车床", "YK3180 滚齿机", "T68 卧式镗床", "M1432B 外圆磨床", "QX-25 清洗机"]
# 车间里还有上百种别的零件，它们的条文与上面几种字面几乎一样、数值不同——手册因此有几百页，
# 检索要在其中挑出问到的那一条。这些零件由程序按编号规则生成（`_filler_parts`）。
N_FILLER_PARTS = 600
# 通用条文（与零件无关）
GENERAL = [
    (2, "手册的适用范围", "本手册适用于减速器车间全部加工、检验与放行活动；与顾客图样不一致时以图样为准。", ["适用范围", "图样"]),
    (2, "术语", "本手册中“终检”指零件入库前的最后一次检验，“首件”指每批次第一个加工完成的零件。", ["术语", "终检", "首件"]),
    (2, "文件的受控与发放", "受控文件由质量部统一编号发放，车间现场只允许存放最新版；作废版本盖“作废”章后交回。", ["受控", "发放", "作废"]),
    (3, "量具校准周期", "{gauge}每 {months} 个月校准一次，校准记录由计量室保存 {years} 年；超期的量具不得用于终检。", ["校准", "量具", "计量室"]),
    (3, "测量不确定度的要求", "终检所用量具的测量不确定度不得大于被测公差带的 {ratio} 分之一。", ["不确定度", "公差", "终检"]),
    (3, "三坐标测量机的使用", "三坐标测量机的测头每班次开机后做一次校验；测量间温度应控制在 20 ± {dt} ℃。", ["三坐标", "测头", "温度"]),
    (3, "量具的日常点检", "班前目视检查量具的测量面有无磕碰、锈蚀，发现异常挂“停用”牌并报计量室。", ["点检", "停用", "测量面"]),
    (4, "首件检验", "每批首件必须全尺寸检验并由检验员签字，首件未判合格不得继续加工。", ["首件", "全尺寸", "检验员"]),
    (4, "末件与巡检", "每批末件保留并记录；连续生产时每 {patrol} 小时巡检一次，每次抽 {n_patrol} 件。", ["末件", "巡检", "抽检"]),
    (4, "过程能力", "关键尺寸的过程能力指数 Cpk 不低于 {cpk}；低于该值时停机调整并追溯已加工零件。", ["过程能力", "Cpk", "关键尺寸"]),
    (5, "不合格品的标识与隔离", "发现不合格品应立即挂红牌并移入隔离区，{hours} 小时内填写不合格品评审单。", ["不合格品", "红牌", "隔离区", "评审单"]),
    (5, "超差的判定与审批", "尺寸超差但不影响装配功能的，由质量工程师提出让步接收意见，经{approver}批准后方可放行；影响功能的一律报废。", ["超差", "让步接收", "批准", "报废"]),
    (5, "返工与返修", "返工后的零件须按原检验项目重新全检，并在记录上注明返工次数；同一零件返工不得超过 {rework} 次。", ["返工", "返修", "全检"]),
    (5, "纠正措施", "同一问题一个月内重复出现 {repeat} 次以上，必须开纠正措施单并做原因分析。", ["纠正措施", "原因分析", "重复"]),
    (6, "检验记录的保存", "检验记录与不合格品评审单保存 {keep} 年；电子记录每 {backup} 天备份一次。", ["记录", "保存", "备份"]),
    (6, "追溯与批次", "每批零件以炉号加日期编批，记录须能从成品反查到原材料炉号。", ["追溯", "批次", "炉号"]),
    (6, "记录的更改", "记录上的笔误用单线划去并签名，不得涂改或撕页。", ["更改", "笔误", "签名"]),
    (7, "检验员的资格", "检验员须经培训考核合格并取得授权，授权有效期 {auth} 年，到期重新考核。", ["检验员", "授权", "考核"]),
    (7, "签字权限", "让步接收单由{approver}签字；报废单由厂长签字，金额超过 {amount} 元的另报总经理。", ["签字", "权限", "报废单"]),
    (7, "新员工的独立操作", "新员工经带岗 {coach} 个月、考核合格后方可独立操作数控设备。", ["新员工", "带岗", "独立操作"]),
    (8, "供应商的评定", "新供应商须通过现场评定与首批样件检验；评定结果每年复核一次。", ["供应商", "评定", "样件"]),
    (8, "来料检验", "来料按批抽检，抽样数按 GB/T 2828.1 的正常检验一次抽样方案确定。", ["来料", "抽检", "抽样方案"]),
    (8, "免检与让步", "连续 {free_lots} 批合格的供应商可申请免检；免检期间每季度抽查一次。", ["免检", "抽查", "季度"]),
]
# 按零件展开的条文（每个零件四条，数值各不相同）
PER_PART = [
    (4, "{part}的同轴度要求", "{part}两端轴颈对公共基准的同轴度公差为 {tol} mm；超差的零件按 5.2 条处理。", ["同轴度", "轴颈", "基准"]),
    (4, "{part}的热处理硬度", "{part}调质后表面硬度应为 {hrc_lo}—{hrc_hi} HRC；每炉抽检 {n_sample} 件。", ["热处理", "硬度", "调质", "抽检"]),
    (4, "{part}的表面粗糙度", "{part}配合面的表面粗糙度 Ra 不大于 {ra} μm，非配合面不大于 {ra2} μm。", ["粗糙度", "Ra", "配合"]),
    (4, "{part}的检验项目", "{part}终检项目包括外观、关键尺寸、同轴度与硬度；记录按 6.1 条保存。", ["检验项目", "终检", "外观"]),
]
# 工序条文：每个零件每道工序一条，留量、转速、进给各不相同（大量字面相似、数值不同的条文）
PROCESS = [("粗车", "单边留量 {a} mm，转速 {b} r/min"), ("精车", "单边留量 {a} mm，转速 {b} r/min"),
           ("磨削", "单次进刀 {a} mm，砂轮线速度 {b} m/s"), ("调质", "保温 {a} 小时，回火温度 {b} ℃"),
           ("清洗与防锈", "清洗液浓度 {a}%，防锈期不少于 {b} 天"), ("装配", "压装力 {a} kN，静置 {b} 分钟")]

PER_MACHINE = [
    (2, "{machine}的开机点检", "{machine}开机前检查油位、气压与防护装置，点检表当班填写。", ["点检", "开机", "防护"]),
    (2, "{machine}的刀具与工装", "{machine}换刀后首件必检；工装定位面每周清洗并记录。", ["刀具", "工装", "换刀"]),
]


def _filler_parts(seed: int = 0) -> list[tuple]:
    """生成车间里其余零件的编号与数值（与问答无关，但让手册有真实的规模与干扰）。"""
    rng = np.random.default_rng(2600 + seed)
    kinds = ["中间轴", "传动轴", "法兰", "端盖", "隔套", "压盖", "齿圈", "拨叉", "连杆", "衬套"]
    pre = ["ZJ", "CD", "FL", "DG", "GT", "YG", "CQ", "BC", "LG", "CT"]
    out = []
    for i in range(N_FILLER_PARTS):
        k = i % len(kinds)
        name = f"{pre[k]}-{100 + i} {kinds[k]}"
        tol = round(float(rng.uniform(0.01, 0.2)), 2)
        hrc_lo = int(rng.integers(20, 50))
        hrc = (hrc_lo, hrc_lo + int(rng.integers(3, 8))) if rng.random() < 0.6 else (None, None)
        ra = float(rng.choice([0.4, 0.8, 1.6, 3.2, 6.3]))
        out.append((name, tol, hrc, ra))
    return out


def _fill(seed: int = 0) -> dict:
    """手册里的数值。固定种子，使条文、问答与评测标准答案三者一致。"""
    return {"gauge": "卡尺、千分尺与量规", "months": 6, "years": 3, "ratio": 10, "dt": 2,
            "part": PART, "tol": 0.02, "hrc_lo": 28, "hrc_hi": 32, "n_sample": 3,
            "ra": 0.8, "ra2": 3.2, "hours": 24, "approver": "质量经理", "rework": 2,
            "keep": 5, "backup": 7, "auth": 3, "amount": 5000, "patrol": 2, "n_patrol": 5,
            "cpk": 1.33, "repeat": 3, "coach": 3, "free_lots": 10}


# 新旧版互相矛盾的地方：旧版条文仍留在附录里，但已被新版替代
# 附录里保留的是旧版条文的**原样**，连题目一起——所以它们与新版条文字面几乎一样，检索时很容易被取回。
# 这正是真实手册的坑：答案字字有出处，出处却是一条早已作废的条文。
OLD_VERSION = [
    ("QM-5.2", "超差的判定与审批", "尺寸超差但不影响装配功能的，由车间主任提出让步接收意见并批准后放行；影响功能的报废。",
     "审批人原为车间主任，新版改为质量工程师提意见、质量经理批准"),
    ("QM-3.1", "量具校准周期", "卡尺、千分尺与量规每 12 个月校准一次，校准记录由计量室保存 2 年。",
     "校准周期原为 12 个月，新版缩短为 6 个月；记录保存由 2 年改为 3 年"),
    ("QM-4.1", "SH-301 输出轴的同轴度要求", "SH-301 输出轴两端轴颈对公共基准的同轴度公差为 0.05 mm。",
     "公差原为 0.05 mm，新版收紧到 0.02 mm"),
]

CHARS_PER_PAGE = 450


def manual(seed: int = 0) -> list[dict]:
    """生成质量手册：每条给出条文号、章、题目、正文、页码、版本。页码按每页 450 字排。

    手册里有三样东西是**故意**做出来的，因为真实手册就是这样，而它们正是 13.6、13.9 节要处理的难处：
    ① 同类条文按零件各写一条，数值不同（问 SH-301 取回 SH-302 就是错的）；
    ② 附录里留着已废止的旧版条文，字面上与新版矛盾；
    ③ 若干条文互相引用（“按 5.2 条处理”“按 6.1 条保存”），答一个问题常要两条一起看。
    """
    v = _fill(seed)
    rows = list(GENERAL)
    for name, tol, hrc, ra in PARTS + _filler_parts(seed):
        pv = dict(v, part=name, tol=tol, hrc_lo=hrc[0], hrc_hi=hrc[1], ra=ra, ra2=max(ra * 4, 3.2))
        for ch, title, body, kw in PER_PART:
            if hrc[0] is None and "硬度" in title:           # 箱体与支承座不调质，没有硬度条文
                continue
            rows.append((ch, title.format(**pv), body.format(**pv), kw))
    for mach in MACHINES:
        for ch, title, body, kw in PER_MACHINE:
            rows.append((ch, title.format(machine=mach), body.format(machine=mach), kw))
    rng = np.random.default_rng(1300 + seed)
    for name, *_ in PARTS:                                   # 工序条文：字面相似、数值各不相同
        for proc, tpl in PROCESS:
            a = round(float(rng.uniform(0.05, 2.5)), 2)
            b = int(rng.integers(60, 900))
            rows.append((4, f"{name} 的{proc}工艺要求",
                         f"{name} {proc}工序：" + tpl.format(a=a, b=b) + "；加工后按本章检验项目自检一次。",
                         [proc, "工艺", "工序"]))

    out, page, chars = [], 1, 0
    by_ch: dict[int, int] = {}
    for ch, title, body, kw in rows:
        by_ch[ch] = by_ch.get(ch, 0) + 1
        t = title.format(**v) if "{" in title else title
        b = body.format(**v) if "{" in body else body
        chars += len(b) + len(t)
        if chars > CHARS_PER_PAGE:
            page, chars = page + 1, len(b) + len(t)
        out.append({"id": f"QM-{ch}.{by_ch[ch]}", "ch": ch, "ch_title": CH_TITLES[ch], "title": t,
                    "text": b, "page": page, "version": "B", "keywords": kw, "obsolete": False})
    for cid, title, body, note in OLD_VERSION:               # 附录里的旧版条文（连原题目一起保留）
        page += 1
        out.append({"id": f"{cid}(A)", "ch": 9, "ch_title": CH_TITLES[9],
                    "title": f"{title}（{cid} 的 A 版，已废止）",
                    "text": body + f"（本条为 A 版原文，自 B 版起废止，仅供查阅历次修订时对照；修订要点：{note}。"
                                   f"现场执行一律以 {cid} 的现行版为准，不得引用本条办理放行、判定或签批。）",
                    "page": page,
                    "version": "A", "keywords": [], "obsolete": True, "note": note})
    return out


def find(man: list[dict], title_part: str) -> dict:
    """按题目里的一段字找条文（生成问答与核对标准答案时用）。"""
    for c in man:
        if title_part in c["title"] and not c["obsolete"]:
            return c
    raise KeyError(title_part)


def questions(seed: int = 0) -> list[dict]:
    """问答对：问题、标准答案的出处（条文号，可以是多条）、答案里必须出现的关键事实。
    条文号由 `find()` 从手册里查出来，不手写——手册一改，标准答案跟着改。
    最后几个是**手册里没有答案**的问题：系统应当说“手册里没有规定”，而不是编一个（13.6、13.9 节）。"""
    v, man = _fill(seed), manual(seed)
    def cid(t):
        return find(man, t)["id"]
    qs = [
        ("SH-301 输出轴的同轴度公差是多少？", [cid("SH-301 输出轴的同轴度")], [str(v["tol"])]),
        ("输出轴同轴度超差了怎么处理、谁批？", [cid("SH-301 输出轴的同轴度"), cid("超差的判定")], ["让步接收", v["approver"], "报废"]),
        ("SH-302 输入轴的同轴度公差呢？", [cid("SH-302 输入轴的同轴度")], ["0.03"]),
        ("量具多久校准一次？校准记录保存几年？", [cid("量具校准周期")], [str(v["months"]), str(v["years"])]),
        ("终检用的量具精度要求是怎么规定的？", [cid("测量不确定度")], [str(v["ratio"])]),
        ("三坐标测量间的温度要求是多少？", [cid("三坐标测量机")], [str(v["dt"])]),
        ("输出轴调质后的硬度范围是多少？每炉抽检几件？", [cid("SH-301 输出轴的热处理")], [str(v["hrc_lo"]), str(v["hrc_hi"]), str(v["n_sample"])]),
        ("主动齿轮的硬度要求和输出轴一样吗？", [cid("GH-12 主动齿轮的热处理"), cid("SH-301 输出轴的热处理")], ["45", "28"]),
        ("输出轴配合面的粗糙度要求？", [cid("SH-301 输出轴的表面粗糙度")], [str(v["ra"])]),
        ("首件没判合格能不能接着加工？", [cid("首件检验")], ["不得继续加工"]),
        ("巡检多久一次、每次抽几件？", [cid("末件与巡检")], [str(v["patrol"]), str(v["n_patrol"])]),
        ("关键尺寸的过程能力要求是多少？不够怎么办？", [cid("过程能力")], [str(v["cpk"]), "停机"]),
        ("发现不合格品后多长时间内要填评审单？", [cid("不合格品的标识")], [str(v["hours"])]),
        ("同一个零件最多返工几次？", [cid("返工与返修")], [str(v["rework"])]),
        ("什么情况下必须开纠正措施单？", [cid("纠正措施")], [str(v["repeat"])]),
        ("检验记录要保存几年？电子记录多久备份？", [cid("检验记录的保存")], [str(v["keep"]), str(v["backup"])]),
        ("能从成品查到原材料炉号吗？怎么编批？", [cid("追溯与批次")], ["炉号", "日期"]),
        ("记录写错了能涂改吗？", [cid("记录的更改")], ["单线", "签名"]),
        ("检验员的授权有效期多长？", [cid("检验员的资格")], [str(v["auth"])]),
        ("报废单谁签字？金额大的要不要再报？", [cid("签字权限")], ["厂长", str(v["amount"]), "总经理"]),
        ("让步接收单谁签字？", [cid("签字权限"), cid("超差的判定")], [v["approver"]]),
        ("新员工多久能独立操作数控车床？", [cid("新员工的独立操作")], [str(v["coach"])]),
        ("滚齿机换刀以后要做什么？", [cid("YK3610 滚齿机的刀具")], ["首件必检"]),
        ("供应商什么条件下可以免检？", [cid("免检与让步")], [str(v["free_lots"]), "季度"]),
        ("来料抽样按哪个标准？", [cid("来料检验")], ["GB/T 2828.1"]),
        # 手册里没有规定的问题：正确的回答是“没有规定”
        ("输出轴的动平衡等级是多少？", [], []),
        ("客户投诉的响应时限是几天？", [], []),
        ("车间的噪声限值是多少分贝？", [], []),
        ("齿轮的齿面接触斑点要求占多少面积？", [], []),
    ]
    out = []
    for q, g, f in qs:
        out.append({"q": q, "q2": COLLOQUIAL.get(q, q), "gold": g, "facts": f, "answerable": len(g) > 0})
    return out


# 同一个问题，工人在现场会怎么问：少用条文里的原词、多用口语。
# 这一列是 13.6 节的关键对照——问法一换，只按词算的检索就掉下来。
COLLOQUIAL = {
    "SH-301 输出轴的同轴度公差是多少？": "301 这个轴，两头转起来晃动卡多少？",
    "输出轴同轴度超差了怎么处理、谁批？": "轴晃动超了还能不能用？谁说了算？",
    "SH-302 输入轴的同轴度公差呢？": "302 那根轴晃动允许多少？",
    "量具多久校准一次？校准记录保存几年？": "卡尺千分尺多久送一次检？单子留多久？",
    "终检用的量具精度要求是怎么规定的？": "量最后一道的尺子要多准才算行？",
    "三坐标测量间的温度要求是多少？": "打三坐标那间屋子多少度？",
    "输出轴调质后的硬度范围是多少？每炉抽检几件？": "301 轴热处理完要多硬？一炉查几个？",
    "主动齿轮的硬度要求和输出轴一样吗？": "齿轮和轴热处理完的硬度一样不一样？",
    "输出轴配合面的粗糙度要求？": "301 轴装轴承那段光洁度要多光？",
    "首件没判合格能不能接着加工？": "第一个零件还没判出来，机床能继续干吗？",
    "巡检多久一次、每次抽几件？": "干活的时候多久过来看一次、看几个？",
    "关键尺寸的过程能力要求是多少？不够怎么办？": "那个 Cpk 要多少才算过关？不够要停机吗？",
    "发现不合格品后多长时间内要填评审单？": "挑出坏件以后，多久要把单子填上？",
    "同一个零件最多返工几次？": "一个件能来回修几遍？",
    "什么情况下必须开纠正措施单？": "同一个毛病老出，要走什么流程？",
    "检验记录要保存几年？电子记录多久备份？": "检验单子存几年？电脑里的多久备份一回？",
    "能从成品查到原材料炉号吗？怎么编批？": "成品能不能倒着查到是哪一炉钢？批号怎么编？",
    "记录写错了能涂改吗？": "单子写错了能不能用涂改液？",
    "检验员的授权有效期多长？": "检验的本子几年过期？",
    "报废单谁签字？金额大的要不要再报？": "废件的单子谁签？钱多了还要往上报吗？",
    "让步接收单谁签字？": "超差放行那张单子谁签？",
    "新员工多久能独立操作数控车床？": "新来的多久能自己上数控车？",
    "滚齿机换刀以后要做什么？": "滚齿机换完刀第一件要不要查？",
    "供应商什么条件下可以免检？": "来料什么时候可以不检？",
    "来料抽样按哪个标准？": "进来的料按哪个国标抽？",
}


# ---------------------------------------------------------------- 分词与切片

_ASCII = re.compile(r"[A-Za-z0-9][A-Za-z0-9.\-/]*")
_HAN = re.compile(r"[一-鿿]")


def tokens(s: str) -> list[str]:
    """中文按字二元组切（相邻两个汉字算一个词元，兼顾单字），英文、数字与编号按词切。
    不用分词器：分词器一换，检索结果就变，而字 n 元组对中文检索足够好，且结果可复算。"""
    out = [m.group(0).lower() for m in _ASCII.finditer(s)]
    han = _HAN.findall(s)
    out += han
    out += [han[i] + han[i + 1] for i in range(len(han) - 1)]
    return out


def document(man: list[dict]) -> tuple[str, list[tuple]]:
    """把手册连成一片正文，并记下每一条占的字符区间——真实流水线拿到的是一份连续的文件，
    不是一条一条的条文，所以切片会把条文切断，这正是“切多长、重叠多少”要讨论的原因。"""
    parts, spans, pos = [], [], 0
    for c in man:
        piece = f"{c['id']} {c['title']}。{c['text']}\n"
        spans.append((pos, pos + len(piece), c["id"], c["page"], c["obsolete"]))
        parts.append(piece)
        pos += len(piece)
    return "".join(parts), spans


def chunks(man: list[dict], size: int = 300, overlap: int = 60, skip_obsolete: bool = False) -> list[dict]:
    """在连续正文上按字符切片。每片记下它覆盖了哪几条、第几页——答案要能指到原文。
    size 与 overlap 以字符计。skip_obsolete=True 时把已废止的旧版条文从索引里去掉（13.9 节比较两种做法）。"""
    man = [c for c in man if not (skip_obsolete and c["obsolete"])]
    text, spans = document(man)
    step = max(1, size - overlap)
    out = []
    for i in range(0, max(1, len(text) - overlap), step):
        piece = text[i:i + size]
        if len(piece) < size // 3 and out:
            break
        srcs = [(cid, pg, ob) for a, b, cid, pg, ob in spans if a < i + len(piece) and b > i]
        out.append({"text": piece, "srcs": [t[0] for t in srcs],
                    "src": srcs[0][0] if srcs else "", "page": srcs[0][1] if srcs else 0,
                    "obsolete": all(t[2] for t in srcs) if srcs else False})
    return out


# ---------------------------------------------------------------- 两种检索

_IDX_CACHE: dict = {}


def index(docs: list[dict]) -> dict:
    """为一组片子建倒排索引（词 → 片号与词频），连同片长与平均片长。建一次，所有问题共用。"""
    key = (id(docs), len(docs))
    got = _IDX_CACHE.get(key)
    if got is not None:
        return got
    post: dict[str, dict[int, int]] = {}
    lens = np.zeros(len(docs))
    for i, d in enumerate(docs):
        t = tokens(d["text"])
        lens[i] = len(t)
        for w in t:
            post.setdefault(w, {}).setdefault(i, 0)
            post[w][i] += 1
    idx = {"post": post, "lens": lens, "avg": max(lens.mean(), 1e-9), "n": len(docs)}
    _IDX_CACHE[key] = idx
    return idx


def bm25(query: str, docs: list[dict], k1: float = 1.5, b: float = 0.75) -> np.ndarray:
    """BM25：按词频与逆文档频率打分，长片打折。公式见 13.6 节。走倒排索引，只碰含查询词的片子。"""
    idx = index(docs)
    post, lens, avg, n = idx["post"], idx["lens"], idx["avg"], idx["n"]
    score = np.zeros(n)
    for w in set(tokens(query)):
        pl = post.get(w)
        if not pl:
            continue
        df = len(pl)
        iw = math.log(1 + (n - df + 0.5) / (df + 0.5))
        for i, f in pl.items():
            score[i] += iw * f * (k1 + 1) / (f + k1 * (1 - b + b * lens[i] / avg))
    return score


def content_tokens(q: str) -> list[str]:
    """问题里的“内容词”：两个汉字的组合与编号、数字，去掉常见的疑问词与虚词。"""
    stop = {"多少", "是不是", "能不能", "怎么", "怎样", "什么", "要不要", "可以", "需要", "规定",
            "要求", "的话", "一下", "我们", "这个", "那个", "几个", "多久", "有没"}
    return [w for w in tokens(q) if len(w) > 1 and w not in stop]


def manual_coverage(query: str, docs: list[dict]) -> float:
    """问题里的内容词，有多少在手册的**某处**出现过（走倒排索引）。
    判断“手册里有没有这件事”，看的是这个，而不是检索分数的高低：
    分数高只说明取回的片子与问法像，问到的东西在不在手册里是另一回事（13.6、13.9 节）。"""
    cw = content_tokens(query)
    if not cw:
        return 0.0
    post = index(docs)["post"]
    return sum(1 for w in cw if w in post) / len(cw)


def idf_coverage(query: str, docs: list[dict]) -> float:
    """按逆文档频率加权的手册覆盖率：罕见词（真正把问题区分开的那些）权重大。
    一个问题里的罕见词在手册里全都查不到，它大概就不是手册能答的问题。
    这是三种“可答性”信号里最好的一个，但在口语问法上仍然分不干净——见算例 13.6.4 的结论。"""
    cw = content_tokens(query)
    if not cw:
        return 0.0
    idx = index(docs)
    post, n = idx["post"], idx["n"]
    num = den = 0.0
    for w in cw:
        df = len(post.get(w, {}))
        weight = math.log(1 + (n + 0.5) / (df + 0.5))      # 没出现过的词权重最大
        den += weight
        if df:
            num += weight
    return num / den if den else 0.0


def coverage(query: str, doc: dict) -> float:
    """问题里的内容词有多少出现在这一片里。分数高不代表答得上——**问到的东西在不在手册里**才是关键，
    所以拒答要看覆盖率，不是看检索分数（13.6 节算例）。"""
    cw = content_tokens(query)
    if not cw:
        return 0.0
    t = doc["text"]
    return sum(1 for w in cw if w in t) / len(cw)


def embed(text: str, dim: int = 256) -> np.ndarray:
    """一个**不需要模型**的向量表示：把词元哈希到 dim 维上（随机符号），归一化。
    它当然比训练出来的句向量弱——它没有语义，同义词落在完全不同的维上——但足以说明“向量检索”的流程，
    而且在任何机器上都算得出同一个结果。真的句向量模型在 GPU 实验 13.6 里测。"""
    v = np.zeros(dim)
    for w in tokens(text):
        h = int(hashlib.blake2b(w.encode(), digest_size=8).hexdigest(), 16)
        v[h % dim] += 1.0 if h >> 63 else -1.0
    n = np.linalg.norm(v)
    return v / n if n > 0 else v


_EMB_CACHE: dict = {}


def embed_matrix(docs: list[dict], dim: int = 256) -> np.ndarray:
    """把一组片子的向量算好存起来（按文本缓存）：问一个问题只要算一次问题的向量。"""
    key = (id(docs), len(docs), dim)
    hit_ = _EMB_CACHE.get(key)
    if hit_ is not None and hit_.shape == (len(docs), dim):
        return hit_
    M = np.stack([embed(d["text"], dim) for d in docs]) if docs else np.zeros((0, dim))
    _EMB_CACHE[key] = M
    return M


def vector_scores(query: str, docs: list[dict], dim: int = 256) -> np.ndarray:
    return embed_matrix(docs, dim) @ embed(query, dim)


# 现场说法 → 手册用词的同义词表。企业场景里，这样一张几十条的表常常比换模型管用（13.6 节）。
SYNONYMS = {
    "晃动": "同轴度", "晃": "同轴度", "圆不圆": "同轴度", "跳动": "同轴度",
    "尺子": "量具", "卡尺": "量具", "千分尺": "量具", "送检": "校准", "送一次检": "校准",
    "多准": "测量不确定度", "光洁度": "表面粗糙度", "多光": "表面粗糙度",
    "多硬": "硬度", "热处理完": "调质", "坏件": "不合格品", "废件": "报废",
    "单子": "记录", "本子": "授权", "过期": "有效期", "来回修": "返工",
    "老出": "重复出现", "超了": "超差", "放行": "让步接收", "倒着查": "追溯",
    "哪一炉钢": "炉号", "涂改液": "更改", "过来看一次": "巡检", "看几个": "抽检",
    "第一个零件": "首件", "第一件": "首件", "停机": "停机", "过关": "过程能力",
    "不检": "免检", "抽": "抽样", "国标": "GB/T", "自己上": "独立操作", "新来的": "新员工",
}


def expand(query: str) -> str:
    """按同义词表把现场说法补成手册用词（原话保留，只是把手册里的词加在后面）。"""
    extra = [v for k, v in SYNONYMS.items() if k in query]
    return query + ("（" + " ".join(dict.fromkeys(extra)) + "）" if extra else "")


_NUM = re.compile(r"[A-Za-z]{2}-?\d{2,4}|\b\d{3}\b")


def part_hint(query: str) -> list[str]:
    """从问题里抠出零件号的线索（“301”“SH-301”“GH-12”）。手册里有几百条字面几乎一样的条文，
    靠零件号把范围缩小，比换检索模型有效得多（13.6 节的算例会把这件事量出来）。"""
    return [m.group(0).upper().replace("-", "") for m in _NUM.finditer(query)]


def boost_by_part(query: str, score: np.ndarray, docs: list[dict], factor: float = 2.0) -> np.ndarray:
    """问题里出现零件号时，把正文里也出现这个号的片子的分数乘上 factor。"""
    hints = part_hint(query)
    if not hints:
        return score
    out = score.copy()
    for i, d in enumerate(docs):
        flat = d["text"].upper().replace("-", "")
        if any(h in flat for h in hints):
            out[i] *= factor
    return out


def retrieve(query: str, docs: list[dict], k: int = 5, how: str = "bm25", alpha: float = 0.5) -> list[int]:
    """取前 k 片。how 取 bm25、vector、hybrid（两种分数各自归一化后加权相加），
    后面可以加 `+syn`（先按同义词表把问题补写一遍）与 `+part`（问题里有零件号时给含该号的片子加权），
    如 "bm25+syn+part"。"""
    use_part = "+part" in how
    how = how.replace("+part", "")
    if how.endswith("+syn"):
        query, how = expand(query), how[:-4]
    if how == "bm25":
        s = bm25(query, docs)
    elif how == "vector":
        s = vector_scores(query, docs)
    else:
        a, b_ = bm25(query, docs), vector_scores(query, docs)
        s = alpha * a / max(a.max(), 1e-9) + (1 - alpha) * b_ / max(b_.max(), 1e-9)
    if use_part:
        s = boost_by_part(query, s, docs)
    return list(np.argsort(-s)[:k])


def hit(idx: list[int], docs: list[dict], gold: list[str]) -> bool:
    """命中：取回的片里至少有一片来自标准答案的条文（没有标准答案的问题不算命中）。"""
    if not gold:
        return False
    return any(c.split("(")[0] in gold for i in idx for c in docs[i]["srcs"])


def recall(idx: list[int], docs: list[dict], gold: list[str]) -> float:
    """召回率：标准答案的那几条里，有几条被取回。"""
    if not gold:
        return float("nan")
    got = {c.split("(")[0] for i in idx for c in docs[i]["srcs"]}
    return len([g for g in gold if g in got]) / len(gold)


# ---------------------------------------------------------------- 词向量（13.1 节）

BASE = ["轴", "齿轮", "轴承", "箱体", "螺栓"]          # 五类零件
GRADE = ["粗", "精"]                                  # 两个等级
CTX_BASE = {"轴": ["车床", "顶尖", "轴颈"], "齿轮": ["滚齿", "齿形", "模数"],
            "轴承": ["压装", "游隙", "内圈"], "箱体": ["镗孔", "结合面", "铸件"],
            "螺栓": ["扭矩", "螺纹", "垫片"]}
CTX_GRADE = {"粗": ["留量", "粗加工", "大进给"], "精": ["终检", "精加工", "小进给"]}


def corpus(n_sent: int = 6000, seed: int = 13) -> list[list[str]]:
    """程序生成的小语料：每个词是“等级 + 零件”（如“精轴”），句子里同时出现零件的上下文词与等级的上下文词。
    这样训出来的词向量会把“等级”这件事放在一个方向上，于是
    `精轴 − 粗轴 + 粗齿轮 ≈ 精齿轮` 这种类比真的成立（13.1 节的算例与动画）。"""
    rng = np.random.default_rng(seed)
    sents = []
    for _ in range(n_sent):
        b = BASE[rng.integers(len(BASE))]
        g = GRADE[rng.integers(len(GRADE))]
        w = g + b
        ctx = list(rng.choice(CTX_BASE[b], 2, replace=False)) + list(rng.choice(CTX_GRADE[g], 2, replace=False))
        rng.shuffle(ctx)
        sents.append([ctx[0], ctx[1], w, ctx[2], ctx[3]])
    return sents


def skipgram(sents: list[list[str]], dim: int = 24, epochs: int = 10, window: int = 2,
             neg: int = 5, lr: float = 0.025, batch: int = 64, seed: int = 0) -> tuple[dict, np.ndarray]:
    """skip-gram + 负采样，几十行 NumPy。返回（词表索引, 词向量矩阵）。
    目标：让“中心词·上下文词”的内积在真实共现上变大、在随机抽到的词上变小。
    按小批量更新（一批 batch 对），所以几万对也只要几秒；负采样按词频的 0.75 次方，与 word2vec 一致。
    批量不能太大：一批里同一个词出现多次时梯度要累加，批大了步子就过头（取 512 时会发散成 NaN），
    所以默认 64 对一批、步长 0.025——这正是“批量与步长要一起调”（2.6 节）在一个小模型上的样子。"""
    vocab = sorted({w for s in sents for w in s})
    ix = {w: i for i, w in enumerate(vocab)}
    rng = np.random.default_rng(seed)
    W = rng.normal(0, 0.1, (len(vocab), dim))              # 中心词向量
    C = rng.normal(0, 0.1, (len(vocab), dim))              # 上下文向量
    freq = np.zeros(len(vocab))
    for s in sents:
        for w in s:
            freq[ix[w]] += 1
    p_neg = freq ** 0.75
    p_neg /= p_neg.sum()
    pairs = np.array([(ix[s[i]], ix[s[j]]) for s in sents for i in range(len(s))
                      for j in range(max(0, i - window), min(len(s), i + window + 1)) if i != j])
    for _ in range(epochs):
        rng.shuffle(pairs)
        for b0 in range(0, len(pairs), batch):
            p = pairs[b0:b0 + batch]
            a, pos = p[:, 0], p[:, 1]
            negs = rng.choice(len(vocab), (len(p), neg), p=p_neg)
            tgt = np.concatenate([pos[:, None], negs], axis=1)        # (B, 1+neg)
            lab = np.zeros_like(tgt, dtype=float)
            lab[:, 0] = 1.0
            w, c = W[a], C[tgt]                                       # (B, d), (B, 1+neg, d)
            z = np.clip(np.einsum("bkd,bd->bk", c, w), -30, 30)       # 夹一下，免得 exp 溢出
            g = lab - 1 / (1 + np.exp(-z))                            # 逻辑回归的梯度
            dW = np.einsum("bk,bkd->bd", g, c)
            dC = g[:, :, None] * w[:, None, :]
            np.add.at(W, a, lr * dW)                                  # 同一个词在一批里可能出现多次，要累加
            np.add.at(C, tgt, lr * dC)
    assert np.isfinite(W).all(), "词向量发散了：把批量调小或步长调小"
    return ix, W


def cos(a: np.ndarray, b: np.ndarray) -> float:
    return float(a @ b / max(np.linalg.norm(a) * np.linalg.norm(b), 1e-12))


def nearest(ix: dict, W: np.ndarray, v: np.ndarray, skip: set[str] = frozenset(), n: int = 1) -> list[tuple]:
    inv = {i: w for w, i in ix.items()}
    sc = [(cos(v, W[i]), inv[i]) for i in range(len(W)) if inv[i] not in skip]
    sc.sort(reverse=True)
    return [(w, s) for s, w in sc[:n]]


# ---------------------------------------------------------------- 两个指标与一个模型

def bleu(ref: list[str], hyp: list[str], n_max: int = 4) -> float:
    """BLEU：n 元组精确率的几何平均 × 长度惩罚。n 元组的切法一换，分数就变（13.2 节）。"""
    if not hyp:
        return 0.0
    logs = []
    for n in range(1, n_max + 1):
        hn = [tuple(hyp[i:i + n]) for i in range(len(hyp) - n + 1)]
        rn = [tuple(ref[i:i + n]) for i in range(len(ref) - n + 1)]
        if not hn:
            return 0.0
        need: dict = {}
        for g in rn:
            need[g] = need.get(g, 0) + 1
        m = 0
        for g in hn:
            if need.get(g, 0) > 0:
                need[g] -= 1
                m += 1
        if m == 0:
            return 0.0
        logs.append(math.log(m / len(hn)))
    bp = min(1.0, math.exp(1 - len(ref) / len(hyp)))        # 太短要罚
    return bp * math.exp(sum(logs) / n_max)


def bradley_terry(pairs: list[tuple], n_item: int, iters: int = 500, lr: float = 0.5) -> np.ndarray:
    """由两两比较（赢者, 输者）求每个回答的分数：P(i 胜 j) = σ(s_i − s_j)，最大似然。
    这就是人类反馈里的奖励模型（13.5 节），直接偏好优化用的是同一个概率模型。"""
    s = np.zeros(n_item)
    for _ in range(iters):
        g = np.zeros(n_item)
        for i, j in pairs:
            p = 1 / (1 + np.exp(-(s[i] - s[j])))
            g[i] += 1 - p
            g[j] -= 1 - p
        s += lr * g / max(len(pairs), 1)
        s -= s.mean()                                       # 分数只有相对意义，固定零点
    return s
