"""写实电影风格（第 37 轮“震撼版”，Eddie 2026-10-17 10:50：“感觉一点都不震撼，没吸引力”）：
Cycles 真实光照（金属反光、深色背景、轮廓光、浅景深），快速运动用多次采样叠加做运动模糊，叠字改成电影式（大字、数字弹出、闪白、中英字幕）。
场景文件写 style: cinematic 即启用；其余字段（模型、运动、镜头）与工程图风格相同。"""
import math

import bpy
from mathutils import Vector
from PIL import Image, ImageDraw, ImageFont

import os
FONT_B = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
if not os.path.exists(FONT_B):                  # 构建机上的字体包只有 Regular、Bold
    FONT_B = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_M = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_R = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"

# 颜色名 → 写实材质：(底色, 金属度, 粗糙度, 清漆, 自发光强度)
PBR = {
    "shell": ((0.035, 0.055, 0.075), 0.15, 0.30, 1.0, 0), "body": ((0.035, 0.055, 0.075), 0.15, 0.30, 1.0, 0),
    "steel": ((0.78, 0.80, 0.83), 1.0, 0.22, 0, 0), "chrome": ((0.96, 0.97, 0.98), 1.0, 0.05, 0, 0),
    "needle": ((0.96, 0.97, 0.98), 1.0, 0.05, 0, 0), "takeup": ((0.96, 0.97, 0.98), 1.0, 0.07, 0, 0),
    "hook": ((1.0, 0.74, 0.32), 1.0, 0.12, 0, 0), "gear": ((0.90, 0.68, 0.36), 1.0, 0.25, 0, 0),
    "feed": ((0.30, 0.32, 0.35), 1.0, 0.35, 0, 0), "dark": ((0.10, 0.11, 0.12), 0.6, 0.45, 0, 0),
    "wood": ((0.06, 0.04, 0.03), 0.0, 0.55, 0.3, 0), "thread": ((0.25, 0.60, 1.0), 0.0, 0.4, 0, 1.2),
    "bobbin": ((1.0, 0.45, 0.12), 0.0, 0.4, 0, 1.2), "joint": ((0.08, 0.09, 0.10), 0.5, 0.35, 0, 0),
    "accent": ((0.10, 0.45, 0.70), 0.3, 0.3, 1.0, 0), "part": ((1.0, 0.55, 0.12), 0.0, 0.4, 0, 0),
    "motor": ((0.85, 0.18, 0.12), 0.2, 0.35, 0.5, 0), "frame": ((0.40, 0.42, 0.45), 1.0, 0.35, 0, 0),
    "table": ((0.25, 0.22, 0.20), 0.0, 0.6, 0, 0), "belt": ((0.05, 0.05, 0.05), 0.0, 0.7, 0, 0),
}


def setup(sc, spec, mats, quick=False):
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = 12 if quick else int(spec.get("samples", 48))
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces, sc.cycles.glossy_bounces, sc.cycles.transparent_max_bounces = 6, 4, 4
    sc.cycles.use_adaptive_sampling = True
    sc.render.use_persistent_data = True          # 逐帧只动零件位置：场景数据留在内存里，不必每帧重建
    sc.cycles.denoising_prefilter = "FAST"
    sc.view_settings.view_transform = "AgX" if "AgX" in [i.identifier for i in sc.view_settings.bl_rna.properties["view_transform"].enum_items] else "Filmic"
    sc.view_settings.look = "None"
    sc.render.film_transparent = False
    w = sc.world
    w.use_nodes = True
    bg = w.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (*spec.get("background", (0.006, 0.008, 0.013)), 1)
    bg.inputs[1].default_value = 1.0
    for name, m in mats.items():
        c, metal, rough, coat, emit = PBR.get(name, ((0.6, 0.6, 0.6), 0, 0.5, 0, 0))
        m.use_nodes = True
        p = m.node_tree.nodes.get("Principled BSDF")
        p.inputs["Base Color"].default_value = (*c, 1)
        p.inputs["Metallic"].default_value = metal
        p.inputs["Roughness"].default_value = rough
        if "Coat Weight" in p.inputs:
            p.inputs["Coat Weight"].default_value = coat
        if emit:
            p.inputs["Emission Color"].default_value = (*c, 1)
            p.inputs["Emission Strength"].default_value = emit
    st = spec.get("stage", {"center": (0, 0, 0), "size": 1.0})
    c, s = Vector(st["center"]), st["size"]
    for name, off, energy, color, size in (("key", (-1.2, -1.6, 1.8), 900, (1.0, 0.95, 0.88), 0.9),
                                           ("rim", (1.4, 1.6, 1.0), 1200, (0.45, 0.65, 1.0), 0.6),
                                           ("top", (0.2, -0.2, 2.4), 400, (1.0, 1.0, 1.0), 1.5),
                                           ("kick", (-1.8, 1.0, 0.3), 500, (1.0, 0.75, 0.45), 0.4)):
        L = bpy.data.lights.new(name, "AREA")
        L.energy, L.color, L.size = energy * s * s * spec.get("light_gain", 0.25), color, size * s
        o = bpy.data.objects.new(name, L)
        o.location = c + Vector(off) * s
        o.rotation_euler = (c - o.location).to_track_quat("-Z", "Y").to_euler()
        sc.collection.objects.link(o)


def dof(cam, look, fstop):
    cam.data.dof.use_dof = True
    cam.data.dof.focus_distance = (look - cam.location).length
    cam.data.dof.aperture_fstop = fstop


def font(path, size, H):
    return ImageFont.truetype(path, max(8, int(size * H / 1080)))


def ease(u):
    u = max(0.0, min(1.0, u))
    return u * u * (3 - 2 * u)


def hud(img, t, spec, W, H):
    """电影式叠字：字幕（配音的中英文）、中央大字、数字弹出、闪白、片尾标识。"""
    s = H / 1080
    base = img.convert("RGBA")
    lay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for y in range(int(H * 0.72), H, 2):            # 底部渐暗，字幕压得住亮背景
        d.rectangle([0, y, W, y + 2], fill=(0, 0, 0, int(150 * max(0.0, (y - H * 0.72) / (H * 0.28)) ** 1.5)))
    for e in spec.get("effects", []):
        a, b = e["t"]
        if e["kind"] == "flash" and a <= t < b:
            k = 1 - (t - a) / (b - a)
            d.rectangle([0, 0, W, H], fill=(255, 255, 255, int(255 * k * k)))
    for v in spec.get("voice", []):
        a, b = v["t"], v["t"] + v.get("dur", 3.0)
        if a <= t < b:
            al = int(255 * min(ease((t - a) / 0.25), ease((b - t) / 0.25)))
            y = H - 150 * s
            d.text((W / 2 + 2 * s, y + 2 * s), v["zh"], font=font(FONT_M, 46, H), fill=(0, 0, 0, al // 2), anchor="ma")
            d.text((W / 2, y), v["zh"], font=font(FONT_M, 46, H), fill=(255, 255, 255, al), anchor="ma")
            d.text((W / 2, y + 66 * s), v["en"], font=font(FONT_R, 28, H), fill=(200, 210, 222, al), anchor="ma")
    for p in spec.get("pops", []):
        a, b = p["t"]
        if a <= t < b:
            u = (t - a) / 0.35
            k = 1 + 0.25 * math.sin(math.pi * min(1, u)) - (1 - min(1, u)) ** 2 * 0.6
            al = int(255 * min(1, ease(u * 2), ease((b - t) / 0.3)))
            size = p.get("size", 120) * max(0.3, k)
            x, y = W * p.get("x", 0.5), H * p.get("y", 0.4)
            col = tuple(p.get("color", (255, 196, 64)))
            d.text((x, y), p["text"], font=font(FONT_B, size, H), fill=(*col, al), anchor="mm")
            if p.get("sub"):
                d.text((x, y + size * 0.75 * s), p["sub"], font=font(FONT_M, 34, H), fill=(230, 235, 240, al), anchor="ma")
    for p in spec.get("titles", []):
        a, b = p["t"]
        if a <= t < b:
            al = int(255 * min(ease((t - a) / 0.5), ease((b - t) / 0.4)))
            d.text((W / 2, H * p.get("y", 0.42)), p["zh"], font=font(FONT_B, p.get("size", 96), H), fill=(255, 255, 255, al), anchor="mm")
            if p.get("en"):
                d.text((W / 2, H * p.get("y", 0.42) + p.get("size", 96) * 0.85 * s), p["en"], font=font(FONT_R, 34, H),
                       fill=(190, 205, 220, al), anchor="mm")
    d.text((W - 40 * s, 40 * s), "问渠 WenQuest", font=font(FONT_M, 24, H), fill=(255, 255, 255, 110), anchor="ra")
    return Image.alpha_composite(base, lay).convert("RGB")
