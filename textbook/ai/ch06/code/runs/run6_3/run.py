"""在多 GPU 机器上编译并运行 p2p.cu 与 allreduce.cu，核对结果，把测得的数合并写进 out.json（第 14 轮附 4.4 节）。
NCCL：机器上装了（/usr/include/nccl.h）就用它；没有就从 PyPI 装 nvidia-nccl-cu12，用其中的头文件与库。"""
import glob
import json
import os
import subprocess
import sys


def nccl_flags():
    if os.path.exists("/usr/include/nccl.h"):
        return ["-lnccl"]
    if subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--user", "nvidia-nccl-cu12"]).returncode != 0:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "nvidia-nccl-cu12"], check=True)   # 虚拟环境里不能用 --user
    import site
    base = next(p for p in [os.path.join(d, "nvidia", "nccl") for d in site.getsitepackages() + [site.getusersitepackages()]]
                if os.path.exists(p))
    lib = os.path.join(base, "lib")
    name = os.path.basename(sorted(glob.glob(os.path.join(lib, "libnccl.so*")))[0])
    return ["-I", os.path.join(base, "include"), "-L", lib, f"-l:{name}", "-Xlinker", "-rpath=" + lib]


def run(exe):
    return json.loads(subprocess.run([exe], check=True, capture_output=True, text=True).stdout.strip().splitlines()[-1])


subprocess.run(["nvcc", "-O3", "-arch=native", "-o", "p2p", "p2p.cu"], check=True)
subprocess.run(["nvcc", "-O3", "-arch=native", "-o", "allreduce", "allreduce.cu", *nccl_flags()], check=True)
a, b = run("./p2p"), run("./allreduce")
assert a["correct"] and b["correct"], "结果不对"
assert a["all_peer"], "有的 GPU 之间不能点对点访问，测到的不是点对点带宽"
out = {**a, **b, "correct": True}
json.dump(out, open("out.json", "w"))
print(out)
