"""三维讲解片的旁白（第 90 轮）：念画面上的字（标题 + 底部字幕），旁白比这一段长就把这一段放慢拉长。

- 念什么：每一段的标题和同一时段的底部字幕，按固定的替换表改成口语读法（r/min 念“转每分”、≤ 念“不超过”……），
  数一字不差，不用 AI。
- 拉长：先配音、量出每句多长；某一段的旁白（加前后留白）比这一段长，就把这一段里所有的时刻按比例拉开，
  后面的整体顺延——镜头、转角、透视、字幕、关键画面一起动，所以慢放还是慢放、关键画面还停在原来那一刻。
  只会拉长不会缩短，改片后再配一遍也不会越拉越长。
- 混音：每句放在它那一段开头稍后一点，混成一条单声道，ffmpeg 编成 audio.m4a（渲染器合成时自动配上）。
"""
import copy
import io
import math
import re
import subprocess
import tempfile
import wave
from pathlib import Path

import numpy as np

LEAD, TAIL = 0.35, 0.45                 # 旁白在一段开头后 0.35 秒开始，读完再留 0.45 秒才进下一段
SPEED = 1.1
VOICES = {"zh": "zf_xiaobei", "en": "af_heart"}         # 同讲课视频的默认声音（lectures.DEFAULT_VOICES）
CIRCLED = "①②③④⑤⑥⑦⑧⑨"
ZH_NUM = "一二三四五六七八九"
EN_NUM = ("one", "two", "three", "four", "five", "six", "seven", "eight", "nine")

# 口语读法：先长后短（m/s² 要在 m/s 前面）
ZH_RULES = [
    (r"⚠\s*", ""), (r"(?<=\d),(?=\d{3})", ""), (r"所需\s*/\s*可用加速度", "所需加速度和可用加速度之比"),
    (r"(?<=\d)-(?=\d)", "杠"),                                     # 模型 9-1、实验 15-1
    (r"[−-](?=\d)", "负"), (r"\+(?=\d)", "正"), (r"±\s*", "正负"), (r"≈\s*", "约"), (r"\s*→\s*", "到"), (r"ε", "伊普西龙"),
    (r"r/min", "转每分"), (r"mm/s", "毫米每秒"), (r"m/s²", "米每二次方秒"), (r"m/s", "米每秒"), (r"N·m", "牛米"),
    (r"(?<=\d)\s*mm\b", "毫米"), (r"(?<=\d)\s*ms\b", "毫秒"), (r"(?<=\d)\s*kg\b", "千克"), (r"(?<=\d)\s*Hz\b", "赫兹"),
    (r"(?<=\d)\s*min\b", "分钟"), (r"(?<=\d)\s*s\b", "秒"), (r"(?<=\d)\s*N\b", "牛"), (r"(?<=\d)\s*°", "度"), (r"°", "度"),
    (r"(负|正)?(\d+(?:\.\d+)?)\s*%", r"\1百分之\2"), (r"\s*/\s*cm\b", "每厘米"), (r"(?<=\d)\s*cm\b", "厘米"),
    (r"(?<=[\d度])\s*[–~]\s*", "到"), (r"≤", "不超过"), (r"≥", "不小于"), (r"×", "乘"),
    (r"\s*·\s*", "，"), (r"\s*/\s*", "和"), (r"…", ""),
]
EN_RULES = [
    (r"⚠\s*", ""), (r"(?<=\d),(?=\d{3})", ""), (r"required\s*/\s*available acceleration", "the ratio of required to available acceleration"),
    (r"(?<=\d)-(?=\d)", " dash "),
    (r"[−-](?=\d)", "minus "), (r"\+(?=\d)", "plus "), (r"±\s*", "plus or minus "), (r"≈\s*", "about "), (r"\s*→\s*", " to "),
    (r"ε", "epsilon"), (r"r/min", "R P M"), (r"mm/s", "millimetres per second"), (r"m/s²", "metres per second squared"),
    (r"m/s", "metres per second"), (r"N·m", "newton metres"), (r"(?<=\d)\s*mm\b", " millimetres"), (r"(?<=\d)\s*ms\b", " milliseconds"),
    (r"(?<=\d)\s*kg\b", " kilograms"), (r"(?<=\d)\s*Hz\b", " hertz"), (r"(?<=\d)\s*min\b", " minutes"), (r"(?<=\d)\s*s\b", " seconds"),
    (r"(?<=\d)\s*N\b", " newtons"), (r"(?<=\d)\s*°", " degrees"), (r"°", " degrees"), (r"(\d)\s*%", r"\1 percent"),
    (r"\s*/\s*cm\b", " per centimetre"), (r"(?<=\d)\s*cm\b", " centimetres"), (r"(?<=[\ds])\s*[–~]\s*(?=[\d+−-]|minus|plus)", " to "),
    (r"≤", "at most"), (r"≥", "at least"), (r"×", " by "), (r"\s*·\s*", ", "), (r"\s*/\s*", " and "),
    (r"…", ""),
]


DIG = "零一二三四五六七八九"


def _int_zh(n: int) -> str:
    """整数的中文读法：941 → 九百四十一，6000 → 六千，10 → 十，105 → 一百零五"""
    if n == 0:
        return "零"
    if n >= 10 ** 8:
        r = n % 10 ** 8
        return _int_zh(n // 10 ** 8) + "亿" + (("零" if r < 10 ** 7 else "") + ("一" if 10 <= r < 20 else "") + _int_zh(r) if r else "")
    if n >= 10 ** 4:
        r = n % 10 ** 4
        return ("两" if n // 10 ** 4 == 2 else _int_zh(n // 10 ** 4)) + "万" + (("零" if r < 1000 else "") + ("一" if 10 <= r < 20 else "") + _int_zh(r) if r else "")
    out, zero = "", False
    for unit, k in (("千", 1000), ("百", 100), ("十", 10), ("", 1)):
        d = n // k % 10
        if d:
            if zero and out:
                out += "零"
            out += ("" if (d == 1 and unit == "十" and not out) else "两" if (d == 2 and unit in ("千", "百") and not out) else DIG[d]) + unit
            zero = False
        elif out:
            zero = True
    return out


def num_zh(m: re.Match) -> str:
    """数字 → 中文读法（小数点后逐位念：0.282 → 零点二八二），避免语音模型把小数读成“二百八十二”"""
    s = m.group(0)
    a, _, b = s.partition(".")
    return _int_zh(int(a)) + ("点" + "".join(DIG[int(c)] for c in b) if b else "")


def spoken(text: str, lang: str = "zh") -> str:
    """画面上的字 → 念的稿（数不动，只改读法）"""
    s = " ".join(str(text).split())
    m = re.match(f"^([{CIRCLED}])\\s*", s)
    head = ""
    if m:
        k = CIRCLED.index(m.group(1))
        head = f"第{ZH_NUM[k]}段，" if lang == "zh" else f"Part {EN_NUM[k]}: "
        s = s[m.end():]
    for a, b in (ZH_RULES if lang == "zh" else EN_RULES):
        s = re.sub(a, b, s)
    if lang == "zh":
        # 线迹代号（401、406、602……）逐位念，别的数按数念
        s = re.sub(r"(?<=线迹 )(\d{3})|(\d{3})(?= ?线迹)", lambda m: "".join(DIG[int(c)] for c in m.group(0)), s)
        s = re.sub(r"\d+(?:\.\d+)?", num_zh, s)
    s = re.sub(r"\s{2,}", " ", s).strip(" ，,")
    return head + s


def lang_of(spec: dict) -> str:
    """旁白用哪种话：跟场景的文字语言（中英两行的念中文）"""
    return "en" if spec.get("lang") == "en" else "zh"


def lines(spec: dict, lang: str) -> list[dict]:
    """每一段要念的：标题（没有 where 的字）和同一时段开始的底部字幕，按时间排。
    返回 [{t0, t1, text, src}]；src 是画面上的原字（测试用：数要一字不差）"""
    labs = [L for L in spec.get("labels") or [] if isinstance(L, dict) and isinstance(L.get("t"), list)]
    key = "en" if lang == "en" else "zh"
    out = []
    for L in labs:
        if L.get("where", "title") != "title":
            continue
        t0, t1 = float(L["t"][0]), float(L["t"][1])
        cap = [B for B in labs if B.get("where") == "bottom" and abs(float(B["t"][0]) - t0) < 0.05]
        src = [str(L.get(key) or "")] + [str(B.get(key) or "") for B in cap[:1]]
        src = [x for x in src if x.strip()]
        if not src:
            continue
        sep = "。" if lang == "zh" else ". "
        out.append({"t0": t0, "t1": t1, "src": src, "text": sep.join(spoken(x, lang) for x in src) + ("。" if lang == "zh" else ".")})
    out.sort(key=lambda x: x["t0"])
    # 同一时刻开始的几条只念第一条；和前一条重叠的往后挪不了，就跳过（场景里本来不会这样）
    keep, end, said = [], -1.0, set()
    for x in out:
        if x["t0"] < end - 1e-6 or x["text"] in said:          # 快放停下以后接着快放：同一句不再念
            continue
        said.add(x["text"])
        keep.append(x)
        end = x["t1"]
    return keep


def warp_map(segs: list[tuple[float, float, float]]):
    """segs：[(t0, t1, 要的长度)]，按时间排、不重叠。返回把原时刻映到新时刻的函数（只拉长不缩短）"""
    pts = []
    shift = 0.0
    for t0, t1, need in segs:
        L = t1 - t0
        if need <= L + 1e-6 or L <= 0:
            continue
        pts.append((t0, t1, need / L, shift))
        shift += need - L

    def f(t: float) -> float:
        s = 0.0
        for t0, t1, k, sh in pts:
            if t <= t0:
                return round(t + s, 4)
            if t <= t1:
                return round(t0 + sh + (t - t0) * k, 4)
            s = sh + (t1 - t0) * k - (t1 - t0)
        return round(t + s, 4)
    return f, shift


def fit(spec: dict, items: list[dict]) -> dict:
    """items：lines() 的结果加上每句的长度 dur（秒）。返回拉长后的新场景（原场景不动），并写上 voice 段（念的稿、开始时刻、长度）"""
    segs = [(x["t0"], x["t1"], LEAD + x["dur"] + TAIL) for x in items]
    f, extra = warp_map(segs)
    s = copy.deepcopy(spec)
    s["duration"] = round(f(float(spec["duration"])), 2)
    for mo in s.get("motion") or []:
        if isinstance(mo, dict) and isinstance(mo.get("angle"), list):
            mo["angle"] = [[f(float(k[0])), k[1]] for k in mo["angle"]]
        for k in ("path", "keys"):
            if isinstance(mo, dict) and isinstance(mo.get(k), list):
                mo[k] = [dict(x, t=f(float(x["t"]))) if isinstance(x, dict) and "t" in x else x for x in mo[k]]
    for c in s.get("camera") or []:
        if isinstance(c, dict) and "t" in c:
            c["t"] = f(float(c["t"]))
    for grp in ("effects", "labels"):
        for e in s.get(grp) or []:
            if isinstance(e, dict) and isinstance(e.get("t"), list) and len(e["t"]) == 2:
                e["t"] = [f(float(e["t"][0])), f(float(e["t"][1]))]
    if isinstance(s.get("stills"), list):
        s["stills"] = [round(f(float(x)), 4) for x in s["stills"]]
    # 第 99 轮统一的 voice 段：t 开口时刻、dur 长度、seg 这一段开头、say 实际念的稿；
    # 解说词（AI 写的，kind=script）保留原来的 zh、en（下次再配照念）；念标题字幕的标 src: labels（下次重新从字幕取）
    out = []
    for x in items:
        v = {"t": round(f(x["t0"]) + LEAD, 2), "dur": round(x["dur"], 2), "seg": round(f(x["t0"]), 4), "say": x["text"]}
        if x.get("kind") == "script":
            v.update({k: x[k] for k in ("zh", "en") if x.get(k)})
        else:
            v["src"] = "labels"
        out.append(v)
    s["voice"] = out
    return s


def _pcm(wav: bytes) -> tuple[np.ndarray, int]:
    with wave.open(io.BytesIO(wav)) as w:
        sr, n, ch, sw = w.getframerate(), w.getnframes(), w.getnchannels(), w.getsampwidth()
        raw = w.readframes(n)
    if sw != 2:
        raise ValueError("only 16-bit WAV")
    a = np.frombuffer(raw, "<i2").astype(np.float32) / 32768
    if ch > 1:
        a = a.reshape(-1, ch).mean(axis=1)
    return a, sr


def mix(clips: list[tuple[float, bytes]], total: float) -> bytes:
    """[(开始秒, WAV)] → 整段 audio.m4a（AAC，单声道）"""
    sr = 24000
    pcs = []
    for t, wb in clips:
        a, r = _pcm(wb)
        if r != sr:                                   # 采样率不同就线性插值到 24 kHz（语音服务本来就是 24 kHz）
            x = np.arange(int(len(a) * sr / r)) * r / sr
            a = np.interp(x, np.arange(len(a)), a).astype(np.float32)
        pcs.append((t, a))
    n = int(math.ceil(total * sr)) + 1
    buf = np.zeros(n, np.float32)
    for t, a in pcs:
        i = int(t * sr)
        j = min(n, i + len(a))
        if i < n:
            buf[i:j] += a[: j - i]
    peak = float(np.max(np.abs(buf))) or 1.0
    buf = np.clip(buf / max(1.0, peak / 0.95), -1, 1)
    with tempfile.TemporaryDirectory() as d:
        wpath, mpath = Path(d) / "a.wav", Path(d) / "a.m4a"
        with wave.open(str(wpath), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(sr)
            w.writeframes((buf * 32767).astype("<i2").tobytes())
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(wpath), "-c:a", "aac", "-b:a", "96k", str(mpath)], check=True)
        return mpath.read_bytes()
