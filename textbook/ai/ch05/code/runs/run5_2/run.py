"""编译并运行 reduce.cu，核对结果，把测得的数写进 out.json（第 14 轮附 4.4 节）。"""
import json
import subprocess

subprocess.run(["nvcc", "-O3", "-arch=native", "-o", "reduce", "reduce.cu"], check=True)
out = json.loads(subprocess.run(["./reduce"], check=True, capture_output=True, text=True).stdout.strip().splitlines()[-1])
assert out["correct"], "结果不对"
json.dump(out, open("out.json", "w"))
print(out)
