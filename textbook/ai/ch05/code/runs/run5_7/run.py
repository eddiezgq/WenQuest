"""编译并运行 gemm.cu，核对结果，把测得的数写进 out.json（第 14 轮附 4.4 节）。"""
import json
import subprocess

subprocess.run(["nvcc", "-O3", "-arch=native", "-o", "gemm", "gemm.cu", "-lcublas"], check=True)
# 先在小矩阵上用 compute-sanitizer 查数据竞争与越界（4.4 节）：CPU 上的模拟（程序 5.9.2）只核对下标，查不出缺同步与越界
for tool in ("racecheck", "memcheck"):
    subprocess.run(["compute-sanitizer", "--tool", tool, "--error-exitcode", "1", "./gemm", "256"], check=True, capture_output=True)
out = json.loads(subprocess.run(["./gemm"], check=True, capture_output=True, text=True).stdout.strip().splitlines()[-1])
assert out["correct"], "结果不对"
json.dump(out, open("out.json", "w"))
print(out)
