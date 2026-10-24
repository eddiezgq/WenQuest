"""每日科普快节奏版共用的小工具（照《会飞的特斯拉》v2 的 helpers 抽出来）：
文字蹦出、大数字、箭头射出、柱子长高、液面下降、移动、转动、一直在动的小装饰，fit() 把动作压进画板在屏幕上的时间，
main() 配音（逐句缓存）并写 lesson.json（pace 0.2、ink 1.7、pan 0.45、subs、语速 1.22、句间 0.12 秒、无手）。"""
import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "services" / "gateway"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.production.whiteboard import ai as wai  # noqa: E402
from app.production.whiteboard.core import missing_chars  # noqa: E402
from app.production.whiteboard.speech import speakable  # noqa: E402
from popkit import txt  # noqa: E402

N = [0]


def uid(p="e"):
    N[0] += 1
    return f"{p}{N[0]}z"


def pop(at, ids, delay=0.0, dur=0.35):
    return {"t": "move", "at": at, "kind": "pop", "targets": ids if isinstance(ids, list) else [ids], "dur": dur, "delay": delay}


def T(at, x, y, s, text, c="ink", d=None, **kw):
    """Text; d = seconds into the sentence when it pops in (None = just drawn)."""
    i = uid("t")
    font = "en" if all(ord(ch) < 128 for ch in text) and any(ch.isalpha() for ch in text) else "zh"
    E = [txt(x, y, s, text, at, c=c, id=i, font=kw.pop("font", font), **kw)]
    if d is not None:
        E.append(pop(at, i, d))
    return E


def BIG(at, x, y, text, c="red", d=0.0, s=140, **kw):
    return T(at, x, y, s, text, c=c, d=d, **kw)


def P(at, d, c="ink", w=4, idp=None, **kw):
    e = {"t": "path", "at": at, "c": c, "w": w, "d": d, **kw}
    if idp:
        e["id"] = idp
    return e


def R(at, x, y, w, h, c="ink", fill=None, idp=None, sw=5):
    e = {"t": "rect", "at": at, "x": x, "y": y, "w": w, "h": h, "c": c, "sw": sw}
    if fill:
        e["fill"] = fill
    if idp:
        e["id"] = idp
    return e


def O(at, cx, cy, r, c="ink", fill=None, idp=None, sw=5):
    e = {"t": "ellipse", "at": at, "x": cx - r, "y": cy - r, "w": 2 * r, "h": 2 * r, "c": c, "sw": sw}
    if fill:
        e["fill"] = fill
    if idp:
        e["id"] = idp
    return e


def bar(at, x, base, w, h, c, d=0.0, dur=0.8):
    i = uid("b")
    return [R(at, x, base - h, w, h, c=c, fill=c, idp=i),
            {"t": "move", "at": at, "kind": "grow", "targets": [i], "axis": "y", "pivot": [x + w / 2, base], "dur": dur, "delay": d}]


def arr(at, x0, y0, x1, y1, c="red", w=6, d=0.0, dur=0.5):
    i = uid("a")
    ax = "y" if abs(x1 - x0) < abs(y1 - y0) else "x"
    return [{"t": "arrow", "at": at, "id": i, "pts": [[x0, y0], [x1, y1]], "c": c, "w": w},
            {"t": "move", "at": at, "kind": "grow", "targets": [i], "axis": ax, "pivot": [x0, y0], "dur": dur, "delay": d}]


def sh(at, ids, dx, dy, d, dur):
    return {"t": "move", "at": at, "kind": "shift", "targets": ids if isinstance(ids, list) else [ids], "dx": dx, "dy": dy, "delay": d, "dur": dur}


def rot(at, ids, to, pivot, d, dur):
    return {"t": "move", "at": at, "kind": "rotate", "targets": ids if isinstance(ids, list) else [ids], "to": to, "pivot": list(pivot), "delay": d, "dur": dur}


def spin(at, i, pivot, rpm=120):
    return {"t": "move", "at": at, "kind": "spin", "targets": [i], "pivot": list(pivot), "rpm": rpm}


def pulse(at, i, d=0.0, dur=0.6):
    return {"t": "move", "at": at, "kind": "pulse", "targets": [i], "delay": d, "dur": dur}


def wig(at, i, pivot, amp=10, hz=2.0):
    return {"t": "move", "at": at, "kind": "wiggle", "targets": [i], "pivot": list(pivot), "amp": amp, "hz": hz}


def bob(at, i, amp=10, hz=1.2):
    return {"t": "move", "at": at, "kind": "bob", "targets": [i], "amp": amp, "hz": hz}


def shape_pop(at, el, d):
    """Give a drawn shape an id and pop it in at d."""
    i = uid("s")
    el["id"] = i
    return [el, pop(at, i, d)]


def check(at, x, y, c="green", d=0.0):
    i = uid("ck")
    return [P(at, f"M{x - 40},{y} L{x - 8},{y + 34} L{x + 48},{y - 40}", c=c, w=9, idp=i), pop(at, i, d)]


def cross(at, x, y, c="red", d=0.0):
    i = uid("cx")
    return [P(at, f"M{x - 36},{y - 36} L{x + 36},{y + 36} M{x + 36},{y - 36} L{x - 36},{y + 36}", c=c, w=9, idp=i), pop(at, i, d)]


def star(at, x, y, d=0.0, c="gold", r=26):
    i = uid("st")
    return [P(at, f"M{x - r},{y} L{x + r},{y} M{x},{y - r} L{x},{y + r} M{x - r * .7},{y - r * .7} L{x + r * .7},{y + r * .7} "
                  f"M{x - r * .7},{y + r * .7} L{x + r * .7},{y - r * .7}", c=c, w=5, idp=i), pop(at, i, d), spin(at, i, (x, y), 60)]


def bubbles(at, x, y, n=4, d=0.2, rise=260, c="blue"):
    """Little bubbles rising (one move per bubble, staggered)."""
    E = []
    for k in range(n):
        i = uid("bu")
        r = 10 + 5 * (k % 3)
        E += [O(at, x + 26 * ((k * 37) % 5 - 2), y - 30 * k, r, c=c, sw=3, idp=i), sh(at, i, 10 * (k % 2 * 2 - 1), -rise, d + 0.35 * k, 2.2)]
    return E


def waves(at, y, x0=80, x1=1840, c="blue", amp=14):
    i = uid("wv")
    n = int((x1 - x0) / 120)
    d = f"M{x0},{y} " + " ".join(f"Q{x0 + 120 * k + 60},{y - amp} {x0 + 120 * (k + 1)},{y}" for k in range(n))
    return [P(at, d, c=c, w=4, idp=i), {"t": "move", "at": at, "kind": "wiggle", "targets": [i], "pivot": [(x0 + x1) / 2, y], "amp": 1.2, "hz": 0.8}]


def sound(at, x, y, k=1.0, c="blue", d=0.0, dirn=1):
    """Three sound arcs that pop out one by one, then pulse."""
    E = []
    for n in range(3):
        i = uid("snd")
        r = (30 + 30 * n) * k
        E += [P(at, f"M{x + dirn * r * 0.5},{y - r} Q{x + dirn * r * 1.1},{y} {x + dirn * r * 0.5},{y + r}", c=c, w=5, idp=i), pop(at, i, d + 0.18 * n)]
    return E


def fit(boards, segs):
    """Squeeze each delayed move into the time its board is on screen (a move after the cut is never seen)."""
    for b in boards:
        last = max(e["at"] for e in b["elements"])
        for e in b["elements"]:
            if e["t"] != "move" or e.get("delay") is None:
                continue
            avail = segs[last]["t1"] - segs[e["at"]]["t0"] - 0.35
            need = e["delay"] + e.get("dur", 1.0)
            if need > avail > 0:
                k = avail / need
                e["delay"] = round(e["delay"] * k, 2)
                e["dur"] = round(max(0.25, e.get("dur", 1.0) * k), 2)
    return boards


# 英文配音的词典补丁（2026-10-24）：sherpa-onnx 的 kokoro 英文只查 lexicon-us-en.txt，查不到的词（复数、过去式、X's、阿拉伯数字）
# 会被直接跳过、不读出来。这里把数字写成英文单词，并按词根 + 词尾给查不到的词补读音，写进 _tts/lex-extra.txt 先查。
VOICELESS, SIBILANT = set("ptkfθ"), {"s", "z", "ʃ", "ʒ", "ʧ", "ʤ"}


def _num_words(line):
    import re
    try:
        from num2words import num2words
    except ImportError:
        return line
    return re.sub(r"\d[\d,]*(\.\d+)?", lambda m: num2words(float(m.group().replace(",", "")) if "." in m.group() else int(m.group().replace(",", ""))).replace("-", " "), line)


def _derive(w, lex):
    lw = w.lower()
    if lw in lex:
        return lex[lw]
    def tail(ph, kind):
        last = ph.split()[-1]
        if kind == "s":
            return ph + (" ɪ z" if last in SIBILANT else " s" if last in VOICELESS else " z")
        if kind == "d":
            return ph + (" ɪ d" if last in ("t", "d") else " t" if last in VOICELESS | {"s", "ʃ", "ʧ"} else " d")
        return ph + kind
    for suf, cut, kind in (("'s", 2, "s"), ("ies", 3, "y_s"), ("es", 2, "s"), ("s", 1, "s"), ("ied", 3, "y_d"), ("ed", 2, "d"), ("ed", 1, "d"),
                           ("ing", 3, " ɪ ŋ"), ("ing", 3, "e ɪ ŋ"), ("er", 2, " ə ɹ"), ("ly", 2, " l i")):
        if not lw.endswith(suf):
            continue
        base = lw[:-cut]
        if kind.startswith("y_"):
            base, kind = base + "y", kind[2:]
        if kind == "e ɪ ŋ":
            base, kind = base + "e", " ɪ ŋ"
        if base in lex:
            return tail(lex[base], kind)
    return None


def en_lexicon(lines, d, here):
    """把这一期英文讲稿里查不到的词补进 _tts/lex-extra.txt；返回补不上的词（交付前要换写法）。"""
    import re
    lex = {}
    for ln in open(d + "lexicon-us-en.txt", encoding="utf8"):
        k, _, v = ln.rstrip("\n").partition(" ")
        lex.setdefault(k.lower(), v)
    extra, miss = {}, set()
    for line in lines:
        for w in re.findall(r"[A-Za-z']+", line):
            w = w.strip("'")
            if not w or w.lower() in lex:
                continue
            ph = _derive(w, lex)
            if ph:
                extra[w] = extra[w.lower()] = ph
            else:
                miss.add(w)
    (here / "_tts").mkdir(exist_ok=True)
    f = here / "_tts" / "lex-extra.txt"
    f.write_text("".join(f"{k} {v}\n" for k, v in extra.items()), encoding="utf8")
    return str(f), miss


def main(here, S, B, title, lang, say=None):
    """S: [(中文, English)]; lang 'zh' speaks the Chinese (zm_yunjian sid 49), 'en' the English (am_michael sid 16)."""
    say = say or {}
    bad = missing_chars("".join(e.get("text", "") for b in B for e in b))
    if bad:
        sys.exit(f"the fonts lack: {bad}")
    # 一句话里用“|”切成两段字幕（配音照样一口气读完，按字数分时间）：画板的 at 写 k 是前半句，k + 0.5 是后半句，好让一句话换两张画板
    IDX, n = {}, 0
    for k, (zh, en) in enumerate(S):
        assert zh.count("|") == en.count("|") <= 1, k
        IDX[k] = n
        if "|" in zh:
            IDX[k + 0.5] = n + 1
        n += 1 + zh.count("|")
    for b in B:
        for e in b:
            e["at"] = IDX[e["at"]]
    boards = [{"elements": b} for b in B]
    if "--boards-only" in sys.argv or "--fake" in sys.argv:
        if "--fake" in sys.argv:
            import numpy as np
            import soundfile as sf
            sf.write(here / "配音.wav", np.zeros(24000 * 4 * len(S), np.float32), 24000)
            segs = [{"zh": z, "en": e_, "t0": 4 * i, "t1": 4 * i + 3.8}
                    for i, (z, e_) in enumerate((a.strip(), b.strip()) for zh, en in S for a, b in zip(zh.split("|"), en.split("|")))]
            lesson = wai.to_lesson(title, segs, boards, audio="配音.wav", duration=4 * len(segs))
        else:
            lesson = json.load(open(here / "lesson.json"))
            lesson["boards"] = boards
        lesson["boards"] = fit(lesson["boards"], lesson["segments"])
        lesson.update(pace=0.2, hand=False, subs=True, ink=1.7, pan=0.45)
        json.dump(lesson, open(here / "lesson.json", "w"), ensure_ascii=False, indent=1)
        sys.exit(print(len(boards), "boards"))
    import numpy as np
    import sherpa_onnx as so
    import soundfile as sf
    d = sys.argv[1].rstrip("/") + "/"
    kw = dict(rule_fsts=d + "date-zh.fst," + d + "number-zh.fst," + d + "phone-zh.fst") if lang == "zh" else {}
    lines = []
    for zh, en in S:
        line = (zh if lang == "zh" else en).replace("| ", "").replace("|", "")
        for k, v in say.items():
            line = line.replace(k, v)
        lines.append(_num_words(line) if lang == "en" else line)
    extra = ""
    if lang == "en":
        f, miss = en_lexicon(lines, d, here)
        extra = f + ","
        if miss:
            print("配音词典里没有、也补不上的词（会被跳过）：", sorted(miss))
    tts = so.OfflineTts(so.OfflineTtsConfig(model=so.OfflineTtsModelConfig(kokoro=so.OfflineTtsKokoroModelConfig(
        model=d + "model.int8.onnx", voices=d + "voices.bin", tokens=d + "tokens.txt", data_dir=d + "espeak-ng-data", dict_dir=d + "dict",
        lexicon=extra + d + "lexicon-us-en.txt," + d + "lexicon-zh.txt"), num_threads=4), max_num_sentences=1, **kw))
    sid = 49 if lang == "zh" else 16
    t, parts, segs, sr = 0.3, [], [], 24000
    for (zh, en), line in zip(S, lines):
        cache = here / "_tts" / (hashlib.md5(f"{sid}{line}".encode()).hexdigest()[:16] + ".wav")
        if cache.exists():
            x, sr = sf.read(cache, dtype="float32")
        else:
            a = tts.generate(speakable(line) if lang == "zh" else line, sid=sid, speed=1.22)
            sr = a.sample_rate
            x = np.array(a.samples, dtype=np.float32)
            cache.parent.mkdir(exist_ok=True)
            sf.write(cache, x, sr)
        if not parts:
            parts.append(np.zeros(int(sr * 0.3), np.float32))
        main_, second = (zh, en) if lang == "zh" else (en, zh)   # 英文期：英文字幕在上（主），中文在下
        mp, sp = [q.strip() for q in main_.split("|")], [q.strip() for q in second.split("|")]
        tot, t_ = sum(len(q) for q in mp), t
        for q, r in zip(mp, sp):
            dt = len(x) / sr * len(q) / tot
            segs.append({"zh": q, "en": r, "t0": round(t_, 2), "t1": round(t_ + dt, 2)})
            t_ += dt
        parts += [x, np.zeros(int(sr * 0.12), np.float32)]
        t += len(x) / sr + 0.12
    parts.append(np.zeros(int(sr * 1.0), np.float32))
    t += 1.0
    sf.write(here / "配音.wav", np.concatenate(parts), sr)
    lesson = wai.to_lesson(title, segs, fit(boards, segs), audio="配音.wav", duration=round(t, 2))
    lesson.update(pace=0.2, hand=False, subs=True, ink=1.7, pan=0.45)
    json.dump(lesson, open(here / "lesson.json", "w"), ensure_ascii=False, indent=1)
    print(len(segs), "segments", len(boards), "boards", round(t, 1), "s")
