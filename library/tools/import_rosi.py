# -*- coding: utf-8 -*-
"""ROS-Industrial 工业机械臂（第 5 轮第 3 步第 3 批）：xacro 模型 + 厂商官方技术参数；
厂商官方开源模型（第 4 批，vendor/vendor_models.yaml，URDF）；已有条目的厂商参数叠加（vendors/arms 里 key 写条目编号的）。

    python3 tools/import_rosi.py list      # 按 vendor/ros_industrial.yaml 稀疏检出，展开 xacro，算出用到的可视网格，写 vendor/rosi_repos.yaml
    python3 tools/import_rosi.py           # 写条目（catalog/B/…/entry.yaml）；厂商参数（vendors/arms/*.yaml）写成 vendor.yaml 叠加
模型：engine xacro:<仓库键>/<xacro 相对路径>，generators/b_urdf.py 展开后按 URDF 生成；许可按 xacro 所在包的 package.xml。
"""
import re
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from wqlib import CATALOG, ROOT  # noqa: E402
from xacro_util import expand, package_license  # noqa: E402

PIN = ROOT / "vendor" / "ros_industrial.yaml"
VPIN = ROOT / "vendor" / "vendor_models.yaml"
REPOS = ROOT / "vendor" / "rosi_repos.yaml"
ARMS = ROOT / "vendors" / "arms"
RD = ROOT / "vendor_src" / "rd"
BASE_SPARSE = ["/*/urdf/", "/*/package.xml", "/LICEN[CS]E*", "/README*"]
VENDOR_NAMES = {"ABB": {"zh": "ABB", "en": "ABB"}, "FANUC": {"zh": "发那科", "en": "FANUC"},
                "KUKA": {"zh": "库卡", "en": "KUKA"}, "Yaskawa": {"zh": "安川电机", "en": "Yaskawa"},
                "UBTECH": {"zh": "优必选", "en": "UBTECH"}}


def pin():
    return yaml.safe_load(PIN.read_text(encoding="utf-8"))


def xacro_rel(repo_dir, key):
    hits = sorted(Path(repo_dir).glob("*_support/urdf/{}.xacro".format(key)))
    if len(hits) != 1:
        raise FileNotFoundError("{}：找到 {} 个 {}.xacro".format(repo_dir, len(hits), key))
    return hits[0].relative_to(repo_dir).as_posix()


def visual_mesh_refs(urdf_text):
    """URDF 里 <visual> 用到的网格（网页只画可视几何，碰撞网格不取）"""
    out = set()
    for blk in re.findall(r"<visual\b.*?</visual>", urdf_text, re.S):
        out.update(re.findall(r"<mesh\b[^>]*?filename\s*=\s*[\"']([^\"']+)[\"']", blk))
    return sorted(out)


def vpin():
    return yaml.safe_load(VPIN.read_text(encoding="utf-8")) if VPIN.exists() else {"repos": {}, "robots": []}


def write_repo_list():
    from fetch_sources import fetch, git
    from import_rd import resolve
    repos = {}
    for kind, p in (("xacro", pin()), ("urdf", vpin())):
        for key, r in p["repos"].items():
            dest = RD / key
            mine = [o for o in p["robots"] if o["repo"] == key]
            base = BASE_SPARSE if kind == "xacro" else ["/" + o["file"] for o in mine] + ["/LICEN[CS]E*", "/README*"]
            fetch(dest, r["url"], r["commit"], sparse=base)
            files = set(git("ls-tree", "-r", "--name-only", "HEAD", cwd=dest).splitlines())
            need, missing = set(), []
            for o in mine:
                rel = xacro_rel(dest, o["key"]) if kind == "xacro" else o["file"]
                text = expand(dest, rel) if kind == "xacro" else (dest / rel).read_text(encoding="utf-8", errors="replace")
                for ref in visual_mesh_refs(text):
                    hit = resolve(ref, rel, files)
                    (need.add(hit) if hit else missing.append(ref))
            sparse = base + ["/" + x for x in sorted(need)]
            fetch(dest, r["url"], r["commit"], sparse=sparse)
            repos[key] = {"url": r["url"], "commit": r["commit"], "sparse": sparse}
            print("  {}：{} 个可视网格{}".format(key, len(need), "，找不到 {} 个：{}".format(len(missing), missing[:3]) if missing else ""))
    REPOS.write_text("# 由 tools/import_rosi.py list 生成：ROS-Industrial 与厂商官方模型仓库（固定提交、稀疏检出清单）\n"
                     + yaml.safe_dump(repos, sort_keys=False, allow_unicode=True, width=200), encoding="utf-8")


def arms():
    """vendors/arms/*.yaml：厂商官方技术参数（模型键 → 参数）"""
    out = {}
    for f in sorted(ARMS.glob("*.yaml")):
        v = yaml.safe_load(f.read_text(encoding="utf-8"))
        for r in v.get("robots") or []:
            out[r["key"]] = (v, r)
    return out


def datasheet_overlay(v, r, model_name):
    from import_vendor import DATASHEET_LABELS, _src
    ds = {k: x for k, x in (r.get("datasheet") or {}).items() if x not in (None, "")}
    if not ds:
        return None
    srcs = r["src"] if isinstance(r["src"], list) else [r["src"]]
    sheet = {"vendor": v["vendor"]["name"]["en"], "model": r["model"], "values": ds,
             "labels": {k: {"zh": DATASHEET_LABELS[k][0], "en": DATASHEET_LABELS[k][1], "unit": DATASHEET_LABELS[k][2]} for k in ds},
             "src": v["sources"][srcs[0]]["url"]}
    if r.get("note"):
        sheet["note"] = r["note"]
    rng, spd = r.get("joint_range_deg") or [], r.get("joint_speed_deg_s") or []
    if rng or spd:
        n = max(len(rng), len(spd))
        sheet["axes"] = [{"axis": i + 1, **({"range_deg": rng[i]} if i < len(rng) and rng[i] else {}),
                          **({"speed_deg_s": spd[i]} if i < len(spd) and spd[i] is not None else {})} for i in range(n)]
    return {"vendor": {"id": v["vendor"]["id"], "name": v["vendor"]["name"], "site": v["vendor"]["site"], "model": r["model"]},
            "datasheet": sheet,
            "data_sources": [_src(v, k, r.get("page")) for k in srcs],
            "tags": [v["vendor"]["name"]["zh"], v["vendor"]["name"]["en"], r["model"], model_name]}


def spdx(dest, rel):
    """许可：package.xml 的 <license> 换成 SPDX 写法；只写“BSD”的，按仓库根目录 LICENSE 原文定"""
    from import_rd import repo_license
    lic, pkg_xml = package_license(dest, rel)
    root = repo_license(Path(dest))
    norm = {"Apache 2.0": "Apache-2.0", "Apache-2.0": "Apache-2.0", "BSD-3-Clause": "BSD-3-Clause"}.get(lic)
    if norm:
        return norm, pkg_xml, "许可取 {} 的 <license>（{}）".format(pkg_xml, lic)
    if lic == "BSD" and root:
        how = "与仓库 LICENSE 一致" if root.startswith("BSD") else "仓库根目录 LICENSE 为 {}，按仓库 LICENSE".format(root)
        return root, pkg_xml, "{} 写 BSD（未注明条款数）；{}".format(pkg_xml, how)
    return lic, pkg_xml, "许可取 {} 的 <license>".format(pkg_xml)


def write_entries():
    from import_menagerie import TYPES
    p = pin()
    sheets = arms()
    made, merged = [], []
    for o in p["robots"]:
        r = p["repos"][o["repo"]]
        dest = RD / o["repo"]
        rel = xacro_rel(dest, o["key"])
        lic, pkg_xml, lic_note = spdx(dest, rel)
        repo_url = r["url"][:-4] if r["url"].endswith(".git") else r["url"]
        vname = VENDOR_NAMES[r["vendor"]]
        sheet = sheets.get(o["key"])
        ov = datasheet_overlay(sheet[0], sheet[1], o["model"]) if sheet else None
        if o.get("dup_of"):                          # 已有同型号条目：加“另有版本”链接，参数叠加
            d = CATALOG / "B" / o["dup_of"]
            (d / "alt_rosi.yaml").write_text(
                "# {} 的其他版本（第 5 轮第 3 步第 3 批：ROS-Industrial xacro）\n".format(o["dup_of"])
                + yaml.safe_dump({"alt_models": [{"format": "xacro", "url": "{}/blob/{}/{}".format(repo_url, r["commit"], rel),
                                                  "license": lic, "via": "ROS-Industrial/{}".format(o["key"])}]},
                                 allow_unicode=True, sort_keys=False), encoding="utf-8")
            if ov and not (d / "vendor.yaml").exists():
                (d / "vendor.yaml").write_text("# {} 的厂商参数（第 5 轮第 3 步第 3 批）\n".format(o["dup_of"])
                                               + yaml.safe_dump(ov, allow_unicode=True, sort_keys=False), encoding="utf-8")
            merged.append(o["dup_of"])
            continue
        cat, rtype, zh_type, principle, courses, labs, uses = TYPES[o.get("type", "ARM")]
        tags = [zh_type, rtype, "工业机器人", vname["zh"], vname["en"], o["model"]] + (["协作机器人", "cobot"] if o.get("cobot") else [])
        doc = {
            "schema": 1, "id": o["id"], "kind": "robot",
            "name": {"zh": "{} {} {}".format(vname["zh"], o["model"], "协作机械臂" if o.get("cobot") else zh_type),
                     "en": "{} {}".format(vname["en"], o["model"])},
            "category": cat, "tags": list(dict.fromkeys(tags)), "standards": [], "params": [], "defaults": {},
            "model": {"engine": "xacro:{}/{}".format(o["repo"], rel), "formats": ["urdf", "glb"],
                      "origin": "URDF 根连杆（base_link）坐标系；glTF 里每个连杆一个节点，节点名 = URDF 连杆名",
                      "note": "网页模型由 ROS-Industrial 的 xacro 展开成 URDF 后，按可视几何生成并简化网格；关节表取自 URDF"
                              + ("。" + o["model_note"] if o.get("model_note") else "")},
            "robot": {"type": rtype},
            "source": {"origin": "ros_industrial", "repo": repo_url, "commit": r["commit"], "path": rel, "license": lic,
                       "attribution": "{} {}（ROS-Industrial {} 支持包）；{}".format(vname["en"], o["model"], pkg_xml.split("/")[0], lic),
                       "checked": {"by": "Claude", "on": "2026-10-01", "note": lic_note}},
            "teaching": {"principle": principle, "uses": uses, "courses": courses, "labs": labs},
            "factory": {"erp_items": [], "suppliers": [vname["en"]]},
        }
        d = CATALOG / "B" / o["id"]
        d.mkdir(parents=True, exist_ok=True)
        (d / "entry.yaml").write_text("# {} · {}（第 5 轮第 3 步第 3 批：ROS-Industrial）\n".format(o["id"], doc["name"]["zh"])
                                      + yaml.safe_dump(doc, allow_unicode=True, sort_keys=False), encoding="utf-8")
        if ov:
            (d / "vendor.yaml").write_text("# {} 的厂商参数（第 5 轮第 3 步第 3 批）\n".format(o["id"])
                                           + yaml.safe_dump(ov, allow_unicode=True, sort_keys=False), encoding="utf-8")
        made.append(o["id"] + ("" if ov else "（无厂商参数）"))
    # 厂商官方开源模型（URDF）
    from import_rd import repo_license
    vp = vpin()
    for o in vp["robots"]:
        r = vp["repos"][o["repo"]]
        dest = RD / o["repo"]
        root = repo_license(dest)
        if root != r["license"]:
            print("  不收 {}：仓库 LICENSE 识别为 {}，登记为 {}".format(o["id"], root, r["license"]))
            continue
        repo_url = r["url"][:-4] if r["url"].endswith(".git") else r["url"]
        vname = VENDOR_NAMES[r["vendor"]]
        cat, rtype, zh_type, principle, courses, labs, uses = TYPES[o.get("type", "ARM")]
        doc = {
            "schema": 1, "id": o["id"], "kind": "robot",
            "name": {"zh": "{} {} {}".format(vname["zh"], o["model"], zh_type), "en": "{} {}".format(vname["en"], o["model"])},
            "category": cat, "tags": list(dict.fromkeys([zh_type, rtype, vname["zh"], vname["en"], o["model"]])),
            "standards": [], "params": [], "defaults": {},
            "model": {"engine": "urdf:{}/{}".format(o["repo"], o["file"]), "formats": ["urdf", "glb"],
                      "origin": "URDF 根连杆坐标系；glTF 里每个连杆一个节点，节点名 = URDF 连杆名",
                      "note": "厂商官方开源模型；网页模型按 URDF 的可视几何生成并简化网格，关节表取自 URDF"},
            "robot": {"type": rtype},
            "source": {"origin": "vendor", "vendor": vname["en"], "repo": repo_url, "commit": r["commit"], "path": o["file"],
                       "license": r["license"],
                       "attribution": "{} {}（{} 官方开源模型）；{}".format(vname["en"], o["model"], vname["en"], r["license"]),
                       "checked": {"by": "Claude", "on": "2026-10-01", "note": "厂商官方 GitHub 账号发布；仓库 LICENSE 识别为 {}".format(root)}},
            "teaching": {"principle": principle, "uses": uses, "courses": courses, "labs": labs},
            "factory": {"erp_items": [], "suppliers": [vname["en"]]},
        }
        d = CATALOG / "B" / o["id"]
        d.mkdir(parents=True, exist_ok=True)
        (d / "entry.yaml").write_text("# {} · {}（第 5 轮第 3 步第 4 批：厂商官方开源模型）\n".format(o["id"], doc["name"]["zh"])
                                      + yaml.safe_dump(doc, allow_unicode=True, sort_keys=False), encoding="utf-8")
        made.append(o["id"])
    # 已有条目（Menagerie、robot_descriptions、厂商官方模型）的厂商参数：vendors/arms 里 key 写条目编号
    over = []
    for key, (v, r) in sheets.items():
        if not key.startswith("B-"):
            continue
        d = CATALOG / "B" / key
        if not (d / "entry.yaml").exists():
            print("  参数没有对应条目：{}".format(key))
            continue
        ov = datasheet_overlay(v, r, r["model"])
        if ov:
            (d / "vendor.yaml").write_text("# {} 的厂商参数（第 5 轮第 3 步第 4 批）\n".format(key)
                                           + yaml.safe_dump(ov, allow_unicode=True, sort_keys=False), encoding="utf-8")
            over.append(key)
    print("新建 {} 个：{}".format(len(made), "、".join(made)))
    print("已有条目加厂商参数 {} 个：{}".format(len(over), "、".join(over)))
    print("已有条目加 xacro 版本：{}".format("、".join(merged)))


if __name__ == "__main__":
    write_repo_list() if sys.argv[1:] == ["list"] else write_entries()
