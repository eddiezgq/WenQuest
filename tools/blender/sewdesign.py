"""gen:sewdesign —— 缝纫机设计软件里“这一台设计”的机构零件（第 56 轮）。

零件、尺寸、每个主轴转角的位置全部由设计软件的计算核心给（services/gateway/app/sewcore/cad.py 的 parts3d），
和网页版三维、导出的 STEP、计算书是同一套：企业改了曲柄半径、连杆长、挑线四杆……视频里的机器跟着变。
机型：平缝机（lockstitch）、包缝机（overlock）——有三维零件的两种。不画线（设计零件里没有线环）。

场景里这样写（网关 sewing_video.py 自动写，人不用写）：
  - id: d
    use: gen:sewdesign
    machine: lockstitch
    params: {n: 6000, mr: 0.1, fn: 240}
    at: [0, 0, 0]
运动用 drive: weblab 同样的写法：{drive: weblab, model: d, angle: [[秒, 主轴累计转角°], …]}。
组：<id>.<零件名>（UpperShaft、NeedleCrank……，同 STEP）和 <id>.<机构>（needle 刺布、takeup 挑线、hook 钩线、feed 送布、drive 轴、
looper 弯针（包缝机）、knife 切刀（包缝机）、frame 针板）。
读数：phi（主轴转角）、needle（平缝机：针尖高出针板 mm）、hookdeg（平缝机：旋梭转角）。
"""
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "services/gateway/app"))          # 计算核心是纯 Python（只用 math），在 Blender 里直接用

from sewcore.cad import GROUPS as GROUP  # noqa: E402  零件 → 机构（和网关写场景用的是同一张表）


def poses(machine, params, phi):
    from sewcore import cad
    return cad.parts3d(params or {}, phi, machine)


def reads(machine, model, params):
    """面板读数（和设计软件的曲线同一套数）"""
    r = {"phi": model["phi"] % 360}
    if machine == "lockstitch":
        from sewcore import design
        p = design.clean(params)
        M = design.mech_of(p)
        r["needle"] = model["z_tip"] - model["z_plate"]
        r["hookdeg"] = (2 * (model["phi"] - M.PHC0 - p["psi"] / 2)) % 360
    return r


class SewDesign:
    S = 0.001

    def __init__(self, mid, m, bpy, mat, add_group, Matrix, Vector):
        self.bpy, self.mat, self.Matrix, self.Vector = bpy, mat, Matrix, Vector
        self.mid, self.machine, self.params = mid, m.get("machine", "lockstitch"), m.get("params", {}) or {}
        if self.machine not in ("lockstitch", "overlock"):
            raise SystemExit(f"gen:sewdesign 只做有三维零件的机型（lockstitch、overlock），不是 {self.machine}")
        at = [float(x) for x in (m.get("at") or (0, 0, 0))][:3]
        self.offset = Matrix.Translation(Vector(at + [0.0] * (3 - len(at))))
        colors = m.get("colors", {})
        self.objs = {}
        self.read = {}
        first = poses(self.machine, self.params, 0.0)
        sc = bpy.context.scene
        for d in first["parts"]:
            name, typ = d["name"], d["type"]
            grp = GROUP.get(name, "frame")
            col = colors.get(name, colors.get(grp, tuple(d.get("color", (0.7, 0.7, 0.7)))))
            if typ == "plate":
                cu = bpy.data.curves.new(name, "CURVE")
                cu.dimensions, cu.fill_mode = "2D", "BOTH"
                cu.extrude = d["t"] / 2
                o = bpy.data.objects.new(f"{mid}.{name}", cu)
            elif typ == "cyl":
                bpy.ops.mesh.primitive_cylinder_add(vertices=40, radius=d["r"], depth=1.0)
                o = bpy.context.object
                o.name = f"{mid}.{name}"
                sc.collection.objects.unlink(o) if o.name in sc.collection.objects else None
            elif typ == "box":
                bpy.ops.mesh.primitive_cube_add(size=1)
                o = bpy.context.object
                o.name = f"{mid}.{name}"
                sc.collection.objects.unlink(o) if o.name in sc.collection.objects else None
            elif typ == "sphere":
                bpy.ops.mesh.primitive_uv_sphere_add(radius=d["r"], segments=24, ring_count=12)
                o = bpy.context.object
                o.name = f"{mid}.{name}"
                sc.collection.objects.unlink(o) if o.name in sc.collection.objects else None
            else:
                continue
            if o.name not in sc.collection.objects:
                sc.collection.objects.link(o)
            o.data.materials.append(mat(col))
            self.objs[name] = (o, typ)
            add_group(f"{mid}.{name}", o)
            add_group(f"{mid}.{grp}", o)
        self.set_phi(0.0, first)

    # ---------- 每帧 ----------
    def set_phi(self, phi, model=None):
        M, V = self.Matrix, self.Vector
        model = model or poses(self.machine, self.params, phi)
        W = self.offset @ M.Diagonal((self.S, self.S, self.S, 1))
        for d in model["parts"]:
            ent = self.objs.get(d["name"])
            if not ent:
                continue
            o, typ = ent
            if typ == "plate":
                self._plate(o, d, W)
            elif typ == "cyl":
                b, u = V(d["base"]), V(d["dir"]).normalized()
                rot = u.to_track_quat("Z", "Y").to_matrix().to_4x4()
                o.matrix_world = W @ M.Translation(b + u * d["h"] / 2) @ rot @ M.Diagonal((1, 1, d["h"], 1))
            elif typ == "box":
                sx, sy, sz = d["size"]
                b = V(d["base"])
                o.matrix_world = W @ M.Translation(b + V((sx / 2, sy / 2, sz / 2))) @ M.Diagonal((sx, sy, sz, 1))
            elif typ == "sphere":
                o.matrix_world = W @ M.Translation(V(d["c"]))
        self.read = reads(self.machine, model, self.params)

    def _plate(self, o, d, W):
        """平板：几个圆的凸包轮廓减去孔，在自己的平面里画（2D 曲线填充 + 两面各拉伸 t/2），物体矩阵把平面摆到位"""
        from sewcore import cad
        M, V = self.Matrix, self.Vector
        f = d.get("frame")
        if f:
            org, u, v, n = V(f["o"]), V(f["u"]), V(f["v"]), V(f["n"])
        else:
            org, u, v, n = V((0, d["y0"], 0)), V((1, 0, 0)), V((0, 0, 1)), V((0, 1, 0))
        cu = o.data
        cu.splines.clear()

        def poly(pts):
            sp = cu.splines.new("POLY")
            sp.points.add(len(pts) - 1)
            for p_, (a, b) in zip(sp.points, pts):
                p_.co = (a, b, 0, 1)
            sp.use_cyclic_u = True
        poly(cad.outline(d["circles"], seg=36))
        for hx, hz, hr in d.get("holes", []):
            poly([(hx + hr * math.cos(2 * math.pi * i / 24), hz + hr * math.sin(2 * math.pi * i / 24)) for i in range(24)])
        basis = M(((u.x, v.x, n.x, 0), (u.y, v.y, n.y, 0), (u.z, v.z, n.z, 0), (0, 0, 0, 1)))
        o.matrix_world = W @ M.Translation(org + n * d["t"] / 2) @ basis
