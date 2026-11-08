"""规则提取：公告类型、关键词命中、排除词、预算、截止时间、采购人、地区。只用规则，不用大模型。"""
import re

PROVINCES = ["北京", "天津", "上海", "重庆", "河北", "山西", "辽宁", "吉林", "黑龙江", "江苏", "浙江", "安徽", "福建",
             "江西", "山东", "河南", "湖北", "湖南", "广东", "海南", "四川", "贵州", "云南", "陕西", "甘肃", "青海",
             "台湾", "内蒙古", "广西", "西藏", "宁夏", "新疆", "香港", "澳门", "兵团"]

TYPE_RULES = [  # 顺序有意义：先判断结果类，再判断招标类
    ("result", ("中标", "成交结果", "成交公告", "结果公告", "废标", "终止公告", "流标", "合同公告")),
    ("correction", ("更正", "变更公告", "澄清", "延期")),
    ("intention", ("采购意向", "意向公开")),
    ("single_source", ("单一来源",)),
    ("negotiation", ("竞争性磋商", "竞争性谈判", "磋商公告", "谈判公告")),
    ("inquiry", ("询价", "比选", "竞价")),
    ("tender", ("招标公告", "公开招标", "邀请招标", "采购公告", "资格预审", "招标")),
]

_NUM = r"([0-9][0-9,，]*(?:\.[0-9]+)?)"
BUDGET_RES = [
    re.compile(r"(?:预算金额|采购预算|项目预算|最高限价|控制价|预算价)[^0-9\n]{0,20}?" + _NUM + r"\s*(万元|万|元)"),
    re.compile(r"(?:预算金额|采购预算|项目预算|最高限价)[（(](万元|元)[)）][:：\s]*" + _NUM),
]
DATE = r"(20\d{2})\s*[-年./]\s*(\d{1,2})\s*[-月./]\s*(\d{1,2})\s*日?(?:\s*(\d{1,2})\s*[:：时点]\s*(\d{1,2})?)?"
DEADLINE_RES = [re.compile(r"(?:提交投标文件截止时间|投标截止时间|响应文件提交截止时间|递交截止时间|开标时间|"
                           r"截止时间|获取.{0,6}文件.{0,6}时间)[^0-9]{0,30}?" + DATE)]
BUYER_RES = [re.compile(r"(?:采购人(?:名称)?|招标人(?:名称)?|采购单位)\s*[:：]\s*([^\s，,。;；|<>]{2,40})")]


def notice_type(text):
    for t, words in TYPE_RULES:
        if any(w in text for w in words):
            return t
    return "other"


def keyword_hits(text, keywords):
    """keywords: {group: [words]} -> (groups, words) 命中情况，大小写不敏感。"""
    low = text.lower()
    groups, words = [], []
    for g, ws in keywords.items():
        for w in ws:
            if w.lower() in low:
                words.append(w)
                if g not in groups:
                    groups.append(g)
    return groups, words


def excluded(text, words):
    return [w for w in words if w in text]


def budget_cny(text):
    """返回预算（元，float）；找不到返回 None。"""
    for rx in BUDGET_RES:
        m = rx.search(text)
        if not m:
            continue
        a, b = m.groups()
        num, unit = (a, b) if rx is BUDGET_RES[0] else (b, a)
        try:
            v = float(num.replace(",", "").replace("，", ""))
        except ValueError:
            continue
        return v * 10000 if unit.startswith("万") else v
    return None


def deadline(text):
    for rx in DEADLINE_RES:
        m = rx.search(text)
        if m:
            y, mo, d, h, mi = m.groups()
            s = f"{int(y):04d}-{int(mo):02d}-{int(d):02d}"
            if h:
                s += f" {int(h):02d}:{int(mi or 0):02d}"
            return s
    return None


def buyer(text):
    for rx in BUYER_RES:
        m = rx.search(text)
        if m:
            return m.group(1).strip("：: ")
    return None


def region(text):
    for p in PROVINCES:
        if p in text:
            return p
    return None


def normalize_date(s):
    m = re.search(r"(20\d{2})\D{1,3}(\d{1,2})\D{1,3}(\d{1,2})", s or "")
    return f"{int(m.group(1)):04d}-{int(m.group(2)):02d}-{int(m.group(3)):02d}" if m else None
