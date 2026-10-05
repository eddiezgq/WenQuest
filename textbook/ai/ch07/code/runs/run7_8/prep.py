"""实测前准备环境（云主机上以普通用户、非交互方式运行；第 14 轮附 4.4 节）。
- pip_install：依次试装到用户目录、直接装（虚拟环境里）、加 --break-system-packages（Ubuntu 24.04 的系统 Python）；
- ninja_on_path：torch.utils.cpp_extension 用 ninja 编译，要它在 PATH 上（pip 装的 ninja 在非交互的 ssh 里常不在 PATH 上）；
- python_headers：编译扩展（load_inline）与 Triton 的启动代码都要 Python.h，没有就用 sudo -n 装 pythonX.Y-dev。"""
import importlib
import os
import site
import subprocess
import sys
import sysconfig


def pip_install(*pkgs):
    for extra in (["--user"], [], ["--user", "--break-system-packages"]):
        if subprocess.run([sys.executable, "-m", "pip", "install", "-q", *extra, *pkgs]).returncode == 0:
            user = site.getusersitepackages()
            if user not in sys.path:
                sys.path.append(user)
            importlib.invalidate_caches()
            return
    raise RuntimeError("pip 装不上：" + " ".join(pkgs))


def ninja_on_path():
    try:
        import ninja
    except ImportError:
        pip_install("ninja")
        import ninja
    os.environ["PATH"] = ninja.BIN_DIR + os.pathsep + os.environ.get("PATH", "")


def python_headers():
    h = os.path.join(sysconfig.get_paths()["include"], "Python.h")
    if not os.path.exists(h):
        v = f"python{sys.version_info.major}.{sys.version_info.minor}-dev"
        subprocess.run(["sudo", "-n", "apt-get", "update", "-q"])
        subprocess.run(["sudo", "-n", "apt-get", "install", "-y", "-q", v])
    if not os.path.exists(h):
        raise RuntimeError("缺少 Python.h：请先安装 python3-dev")
