# -*- coding: utf-8 -*-
"""xacro → URDF（第 5 轮第 3 步第 3 批：ROS-Industrial 的机械臂模型都是 xacro）。

不装 ROS：用 PyPI 上的 xacro 包展开；$(find 包名) 按仓库里各 package.xml 的 <name> 找到包目录。
"""
import re
from pathlib import Path


def packages(repo):
    """仓库内 包名 → 包目录"""
    out = {}
    for px in Path(repo).rglob("package.xml"):
        m = re.search(r"<name>\s*([^<\s]+)\s*</name>", px.read_text(encoding="utf-8", errors="replace"))
        if m:
            out.setdefault(m.group(1), px.parent.resolve())
    return out


def expand(repo, rel, mappings=None):
    """展开 repo/rel 这个 xacro，返回 URDF 文本"""
    import xacro
    from xacro import substitution_args
    repo = Path(repo).resolve()
    pk = packages(repo)

    def find(pkg):
        if pkg not in pk:
            raise KeyError("仓库里找不到包 {}".format(pkg))
        return str(pk[pkg])
    old = substitution_args._eval_find
    substitution_args._eval_find = find
    try:
        # 传副本：xacro 会把解析出的参数写回字典；参数里的 $R 代表仓库目录（条目里不能存本机路径）
        args = {k: (v.replace("$R", str(repo)) if isinstance(v, str) else v) for k, v in (mappings or {}).items()}
        doc = xacro.process_file(str(Path(repo) / rel), mappings=args)
    finally:
        substitution_args._eval_find = old
    text = doc.toprettyxml(indent="  ")
    # 参数里带仓库目录时，展开结果会有本机绝对路径：换成相对仓库根目录的路径（下载的 URDF 不能带本机路径）
    return text.replace("file://" + str(repo) + "/", "").replace(str(repo) + "/", "")


def package_license(repo, rel):
    """xacro 所在包的 package.xml 里写的许可"""
    p = (Path(repo) / rel).parent
    while p != Path(repo).parent:
        px = p / "package.xml"
        if px.exists():
            m = re.search(r"<license>\s*([^<]+?)\s*</license>", px.read_text(encoding="utf-8", errors="replace"))
            return (m.group(1) if m else None), px.relative_to(repo).as_posix()
        p = p.parent
    return None, None
