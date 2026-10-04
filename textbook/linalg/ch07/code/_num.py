"""本章共用：把数写成 LaTeX 的科学记数法。以下划线开头，构建时不单独运行。"""


def sci(x, d=2):
    """3.34e+10 → 3.34\\times10^{10}；d 为小数位数。"""
    m, e = f"{x:.{d}e}".split("e")
    return rf"{m}\times10^{{{int(e)}}}"
