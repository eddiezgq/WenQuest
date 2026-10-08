# -*- coding: utf-8 -*-
"""第 19 轮 J-10：帮助在网页里读——每页右上角“帮助”打开对应的帮助文件（digital/help/ 里的副本，原件在仓库 docs/帮助/、docs/演示/）。
总目录是《帮助_数字工厂使用说明》。Markdown 在服务器转成 HTML（文件都是仓库里的，可信）。"""
import os
import re

from fastapi import Depends, HTTPException

HERE = os.path.dirname(os.path.abspath(__file__))
DIGITAL = os.path.dirname(HERE)
HELP_DIR = os.path.join(DIGITAL, "help")
INDEX = os.path.join(DIGITAL, "帮助_数字工厂使用说明.md")
GROUPS = [("开始", ["使用说明", "两周情景", "数字工厂术语表"]),
          ("厂情中枢与七个领域", ["厂情中枢", "客户与服务", "采购与来料", "经营与财务", "设备维护", "人员与排班", "安全环保", "能源与环境"]),
          ("设计与工程软件", ["仿真与分析", "流体分析", "数控编程", "数字孪生", "设计优化", "虚拟PLC", "零件与机器人库"]),
          ("演示", ["学校版演示脚本", "企业版演示脚本", "演示前检查表"]),
          ("企业版与课程", ["数字工厂企业版使用说明", "数字工厂课程接口"])]


def path_of(name):
    if name == "使用说明":
        return INDEX
    if not re.fullmatch(r"[\w一-鿿·\-（）()]+", name or ""):
        return None
    p = os.path.join(HELP_DIR, name + ".md")
    return p if os.path.exists(p) else None


def title_of(md, name):
    m = re.search(r"^#\s+(.+)$", md, re.M)
    return m.group(1).strip() if m else name


def render(md):
    import markdown
    html = markdown.markdown(md, extensions=["tables", "fenced_code", "sane_lists", "toc"], output_format="html5")
    # 帮助之间的相对链接（xxx.md）→ 网页里的帮助页
    return re.sub(r'href="(?:\./)?([^"/#]+)\.md(#[^"]*)?"', lambda m: 'href="/help/{}{}"'.format(m.group(1), m.group(2) or ""), html)


def listing():
    out = []
    for g, names in GROUPS:
        items = []
        for n in names:
            p = path_of(n)
            if p:
                with open(p, encoding="utf-8") as f:
                    items.append({"name": n, "title": title_of(f.read(), n)})
        out.append({"group": g, "items": items})
    return out


def mount(app, user_of):
    @app.get("/api/help")
    def help_index(u=Depends(user_of)):
        return {"groups": listing()}

    @app.get("/api/help/{name}")
    def help_doc(name: str, u=Depends(user_of)):
        p = path_of(name)
        if not p:
            raise HTTPException(404, "没有这份帮助：{}".format(name))
        with open(p, encoding="utf-8") as f:
            md = f.read()
        return {"name": name, "title": title_of(md, name), "html": render(md)}
