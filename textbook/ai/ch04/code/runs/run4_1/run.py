"""编译并运行 vadd.cu、gray.cu，核对结果，把数值写进 out.json（第 14 轮附 4.4 节）。"""
import json
import subprocess

out = {}
for name in ("vadd", "gray"):
    subprocess.run(["nvcc", "-O3", "-arch=native", "-o", name, f"{name}.cu"], check=True)
    line = subprocess.run([f"./{name}"], check=True, capture_output=True, text=True).stdout.strip().splitlines()[-1]
    out.update(json.loads(line))
assert out["vadd_err"] == 0, "向量加法结果不对"
assert out["gray_diff"] == 0, f"有 {out['gray_diff']} 个像素的灰度与主机上算的不同"
assert out["gray_dark"] == 11277, f"暗斑像素数不对：{out['gray_dark']}"      # 与程序 4.2.2（ex4_2.py）在 CPU 上数出的相同
json.dump(out, open("out.json", "w"))
print(out)
