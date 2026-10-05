# GPU 实验 9.8 的笔记本（百分号格式，构建时转成 .ipynb）
# %% [markdown]
# # GPU 实验 9.8　用 vLLM 部署一个开源大模型
# %%
import sys; sys.path.insert(0, "..")
import json
import os
import wqgpu
env = wqgpu.check(("gpu",))
# %% [markdown]
# ## 1. 安装 vLLM（约 5 分钟）
# 装在单独的虚拟环境里，不影响机器上原有的 PyTorch。
# %%
venv = os.path.expanduser("~/wq-vllm")
py = os.path.join(venv, "bin", "python")
if not os.path.exists(py):
    import subprocess
    if subprocess.run([sys.executable, "-m", "venv", venv]).returncode != 0:     # Ubuntu 上可能缺 pythonX.Y-venv
        v = f"python{sys.version_info.major}.{sys.version_info.minor}-venv"
        wqgpu.sh(f"sudo -n apt-get -o DPkg::Lock::Timeout=300 install -y -q {v} && {sys.executable} -m venv --clear {venv}", timeout=900)
    wqgpu.sh(f"{py} -m pip install -q --upgrade pip && {py} -m pip install -q vllm", timeout=1800)
print(wqgpu.sh(f"{py} -c 'import vllm; print(vllm.__version__)'"))     # 打印出版本号说明装好了
# %% [markdown]
# ## 2. 首字延迟、每个词元的时间、吞吐量（任务 1）
# `serve.py` 部署 Qwen2.5-0.5B-Instruct（约 5 亿参数，半精度），测一条约 500 个词元的提示词的首字延迟、单条序列每个词元的时间，
# 以及 256 条请求一起交给引擎时每秒生成的词元数。第一次运行要下载模型（约 1 GB）。
# %%
wqgpu.sh(f"{py} serve.py", timeout=1800)
r = json.load(open("out.json"))
print(f"首字延迟 {r['ttft_ms']:.0f} ms；单条序列每个词元 {r['tpot_ms']:.1f} ms（{r['single_tok_s']:.0f} 词元/秒）")
print(f"256 条一起：{r['batch_tok_s']:.0f} 词元/秒，是单条的 {r['speedup']:.0f} 倍")
# %% [markdown]
# ## 3. 改一改（任务 2）
# 把 `serve.py` 中的请求数改成 16、64，或把生成长度改成 64，吞吐量怎样变化？连续批处理与分页注意力在哪里起作用？
# %%
# 在这里改 serve.py 后重新运行上一格
# %% [markdown]
# ## 4. 回传结果
# %%
wqgpu.submit(ttft_ms=r["ttft_ms"], tpot_ms=r["tpot_ms"], batch_tok_s=r["batch_tok_s"], speedup=r["speedup"])
