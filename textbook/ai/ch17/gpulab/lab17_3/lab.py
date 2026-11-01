# GPU 实验 17.3 的笔记本（百分号格式，构建时转成 .ipynb）
# %% [markdown]
# # GPU 实验 17.3　多步工具调用的时间都花在哪
# 17.3 节算过一笔账：智能体每走一步，都要把前面所有东西重新过一遍——系统提示、工具定义、
# 之前每一步的工具返回。所以第 n 步要处理的输入词元随 n 线性增长，整个任务的总量随 n² 增长。
#
# 这里在真模型上把它测出来：预填充时延随上下文长度怎么长、前缀复用（KV 缓存）省多少、
# 一个 20 步的任务到底要多久。
# %%
import sys; sys.path.insert(0, "..")
import time

import torch
import wqgpu
env = wqgpu.check(("gpu", "torch"))
wqgpu.sh(f"{sys.executable} -m pip install -q transformers accelerate", timeout=1800)
from transformers import AutoModelForCausalLM, AutoTokenizer
dev = "cuda"
print(torch.cuda.get_device_name(0), torch.__version__)

# %% [markdown]
# ## 1. 模型（任务 1）
# %%
MODEL = "Qwen/Qwen2.5-1.5B"
tok = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.bfloat16).to(dev).eval()
print(f"参数量 {sum(p.numel() for p in model.parameters()) / 1e6:.0f} M")


def timed(fn, warmup=1, runs=3):
    for _ in range(warmup):
        fn()
    torch.cuda.synchronize()
    t0 = time.perf_counter()
    for _ in range(runs):
        fn()
    torch.cuda.synchronize()
    return (time.perf_counter() - t0) / runs


# %% [markdown]
# ## 2. 预填充时延随上下文长度（任务 2）
# 预填充就是"把整段上下文过一遍"。它的算力与长度成正比，长度再大时注意力那一项还会更陡。
# %%
LENS = [512, 1024, 2048, 4096, 8192]
prefill = {}
for L in LENS:
    ids = torch.randint(0, tok.vocab_size, (1, L), device=dev)
    with torch.no_grad():
        prefill[L] = timed(lambda ids=ids: model(ids)) * 1000
    print(f"  {L:5d} 词元：预填充 {prefill[L]:7.1f} ms，每词元 {prefill[L] * 1000 / L:5.1f} μs")
ratio = prefill[LENS[-1]] / prefill[LENS[0]]
print(f"\n最长那档比最短那档慢 {ratio:.1f} 倍，而词元数只差 {LENS[-1] / LENS[0]:.0f} 倍")

# 解码速度：逐词元生成，受显存带宽限制，与上下文长度关系不大
ids = torch.randint(0, tok.vocab_size, (1, 1024), device=dev)
with torch.no_grad():
    t0 = time.perf_counter()
    out = model.generate(ids, max_new_tokens=64, do_sample=False, pad_token_id=tok.eos_token_id)
    torch.cuda.synchronize()
    dt = time.perf_counter() - t0
decode_rate = 64 / dt
print(f"解码速度约 {decode_rate:.0f} 词元/秒")

# %% [markdown]
# ## 3. 一个 20 步的智能体循环（任务 3）
# 每一步：上下文 = 系统提示 + 工具定义 + 之前每一步的（模型输出 + 工具返回），
# 这一步再加上新的一段。两种做法：
#   **每步重算**：把整段上下文重新过一遍（没有前缀复用时就是这样）；
#   **复用前缀**：把上一步算过的键值留着，这一步只算新增的那一段。
# %%
SYS, TOOLS_TOK, PER_STEP, STEPS = 500, 2686, 800, 20


def run_loop(reuse: bool, tools_tokens: int = TOOLS_TOK):
    """返回 (总耗时, 最后一步耗时, 一共处理了多少输入词元)。"""
    prefix = SYS + tools_tokens
    total, last, processed = 0.0, 0.0, 0
    past = None
    ctx = torch.randint(0, tok.vocab_size, (1, prefix), device=dev)
    torch.cuda.synchronize()
    for step in range(1, STEPS + 1):
        new = torch.randint(0, tok.vocab_size, (1, PER_STEP), device=dev)
        t0 = time.perf_counter()
        with torch.no_grad():
            if reuse and past is not None:
                o = model(new, past_key_values=past, use_cache=True)
                past = o.past_key_values
                processed += PER_STEP
            else:
                ctx = torch.cat([ctx, new], 1)
                o = model(ctx, use_cache=reuse)
                past = o.past_key_values if reuse else None
                processed += ctx.shape[1]
        torch.cuda.synchronize()
        dt = time.perf_counter() - t0
        total += dt
        last = dt
    return total, last, processed


no_cache = run_loop(False)
with_cache = run_loop(True)
print(f"每步重算：总 {no_cache[0]:6.2f} s，最后一步 {no_cache[1]:.3f} s，"
      f"一共处理 {no_cache[2]:,} 个输入词元")
print(f"复用前缀：总 {with_cache[0]:6.2f} s，最后一步 {with_cache[1]:.3f} s，"
      f"一共处理 {with_cache[2]:,} 个输入词元")
print(f"\n复用前缀快 {no_cache[0] / with_cache[0]:.1f} 倍；"
      f"处理的词元少 {no_cache[2] / with_cache[2]:.1f} 倍")
print(f"对照 17.3 节的折算：20 步不复用时输入词元总量是 "
      f"{sum(SYS + TOOLS_TOK + PER_STEP * t for t in range(1, STEPS + 1)):,}")

# %% [markdown]
# ## 4. 工具定义加长一倍（任务 4）
# 工具定义是前缀里最稳定的一段：每一步都一模一样。它越长，"复用"与"不复用"的差距越大。
# %%
big = run_loop(True, TOOLS_TOK * 2)
big_nc = run_loop(False, TOOLS_TOK * 2)
print(f"工具定义加倍后：复用前缀 {big[0]:.2f} s（原来 {with_cache[0]:.2f} s，"
      f"多了 {(big[0] / with_cache[0] - 1) * 100:.0f}%）")
print(f"                每步重算 {big_nc[0]:.2f} s（原来 {no_cache[0]:.2f} s，"
      f"多了 {(big_nc[0] / no_cache[0] - 1) * 100:.0f}%）")
print("工具定义是每一步都要重过一遍的那一段——所以它是最该被缓存的")

# %% [markdown]
# ## 回传结果
# %%
wqgpu.submit(prefill_short=prefill[LENS[0]], prefill_long=prefill[LENS[-1]],
             prefill_ratio=ratio, ctx_short=LENS[0], ctx_long=LENS[-1],
             decode_rate=decode_rate,
             step_no_cache=no_cache[0], step_with_cache=with_cache[0],
             cache_speedup=no_cache[0] / with_cache[0], tokens_20_steps=no_cache[2])
