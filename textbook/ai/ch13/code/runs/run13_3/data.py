"""实测用的语料：公开的 Tiny Shakespeare（约 110 万字符），从 GitHub 下载；
下不来时退回程序生成的语料（一个有固定语法的小语言，熵已知，训练曲线同样能拟出幂律）。
"""
import hashlib
import urllib.request

URL = ("https://raw.githubusercontent.com/karpathy/char-rnn/master/data/tinyshakespeare/input.txt")


def synthetic(n_char: int = 1_100_000, seed: int = 13) -> str:
    """一个小语言：主语 + 谓语 + 宾语 + 句号，词表固定、语法固定。
    它的熵可以算出来，所以训练到什么程度算“学会了”是知道的。"""
    import random
    r = random.Random(seed)
    S = ["轴", "齿轮", "箱体", "检验员", "机床"]
    V = ["加工", "检验", "装配", "送检", "返工"]
    O = ["到工位", "按图样", "按手册", "两遍", "合格"]
    out = []
    while sum(len(x) for x in out) < n_char:
        out.append(f"{r.choice(S)}{r.choice(V)}{r.choice(O)}。")
    return "".join(out)[:n_char]


def load() -> tuple:
    """返回（文本, 来源说明, 校验和前 8 位）。校验和记进结果，便于日后复算。"""
    try:
        with urllib.request.urlopen(URL, timeout=60) as f:
            text = f.read().decode("utf-8")
        src = "tinyshakespeare"
    except Exception as e:                                   # 机器连不上 GitHub 时退回合成语料
        text = synthetic()
        src = f"synthetic ({type(e).__name__})"
    return text, src, hashlib.sha256(text.encode()).hexdigest()[:8]
