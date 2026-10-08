"""实测前的准备：装上 transformers、peft、datasets（做法与第 7、8、12 章的 prep.py 一致：
依次试用户目录、普通安装、--break-system-packages，哪一种成功就用哪一种）。"""
import subprocess
import sys

PKGS = ["transformers", "peft", "datasets", "accelerate"]


def pip_install(pkgs):
    for extra in (["--user"], [], ["--user", "--break-system-packages"], ["--break-system-packages"]):
        r = subprocess.run([sys.executable, "-m", "pip", "install", "-q", *extra, *pkgs],
                           capture_output=True, text=True)
        if r.returncode == 0:
            return True
    return False


def ensure():
    try:
        import datasets, peft, transformers  # noqa: F401
        return True
    except Exception:
        return pip_install(PKGS)


if __name__ == "__main__":
    ok = ensure()
    print("依赖就绪" if ok else "依赖安装失败")
    sys.exit(0 if ok else 1)
