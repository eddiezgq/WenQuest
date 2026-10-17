"""三维仿真视频渲染器（第 37 轮第 2 步）：一段视频 = 一个场景文件 scene.yaml（只有数据，AI 写的也是它），本程序照着出片。
    python3 tools/blender/render.py <场景目录> [--draft] [--still 秒,秒] [--shard k/N] [--encode]
      --draft   960×540、15 帧/秒的小样          --still  只出这几秒的单帧（_frames/still_*.png）
      --shard   并行：只画第 k 份（GitHub 工作流 video3d.yml 用）     --encode  帧齐了以后只合成
场景文件写什么，见 tools/blender/场景格式.md。模型只用已有的：程序生成的机构（gen:arm6、gen:conveyor）、简单形体（box、cyl）、
已有虚拟实验里的整机模型（weblab:…，运动也取自实验本身）。运动都由程序算（逆运动学、实验的机构计算），不手调。"""
import json
import math
import subprocess
import sys
from pathlib import Path

import bpy
import yaml
from mathutils import Euler, Matrix, Vector
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
DIR = Path(sys.argv[1]).resolve()
SPEC = yaml.safe_load((DIR / "scene.yaml").read_text(encoding="utf-8"))
ARGV = sys.argv[2:]
DRAFT = "--draft" in ARGV
STILLS = [float(x) for x in ARGV[ARGV.index("--still") + 1].split(",")] if "--still" in ARGV else None
SHARD = [int(x) for x in ARGV[ARGV.index("--shard") + 1].split("/")] if "--shard" in ARGV else None
ENCODE = "--encode" in ARGV
W, H = (960, 540) if DRAFT else (1920, 1080)
FPS = 15 if DRAFT else int(SPEC.get("fps", 30))
TOTAL = float(SPEC["duration"])
NAME = SPEC.get("name", DIR.name)
FONT_B = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_R = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"



def encode():
    name = DIR / (NAME + ("_小样" if DRAFT else ""))
    pat = str(DIR / "_frames" / "f%05d.png")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", pat, "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    "-crf", "18", str(name) + ".mp4"], check=True)
    if not DRAFT:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", pat, "-c:v", "libvpx-vp9", "-b:v", "0",
                        "-crf", "30", "-row-mt", "1", "-cpu-used", "4", str(name) + ".webm"], check=True)
    print("→", name)


if ENCODE:              # 帧都齐了：只合成，不建场景
    encode()
    sys.exit()

PALETTE = {"body": (0.80, 0.84, 0.88), "joint": (0.22, 0.25, 0.29), "accent": (0.13, 0.44, 0.62), "part": (0.93, 0.55, 0.15),
           "table": (0.70, 0.66, 0.60), "belt": (0.25, 0.27, 0.30), "frame": (0.55, 0.58, 0.62), "floor": (1.0, 1.0, 0.98),
           "motor": (0.85, 0.22, 0.18), "gear": (0.95, 0.75, 0.20), "needle": (0.20, 0.47, 0.80), "takeup": (0.20, 0.62, 0.38),
           "hook": (0.93, 0.66, 0.15), "feed": (0.55, 0.36, 0.72), "steel": (0.72, 0.75, 0.78), "shell": (0.86, 0.88, 0.90),
           "wood": (0.62, 0.50, 0.38), "thread": (0.16, 0.45, 0.92), "bobbin": (0.90, 0.40, 0.18), "dark": (0.30, 0.33, 0.37)}
MATS = {}


def mat(name):
    if name not in MATS:
        m = bpy.data.materials.new(name)
        c = PALETTE.get(name, (0.7, 0.7, 0.7)) if isinstance(name, str) else name
        m.diffuse_color = (*c, 1)
        MATS[name] = m
    return MATS[name]


def smooth(u):
    u = max(0.0, min(1.0, u))
    return u * u * u * (u * (6 * u - 15) + 10)


def keyed(keys, t, field, ease=True):
    """keys = [{t: …, field: …}, …] → 时刻 t 的值（相邻两个关键点之间平滑过渡；数值或数列）。"""
    ks = [k for k in keys if field in k]
    if t <= ks[0]["t"]:
        return ks[0][field]
    for a, b in zip(ks, ks[1:]):
        if t <= b["t"]:
            u = (t - a["t"]) / max(1e-9, b["t"] - a["t"])
            u = smooth(u) if ease else u
            va, vb = a[field], b[field]
            return [x + (y - x) * u for x, y in zip(va, vb)] if isinstance(va, list) else va + (vb - va) * u
    return ks[-1][field]


# ------------------------------------------------------------------ 场景
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
OBJ = {}          # 每个模型 id → 对象
GROUPS = {}       # 组名 → [对象]（xray、显示隐藏用）
HIDDEN = set()    # 平时不画、只在透视时画的组


def add_group(g, o):
    GROUPS.setdefault(g, []).append(o)


def mesh(kind, size, loc=(0, 0, 0), rot=(0, 0, 0), color="body", parent=None, name=None):
    if kind == "box":
        bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
        bpy.context.object.scale = size
    else:
        bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=size[0], depth=size[1], location=loc, rotation=rot)
    o = bpy.context.object
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat(color))
    if name:
        o.name = name
    if parent:
        o.parent = parent
        o.matrix_parent_inverse = Matrix.Identity(4)
        o.location, o.rotation_euler = Vector(loc), Euler(rot)
    return o


def empty(name, loc, parent=None):
    e = bpy.data.objects.new(name, None)
    sc.collection.objects.link(e)
    e.parent, e.location = parent, Vector(loc)
    return e


Y90, X90 = (math.pi / 2, 0, 0), (0, math.pi / 2, 0)


class Arm6:
    """gen:arm6 —— 程序生成的六轴机械臂（尺寸来自场景文件），逆运动学：夹爪竖直朝下。组：shell（外壳）、motors（电机和减速器，平时不画）。"""

    def __init__(self, mid, p):
        self.D1, self.L2, self.L3, self.TOOL = p.get("d1", 0.45), p.get("l2", 0.55), p.get("l3", 0.50), p.get("tool", 0.19)
        D1, L2, L3 = self.D1, self.L2, self.L3
        sh, mo = f"{mid}.shell", f"{mid}.motors"
        HIDDEN.add(mo)
        add_group(sh, mesh("cyl", (0.17, 0.08), (0, 0, 0.04), color="joint"))
        J = [empty("J1", (0, 0, 0))]
        add_group(sh, mesh("cyl", (0.12, D1 - 0.08), (0, 0, 0.08 + (D1 - 0.08) / 2 - 0.04), parent=J[0]))
        add_group(mo, mesh("cyl", (0.06, 0.14), (0, 0, 0.16), color="motor", parent=J[0]))
        J.append(empty("J2", (0, 0, D1), J[0]))
        add_group(sh, mesh("cyl", (0.11, 0.24), (0, 0, 0), Y90, "joint", J[1]))
        add_group(sh, mesh("box", (L2, 0.13, 0.13), (L2 / 2, 0, 0), parent=J[1]))
        add_group(mo, mesh("cyl", (0.06, 0.20), (0, 0.19, 0), Y90, "motor", J[1]))
        add_group(mo, mesh("cyl", (0.085, 0.05), (0, 0.06, 0), Y90, "gear", J[1]))
        J.append(empty("J3", (L2, 0, 0), J[1]))
        add_group(sh, mesh("cyl", (0.09, 0.20), (0, 0, 0), Y90, "joint", J[2]))
        add_group(mo, mesh("cyl", (0.05, 0.16), (0, -0.16, 0), Y90, "motor", J[2]))
        add_group(mo, mesh("cyl", (0.07, 0.04), (0, -0.05, 0), Y90, "gear", J[2]))
        J.append(empty("J4", (0, 0, 0), J[2]))
        add_group(sh, mesh("cyl", (0.055, L3 - 0.06), ((L3 - 0.06) / 2 + 0.03, 0, 0), X90, "body", J[3]))
        add_group(mo, mesh("cyl", (0.035, 0.12), (0.14, 0, 0), X90, "motor", J[3]))
        J.append(empty("J5", (L3, 0, 0), J[3]))
        add_group(sh, mesh("cyl", (0.06, 0.14), (0, 0, 0), Y90, "joint", J[4]))
        add_group(mo, mesh("cyl", (0.03, 0.10), (0, 0.11, 0), Y90, "motor", J[4]))
        J.append(empty("J6", (0.07, 0, 0), J[4]))
        add_group(sh, mesh("cyl", (0.045, 0.04), (0, 0, 0), X90, "accent", J[5]))
        add_group(mo, mesh("cyl", (0.025, 0.05), (-0.03, 0, 0), X90, "motor", J[5]))
        add_group(sh, mesh("box", (0.03, 0.16, 0.05), (0.035, 0, 0), color="joint", parent=J[5]))
        self.fing = [mesh("box", (0.10, 0.015, 0.04), (0.10, s * 0.06, 0), color="joint", parent=J[5]) for s in (1, -1)]
        for f in self.fing:
            add_group(sh, f)
        self.J, self.tipE = J, empty("tip", (self.TOOL - 0.07, 0, 0), J[4])
        self.q, self.grip = [0.0] * 6, 0.0

    def ik(self, p):
        wc = Vector(p) + Vector((0, 0, self.TOOL))
        j1 = math.atan2(wc.y, wc.x)
        r, z = math.hypot(wc.x, wc.y), wc.z - self.D1
        d = (r * r + z * z - self.L2 ** 2 - self.L3 ** 2) / (2 * self.L2 * self.L3)
        if abs(d) > 1:
            raise SystemExit(f"机械臂够不着 {tuple(round(v, 3) for v in p)}")
        j3 = -math.acos(d)
        j2 = math.atan2(z, r) - math.atan2(self.L3 * math.sin(j3), self.L2 + self.L3 * math.cos(j3))
        return [j1, j2, j3, 0.0, -math.pi / 2 - j2 - j3, j1]

    def set(self, p, grip):
        self.q, self.grip = self.ik(p), grip
        for i, (j, v) in enumerate(zip(self.J, self.q)):
            j.rotation_euler = (0, 0, v) if i == 0 else ((0, -v, 0) if i in (1, 2, 4) else (v, 0, 0))
        gap = 0.06 - 0.019 * grip
        self.fing[0].location.y, self.fing[1].location.y = gap, -gap

    def tip(self):
        return self.tipE.matrix_world.translation.copy()


class Conveyor:
    """gen:conveyor —— 传送带（沿 x），皮带纹路按速度走。"""

    def __init__(self, mid, p):
        L, Wd, h = p.get("length", 1.9), p.get("width", 0.30), p.get("height", 0.35)
        cx, cy = p["at"]
        self.speed, self.x0, self.L = p.get("speed", 0.12), cx - L / 2, L
        mesh("box", (L, Wd, 0.04), (cx, cy, h - 0.02), color="belt")
        mesh("box", (L, Wd + 0.04, h - 0.04), (cx, cy, (h - 0.04) / 2), color="frame")
        for x in (self.x0, self.x0 + L):
            mesh("cyl", (0.02, Wd + 0.02), (x, cy, h), Y90, "joint")
        self.stripes = [mesh("box", (0.02, Wd, 0.004), (self.x0 + 0.15 * k, cy, h + 0.002), color="frame") for k in range(int(L / 0.15))]

    def update(self, t):
        for k, s in enumerate(self.stripes):
            s.location.x = self.x0 + ((0.15 * k + self.speed * t) % self.L)


class WebLab:
    """weblab:<实验> —— 已有虚拟实验的整机模型和运动。组：按零件表的 group（frame、needle、takeup、hook、feed、drive）+ threads。"""
    S = 0.001

    def __init__(self, mid, name, p):
        import base64
        from array import array
        from weblab import Lab
        self.name, self.mid = name, mid
        self.C = Matrix(((1, 0, 0, 0), (0, 0, -1, 0), (0, 1, 0, 0), (0, 0, 0, 1))) @ Matrix.Diagonal((self.S,) * 3 + (1,))
        self.offset = Matrix.Translation(Vector(p.get("at", (0, 0, 0))))
        self.lab = Lab(name).__enter__()
        M = self.lab.mesh()
        self.info = {q["key"]: q for q in M["parts"]}
        colors = p.get("colors", {})
        self.objs = {}
        for key, m in M["mesh"].items():
            if key in ("panes",):
                continue
            v = array("f")
            v.frombytes(base64.b64decode(m["v"]))
            idx = array("I" if m["i32"] else "H")
            idx.frombytes(base64.b64decode(m["i"]))
            me = bpy.data.meshes.new(key)
            me.from_pydata([tuple(v[i:i + 3]) for i in range(0, len(v), 3)], [], [tuple(idx[i:i + 3]) for i in range(0, len(idx), 3)])
            me.validate()
            for poly in me.polygons:
                poly.use_smooth = True
            o = bpy.data.objects.new(f"{mid}.{key}", me)
            sc.collection.objects.link(o)
            grp = self.info.get(key, {}).get("group", "frame")
            o.data.materials.append(mat(colors.get(key, colors.get(grp, "shell" if grp == "frame" else grp))))
            o.matrix_world = self.offset @ self.C
            self.objs[key] = o
            add_group(f"{mid}.{grp}", o)
            add_group(f"{mid}.{key}", o)
        self.objs["body_cut"].hide_render = True
        self.threads = {}
        self.read = {}

    def set(self, d):
        for key, m in d["parts"].items():
            if key in self.objs and key not in ("body",):
                self.objs[key].matrix_world = self.offset @ self.C @ Matrix([m[0:4], m[4:8], m[8:12], m[12:16]]).transposed()
        for name, pts in d["tubes"].items():
            self.tube(name, pts)
        self.read = dict(d["read"], phi=d["phi"])

    def tube(self, name, pts):
        o = self.threads.get(name)
        if o is not None:
            bpy.data.objects.remove(o, do_unlink=True)
            self.threads[name] = None
        if not pts:
            return
        cu = bpy.data.curves.new(name, "CURVE")
        cu.dimensions, cu.bevel_depth, cu.bevel_resolution = "3D", 0.00045, 2
        sp = cu.splines.new("NURBS")
        sp.points.add(len(pts) - 1)
        for p_, q in zip(sp.points, pts):
            w = self.offset @ self.C @ Vector(q)
            p_.co = (w.x, w.y, w.z, 1)
        sp.use_endpoint_u, sp.order_u = True, 3
        o = bpy.data.objects.new(f"{self.mid}.thread.{name}", cu)
        o.data.materials.append(mat("bobbin" if name == "bobbin" else "thread"))
        sc.collection.objects.link(o)
        self.threads[name] = o
        GROUPS[f"{self.mid}.threads"] = [x for x in self.threads.values() if x is not None]


class Item:
    """一个会被搬运的小物件：在 start 处出现 → 被机械臂夹住随夹爪走 → 放上传送带随皮带走。"""

    def __init__(self, mid, p):
        self.p = p
        self.o = mesh("box", tuple(p.get("size", (0.08, 0.08, 0.08))), (0, 0, -5), color=p.get("color", "part"))

    def update(self, t):
        p = self.p
        if t < p.get("appear", 0):
            self.o.location = (0, 0, -5)
        elif t < p["pick"]:
            self.o.location = Vector(p["start"])
        elif t < p["drop"]:
            self.o.location = OBJ[p["arm"]].tip()
        else:
            if "_drop_at" not in p:
                p["_drop_at"] = list(PATHS[p["arm"]](p["drop"])[0])
            v = OBJ[p["belt"]].speed if p.get("belt") else 0
            d = Vector(p["_drop_at"])
            self.o.location = (d.x + v * (t - p["drop"]), d.y, d.z)


for m in SPEC["models"]:
    use, mid = m["use"], m["id"]
    if use == "gen:arm6":
        OBJ[mid] = Arm6(mid, m.get("params", {}))
    elif use == "gen:conveyor":
        OBJ[mid] = Conveyor(mid, m)
    elif use.startswith("weblab:"):
        OBJ[mid] = WebLab(mid, use[7:], m)
    elif use == "item":
        OBJ[mid] = Item(mid, m)
    elif use in ("box", "cyl"):
        OBJ[mid] = mesh(use, tuple(m["size"]), tuple(m["at"]), tuple(math.radians(a) for a in m.get("rot", (0, 0, 0))), m.get("color", "body"))
    else:
        raise SystemExit(f"不认识的模型：{use}（只能用已有模型，见 场景格式.md）")
if SPEC.get("floor", True):
    mesh("box", (40, 40, 0.02), (0, 0, -0.01 + SPEC.get("floor_z", 0)), color="floor")

# ------------------------------------------------------------------ 运动
PATHS = {}
STEP_AT = {}


def pick_place(arm, steps, points):
    P = lambda v: Vector(points[v]) if isinstance(v, str) else Vector(v)   # noqa: E731

    def f(t):
        for k, s in enumerate(steps):
            t0, t1 = s["t"]
            if t0 <= t < t1 or k == len(steps) - 1:
                u = smooth((t - t0) / (t1 - t0))
                a, b = P(s.get("from", s.get("at"))), P(s.get("to", s.get("at")))
                p = a.lerp(b, u)
                if (a - b).length > 0.3:
                    p = p + Vector((0, 0, s.get("arch", 0.12) * math.sin(math.pi * u)))
                g = {"grip": u, "release": 1 - u}.get(s.get("do"), 1.0 if s.get("holding") else 0.0)
                return p, g
        raise ValueError(t)
    return f


WEBLAB_A = {}
for d in SPEC.get("motion", []):
    if d["drive"] == "pick_place":
        PATHS[d["model"]] = pick_place(OBJ[d["model"]], d["steps"], SPEC.get("points", {}))
    elif d["drive"] == "weblab":
        WEBLAB_A[d["model"]] = d["angle"]       # [[时间, 主轴累计转角°], …]，相邻两点之间匀速


def shaft_angle(mid, t):
    ks = WEBLAB_A[mid]
    if t <= ks[0][0]:
        return ks[0][1]
    for (t0, a0), (t1, a1) in zip(ks, ks[1:]):
        if t <= t1:
            return a0 + (a1 - a0) * (t - t0) / max(1e-9, t1 - t0)
    return ks[-1][1]


# ------------------------------------------------------------------ 画面风格、镜头
sc.render.engine = "BLENDER_WORKBENCH"
shd = sc.display.shading
shd.light, shd.color_type, shd.studio_light = "STUDIO", "MATERIAL", SPEC.get("light", "paint.sl")
shd.show_shadows, shd.shadow_intensity, shd.show_cavity = True, 0.35, True
shd.cavity_type, shd.show_object_outline = "BOTH", True
sc.display.light_direction = (0.45, -0.35, 0.82)
sc.world = bpy.data.worlds.new("w")
sc.world.color = (0.97, 0.96, 0.93)
sc.render.resolution_x, sc.render.resolution_y = W, H
sc.display.render_aa = "16"
sc.view_settings.view_transform = "Standard"
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.clip_start = SPEC.get("clip", 0.01)


def camera(t):
    keys = SPEC["camera"]
    look = Vector(keyed(keys, t, "look"))
    az, el, dist = (math.radians(keyed(keys, t, "az")), math.radians(keyed(keys, t, "el")), keyed(keys, t, "dist"))
    cam.data.lens = keyed(keys, t, "lens") if any("lens" in k for k in keys) else 40
    pos = look + dist * Vector((math.cos(el) * math.sin(az), -math.cos(el) * math.cos(az), math.sin(el)))
    cam.location = pos
    cam.rotation_euler = (look - pos).to_track_quat("-Z", "Y").to_euler()


def effect(t):
    """透视程度 xu（0–1）、要叠在上面的组；剖开（换成开窗机壳、去掉外盖）。"""
    xu, top = 0.0, []
    for e in SPEC.get("effects", []):
        a, b = e["t"]
        if e["kind"] == "xray" and a - 1.5 < t < b + 1.5:
            u = smooth((t - a) / 1.5) - smooth((t - b) / 1.5)
            if u > xu:
                xu, top = u, e["top"]
        if e["kind"] == "cutaway":
            on = a <= t < b
            for g in e.get("hide", []):
                for o in GROUPS.get(g, []):
                    o.hide_render = on
            for g in e.get("show", []):
                for o in GROUPS.get(g, []):
                    o.hide_render = not on
    return xu, top


def labels(t, read):
    for L in SPEC.get("labels", []):
        a, b = L["t"]
        if a <= t < b and ("phi" not in L or (read and L["phi"][0] <= read.get("phi", -1) < L["phi"][1])):
            yield L


# ------------------------------------------------------------------ 叠字
def font(path, size):
    return ImageFont.truetype(path, int(size * H / 1080))


CURVES = {}


def hud(img, t, read):
    d = ImageDraw.Draw(img, "RGBA")
    s = H / 1080
    d.rectangle([0, 0, W, 160 * s], fill=(251, 250, 247, 225))
    title = [L for L in labels(t, read) if L.get("where", "title") == "title"]
    zh, en = (title[-1]["zh"], title[-1]["en"]) if title else (SPEC["title"]["zh"], SPEC["title"]["en"])
    d.text((60 * s, 40 * s), zh, font=font(FONT_B, 54), fill=(29, 35, 41))
    d.text((62 * s, 112 * s), en, font=font(FONT_R, 30), fill=(95, 107, 118))
    caps = [L for L in labels(t, read) if L.get("where") == "bottom"]
    if caps:
        c = caps[-1]
        d.rounded_rectangle([W / 2 - 700 * s, H - 150 * s, W / 2 + 700 * s, H - 40 * s], 18 * s, fill=(29, 35, 41, 210))
        d.text((W / 2, H - 128 * s), c["zh"], font=font(FONT_B, 40), fill=(255, 255, 255), anchor="ma")
        d.text((W / 2, H - 78 * s), c["en"], font=font(FONT_R, 26), fill=(205, 212, 218), anchor="ma")
    pan = SPEC.get("panel")
    if not pan:
        return img
    x0, y0, w = W - 470 * s, 210 * s, 410 * s
    rows = []
    if pan["kind"] == "joints":
        arm = OBJ[pan["arm"]]
        names = ["J1 底座 base", "J2 肩 shoulder", "J3 肘 elbow", "J4 小臂 forearm", "J5 手腕 wrist", "J6 法兰 flange"]
        rows = [(n, math.degrees(v), "{:+6.1f}°", 180) for n, v in zip(names, arm.q)]
        head = "关节角  Joint angles"
    else:
        rows = [(f"{r['zh']} {r['en']}", read.get(r["key"], 0) or 0, r.get("fmt", "{:6.1f}") + r.get("unit", ""), r.get("scale", 0))
                for r in pan["items"]]
        head = pan.get("head", "读数  Readouts")
    hgt = len(rows) * 74 * s + 40 * s + (230 * s if pan.get("plot") else 0) + (34 * s if pan["kind"] == "joints" else 0)
    d.rounded_rectangle([x0 - 24 * s, y0 - 70 * s, x0 + w + 10 * s, y0 + hgt], 18 * s, fill=(255, 255, 255, 215), outline=(200, 205, 210))
    d.text((x0, y0 - 56 * s), head, font=font(FONT_B, 30), fill=(29, 35, 41))
    for i, (n, v, fmt, sc_) in enumerate(rows):
        y = y0 + i * 74 * s
        d.text((x0, y), n, font=font(FONT_R, 24), fill=(60, 68, 76))
        d.text((x0 + w - 6 * s, y), fmt.format(v), font=font(FONT_B, 26), fill=(33, 112, 158), anchor="ra")
        if sc_:
            bx, by, bw = x0, y + 38 * s, w - 10 * s
            d.rounded_rectangle([bx, by, bx + bw, by + 12 * s], 6 * s, fill=(225, 228, 232))
            mid = bx + bw / 2
            end = mid + bw / 2 * max(-1, min(1, v / sc_))
            d.rounded_rectangle([min(mid, end), by, max(mid, end), by + 12 * s], 6 * s, fill=(33, 112, 158))
            d.line([mid, by - 3 * s, mid, by + 15 * s], fill=(120, 128, 136), width=max(1, int(2 * s)))
    y = y0 + len(rows) * 74 * s
    if pan["kind"] == "joints":
        d.text((x0, y), f"夹爪 gripper：{'夹紧 closed' if arm.grip > 0.5 else '张开 open'}", font=font(FONT_R, 24), fill=(60, 68, 76))
        y += 34 * s
    pl = pan.get("plot")
    if pl and pl["key"] in CURVES:
        px, py, pw, ph = x0, y + 20 * s, w - 10 * s, 170 * s
        d.rectangle([px, py, px + pw, py + ph], fill=(246, 247, 248), outline=(210, 214, 218))
        vals = CURVES[pl["key"]]
        lo, hi = min(vals), max(vals)
        pts = [(px + pw * i / 359, py + ph - 10 * s - (ph - 20 * s) * (v - lo) / max(1e-9, hi - lo)) for i, v in enumerate(vals)]
        d.line(pts, fill=(33, 112, 158), width=max(1, int(3 * s)))
        for k, m in enumerate(pl.get("marks", [])):
            mx = px + pw * m["phi"] / 359
            d.line([mx, py, mx, py + ph], fill=(217, 56, 46, 160), width=max(1, int(2 * s)))
            d.text((mx + 4 * s, py + (4 + 24 * k) * s), m["zh"], font=font(FONT_R, 18), fill=(217, 56, 46))
        cx = px + pw * (read.get("phi", 0) % 360) / 359
        d.line([cx, py, cx, py + ph], fill=(29, 35, 41), width=max(1, int(3 * s)))
        d.text((px, py + ph + 8 * s), f"{pl['zh']} {pl['en']}（横轴：主轴转角 0–360°）", font=font(FONT_R, 20), fill=(95, 107, 118))
    d.text((W - 60 * s, H - 20 * s), "问渠 WenQuest · 三维仿真", font=font(FONT_R, 22), fill=(140, 146, 152), anchor="rs")
    return img


# ------------------------------------------------------------------ 出片
out = DIR / "_frames"
out.mkdir(exist_ok=True)
NF = int(TOTAL * FPS)
if STILLS:
    jobs = [(None, t) for t in STILLS]
elif ENCODE:
    jobs = []
else:
    lo, hi = (SHARD[0] * NF // SHARD[1], (SHARD[0] + 1) * NF // SHARD[1]) if SHARD else (0, NF)
    jobs = [(i, i / FPS) for i in range(lo, hi)]

# 虚拟实验：先把这一份要用的转角一次取齐（还有一圈 0–359° 的读数，画曲线用）
DUMPS = {}
for mid in WEBLAB_A:
    lab = OBJ[mid]
    angles = sorted({round(shaft_angle(mid, t), 3) for _, t in jobs})
    for a, d in zip(angles, lab.lab.dumps(angles)):
        DUMPS[(mid, a)] = d
    pan = SPEC.get("panel") or {}
    if pan.get("plot") and jobs:
        CURVES[pan["plot"]["key"]] = [x["read"][pan["plot"]["key"]] for x in lab.lab.dumps(list(range(360)))]

for n, t in jobs:
    read = {}
    for mid, o in OBJ.items():
        if isinstance(o, Arm6) and mid in PATHS:
            p, g = PATHS[mid](t)
            o.set(p, g)
        if isinstance(o, Conveyor):
            o.update(t)
    bpy.context.view_layer.update()
    for mid, o in OBJ.items():
        if isinstance(o, Item):
            o.update(t)
        if isinstance(o, WebLab) and mid in WEBLAB_A:
            o.set(DUMPS[(mid, round(shaft_angle(mid, t), 3))])
            read = o.read
    xu, top = effect(t)
    shd.show_xray, shd.xray_alpha = xu > 0.05, 1 - 0.7 * xu
    for g in HIDDEN:
        for o in GROUPS.get(g, []):
            o.hide_render = True
    camera(t)
    f = out / (f"still_{t:05.1f}.png" if n is None else f"f{n:05d}.png")
    sc.render.filepath = str(f)
    bpy.ops.render.render(write_still=True)
    img = Image.open(f).convert("RGBA")
    if xu > 0.05:                                     # 第二层：只画要“透出来”的组（透明底），按透视程度叠上去
        keep = {id(o) for g in top for o in GROUPS.get(g, [])}
        saved = {o.name: o.hide_render for o in sc.objects}
        for o in sc.objects:
            if o.type in ("MESH", "CURVE"):
                o.hide_render = id(o) not in keep
        shd.show_xray, sc.render.film_transparent = False, True
        tmp = out / f"_top_{SHARD[0] if SHARD else 0}.png"
        sc.render.filepath = str(tmp)
        bpy.ops.render.render(write_still=True)
        top_img = Image.open(tmp).convert("RGBA")
        top_img.putalpha(top_img.getchannel("A").point(lambda v: int(v * min(1.0, xu))))
        img = Image.alpha_composite(img, top_img)
        for o in sc.objects:
            o.hide_render = saved[o.name]
        sc.render.film_transparent = False
    hud(img.convert("RGB"), t, read).save(f)
    if n is not None and n % 50 == 0:
        print(f"{n}/{NF}", flush=True)

for o in OBJ.values():
    if isinstance(o, WebLab):
        o.lab.__exit__()

if not STILLS and not SHARD:
    encode()
