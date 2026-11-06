"""平台“三维视频”的旁白（第 99 轮）：第 90 轮只给缝纫机讲解片配，本轮所有三维视频都能配。

- 念什么：场景里有解说词（voice 段，AI 写场景时顺带写的，每段镜头一两句，中英成对）就念解说词；
  没有（从样片复制、老视频、缝纫机讲解片）就照第 90 轮念画面上的标题和底部字幕。缝纫机讲解片（有 lock）一律念字幕，数锁定。
- 解说词里的数只能是画面上已有的数（标题、标注、面板里出现过的），1–10 的小整数除外（“3 个关节”“第 2 步”）；
  电影风格（style: cinematic）的解说词本身就画在屏上当大字幕，不查。
- 统一的 voice 段：[{t, zh, en}]（AI 写），配好后网关补上 dur（长度）、seg（这一段开头）、say（实际念的稿）；
  念字幕配出来的标 src: labels。旧格式 {t, dur, text}（第 90 轮）照样认。
- 拉长、混音沿用 sewing_voice（旁白长的段放慢拉长，读完再进下一段）。
"""
from __future__ import annotations

import re

from . import sewing_voice as SVO

NUM_RE = re.compile(r"\d+(?:\.\d+)?")
MAX_ZH, MAX_EN = 90, 260            # 一段解说词：中文最多 90 字、英文 260 字符（一两句）


def script(spec: dict) -> list[dict]:
    """AI 写的解说词（不含网关念字幕时写的 src: labels，也不含第 90 轮旧格式）"""
    v = spec.get("voice")
    if not isinstance(v, list):
        return []
    return [x for x in v if isinstance(x, dict) and x.get("src") != "labels" and (x.get("zh") or x.get("en"))]


def screen_numbers(spec: dict) -> set[str]:
    """画面上出现的数：标题、标注、面板里写的字"""
    out: set[str] = set()
    texts = [spec.get("title") or {}] + [x for x in spec.get("labels") or [] if isinstance(x, dict)]
    for x in texts:
        for k in ("zh", "en"):
            out |= set(NUM_RE.findall(str(x.get(k) or "")))
    p = spec.get("panel")
    if isinstance(p, dict):
        out |= set(NUM_RE.findall(str(p)))
    return out


def _small(n: str) -> bool:
    return "." not in n and 0 <= int(n) <= 10


def errors(spec: dict, dur: float) -> list[str]:
    """voice 段的格式检查；解说词里的数要是画面上有的。问题用中文写，直接交给 AI 改"""
    v = spec.get("voice")
    if v is None:
        return []
    if not isinstance(v, list):
        return ["voice（解说词）要是列表：[{t: 秒, zh: 中文, en: English}, …]"]
    errs, nums = [], screen_numbers(spec)
    last = -1.0
    for i, x in enumerate(v):
        if not isinstance(x, dict) or not isinstance(x.get("t"), (int, float)) or isinstance(x.get("t"), bool):
            errs.append(f"voice 第 {i + 1} 句要写 t（这句解说从第几秒的镜头开始）")
            continue
        if not -0.01 <= float(x["t"]) <= dur:
            errs.append(f"voice 第 {i + 1} 句的 t={x['t']} 超出视频长度")
        if float(x["t"]) < last - 1e-6:
            errs.append("voice 各句的 t 要从小到大")
        last = float(x["t"])
        if x.get("src") == "labels" or "text" in x:          # 网关念字幕时写的 / 第 90 轮旧格式
            continue
        zh, en = x.get("zh"), x.get("en")
        if not (isinstance(zh, str) and zh.strip()) and not (isinstance(en, str) and en.strip()):
            errs.append(f"voice 第 {i + 1} 句要有 zh、en（念的解说词）")
            continue
        if len(str(zh or "")) > MAX_ZH or len(str(en or "")) > MAX_EN:
            errs.append(f"voice 第 {i + 1} 句太长（中文最多 {MAX_ZH} 字、英文 {MAX_EN} 字符，一两句话）")
        if spec.get("style") == "cinematic":                 # 电影风格：解说词本身就画在屏上当大字幕，不另查
            continue
        bad = sorted({n for n in NUM_RE.findall(f"{zh or ''} {en or ''}") if n not in nums and not _small(n)})
        if bad:
            errs.append(f"voice 第 {i + 1} 句里的数 {'、'.join(bad[:4])} 画面上没有：解说词里的数只能用标题、标注里已有的数")
    return errs


def lines(spec: dict, lang: str, locked: bool = False) -> tuple[list[dict], str]:
    """要念的句子 [{t0, t1, text, src, kind, zh?, en?}] 和来源（script = 解说词，labels = 标题字幕）。
    缝纫机讲解片（locked）一律念字幕。"""
    sc = [] if locked else script(spec)
    if not sc:
        items = SVO.lines(spec, lang)
        for x in items:
            x["kind"] = "labels"
        return items, "labels"
    dur = float(spec.get("duration") or 0)
    key = "en" if lang == "en" else "zh"
    starts = [float(x.get("seg", x["t"])) for x in sc]
    out = []
    for i, x in enumerate(sc):
        raw = str(x.get(key) or "").strip()                    # 缺这种话的那句不念（不拿另一种话凑）
        if not raw:
            continue
        t1 = starts[i + 1] if i + 1 < len(sc) else dur
        if lang == "zh":                                          # “快 2 倍”“2 个关节”念“两”
            raw_say = re.sub(r"(?<![\d.])\s*(?<![\d.])2\s*(?=[个倍台次段种根条把块])", "两", raw)
        else:
            raw_say = raw
        text = SVO.spoken(raw_say, lang)
        if lang == "zh" and not text.endswith(("。", "！", "？")):
            text += "。"
        elif lang == "en" and not text.endswith((".", "!", "?")):
            text += "."
        out.append({"t0": starts[i], "t1": max(t1, starts[i]), "text": text, "src": [raw], "kind": "script",
                    "zh": x.get("zh"), "en": x.get("en")})
    return out, "script"


def unpin(text: str) -> str:
    """AI 或人改过配好旁白的场景：解说词的开口时刻退回这一段开头（t = seg），去掉 seg、say（下次配音重写），
    免得每重配一次往后挪一点；dur 留着（标明这是配过旁白、可以到 150 秒的片子）。改了 t 的那句照改后的 t。"""
    import yaml
    try:
        s = yaml.safe_load(text)
    except yaml.YAMLError:
        return text
    if not isinstance(s, dict) or not isinstance(s.get("voice"), list):
        return text
    changed = False
    for x in s["voice"]:
        if not isinstance(x, dict) or x.get("src") == "labels" or "seg" not in x:
            continue
        try:
            if abs(float(x["t"]) - float(x["seg"]) - SVO.LEAD) < 0.06:
                x["t"] = x["seg"]
        except (TypeError, ValueError, KeyError):
            pass
        x.pop("seg", None)
        x.pop("say", None)
        changed = True
    return yaml.safe_dump(s, allow_unicode=True, sort_keys=False, width=200) if changed else text
