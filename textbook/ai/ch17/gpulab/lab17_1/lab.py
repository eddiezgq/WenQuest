# GPU 实验 17.1 的笔记本（百分号格式，构建时转成 .ipynb）
# %% [markdown]
# # GPU 实验 17.1　pass@1 与 pass@10：温度该调多少
# 17.1 节在一个玩具上算出来：pass@1 与 pass@k 的最优温度不是同一个，k 越大最优温度越高。
# 这里在一个真的小代码模型上把这两条曲线测出来。
#
# 题目**自己写**——公开基准很可能已经进过训练数据（17.1 节给了重叠率的原始数字），
# 用它测出来的分数会虚高。自写的题目少、噪声大，但口径干净。
#
# 还有一件要紧的事：**执行模型生成的代码本身就是安全风险**（Codex 论文第 2.3 节的原话）。
# 本实验按最小的一套来做：单独的子进程、硬超时、不给网络。
# %%
import sys; sys.path.insert(0, "..")
import json
import math
import subprocess
import tempfile
import time
from pathlib import Path

import torch
import wqgpu
env = wqgpu.check(("gpu", "torch"))
wqgpu.sh(f"{sys.executable} -m pip install -q transformers accelerate", timeout=1800)
from transformers import AutoModelForCausalLM, AutoTokenizer
dev = "cuda"
print(torch.cuda.get_device_name(0), torch.__version__)

# %% [markdown]
# ## 1. 模型（任务 1）
# 用一个小的公开权重代码模型。小是故意的：这一节要看的是两条曲线的形状，不是绝对分数，
# 而小模型的 pass@1 不会贴着天花板，曲线反而看得更清楚。
# %%
MODEL = "Qwen/Qwen2.5-Coder-1.5B"
tok = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.bfloat16).to(dev).eval()
print(f"参数量 {sum(p.numel() for p in model.parameters()) / 1e6:.0f} M")

# %% [markdown]
# ## 2. 题目与执行器（任务 2）
# 每道题给一个函数签名与一段说明，再给一组断言当测试。**断言不给模型看**——
# 这一点与 MBPP 的默认口径不同（MBPP 把断言一起给出），所以两者的分数不可比（17.1 节）。
#
# 执行器：把"生成的代码 + 测试"写进临时文件，用 `subprocess` 另起一个进程跑，带硬超时。
# 超时与报错都算不通过，分别计数——这两个数本身就说明了不少问题。
# %%
PROBLEMS = [
    ("def second_largest(xs):\n    \"\"\"返回列表里第二大的**不同**的数；不足两个不同的数时返回 None。\"\"\"\n",
     "assert second_largest([3,1,4,4,1,5])==4\nassert second_largest([2,2])is None\nassert second_largest([])is None\nassert second_largest([-1,-5])==-5"),
    ("def run_length(s):\n    \"\"\"把字符串按游程压缩成 [(字符, 个数), ...]。空串返回空表。\"\"\"\n",
     "assert run_length('aaabbc')==[('a',3),('b',2),('c',1)]\nassert run_length('')==[]\nassert run_length('x')==[('x',1)]"),
    ("def balanced(s):\n    \"\"\"判断只含 ()[]{} 的字符串括号是否配对。\"\"\"\n",
     "assert balanced('([]{})')\nassert not balanced('(]')\nassert balanced('')\nassert not balanced('(')"),
    ("def merge_ranges(rs):\n    \"\"\"把一组闭区间 [(a,b), ...] 合并成不重叠的、按起点排好序的区间表。\"\"\"\n",
     "assert merge_ranges([(1,3),(2,6),(8,10)])==[(1,6),(8,10)]\nassert merge_ranges([])==[]\nassert merge_ranges([(5,5)])==[(5,5)]"),
    ("def digits_sum_base(n, b):\n    \"\"\"返回非负整数 n 在 b 进制下各位数字之和（2 <= b <= 16）。\"\"\"\n",
     "assert digits_sum_base(255,16)==30\nassert digits_sum_base(0,2)==0\nassert digits_sum_base(10,2)==2"),
    ("def rotate(mat):\n    \"\"\"把方阵顺时针转 90 度，返回新的二维列表。\"\"\"\n",
     "assert rotate([[1,2],[3,4]])==[[3,1],[4,2]]\nassert rotate([[1]])==[[1]]"),
    ("def longest_run(xs):\n    \"\"\"返回最长的连续相同元素段的长度；空表返回 0。\"\"\"\n",
     "assert longest_run([1,1,2,2,2,3])==3\nassert longest_run([])==0\nassert longest_run([7])==1"),
    ("def is_palindrome_num(n):\n    \"\"\"判断非负整数的十进制表示是不是回文，不许转成字符串。\"\"\"\n",
     "assert is_palindrome_num(12321)\nassert not is_palindrome_num(123)\nassert is_palindrome_num(0)"),
    ("def chunk(xs, k):\n    \"\"\"把列表切成每段 k 个的若干段，最后一段可以不满；k <= 0 时返回空表。\"\"\"\n",
     "assert chunk([1,2,3,4,5],2)==[[1,2],[3,4],[5]]\nassert chunk([],3)==[]\nassert chunk([1],0)==[]"),
    ("def two_sum(xs, t):\n    \"\"\"返回和为 t 的两个下标 (i, j)，i < j；没有就返回 None。有多组时返回 i 最小的那一组。\"\"\"\n",
     "assert two_sum([2,7,11,15],9)==(0,1)\nassert two_sum([3,3],6)==(0,1)\nassert two_sum([1,2],9)is None"),
    ("def flatten(x):\n    \"\"\"把任意层嵌套的列表拍平成一维列表（只处理 list）。\"\"\"\n",
     "assert flatten([1,[2,[3,[4]]]])==[1,2,3,4]\nassert flatten([])==[]\nassert flatten([[],[1]])==[1]"),
    ("def mode(xs):\n    \"\"\"返回出现次数最多的元素；并列时返回最先出现的那个；空表返回 None。\"\"\"\n",
     "assert mode([1,2,2,3])==2\nassert mode([1,1,2,2])==1\nassert mode([])is None"),
]
print(f"自写 {len(PROBLEMS)} 道题")

TIMEOUT_S = 5


def run_one(code: str, tests: str):
    """在子进程里跑一份候选代码，带硬超时。返回 'pass' / 'fail' / 'timeout' / 'crash'。"""
    with tempfile.TemporaryDirectory() as d:
        f = Path(d) / "cand.py"
        f.write_text(code + "\n" + tests + "\nprint('OK')\n", encoding="utf-8")
        try:
            r = subprocess.run([sys.executable, "-I", str(f)], capture_output=True,
                               timeout=TIMEOUT_S, cwd=d, text=True)
        except subprocess.TimeoutExpired:
            return "timeout"
        if r.returncode != 0:
            return "crash" if "Error" in r.stderr and "Assertion" not in r.stderr else "fail"
        return "pass" if "OK" in r.stdout else "fail"


# %% [markdown]
# ## 3. 扫温度（任务 3）
# 每道题每档温度采 N 个样本。pass@k 用无偏估计量算：
# 一道题 n 个样本里有 c 个通过，这道题的 pass@k 是 1 − C(n−c,k)/C(n,k)。
# %%
N_SAMPLES = 20
TEMPS = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
MAX_NEW = 256


def pass_at_k(n, c, k):
    if n - c < k:
        return 1.0
    p = 1.0
    for i in range(n - c + 1, n + 1):
        p *= 1.0 - k / i
    return 1.0 - p


@torch.no_grad()
def generate(prompt, temp, n):
    ids = tok(prompt, return_tensors="pt").to(dev)
    kw = dict(max_new_tokens=MAX_NEW, pad_token_id=tok.eos_token_id)
    if temp <= 0:
        outs = model.generate(**ids, do_sample=False, num_return_sequences=1, **kw)
        outs = outs.repeat(n, 1)                      # 贪心：n 个样本都一样
    else:
        outs = model.generate(**ids, do_sample=True, temperature=temp, top_p=0.95,
                              num_return_sequences=n, **kw)
    return [tok.decode(o[ids["input_ids"].shape[1]:], skip_special_tokens=True) for o in outs]


def body_only(sig, text):
    """只取到下一个顶格定义为止，免得模型接着往下写别的东西。"""
    lines, keep = text.split("\n"), []
    for ln in lines:
        if ln and not ln[0].isspace() and not ln.startswith(")"):
            break
        keep.append(ln)
    return sig + "\n".join(keep)


rows, counts, t0 = [], {"timeout": 0, "crash": 0}, time.time()
n_gen = 0
for temp in TEMPS:
    p1 = p10 = 0.0
    for sig, tests in PROBLEMS:
        outs = generate(sig, temp, N_SAMPLES)
        n_gen += len(outs)
        c = 0
        for o in outs:
            r = run_one(body_only(sig, o), tests)
            counts[r] = counts.get(r, 0) + 1
            c += int(r == "pass")
        p1 += pass_at_k(N_SAMPLES, c, 1)
        p10 += pass_at_k(N_SAMPLES, c, 10)
    p1, p10 = p1 / len(PROBLEMS) * 100, p10 / len(PROBLEMS) * 100
    rows.append((temp, p1, p10))
    print(f"  T = {temp:.1f}：pass@1 {p1:5.1f}%  pass@10 {p10:5.1f}%")

best1 = max(rows, key=lambda r: r[1])
best10 = max(rows, key=lambda r: r[2])
print(f"\npass@1 最高在 T = {best1[0]}（{best1[1]:.1f}%）；"
      f"pass@10 最高在 T = {best10[0]}（{best10[2]:.1f}%）")
if best10[0] > best1[0]:
    print("两条曲线的最优温度不是同一个——与 17.1 节算出来的方向一致")
else:
    print("这一次两者落在同一档：题目太少，噪声盖过了差别。多跑两遍再看")

# %% [markdown]
# ## 4. 执行的账与估计量的偏差（任务 4）
# %%
sec = time.time() - t0
print(f"一共生成 {n_gen} 个样本，用了 {sec / 60:.1f} 分钟，"
      f"平均每个 {sec / max(n_gen, 1):.2f} 秒")
print(f"超时 {counts.get('timeout', 0)} 个，直接报错 {counts.get('crash', 0)} 个")
print("（超时的多半是写出了死循环——这正是必须带超时跑的理由）")

# 同一批数据，用有偏的写法再算一次 pass@10
temp_hot = best10[0]
p_hat_sum = biased = unbiased = 0.0
for sig, tests in PROBLEMS:
    outs = generate(sig, temp_hot, N_SAMPLES)
    c = sum(int(run_one(body_only(sig, o), tests) == "pass") for o in outs)
    p_hat = c / N_SAMPLES
    biased += 1 - (1 - p_hat) ** 10
    unbiased += pass_at_k(N_SAMPLES, c, 10)
biased, unbiased = biased / len(PROBLEMS) * 100, unbiased / len(PROBLEMS) * 100
print(f"\nT = {temp_hot} 时：无偏估计量 {unbiased:.1f}%，用 1−(1−p̂)^10 算 {biased:.1f}%，"
      f"差 {abs(unbiased - biased):.1f} 个点")

# %% [markdown]
# ## 回传结果
# %%
wqgpu.submit(best_t_pass1=best1[0], best_t_pass10=best10[0],
             pass1_best=best1[1], pass10_best=best10[2],
             pass1_at_hot=rows[-1][1], n_problems=len(PROBLEMS), n_samples=N_SAMPLES,
             timeouts=counts.get("timeout", 0), crashes=counts.get("crash", 0),
             sec_per_sample=sec / max(n_gen, 1))
