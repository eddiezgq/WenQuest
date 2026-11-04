"""实测前的准备：装上 transformers、datasets、soundfile（与第 7、8 章 prep.py 的做法一致：
依次试用户目录、普通安装、--break-system-packages，哪一种成功就用哪一种）。"""
import subprocess
import sys

PKGS = ["transformers", "datasets", "soundfile", "librosa"]


def pip_install(pkgs):
    for extra in (["--user"], [], ["--user", "--break-system-packages"], ["--break-system-packages"]):
        r = subprocess.run([sys.executable, "-m", "pip", "install", "-q", *extra, *pkgs], capture_output=True, text=True)
        if r.returncode == 0:
            return True
    return False


def modern_pillow():
    """transformers 的惰性导入要 PIL.Image.Resampling（Pillow ≥ 9.1）。租来的机器上常常是更老的
    Pillow，于是任何一个模型类都报成"Could not import module 'XxxModel'"，真正的原因被藏在下面
    （2026-11-04 实测 run12_4、run13_5、run13_6 都倒在这里）。太老就升一下。"""
    try:
        from PIL import Image
        if hasattr(Image, "Resampling"):
            return True
    except ImportError:
        pass
    return pip_install(["--upgrade", "Pillow"])


def ensure():
    modern_pillow()
    try:
        import datasets, soundfile, transformers  # noqa: F401
        return True
    except ImportError:
        pass
    if not pip_install(PKGS):
        raise SystemExit("装不上 transformers / datasets，实测无法进行")
    return True
