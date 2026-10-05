"""编译并运行 dnn.cu，核对结果，把测得的数写进 out.json（第 14 轮附 4.4 节）。
cuDNN：机器上装了（/usr/include 下有 cudnn.h）就用它；没有就从 PyPI 装 nvidia-cudnn-cu12，用其中的头文件与库。"""
import glob
import json
import os
import subprocess
import sys


def cudnn_flags():
    if glob.glob("/usr/include/cudnn.h") + glob.glob("/usr/include/*/cudnn.h"):
        return ["-lcudnn"], {}
    for extra in (["--user"], [], ["--user", "--break-system-packages"]):     # 虚拟环境里不能用 --user；Ubuntu 24.04 的系统 Python 要加后者
        if subprocess.run([sys.executable, "-m", "pip", "install", "-q", *extra, "nvidia-cudnn-cu12"]).returncode == 0:
            break
    else:
        raise RuntimeError("装不上 nvidia-cudnn-cu12")
    import site
    base = next(p for p in [os.path.join(d, "nvidia", "cudnn") for d in site.getsitepackages() + [site.getusersitepackages()]]
                if os.path.exists(p))
    lib = os.path.join(base, "lib")
    name = os.path.basename(sorted(glob.glob(os.path.join(lib, "libcudnn.so*")))[0])
    # cuDNN 9 运行时还要按需加载同一文件夹里的子库（libcudnn_cnn 等），所以运行时也把这个文件夹加进 LD_LIBRARY_PATH
    return (["-I", os.path.join(base, "include"), "-L", lib, f"-l:{name}", "-Xlinker", "-rpath=" + lib],
            {"LD_LIBRARY_PATH": lib + ":" + os.environ.get("LD_LIBRARY_PATH", "")})


flags, env = cudnn_flags()
subprocess.run(["nvcc", "-O3", "-arch=native", "-o", "dnn", "dnn.cu", *flags], check=True)
out = json.loads(subprocess.run(["./dnn"], check=True, capture_output=True, text=True, env={**os.environ, **env}).stdout.strip().splitlines()[-1])
assert out["correct"], f"结果不对：{out}"
json.dump(out, open("out.json", "w"), ensure_ascii=False)
print(out)
