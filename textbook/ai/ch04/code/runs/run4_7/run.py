"""编译并运行 transpose.cu，核对转置正确，把带宽写进 out.json（第 14 轮附 4.4 节）。"""
import json
import subprocess

subprocess.run(["nvcc", "-O3", "-arch=native", "-o", "transpose", "transpose.cu"], check=True)
out = json.loads(subprocess.run(["./transpose"], check=True, capture_output=True, text=True).stdout.strip().splitlines()[-1])
assert out["correct"], "转置结果不对"
json.dump(out, open("out.json", "w"))
print(out)
