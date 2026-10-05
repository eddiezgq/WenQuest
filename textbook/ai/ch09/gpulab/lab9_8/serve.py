"""程序 9.8.2：用开源推理引擎 vLLM 部署一个小的开源模型，测吞吐量与首字延迟（9.8 节）。由 run.py 在单独的虚拟环境里运行。
模型：Qwen2.5-0.5B-Instruct（阿里巴巴通义千问，Apache 2.0 许可，约 5 亿参数），半精度，A10。
（1）首字延迟：一条约 500 个词元的提示词，只生成 1 个词元，取 10 次的中位数（主要是预填充）；
（2）单条序列的解码：同一条提示词生成 256 个词元，(总时间 − 首字延迟) ÷ 255 为每个词元的时间；
（3）吞吐量：256 条不同的提示词一起交给引擎（连续批处理、分页注意力），各生成 256 个词元，每秒生成多少词元。
关掉前缀缓存：否则同一条提示词第二次起不再预填充，首字延迟测不准。结果写进 out.json。"""
import json
import statistics
import time

from vllm import LLM, SamplingParams

BASE = "请详细介绍检测工位上用机器视觉识别零件表面缺陷的流程，包括相机、照明、标定、算法与误检的处理。"


def main():
    llm = LLM(model="Qwen/Qwen2.5-0.5B-Instruct", dtype="float16", gpu_memory_utilization=0.85, seed=0,
              enable_prefix_caching=False)
    prompt = BASE * 10                                      # 约 500 个词元
    n_prompt = len(llm.get_tokenizer().encode(prompt))

    def run(prompts, n):
        sp = SamplingParams(temperature=0.0, max_tokens=n, ignore_eos=True)
        t = time.perf_counter()
        outs = llm.generate(prompts, sp, use_tqdm=False)
        return time.perf_counter() - t, sum(len(o.outputs[0].token_ids) for o in outs)

    run([prompt], 8)                                        # 预热
    ttft = statistics.median(run([prompt], 1)[0] for _ in range(10))
    t256, _ = run([prompt], 256)
    per_tok = (t256 - ttft) / 255
    prompts = [f"第 {i} 号工位：" + BASE for i in range(256)]
    tb, ntok = run(prompts, 256)
    out = {"n_prompt": n_prompt, "ttft_ms": ttft * 1e3, "tpot_ms": per_tok * 1e3, "single_tok_s": 1 / per_tok,
           "batch_tok_s": ntok / tb, "batch_s": tb, "speedup": (ntok / tb) * per_tok}
    json.dump(out, open("out.json", "w"))
    print(out)


if __name__ == "__main__":                                  # vLLM 会启动子进程，入口必须放在这里
    main()
