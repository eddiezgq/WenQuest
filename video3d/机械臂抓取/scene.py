"""三维仿真样片 A：六轴机械臂抓取与放置（第 36 轮，Eddie 2026-10-16 19:12“做a看看”）。
运动全部自己算：夹爪走的路线（直线 + 平滑加减速）→ 逆运动学算出 6 个关节角 → 写进 Blender；零件夹住时跟着夹爪走，放上传送带后随皮带走。
Blender（bpy 模块）只负责画：工程图风格（Workbench），中英标注和关节角面板用 PIL 叠在每一帧上，最后 ffmpeg 合成。
    python3 scene.py [--draft] [--still 秒,秒,...]       # --draft：960×540、15 帧/秒；--still：只出这几秒的单帧
    python3 scene.py [--draft] --shard k/N               # 并行：只画第 k 份（共 N 份）的帧（GitHub 工作流 video3d.yml 用）
    python3 scene.py [--draft] --encode                  # 帧都齐了以后只合成视频
输出：本目录 机械臂抓取.mp4 / 机械臂抓取.webm（中间帧在 _frames/，不进仓库）。"""
import math
import subprocess
import sys
from pathlib import Path

import bpy
from mathutils import Euler, Matrix, Vector
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
DRAFT = "--draft" in sys.argv
STILLS = [float(x) for x in sys.argv[sys.argv.index("--still") + 1].split(",")] if "--still" in sys.argv else None
W, H, FPS = (960, 540, 15) if DRAFT else (1920, 1080, 30)
FONT_B = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_R = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"

# ------------------------------------------------------------------ 机械臂尺寸（米）
D1, L2, L3, TOOL = 0.45, 0.55, 0.50, 0.19      # 肩高、大臂、小臂、腕心到夹持点
PICK = Vector((0.62, -0.40, 0.29))             # 零件中心（放在工作台上）
PLACE = Vector((0.45, 0.55, 0.39))             # 放到传送带上的位置
HOME = Vector((0.55, 0.0, 0.75))
BELT_V = 0.12                                  # 皮带速度 m/s


def ik(p, yaw_tool=0.0):
    """夹持点 p（夹爪竖直朝下）→ 6 个关节角（弧度）。J1 转底座，J2/J3 平面两连杆（肘朝上），J5 让夹爪竖直，J6 对准零件。"""
    wc = p + Vector((0, 0, TOOL))                       # 腕心
    j1 = math.atan2(wc.y, wc.x)
    r, z = math.hypot(wc.x, wc.y), wc.z - D1
    d = (r * r + z * z - L2 * L2 - L3 * L3) / (2 * L2 * L3)
    j3 = -math.acos(max(-1.0, min(1.0, d)))             # 肘朝上
    j2 = math.atan2(z, r) - math.atan2(L3 * math.sin(j3), L2 + L3 * math.cos(j3))
    j5 = -math.pi / 2 - j2 - j3                         # 夹爪绝对俯仰 = -90°
    j6 = j1 - yaw_tool
    return [j1, j2, j3, 0.0, j5, j6]


def smooth(u):
    u = max(0.0, min(1.0, u))
    return u * u * u * (u * (6 * u - 15) + 10)          # 五次多项式：起止速度、加速度都为 0


# ------------------------------------------------------------------ 时间线（秒）
UP = Vector((0, 0, 0.22))
STEPS = [  # (起, 止, 动作, 起点, 终点, 夹爪开度 0 开 1 合, 中文, 英文)
    (0.0, 5.0, "hold", HOME, HOME, 0, "六轴机械臂：抓取与放置", "6-axis robot arm: pick and place"),
    (5.0, 8.0, "move", HOME, PICK + UP, 0, "① 移到零件上方", "① Move above the part"),
    (8.0, 9.6, "move", PICK + UP, PICK, 0, "② 下降", "② Descend"),
    (9.6, 10.6, "grip", PICK, PICK, 1, "③ 夹紧", "③ Grip"),
    (10.6, 12.0, "move", PICK, PICK + UP, 1, "④ 提起", "④ Lift"),
    (12.0, 15.5, "move", PICK + UP, PLACE + UP, 1, "⑤ 移到传送带", "⑤ Carry to the conveyor"),
    (15.5, 17.0, "move", PLACE + UP, PLACE, 1, "⑥ 放下", "⑥ Lower"),
    (17.0, 18.0, "release", PLACE, PLACE, 0, "⑦ 松开", "⑦ Release"),
    (18.0, 21.0, "move", PLACE, HOME, 0, "⑧ 回原位", "⑧ Return home"),
    (21.0, 31.0, "xray", HOME, HOME, 0, "透视：每个关节一台伺服电机 + 减速器", "X-ray: a servo motor and a reducer in every joint"),
    (31.0, 33.0, "move", HOME, PICK + UP, 0, "再来一次，快 2 倍", "Again, twice as fast"),
    (33.0, 33.8, "move", PICK + UP, PICK, 0, "再来一次，快 2 倍", "Again, twice as fast"),
    (33.8, 34.3, "grip", PICK, PICK, 1, "再来一次，快 2 倍", "Again, twice as fast"),
    (34.3, 35.0, "move", PICK, PICK + UP, 1, "再来一次，快 2 倍", "Again, twice as fast"),
    (35.0, 36.8, "move", PICK + UP, PLACE + UP + Vector((-0.25, 0, 0)), 1, "再来一次，快 2 倍", "Again, twice as fast"),
    (36.8, 37.6, "move", PLACE + UP + Vector((-0.25, 0, 0)), PLACE + Vector((-0.25, 0, 0)), 1, "再来一次，快 2 倍", "Again, twice as fast"),
    (37.6, 38.1, "release", PLACE + Vector((-0.25, 0, 0)), PLACE + Vector((-0.25, 0, 0)), 0, "再来一次，快 2 倍", "Again, twice as fast"),
    (38.1, 40.0, "move", PLACE + Vector((-0.25, 0, 0)), HOME, 0, "逆运动学：给出夹爪位置 → 算出 6 个关节角", "Inverse kinematics: gripper pose in, six joint angles out"),
    (40.0, 43.0, "hold", HOME, HOME, 0, "逆运动学：给出夹爪位置 → 算出 6 个关节角", "Inverse kinematics: gripper pose in, six joint angles out"),
]
TOTAL = STEPS[-1][1]


def state(t):
    """t 秒时：夹持点、夹爪开合、哪一步、两个零件在哪。"""
    for k, (t0, t1, kind, a, b, g, zh, en) in enumerate(STEPS):
        if t0 <= t < t1 or k == len(STEPS) - 1:
            u = smooth((t - t0) / (t1 - t0))
            p = a.lerp(b, u) if kind == "move" else a
            if kind == "move" and (a - b).length > 0.3:          # 远距离搬运走一条拱形，绕开台面
                p = p + Vector((0, 0, 0.12 * math.sin(math.pi * u)))
            grip = {"grip": u, "release": 1 - u}.get(kind, g)
            return p, grip, k, zh, en
    raise ValueError(t)


def parts(t, tip):
    """两个零件的位置：在台上 → 被夹住随夹爪 → 放上皮带随皮带走。第二个零件在第一个被拿走后“补料”出现。"""
    out = []
    for show, pick_t, drop_t, x0 in ((0.0, 10.1, 17.5, PLACE.x), (18.0, 34.05, 37.85, PLACE.x - 0.25)):
        if t < show:
            out.append(None)
        elif t < pick_t:
            out.append(PICK.copy())
        elif t < drop_t:
            out.append(tip.copy())
        else:
            out.append(Vector((x0 + BELT_V * (t - drop_t), PLACE.y, PLACE.z)))
    return out


# ------------------------------------------------------------------ 建场景
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
COLORS = {"body": (0.80, 0.84, 0.88, 1), "joint": (0.22, 0.25, 0.29, 1), "accent": (0.13, 0.44, 0.62, 1),
          "part": (0.93, 0.55, 0.15, 1), "table": (0.70, 0.66, 0.60, 1), "belt": (0.25, 0.27, 0.30, 1),
          "frame": (0.55, 0.58, 0.62, 1), "floor": (1.0, 1.0, 0.98, 1), "motor": (0.85, 0.22, 0.18, 1),
          "gear": (0.95, 0.75, 0.20, 1)}
MATS = {}
for k, c in COLORS.items():
    m = bpy.data.materials.new(k)
    m.diffuse_color = c
    MATS[k] = m


def mesh(kind, size, loc=(0, 0, 0), rot=(0, 0, 0), mat="body", parent=None, name=None):
    if kind == "box":
        bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
        bpy.context.object.scale = size
    elif kind == "cyl":
        bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=size[0], depth=size[1], location=loc, rotation=rot)
    o = bpy.context.object
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(MATS[mat])
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


Y90 = (math.pi / 2, 0, 0)            # 圆柱轴转到 y（关节轴）
X90 = (0, math.pi / 2, 0)            # 圆柱轴转到 x（连杆方向）
SHELL, MOTORS = [], []
FLOOR = mesh("box", (40, 40, 0.02), (0.4, 0.1, -0.01), mat="floor")
# 底座与 J1
SHELL.append(mesh("cyl", (0.17, 0.08), (0, 0, 0.04), mat="joint"))
J = [empty("J1", (0, 0, 0))]
SHELL.append(mesh("cyl", (0.12, D1 - 0.08), (0, 0, 0.08 + (D1 - 0.08) / 2 - 0.04), parent=J[0]))
MOTORS.append(mesh("cyl", (0.06, 0.14), (0, 0, 0.16), mat="motor", parent=J[0]))
# J2 肩
J.append(empty("J2", (0, 0, D1), J[0]))
SHELL.append(mesh("cyl", (0.11, 0.24), (0, 0, 0), Y90, "joint", J[1]))
SHELL.append(mesh("box", (L2, 0.13, 0.13), (L2 / 2, 0, 0), mat="body", parent=J[1]))
MOTORS.append(mesh("cyl", (0.06, 0.20), (0, 0.19, 0), Y90, "motor", J[1]))
MOTORS.append(mesh("cyl", (0.085, 0.05), (0, 0.06, 0), Y90, "gear", J[1]))
# J3 肘
J.append(empty("J3", (L2, 0, 0), J[1]))
SHELL.append(mesh("cyl", (0.09, 0.20), (0, 0, 0), Y90, "joint", J[2]))
MOTORS.append(mesh("cyl", (0.05, 0.16), (0, -0.16, 0), Y90, "motor", J[2]))
MOTORS.append(mesh("cyl", (0.07, 0.04), (0, -0.05, 0), Y90, "gear", J[2]))
# J4 小臂自转
J.append(empty("J4", (0.0, 0, 0), J[2]))
SHELL.append(mesh("cyl", (0.055, L3 - 0.06), ((L3 - 0.06) / 2 + 0.03, 0, 0), X90, "body", J[3]))
MOTORS.append(mesh("cyl", (0.035, 0.12), (0.14, 0, 0), X90, "motor", J[3]))
# J5 手腕
J.append(empty("J5", (L3, 0, 0), J[3]))
SHELL.append(mesh("cyl", (0.06, 0.14), (0, 0, 0), Y90, "joint", J[4]))
MOTORS.append(mesh("cyl", (0.03, 0.10), (0, 0.11, 0), Y90, "motor", J[4]))
# J6 法兰 + 夹爪（夹爪沿 J5 的 +x 伸出）
J.append(empty("J6", (0.07, 0, 0), J[4]))
SHELL.append(mesh("cyl", (0.045, 0.04), (0.0, 0, 0), X90, "accent", J[5]))
MOTORS.append(mesh("cyl", (0.025, 0.05), (-0.03, 0, 0), X90, "motor", J[5]))
palm = mesh("box", (0.03, 0.16, 0.05), (0.035, 0, 0), mat="joint", parent=J[5])
SHELL.append(palm)
FING = [mesh("box", (0.10, 0.015, 0.04), (0.10, s * 0.06, 0), mat="joint", parent=J[5]) for s in (1, -1)]
SHELL += FING
TIP = empty("tip", (TOOL - 0.07, 0, 0), J[5])
# 工作台、传送带
mesh("box", (0.36, 0.36, 0.25), (PICK.x, PICK.y, 0.125), mat="table")
mesh("box", (1.9, 0.30, 0.04), (0.65, PLACE.y, 0.33), mat="belt")
mesh("box", (1.9, 0.34, 0.31), (0.65, PLACE.y, 0.155), mat="frame")
ROLL = [mesh("cyl", (0.02, 0.32), (x, PLACE.y, 0.35), Y90, "joint") for x in (-0.28, 1.58)]
STRIPES = [mesh("box", (0.02, 0.30, 0.004), (-0.25 + 0.15 * k, PLACE.y, 0.352), mat="frame") for k in range(13)]
PART = [mesh("box", (0.08, 0.08, 0.08), (0, 0, -5), mat="part") for _ in range(2)]

# 灯光与画面风格（Workbench：平涂 + 阴影 + 凹痕，像工程图）
sc.render.engine = "BLENDER_WORKBENCH"
sh = sc.display.shading
sh.light, sh.color_type = "STUDIO", "MATERIAL"; sh.studio_light = "paint.sl"
sh.show_shadows, sh.shadow_intensity, sh.show_cavity = True, 0.35, True
sh.cavity_type, sh.show_object_outline = "BOTH", True
sc.display.light_direction = (0.45, -0.35, 0.82)
sc.world = bpy.data.worlds.new("w")
sc.world.color = (0.97, 0.96, 0.93)
sc.render.resolution_x, sc.render.resolution_y = W, H
sc.display.render_aa = "16"
sc.view_settings.view_transform = "Standard"
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.lens = 40


def camera(t):
    """镜头：开头环绕一圈半 → 斜上方看全景 → 透视段拉近机械臂 → 快速段跟到夹爪。"""
    look = Vector((0.45, 0.05, 0.45))
    if t < 5:
        a = math.radians(-60 + 70 * smooth(t / 5))
        dist, h = 2.9 - 0.3 * smooth(t / 5), 1.5
    elif t < 21:
        a, dist, h = math.radians(10), 2.6, 1.5
    elif t < 31:
        u = smooth((t - 21) / 2) - smooth((t - 29) / 2)
        a, dist, h = math.radians(10 - 50 * smooth((t - 21) / 10)), 2.6 - 0.6 * u, 1.5 - 0.2 * u
        look = Vector((0.25, 0.0, 0.6)).lerp(look, 1 - u)
    else:
        a, dist, h = math.radians(-40 + 50 * smooth((t - 31) / 3)), 2.6, 1.5
    pos = look + Vector((dist * math.cos(a - math.pi / 2), dist * math.sin(a - math.pi / 2), h))
    cam.location = pos
    cam.rotation_euler = (look - pos).to_track_quat("-Z", "Y").to_euler()


XU = 0.0


def pose(t):
    p, grip, k, zh, en = state(t)
    q = ik(p)
    for i, (j, v) in enumerate(zip(J, q)):
        if i == 0:
            j.rotation_euler = (0, 0, v)
        elif i in (1, 2, 4):
            j.rotation_euler = (0, -v, 0)
        else:
            j.rotation_euler = (v, 0, 0)
    gap = 0.06 - 0.019 * grip                         # 夹爪半开口：0.06 开 → 0.041 夹住 8 cm 零件
    FING[0].location.y, FING[1].location.y = gap, -gap
    bpy.context.view_layer.update()
    tip = TIP.matrix_world.translation.copy()
    for o, at in zip(PART, parts(t, tip)):
        o.location = at if at is not None else Vector((0, 0, -5))
        o.rotation_euler = (0, 0, 0)
    for s in STRIPES:                                 # 皮带纹路往前走
        x0 = -0.25 + STRIPES.index(s) * 0.15
        s.location.x = -0.28 + ((x0 + 0.28 + BELT_V * t) % 1.86)
    xr = STEPS[k][2] == "xray"
    xu = smooth((t - 21) / 1.5) - smooth((t - 29.5) / 1.5) if xr else 0
    sc.display.shading.show_xray = xu > 0.05            # 透视：外壳变半透明（电机、减速器另画一层叠在上面，见 render_frame）
    sc.display.shading.xray_alpha = 1 - 0.7 * xu
    for o in MOTORS:
        o.hide_render = True
    global XU
    XU = xu
    camera(t)
    return q, grip, k, zh, en, xu > 0.5


# ------------------------------------------------------------------ 叠字：标题、步骤、关节角面板
def font(path, size):
    return ImageFont.truetype(path, int(size * H / 1080))


def hud(img, t, q, grip, k, zh, en, xray):
    d = ImageDraw.Draw(img, "RGBA")
    s = H / 1080
    d.rectangle([0, 0, W, 160 * s], fill=(251, 250, 247, 225))
    d.text((60 * s, 40 * s), zh, font=font(FONT_B, 54), fill=(29, 35, 41))
    d.text((62 * s, 112 * s), en, font=font(FONT_R, 30), fill=(95, 107, 118))
    x0, y0, w = W - 470 * s, 210 * s, 410 * s
    d.rounded_rectangle([x0 - 24 * s, y0 - 70 * s, x0 + w + 10 * s, y0 + 6 * 74 * s + 40 * s], 18 * s, fill=(255, 255, 255, 215),
                        outline=(200, 205, 210))
    d.text((x0, y0 - 56 * s), "关节角  Joint angles", font=font(FONT_B, 30), fill=(29, 35, 41))
    names = ["J1 底座 base", "J2 肩 shoulder", "J3 肘 elbow", "J4 小臂 forearm", "J5 手腕 wrist", "J6 法兰 flange"]
    for i, (n, v) in enumerate(zip(names, q)):
        y = y0 + i * 74 * s
        deg = math.degrees(v)
        d.text((x0, y), n, font=font(FONT_R, 24), fill=(60, 68, 76))
        d.text((x0 + w - 6 * s, y), f"{deg:+6.1f}°", font=font(FONT_B, 26), fill=(33, 112, 158), anchor="ra")
        bx, by, bw = x0, y + 38 * s, w - 10 * s
        d.rounded_rectangle([bx, by, bx + bw, by + 12 * s], 6 * s, fill=(225, 228, 232))
        mid = bx + bw / 2
        end = mid + bw / 2 * max(-1, min(1, deg / 180))
        d.rounded_rectangle([min(mid, end), by, max(mid, end), by + 12 * s], 6 * s, fill=(33, 112, 158))
        d.line([mid, by - 3 * s, mid, by + 15 * s], fill=(120, 128, 136), width=max(1, int(2 * s)))
    y = y0 + 6 * 74 * s
    d.text((x0, y), f"夹爪 gripper：{'夹紧 closed' if grip > 0.5 else '张开 open'}", font=font(FONT_R, 24), fill=(60, 68, 76))
    if xray:
        for lab, c in (("伺服电机 servo motor", (217, 56, 46)), ("减速器 reducer", (242, 191, 51))):
            y += 40 * s
            d.rectangle([x0, y + 8 * s, x0 + 22 * s, y + 30 * s], fill=c)
            d.text((x0 + 34 * s, y), lab, font=font(FONT_R, 24), fill=(60, 68, 76))
    d.text((W - 60 * s, H - 50 * s), "问渠 WenQuest · 三维仿真", font=font(FONT_R, 22), fill=(140, 146, 152), anchor="rs")
    return img


# ------------------------------------------------------------------ 出片
out = HERE / "_frames"
out.mkdir(exist_ok=True)
SHARD = [int(x) for x in sys.argv[sys.argv.index("--shard") + 1].split("/")] if "--shard" in sys.argv else None
ENCODE = "--encode" in sys.argv
NF = int(TOTAL * FPS)
if STILLS:
    jobs = list(enumerate(STILLS))
elif ENCODE:
    jobs = []
else:
    lo, hi = (SHARD[0] * NF // SHARD[1], (SHARD[0] + 1) * NF // SHARD[1]) if SHARD else (0, NF)
    jobs = [(i, i / FPS) for i in range(lo, hi)]
times = [t for _, t in jobs]
for n, t in jobs:
    q, grip, k, zh, en, xray = pose(t)
    f = out / (f"still_{t:05.1f}.png" if STILLS else f"f{n:05d}.png")
    sc.render.filepath = str(f)
    bpy.ops.render.render(write_still=True)
    img = Image.open(f).convert("RGBA")
    if XU > 0.05:                                     # 第二层：只画电机和减速器（透明底），按透视程度叠上去
        others = [o for o in sc.objects if o.type == "MESH" and o not in MOTORS]
        for o in others:
            o.hide_render = True
        for o in MOTORS:
            o.hide_render = False
        sc.display.shading.show_xray, sc.render.film_transparent = False, True
        tmp = out / f"_motors_{SHARD[0] if SHARD else 0}.png"
        sc.render.filepath = str(tmp)
        bpy.ops.render.render(write_still=True)
        top = Image.open(tmp).convert("RGBA")
        top.putalpha(top.getchannel("A").point(lambda v: int(v * min(1.0, XU))))
        img = Image.alpha_composite(img, top)
        for o in others:
            o.hide_render = False
        sc.render.film_transparent = False
    hud(img.convert("RGB"), t, q, grip, k, zh, en, xray).save(f)
    if n % 50 == 0:
        print(f"{n}/{NF}", flush=True)
if not STILLS and not SHARD:
    name = HERE / ("机械臂抓取_小样" if DRAFT else "机械臂抓取")
    pat = str(out / "f%05d.png")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", pat, "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    "-crf", "18", str(name) + ".mp4"], check=True)
    if not DRAFT:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", pat, "-c:v", "libvpx-vp9", "-b:v", "0",
                        "-crf", "30", "-row-mt", "1", "-cpu-used", "4", str(name) + ".webm"], check=True)
    print("→", name)
