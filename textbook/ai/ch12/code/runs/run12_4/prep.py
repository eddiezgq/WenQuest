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


def ensure():
    try:
        import datasets, soundfile, transformers  # noqa: F401
        return True
    except ImportError:
        pass
    if not pip_install(PKGS):
        raise SystemExit("装不上 transformers / datasets，实测无法进行")
    return True
