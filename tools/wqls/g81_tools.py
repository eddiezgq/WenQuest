"""G8.1 装配：每颗螺钉的工具通道——螺丝刀 / 内六角扳手沿螺钉轴线从螺钉头往外伸 L，查它和整机其他零件、机壳的最近距离。

    python3 tools/wqls/g81_tools.py <整机目录（含 *.stl、frames.json）> <机壳 part_upper.stl> <机壳 part_lower.stl> <输出 json>

运动件上的螺钉按一转里每 10° 查一次，取通道最宽的那个转角（拧螺钉时可以先转手轮把它转到这个位置）。
工具：直的螺丝刀或内六角扳手，杆半径 r（螺丝刀刀杆按螺钉头径的一半、至少 2.5；内六角扳手按对边 / 2 + 0.3），伸出长度 L = 120。
合格：通道上离别的东西 ≥ 0.5 mm；不合格的写出挡住的零件。经孔、窗口伸进去的也算（直线能过就行）。
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np
import trimesh

# 螺钉：名字 → (所在零件（运动跟它）, 螺钉头支承面中心 (x, y, z)（φ = 0 位置）, 工具往外伸的方向, 工具半径, 说明)
# 坐标同 cad/mech.py；zb = 针杆下端（φ = 0），zB = 针杆连接销（φ = 0）
ZB0, ZB_LINK = 42.5 + 0.0, 160.5
ZH = -21.5                                          # 旋梭轴心高（spec.ZH）


def screws(zb, zB, C0, oil):
    out = {
        "紧针螺钉 SMP 9/64-40": ("needle_clamp", (7.6, 0, zb + 2.5), (1, 0, 0), 2.5, "换针时拧"),
        "针杆连接块紧定 SMS 11/64-40（上）": ("nb_link", (0, -7.0, zB + 4), (0, -1, 0), 1.3, "调针杆高度时拧"),
        "针杆连接块紧定 SMS 11/64-40（下）": ("nb_link", (0, -7.0, zB - 4), (0, -1, 0), 1.3, "调针杆高度时拧"),
        "导轨螺钉 SMP 9/64-40（上）": ("slide_rail", (24.4, 0, 148), (-1, 0, 0), 2.5, "装导轨"),
        "导轨螺钉 SMP 9/64-40（下）": ("slide_rail", (24.4, 0, 125), (-1, 0, 0), 2.5, "装导轨"),
        "分油块 M4（前）": ("oil_block", (175, -6, oil["BLOCK"]["z"][1] - 4.5 + 4), (0, 0, 1), 1.8, "顶盖拆下后拧"),
        "油毡盒 SMP 9/64-40": ("oil_box", (12, 19, oil["HEAD_TOP"] + 2.1), (0, 0, 1), 2.5, "机头顶外面"),
        # 旋梭尾部轴套 Ø14（x 18.5…22.5）上的紧定螺钉，径向；随旋梭转，按转角扫一圈就把各个径向方向都查到了
        "旋梭紧定螺钉（内六角）": ("hook", (20.5, 0, ZH - 7.0), (0, 0, -1), 1.3, "换旋梭、调梭尖时拧（梭芯套先取出）"),
        "旋梭紧定螺钉（一字）": ("hook", (20.5, 0, ZH - 7.0), (0, 0, -1), 2.5, "同上，用螺丝刀"),
    }
    return out


def load(d: Path, k: str):
    p = d / f"{k}.stl"
    return trimesh.load(p) if p.exists() else None


def M44(m):
    return np.array(m, float).reshape(4, 4)


def main():
    d, hu, hl, out = Path(sys.argv[1]), sys.argv[2], sys.argv[3], Path(sys.argv[4])
    F = json.loads((d / "frames.json").read_text())
    fr = F["frames"] if isinstance(F, dict) else F
    sys.path.insert(0, str(Path(__file__).resolve().parent / "cad"))
    import oil_geo as OG  # noqa: E402
    oil = dict(BLOCK=OG.BLOCK, HEAD_TOP=OG.HEAD_TOP)
    names = sorted(p.stem for p in d.glob("*.stl") if p.stem not in ("bed", "head"))
    meshes = {k: load(d, k) for k in names}
    meshes["casting_upper"], meshes["casting_lower"] = trimesh.load(hu), trimesh.load(hl)
    S = screws(ZB0, ZB_LINK, None, oil)
    if os.environ.get("WQ_ONLY_SCREW"):
        S = {k: v for k, v in S.items() if os.environ["WQ_ONLY_SCREW"] in k}
    res = {}
    for nm, (owner, p0, u, r, why) in S.items():
        u = np.array(u, float)
        best = None
        for f in fr[::5]:                                   # 每 10°
            M = f["M"]
            T = M44(M[owner]) if owner in M and M[owner] else np.eye(4)
            p = T[:3, :3] @ np.array(p0, float) + T[:3, 3]
            uu = T[:3, :3] @ u
            pts = p + np.outer(np.linspace(0.5, 120, 240), uu)
            worst, who = 1e9, ""
            for k, m in meshes.items():
                if m is None or k in (owner, *SELF.get(nm, ())) or k.startswith(owner):
                    continue
                Tk = M44(M[k]) if k in M and M[k] else np.eye(4)
                q = (np.linalg.inv(Tk) @ np.c_[pts, np.ones(len(pts))].T).T[:, :3]
                bb = m.bounds
                if (q.min(0) > bb[1] + r + 2).any() or (q.max(0) < bb[0] - r - 2).any():
                    continue
                dist = trimesh.proximity.ProximityQuery(m).signed_distance(q)   # 正 = 在里面
                gap = float((-dist).min()) - r
                if gap < worst:
                    worst, who = gap, k
            if best is None or worst > best[0]:
                best = (worst, f["phi"], who)
            if best[0] > 5:
                break
        res[nm] = dict(gap_mm=round(best[0], 2), phi=best[1], nearest=best[2], ok=best[0] >= 0.5, tool_r=r, why=why)
        print(nm, res[nm])
    out.write_text(json.dumps(res, ensure_ascii=False, indent=1))


# 螺钉自己（工具从螺钉头上出发）不算挡
SELF = {"紧针螺钉 SMP 9/64-40": ("clamp_screw",), "针杆连接块紧定 SMS 11/64-40（上）": ("link_screws",),
        "针杆连接块紧定 SMS 11/64-40（下）": ("link_screws",), "导轨螺钉 SMP 9/64-40（上）": ("rail_screws",),
        "导轨螺钉 SMP 9/64-40（下）": ("rail_screws",), "分油块 M4（前）": ("oil_screws",), "油毡盒 SMP 9/64-40": ("oil_screws",),
        "旋梭紧定螺钉（内六角）": ("hook_shaft", "bobbin_case"), "旋梭紧定螺钉（一字）": ("hook_shaft", "bobbin_case")}
if __name__ == "__main__":
    main()
