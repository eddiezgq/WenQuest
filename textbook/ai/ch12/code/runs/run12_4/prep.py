"""实测前的准备：装上 transformers、datasets、soundfile（与第 7、8 章 prep.py 的做法一致：
依次试用户目录、普通安装、--break-system-packages，哪一种成功就用哪一种）。"""
import subprocess
import sys

PKGS = ["transformers", "datasets", "soundfile", "librosa", "numpy>=1.23,<2", "torchcodec<0.5"]
# datasets 解码音频要 torchcodec；新版是按 CUDA 13 编的（libnvrtc.so.13），这台机器是 12.8，
# 所以钉在 0.5 以下（配 torch 2.7）。numpy 要 ≥1.23（transformers 的 np._CopyMode）又不能到 2。


def pip_install(pkgs):
    for extra in (["--user"], [], ["--user", "--break-system-packages"], ["--break-system-packages"]):
        r = subprocess.run([sys.executable, "-m", "pip", "install", "-q", *extra, *pkgs], capture_output=True, text=True)
        if r.returncode == 0:
            return True
    return False


def modern_pillow():
    """transformers 的惰性导入要 PIL.Image.Resampling（Pillow ≥ 9.1）。租来的机器上常常是更老的
    Pillow，于是任何一个模型类都报成"Could not import module 'XxxModel'"，真正的原因被藏在下面
    （2026-11-04 实测 run12_4、run13_5、run13_6 都倒在这里）。

    **查版本不能用 import**：一旦把老的 PIL 导进来，后面再升级也换不掉进程里那一份
    （这个坑踩过两次了）。所以用包的元数据查。"""
    try:
        from importlib.metadata import version
        if tuple(int(x) for x in version("Pillow").split(".")[:2]) >= (9, 1):
            return True
    except Exception:
        pass
    return pip_install(["--upgrade", "Pillow"])


def numpy_ok():
    """transformers 的模型类要 np._CopyMode（numpy ≥ 1.23）。装得动 transformers 不等于能用它——
    真正的报错要等到 import 某个模型类时才冒出来，而且被包装成 "Could not import module 'XxxModel'"。"""
    try:
        import numpy
        return tuple(int(x) for x in numpy.__version__.split(".")[:2]) >= (1, 23)
    except Exception:
        return False


def ensure():
    modern_pillow()
    try:
        import datasets, soundfile, torchcodec, transformers  # noqa: F401
        if numpy_ok():
            return True
    except ImportError:
        pass
    if not pip_install(PKGS):
        raise SystemExit("装不上 transformers / datasets，实测无法进行")
    return True
