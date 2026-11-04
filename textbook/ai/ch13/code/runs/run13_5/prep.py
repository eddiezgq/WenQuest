"""实测前的准备：装上 transformers、peft、datasets（做法与第 7、8、12 章的 prep.py 一致：
依次试用户目录、普通安装、--break-system-packages，哪一种成功就用哪一种）。"""
import subprocess
import sys

PKGS = ["transformers", "peft", "datasets", "accelerate", "jinja2>=3.1.0"]   # apply_chat_template 要 jinja2 ≥ 3.1


def pip_install(pkgs):
    for extra in (["--user"], [], ["--user", "--break-system-packages"], ["--break-system-packages"]):
        r = subprocess.run([sys.executable, "-m", "pip", "install", "-q", *extra, *pkgs],
                           capture_output=True, text=True)
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


def ensure():
    modern_pillow()
    try:
        import jinja2
        import datasets, peft, transformers  # noqa: F401
        if tuple(int(x) for x in jinja2.__version__.split(".")[:2]) >= (3, 1):
            return True
    except Exception:
        pass
    return pip_install(PKGS)


if __name__ == "__main__":
    ok = ensure()
    print("依赖就绪" if ok else "依赖安装失败")
    sys.exit(0 if ok else 1)
