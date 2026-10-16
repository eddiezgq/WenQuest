"""白板课的声音（第 35 轮第 3 步）：配音前把符号换成读法；录音识别结果合并成句；换录音后画板按文字对上新的分段。"""
import difflib
import re

# 合成前：符号 → 读法（语音合成不认识的符号会被跳过或读错）
SAY = [("τ", "tau"), ("θ", "theta"), ("ω", "omega"), ("α", "alpha"), ("β", "beta"), ("λ", "lambda"), ("μ", "mu"), ("π", "派"),
       ("Δ", "delta"), ("Σ", "求和"), ("×", "乘以"), ("·", "乘"), ("÷", "除以"), ("≈", "约等于"), ("≠", "不等于"), ("≤", "小于等于"),
       ("≥", "大于等于"), ("±", "正负"), ("√", "根号"), ("°", "度"), ("²", "的平方"), ("³", "的立方"), ("→", "到"), ("∞", "无穷"),
       ("%", "百分之")]
UNITS = [(r"N·m", "牛米"), (r"N\s*m\b", "牛米"), (r"\bm/s²", "米每二次方秒"), (r"\bm/s\b", "米每秒"), (r"\brad/s\b", "弧度每秒"),
         (r"\bkg\b", "千克"), (r"\bkW\b", "千瓦"), (r"\bmm\b", "毫米"), (r"\bcm\b", "厘米")]


def speakable(text: str) -> str:
    """The words to send to speech synthesis for one Chinese segment (the caption keeps the symbols)."""
    t = text
    for pat, word in UNITS:
        t = re.sub(r"(?<=\d)\s*" + pat, word, t)
    t = re.sub(r"(\d+(?:\.\d+)?)\s*%", r"百分之\1", t)
    for sym, word in SAY:
        t = t.replace(sym, f" {word} " if word.isascii() else word)
    t = re.sub(r"(?<=\d)\s*=\s*(?=\d)", "等于", t)
    t = t.replace("=", "等于")
    return re.sub(r"\s+", " ", t).strip()


def merge_asr(rows: list[dict]) -> list[dict]:
    """Speech-recognition pieces [{start, end, text}] → lecture segments [{t0, t1, zh}]: short pieces of one sentence
    (a short pause, still short) are joined, so every segment is about one thing to draw."""
    out: list[dict] = []
    for r in rows:
        text = str(r.get("text") or "").strip()
        if not text:
            continue
        s = {"t0": round(float(r.get("start", 0)), 2), "t1": round(float(r.get("end", 0)), 2), "zh": text}
        last = out[-1] if out else None
        if (last and s["t0"] - last["t1"] < 0.5 and len(last["zh"]) + len(text) < 28
                and not last["zh"].endswith(("。", "？", "！", ".", "?", "!"))):
            last["t1"] = s["t1"]
            last["zh"] += text if last["zh"].endswith(("，", "、", ",")) else "，" + text
        else:
            out.append(s)
    return out


def remap(old: list[dict], new: list[dict]) -> list[int]:
    """old segment index → new segment index, by matching the words (a new recording rarely splits sentences the same way)."""
    a = "".join(s["zh"] for s in old)
    b = "".join(s["zh"] for s in new)
    a_start, pos = [], 0
    for s in old:
        a_start.append(pos)
        pos += len(s["zh"])
    b_owner: list[int] = []
    for i, s in enumerate(new):
        b_owner += [i] * len(s["zh"])
    cmap = {}
    for blk in difflib.SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks():
        for k in range(blk.size):
            cmap[blk.a + k] = blk.b + k
    out = []
    for i, st in enumerate(a_start):
        end = a_start[i + 1] if i + 1 < len(a_start) else len(a)
        hits = [cmap[c] for c in range(st, end) if c in cmap]
        if hits and b_owner:
            out.append(b_owner[min(hits[0], len(b_owner) - 1)])
        else:   # no matching words: the same relative position
            out.append(round(i * (len(new) - 1) / max(1, len(old) - 1)))
    for i in range(1, len(out)):  # keep the order of the lecture
        out[i] = max(out[i], out[i - 1])
    return out


def remap_scene(scene: dict, moves: list[dict], mapping: list[int]) -> None:
    """Move every drawing (and every move) to the new segment its words went to."""
    if not mapping:
        return
    at = 0
    for e in scene.get("elements") or []:
        if e.get("type") == "frame" or e.get("isDeleted"):
            continue
        cd = dict(e.get("customData") or {})
        if isinstance(cd.get("wq_at"), int):
            at = cd["wq_at"]
        cd["wq_at"] = mapping[max(0, min(at, len(mapping) - 1))]
        e["customData"] = cd
    for m in moves:
        a = int(m.get("at", 0))
        m["at"] = mapping[max(0, min(a, len(mapping) - 1))]
        if isinstance(m.get("until"), int):
            m["until"] = mapping[max(0, min(m["until"], len(mapping) - 1))]
