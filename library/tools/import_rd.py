# -*- coding: utf-8 -*-
"""robot_descriptions 接入（第 5 轮 P8 / 第 4 步）：按登记表选出可收的 URDF 机器人，写条目。

    python3 tools/import_rd.py list     # 算出候选，写 vendor/rd_repos.yaml（要取的原仓库及提交）
    python3 tools/fetch_sources.py rd   # 取原仓库
    python3 tools/import_rd.py          # 核对各仓库 LICENSE，写 catalog/B 条目；重复型号写 alt_models 叠加
"""
import re
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from wqlib import ALLOWED_LICENSES, CATALOG, ROOT  # noqa: E402

REG = ROOT / "vendor_src" / "robot_descriptions"
PIN = ROOT / "vendor" / "robot_descriptions.yaml"
REPOS = ROOT / "vendor" / "rd_repos.yaml"
TAG_CAT = [("end_effector", "EEF"), ("drone", "UAV"), ("dual_arm", "ARM"), ("mobile_manipulator", "MAN"), ("humanoid", "HUM"),
           ("quadruped", "LEG"), ("biped", "LEG"), ("wheeled", "MOB"), ("arm", "ARM"), ("educational", "EDU")]
TYPE_ZH = {"ARM": "机械臂", "EEF": "末端执行器", "UAV": "无人机", "MAN": "移动操作机器人", "HUM": "人形机器人", "LEG": "足式机器人",
           "MOB": "移动机器人", "EDU": "教学模型"}


def registry():
    sys.path.insert(0, str(REG))
    from robot_descriptions._descriptions import DESCRIPTIONS, Format
    from robot_descriptions._repositories import REPOSITORIES
    out = []
    for name, d in DESCRIPTIONS.items():
        src = (REG / "robot_descriptions" / (name + ".py")).read_text(encoding="utf-8")
        m = re.search(r'_clone_to_cache\(\s*"([^"]+)"', src)
        key = m.group(1) if m else None
        code = re.sub(r"from \._cache import clone_to_cache as _clone_to_cache", '_clone_to_cache = lambda k, **kw: "$R"', src)
        code = re.sub(r"from \._\w+ import .*", "", code)
        g = {}
        try:
            exec(code, g)  # noqa: S102 —— 登记表模块只拼路径；克隆函数已换成占位
            urdf, xacro = g.get("URDF_PATH"), g.get("XACRO_PATH")
        except Exception:  # noqa: BLE001
            urdf = xacro = None
        r = REPOSITORIES.get(key)
        rel = lambda x: x.replace("$R/", "", 1) if isinstance(x, str) and x.startswith("$R/") else None  # noqa: E731
        out.append({"name": name, "maker": d.maker, "robot": d.robot, "dof": d.dof, "license": d.license_spdx,
                    "tags": sorted(d.tags), "repo": key, "url": r.url if r else None, "commit": r.commit if r else None,
                    "urdf": rel(urdf), "xacro": "xacro" in src.lower(), "xacro_path": rel(xacro),
                    "xacro_args": {k: str(v) for k, v in (g.get("XACRO_ARGS") or {}).items()},
                    "n_repos": src.count("_clone_to_cache("), "has_urdf": Format.URDF in d.formats})
    return out


def candidates():
    pin = yaml.safe_load(PIN.read_text(encoding="utf-8"))
    dup = pin.get("duplicates") or {}
    new, dups = [], []
    for o in registry():
        if not o["has_urdf"] or o["repo"] == "mujoco_menagerie":
            continue
        if not o["urdf"]:                                  # 只有 xacro 的（第 5 轮第 3 批起能展开）：只收单个原仓库的
            if not o["xacro_path"] or (o["n_repos"] != 1 and o["name"] not in dup):   # 多仓库组合的：只作为已有条目的“另有版本”链接
                continue
            o = dict(o, model=o["xacro_path"], engine="xacro")
        else:
            o = dict(o, model=o["urdf"], engine="urdf")
        if o["license"] not in ALLOWED_LICENSES or (o["maker"] or "").startswith("Universal Robots"):
            continue
        (dups if o["name"] in dup else new).append(dict(o, dup_of=dup.get(o["name"])))
    return new, dups


def mesh_refs(urdf_text):
    """URDF 里所有网格文件名（用正则：有的 URDF 带未声明的命名空间前缀，不是严格的 XML）"""
    return sorted(set(re.findall(r"<mesh\b[^>]*?filename\s*=\s*[\"']([^\"']+)[\"']", urdf_text)))


def resolve(ref, urdf_rel, files):
    """URDF 里的网格路径 → 仓库内相对路径（package://包名/… 按目录名匹配；相对路径按 URDF 所在目录）"""
    import posixpath
    if ref.startswith("package://"):
        pkg, _, rest = ref[len("package://"):].partition("/")
        cands = [f for f in files if f.endswith("/" + pkg + "/" + rest) or f == pkg + "/" + rest]
        if not cands:
            cands = [f for f in files if f == rest or f.endswith("/" + rest)]
        return min(cands, key=len) if cands else None
    if ref.startswith("file://"):
        ref = ref[len("file://"):]
    if posixpath.isabs(ref):                      # 绝对路径（xacro 参数里带了仓库目录展开出来的）：按仓库内路径后缀匹配
        cands = [f for f in files if ref.endswith("/" + f)]
        return max(cands, key=len) if cands else None
    d = posixpath.dirname(urdf_rel)
    while True:                                   # 相对路径：先按 URDF 所在目录，不在就逐级往上找（有的按包根目录写）
        p = posixpath.normpath(posixpath.join(d, ref))
        if p in files:
            return p
        if not d:
            break
        d = posixpath.dirname(d)
    tail = posixpath.normpath(ref).lstrip("./")
    cands = [f for f in files if f.endswith("/" + tail)]
    return cands[0] if len(cands) == 1 else None


NO_MESH = ["/*", "!*.stl", "!*.STL", "!*.dae", "!*.DAE", "!*.obj", "!*.OBJ", "!*.ply", "!*.PLY", "!*.glb", "!*.gltf",
           "!*.png", "!*.jpg", "!*.usd", "!*.usda", "!*.usdc"]


def model_text(dest, o):
    """URDF 文本：URDF 直接读，xacro 先展开（带登记表里的参数）"""
    if o["engine"] == "xacro":
        from xacro_util import expand
        return expand(dest, o["model"], mappings=o.get("xacro_args") or None)
    return (dest / o["model"]).read_text(encoding="utf-8", errors="replace")


def write_repo_list():
    """两步取：先只取模型文件（URDF；有 xacro 的取除网格外的全部文件）和 LICENSE，解析出用到的网格，再把稀疏清单扩到这些网格。"""
    import subprocess
    from fetch_sources import SRC, fetch, git
    new, dups = candidates()
    by_repo = {}
    for o in new + [d for d in dups if d["n_repos"] == 1]:     # 多仓库组合的只给链接，不取仓库
        by_repo.setdefault(o["repo"], {"url": o["url"], "commit": o["commit"], "models": []})["models"].append(o)
    repos, failed = {}, []
    for key, r in sorted(by_repo.items()):
        dest = SRC / "rd" / key
        xac = any(o["engine"] == "xacro" for o in r["models"])
        base = (NO_MESH if xac else sorted({o["model"] for o in r["models"]})) + ["/LICEN[CS]E*", "/COPYING*"]
        try:
            fetch(dest, r["url"], r["commit"], sparse=base)
        except subprocess.CalledProcessError as e:
            print("  {}：取不到，跳过（{}）".format(key, (e.stderr or "")[-120:].strip()))
            continue
        files = set(git("ls-tree", "-r", "--name-only", "HEAD", cwd=dest).splitlines())
        need, missing = set(), 0
        for o in r["models"]:
            if not (dest / o["model"]).exists():
                continue
            try:
                text = model_text(dest, o)
            except Exception as ex:  # noqa: BLE001
                failed.append((o["name"], "xacro 展开失败：{}".format(str(ex)[:120])))
                continue
            for ref in mesh_refs(text):
                p = resolve(ref, o["model"], files)
                if p:
                    need.add(p)
                else:
                    missing += 1
        sparse = base + ["/" + p for p in sorted(need)]
        fetch(dest, r["url"], r["commit"], sparse=sparse)
        repos[key] = {"url": r["url"], "commit": r["commit"], "sparse": sparse}
        print("  {}：{} 个模型、{} 个网格{}".format(key, len(r["models"]), len(need), "，{} 个找不到".format(missing) if missing else ""))
    REPOS.write_text("# 由 tools/import_rd.py list 生成：robot_descriptions 登记的各模型原仓库（固定提交、稀疏检出清单）\n"
                     + yaml.safe_dump(repos, sort_keys=False, allow_unicode=True, width=200), encoding="utf-8")
    print("候选：新建 {} 个、并入已有 {} 个；原仓库 {} 个（取到 {} 个）".format(len(new), len(dups), len(by_repo), len(repos)))
    for n, why in failed:
        print("  不收 {}：{}".format(n, why))


LICENSE_PATTERNS = [("Apache-2.0", r"Apache License\s+Version 2\.0"), ("MIT", r"Permission is hereby granted, free of charge"),
                    ("BSD-3-Clause-Clear", r"BSD 3-Clause Clear|NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT"),
                    ("BSD-3-Clause", r"Neither the name of|Redistributions in binary form.*?\n.*?3\."),
                    ("BSD-2-Clause", r"Redistributions in binary form must reproduce")]


def repo_license(path):
    """原仓库根目录 LICENSE 的许可类型（按文本特征识别）；找不到返回 None"""
    for f in sorted(path.glob("LICEN[CS]E*")) + sorted(path.glob("COPYING*")):
        t = f.read_text(encoding="utf-8", errors="replace")
        for spdx, pat in LICENSE_PATTERNS:
            if re.search(pat, t, re.S | re.I):
                if spdx == "BSD-3-Clause" and "Neither the name" not in t:
                    continue
                return spdx
        return "unknown"
    return None


TAG_TYPE = {"end_effector": "END_EFFECTOR", "drone": "DRONE", "dual_arm": "DUAL_ARM", "mobile_manipulator": "MOBILE_MANIPULATOR",
            "humanoid": "HUMANOID", "quadruped": "QUADRUPED", "biped": "BIPED", "wheeled": "MOBILE_BASE", "arm": "ARM",
            "educational": "ARM"}
EDU = ("教学模型", "两三个关节的简单模型，用来讲关节、连杆和运动学的基本概念。",
       [{"course": "机器人技术", "chapter": "运动学入门"}], ["拖动关节看末端轨迹"], ["教学", "算法验证"])


def mtype(o):
    for t in ("end_effector", "drone", "dual_arm", "mobile_manipulator", "humanoid", "quadruped", "biped", "wheeled", "arm", "educational"):
        if t in o["tags"]:
            return t
    return "arm"


def slug(s):
    return re.sub(r"[^A-Z0-9]", "", str(s).upper())


def write_entries():
    from import_menagerie import TYPES
    pin = yaml.safe_load(PIN.read_text(encoding="utf-8"))
    fetched = yaml.safe_load(REPOS.read_text(encoding="utf-8")) if REPOS.exists() else {}
    new, dups = candidates()
    ids = {d.name for d in (CATALOG / "B").iterdir()}
    mine = {}                                              # 以前导入过的：登记名 → 编号（重跑时沿用，不另起编号）
    for d in (CATALOG / "B").iterdir():
        f = d / "entry.yaml"
        if f.exists() and "robot_descriptions" in f.read_text(encoding="utf-8"):
            reg = ((yaml.safe_load(f.read_text(encoding="utf-8")) or {}).get("source") or {}).get("registry") or {}
            if reg.get("name"):
                mine[reg["name"]] = d.name
    made, skipped, merged = [], [], []
    for o in new:
        repo = ROOT / "vendor_src" / "rd" / o["repo"]
        if o["repo"] not in fetched or not (repo / o["model"]).exists():
            skipped.append((o["name"], "原仓库取不到"))
            continue
        try:
            model_text(repo, o)
        except Exception as ex:  # noqa: BLE001
            skipped.append((o["name"], "xacro 展开失败：{}".format(str(ex)[:100])))
            continue
        lic = repo_license(repo)
        if lic is None or lic == "unknown" or (lic != o["license"] and not (lic.startswith("BSD") and o["license"].startswith("BSD"))):
            skipped.append((o["name"], "原仓库 LICENSE 识别为 {}，登记为 {}".format(lic, o["license"])))
            continue
        t = mtype(o)
        if t == "educational":
            cat, rtype, zh_type, principle, courses, labs, uses = ("EDU", "educational") + EDU
        else:
            cat, rtype, zh_type, principle, courses, labs, uses = TYPES[TAG_TYPE[t]]
        eid = mine.get(o["name"])
        if eid is None:
            eid = "B-{}-{}".format(cat, slug(o["robot"]))
            if eid in ids:
                eid = "B-{}-{}".format(cat, slug((o["maker"] or "") + o["robot"]))
            ids.add(eid)
        maker = o["maker"] or ""
        doc = {
            "schema": 1, "id": eid, "kind": "robot",
            "name": {"zh": "{} {}".format(o["robot"], zh_type) if not maker else "{} {} {}".format(maker, o["robot"], zh_type),
                     "en": "{} {}".format(maker, o["robot"]).strip()},
            "category": cat, "tags": [zh_type, rtype] + [x for x in o["tags"] if x != rtype] + ([maker] if maker else []),
            "standards": [], "params": [], "defaults": {},
            "model": {"engine": "{}:{}/{}".format(o["engine"], o["repo"], o["model"]), "formats": ["urdf", "glb"],
                      **({"xacro_args": o["xacro_args"]} if o["engine"] == "xacro" and o.get("xacro_args") else {}),
                      "origin": "URDF 根连杆坐标系；glTF 里每个连杆一个节点，节点名 = URDF 连杆名",
                      "note": "网页模型按 URDF 的可视几何生成并简化网格；关节表取自 URDF"},
            "robot": {"type": rtype, **({"dof": o["dof"]} if o["dof"] else {})},
            "source": {"origin": "robot_descriptions", "repo": o["url"][:-4] if o["url"].endswith(".git") else o["url"],
                       "commit": o["commit"], "path": o["model"], "license": o["license"],
                       "attribution": "{}（{}）；经 robot_descriptions 登记；{}".format(o["robot"], maker or "开源社区", o["license"]),
                       "checked": {"by": "Claude", "on": "2026-09-30",
                                   "note": "robot_descriptions 登记 {}；原仓库 LICENSE 识别为 {}".format(o["license"], lic)},
                       "registry": {"name": o["name"], "commit": pin["commit"]}},
            "teaching": {"principle": principle, "uses": uses, "courses": courses, "labs": labs},
            "factory": {"erp_items": [], "suppliers": []},
        }
        d = CATALOG / "B" / eid
        d.mkdir(parents=True, exist_ok=True)
        (d / "entry.yaml").write_text("# {} · {}（第 5 轮第 4 步：robot_descriptions）\n".format(eid, doc["name"]["zh"])
                                      + yaml.safe_dump(doc, allow_unicode=True, sort_keys=False), encoding="utf-8")
        made.append(eid)
    # 已有型号：在已有条目上记“另有 URDF 版本”（alt.yaml，load 时合并到 alt_models）
    alts = {}
    for o in dups:                                         # 链接不必取到原仓库：按登记的提交指向模型文件
        d = CATALOG / "B" / o["dup_of"]
        if not d.exists():
            continue
        url = (o["url"][:-4] if o["url"].endswith(".git") else o["url"]) + "/blob/{}/{}".format(o["commit"], o["model"])
        alts.setdefault(o["dup_of"], []).append({"format": o["engine"], "url": url, "license": o["license"],
                                                 "via": "robot_descriptions/{}".format(o["name"])})
    for eid, lst in alts.items():
        (CATALOG / "B" / eid / "alt.yaml").write_text(
            "# {} 的其他版本（第 5 轮第 4 步：robot_descriptions 登记的 URDF / xacro）\n".format(eid)
            + yaml.safe_dump({"alt_models": lst}, allow_unicode=True, sort_keys=False), encoding="utf-8")
        merged.append(eid)
    print("新建 {} 个：{}".format(len(made), "、".join(made)))
    print("已有条目加 URDF / xacro 版本 {} 个".format(len(merged)))
    for n, why in skipped:
        print("  不收 {}：{}".format(n, why))
    return made, skipped


if __name__ == "__main__":
    if sys.argv[1:] == ["list"]:
        write_repo_list()
    else:
        write_entries()
