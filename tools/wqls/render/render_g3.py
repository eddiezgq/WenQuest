"""第 138 轮 G3：用 Blender（bpy，Cycles）把 FreeCAD 导出的 WQ-LS 外观网格渲染成效果图。

    python3 tools/wqls/render/render_g3.py <网格目录> <输出.png> [视角 front|rear|top] [采样数]

网格目录里是 housing.py 按材料分组导出的 STL（paint、graphite、metal、chrome、black、blue、glass）。
机头装在工作台的开孔里，机座顶面与台面平齐（工业平缝机的装法）。
"""
from __future__ import annotations

import math
import os
import sys

import bpy

src, out = sys.argv[1], sys.argv[2]
view = sys.argv[3] if len(sys.argv) > 3 else "front"
samples = int(sys.argv[4]) if len(sys.argv) > 4 else 96
VARIANT = os.path.basename(os.path.normpath(src))

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.unit_settings.system = "METRIC"


def mat(name, color, rough, metal=0.0, coat=0.0, emit=None, emit_s=0.0, transm=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    for k in ("Coat Weight", "Clearcoat"):
        if k in b.inputs:
            b.inputs[k].default_value = coat
            break
    if "Coat Roughness" in b.inputs:
        b.inputs["Coat Roughness"].default_value = 0.06
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1)
        b.inputs["Emission Strength"].default_value = emit_s
    if transm and "Transmission Weight" in b.inputs:
        b.inputs["Transmission Weight"].default_value = transm
    return m


PAINT = {"A": (0.90, 0.90, 0.88), "B": (0.92, 0.92, 0.90), "C": (0.86, 0.87, 0.86)}.get(VARIANT, (0.9, 0.9, 0.88))
MATS = {
    "paint": mat("paint", PAINT, 0.32, coat=0.7),
    "graphite": mat("graphite", (0.06, 0.065, 0.075), 0.42, coat=0.4),
    "metal": mat("metal", (0.72, 0.73, 0.74), 0.32, metal=1.0),
    "chrome": mat("chrome", (0.86, 0.87, 0.88), 0.08, metal=1.0),
    "black": mat("black", (0.018, 0.018, 0.02), 0.55),
    "blue": mat("blue", (0.03, 0.22, 0.62), 0.35, coat=0.5),
    "glass": mat("glass", (0.02, 0.05, 0.06), 0.1, emit=(0.55, 0.85, 1.0), emit_s=1.2),
}

for name, m in MATS.items():
    p = os.path.join(src, f"{name}.stl")
    if not os.path.exists(p):
        continue
    bpy.ops.wm.stl_import(filepath=p, global_scale=0.001)
    ob = bpy.context.selected_objects[0]
    ob.name = name
    ob.data.materials.append(m)
    for poly in ob.data.polygons:
        poly.use_smooth = True
    md = ob.modifiers.new("split", "EDGE_SPLIT")
    md.split_angle = math.radians(32)

# 工作台：台面与机座顶面平齐，开孔比机座大 3 mm
bpy.ops.mesh.primitive_cube_add(size=1, location=(0.15, 0.05, -0.016))
tab = bpy.context.active_object
tab.scale = (1.25, 0.62, 0.032)
bpy.ops.mesh.primitive_cube_add(size=1, location=((-0.105 + 0.412) / 2, (-0.062 + 0.116) / 2, -0.02))
hole = bpy.context.active_object
hole.scale = (0.517 + 0.006, 0.178 + 0.006, 0.06)
bo = tab.modifiers.new("hole", "BOOLEAN")
bo.object = hole
bo.operation = "DIFFERENCE"
bpy.context.view_layer.objects.active = tab
bpy.ops.object.modifier_apply(modifier="hole")
bpy.data.objects.remove(hole)
bev = tab.modifiers.new("bev", "BEVEL")
bev.width = 0.003
bev.segments = 3
tab.data.materials.append(mat("table", (0.80, 0.79, 0.76), 0.55))
# 地面（远处的影子接收）
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, -0.78))
bpy.context.active_object.data.materials.append(mat("floor", (0.55, 0.56, 0.58), 0.8))

# 世界与灯光：柔光棚
w = bpy.data.worlds.new("w")
sc.world = w
w.use_nodes = True
bg = w.node_tree.nodes["Background"]
bg.inputs["Color"].default_value = (0.86, 0.88, 0.90, 1)
bg.inputs["Strength"].default_value = 0.55


def area(name, loc, rot, size, power, color=(1, 1, 1)):
    bpy.ops.object.light_add(type="AREA", location=loc, rotation=rot)
    L = bpy.context.active_object
    L.name = name
    L.data.size = size
    L.data.energy = power
    L.data.color = color
    return L


def look_at(obj, target):
    from mathutils import Vector
    d = Vector(target) - obj.location
    obj.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


k = area("key", (-0.9, -1.1, 1.1), (0, 0, 0), 1.4, 420)
look_at(k, (0.15, 0.0, 0.12))
f = area("fill", (1.3, -0.9, 0.45), (0, 0, 0), 1.8, 160, (0.95, 0.97, 1.0))
look_at(f, (0.15, 0.0, 0.12))
r = area("rim", (0.4, 1.3, 1.0), (0, 0, 0), 1.2, 300)
look_at(r, (0.15, 0.0, 0.15))
t = area("top", (0.15, 0.0, 1.6), (0, 0, 0), 1.6, 160)

# 相机
CAMS = {"front": ((-0.42, -0.98, 0.46), (0.16, 0.0, 0.11), 50),
        "rear": ((1.05, 0.95, 0.52), (0.15, 0.02, 0.12), 50),
        "face": ((-0.75, -0.38, 0.26), (0.0, 0.0, 0.12), 60),
        "side": ((0.15, -1.25, 0.16), (0.15, 0.0, 0.11), 55)}
loc, tgt, lens = CAMS[view]
bpy.ops.object.camera_add(location=loc)
cam = bpy.context.active_object
look_at(cam, tgt)
cam.data.lens = lens
cam.data.dof.use_dof = False
sc.camera = cam

sc.render.engine = "CYCLES"
sc.cycles.device = "CPU"
sc.cycles.samples = samples
sc.cycles.use_denoising = True
try:
    sc.cycles.denoiser = "OPENIMAGEDENOISE"
except Exception:  # noqa: BLE001
    pass
sc.render.resolution_x = int(os.environ.get("WQ_W", 1600))
sc.render.resolution_y = int(os.environ.get("WQ_H", 1000))
sc.render.film_transparent = False
sc.view_settings.view_transform = "AgX" if "AgX" in [i.identifier for i in sc.view_settings.bl_rna.properties["view_transform"].enum_items] else "Filmic"
sc.view_settings.look = "None"
sc.render.image_settings.file_format = "PNG"
sc.render.filepath = out
bpy.ops.render.render(write_still=True)
print("rendered", out)
