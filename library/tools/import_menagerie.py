# -*- coding: utf-8 -*-
"""从 MuJoCo Menagerie 生成 B 部分现成机器人的条目（catalog/B/*/entry.yaml）。

每个模型：类型取 Menagerie 自己的 catalog.py；许可读该模型文件夹的 LICENSE（B.6 名单外的不收）；
名称取 Menagerie 的显示名（中文名 = 显示名 + 类型）。已有条目只更新来源与许可，不覆盖人工写过的教学字段。

    python3 tools/import_menagerie.py --src vendor_src/mujoco_menagerie
"""
import argparse
import datetime as dt
import re
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import wqlib  # noqa: E402

VENDOR = yaml.safe_load(open(wqlib.ROOT / "vendor" / "menagerie.yaml", encoding="utf-8"))
GENERIC = {"hand", "left_hand", "right_hand", "robot", "2f85", "scene"}

TYPES = {  # Menagerie 类型 → 类别、robot.type、中文、教学
    "ARM": ("ARM", "arm", "机械臂", "多个转动关节串联：前几个关节主要决定末端位置，腕部关节决定姿态。",
            [{"course": "机器人技术", "chapter": "串联机械臂正运动学"}, {"course": "机器人技术", "chapter": "逆运动学与轨迹规划"}],
            ["拖动关节看末端轨迹", "正逆运动学虚拟实验"], ["装配", "上下料", "人机协作"]),
    "DUAL_ARM": ("ARM", "dual_arm", "双臂机器人", "两条机械臂协同工作，一条固定、一条操作，或两条一起搬运、装配。",
                 [{"course": "机器人技术", "chapter": "多臂协作"}], ["双臂协同搬运演示"], ["双手操作", "遥操作数据采集"]),
    "END_EFFECTOR": ("EEF", "end_effector", "末端执行器", "装在机械臂末端：夹爪靠手指开合夹持物体，灵巧手用多个关节模仿人手。",
                     [{"course": "机器人技术", "chapter": "末端执行器与抓取"}], ["手指关节拖动", "抓取姿态演示"], ["抓取", "精细操作"]),
    "MOBILE_MANIPULATOR": ("MAN", "mobile_manipulator", "移动操作机器人", "移动底盘加机械臂：既能在场地里走，又能伸手操作。",
                           [{"course": "移动机器人", "chapter": "移动操作"}], ["底盘与机械臂的协同"], ["仓储搬运", "服务机器人"]),
    "MOBILE_BASE": ("MOB", "mobile_base", "移动机器人", "轮式底盘靠两侧车轮转速差转向（差速驱动），在平面上移动。",
                    [{"course": "移动机器人", "chapter": "差速驱动运动学"}], ["差速小车轨迹"], ["巡检", "竞赛"]),
    "QUADRUPED": ("LEG", "quadruped", "四足机器人", "每条腿 3 个关节，四条腿交替支撑与摆动（步态），保持机身平衡前进。",
                  [{"course": "足式机器人", "chapter": "步态与平衡"}], ["单腿关节拖动", "步态动画"], ["巡检", "野外作业"]),
    "BIPED": ("LEG", "biped", "双足机器人", "两条腿交替支撑行走，靠控制质心和落脚点保持动态平衡。",
              [{"course": "足式机器人", "chapter": "双足行走"}], ["腿部关节拖动"], ["双足行走研究"]),
    "HUMANOID": ("HUM", "humanoid", "人形机器人", "躯干、双臂、双腿按人体比例布置，行走时控制质心，手臂负责操作。",
                 [{"course": "人形与学习控制", "chapter": "人形机器人结构"}], ["全身关节拖动", "行走动画"], ["科研", "服务", "制造"]),
    "DRONE": ("UAV", "drone", "无人机", "多个旋翼转速不同产生升力差和反扭矩，从而控制姿态和位置。",
              [{"course": "无人机", "chapter": "多旋翼动力学"}], ["姿态控制演示"], ["航拍", "巡检"]),
    "MISC": ("SEN", "sensor", "传感器", "深度相机用双目或结构光测距，同时输出彩色图像和深度图。",
             [{"course": "机器人技术", "chapter": "机器人视觉与传感器"}], ["深度图与点云演示"], ["机器人视觉", "三维重建"]),
}


def slug(key):
    folder, stem = key.split("/")
    base = folder if stem.lower() in GENERIC or stem.lower().startswith(("scene", "left_", "right_")) else stem
    return re.sub(r"[^A-Z0-9]", "", base.upper())


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=str(wqlib.ROOT / "vendor_src" / "mujoco_menagerie"))
    a = ap.parse_args(argv)
    src = Path(a.src)
    sys.path.insert(0, str(src))
    import os
    cwd = os.getcwd()
    os.chdir(src)                      # catalog.display_name 按相对路径读 README
    import catalog
    made, skipped, ids = 0, [], {}
    today = dt.date.today().isoformat()
    for key, mtype in sorted(catalog.MODEL_MAP.items()):
        folder, stem = key.split("/")
        if mtype.name in VENDOR["skip_types"]:
            skipped.append((key, "不是机器人（{}）".format(mtype.name)))
            continue
        lic_file = src / folder / "LICENSE"
        lic = catalog.detect_license(lic_file) if lic_file.exists() else "NONE"
        if lic not in wqlib.ALLOWED_LICENSES:
            skipped.append((key, "许可 {}".format(lic)))
            continue
        cat, rtype, zh_type, principle, courses, labs, uses = TYPES[mtype.name]
        eid = "B-{}-{}".format(cat, slug(key))
        if eid in ids:                  # 同名（如两代 Stretch）：用文件夹名
            eid = "B-{}-{}".format(cat, re.sub(r"[^A-Z0-9]", "", folder.upper()))
        ids[eid] = key
        xml = "{}/{}.xml".format(folder, stem)
        if not (src / xml).exists():
            skipped.append((key, "找不到 {}".format(xml)))
            continue
        name_en = catalog.display_name(key)
        holder = lic_file.read_text(encoding="utf-8").strip().splitlines()[0][:120]
        d = wqlib.CATALOG / "B" / eid
        d.mkdir(parents=True, exist_ok=True)
        f = d / "entry.yaml"
        old = yaml.safe_load(open(f, encoding="utf-8")) if f.exists() else {}
        doc = {
            "schema": 1, "id": eid, "kind": "robot",
            "name": old.get("name") or {"zh": "{} {}".format(name_en, zh_type), "en": name_en},
            "category": cat, "tags": old.get("tags") or [zh_type, rtype.replace("_", " "), folder.split("_")[0]],
            "standards": [], "params": [], "defaults": {},
            "model": {"engine": "menagerie:" + xml, "formats": ["mjcf", "glb"],
                      "origin": "MJCF 的世界坐标系（Z 向上）；glTF 里每个连杆一个节点，节点名 = MJCF 的 body 名",
                      "note": "网页模型按 MJCF 的可视几何生成并简化网格；关节表由构建时从 MJCF 提取"},
            "robot": {"type": rtype},
            "source": {"origin": "menagerie", "repo": VENDOR["repo"], "commit": VENDOR["commit"], "path": folder + "/",
                       "license": lic,
                       "attribution": "MuJoCo Menagerie（Google DeepMind）· {}；{}；{}".format(folder, lic, holder),
                       "checked": {"by": "Claude", "on": today, "note": "按该模型文件夹的 LICENSE 自动识别（Menagerie catalog.detect_license）"}},
            "teaching": old.get("teaching") or {"principle": principle, "uses": uses, "courses": courses, "labs": labs},
            "factory": old.get("factory") or {"erp_items": [], "suppliers": []},
        }
        with open(f, "w", encoding="utf-8") as fh:
            fh.write("# {} · {}（第一期，现成模型：MuJoCo Menagerie）\n".format(eid, doc["name"]["zh"]))
            yaml.safe_dump(doc, fh, allow_unicode=True, sort_keys=False, width=120)
        made += 1
    os.chdir(cwd)
    print("写入 {} 个机器人条目；不收 {} 个：".format(made, len(skipped)))
    for k, why in skipped:
        print("  {}：{}".format(k, why))


if __name__ == "__main__":
    main()
