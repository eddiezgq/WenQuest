"""编译并运行 copy.cu，把传输带宽写进 out.json（第 14 轮附 4.4 节）。"""
import json
import subprocess

subprocess.run(["nvcc", "-O3", "-arch=native", "-o", "copy", "copy.cu"], check=True)
out = json.loads(subprocess.run(["./copy"], check=True, capture_output=True, text=True).stdout.strip().splitlines()[-1])
json.dump(out, open("out.json", "w"))
print(out)
