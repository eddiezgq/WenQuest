"""白板讲解《未来工厂》（2026-10-17）：三张立体（等轴测）画板——全景、机器视觉自动质检、数据中枢闭环。
设想场景，不是某家真实工厂；片中没有具体性能数字。中文配音（Kokoro 云健），中英字幕，无手。
    python3 make.py <kokoro 模型目录> | --fake | --boards-only   然后  WB_CRF=17 python3 ../../../tools/whiteboard/wb.py . --mp4"""
import math
import sys
from pathlib import Path

here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent / "每日科普"))
sys.path.insert(0, str(here.parent))
from fastkit import O, P, R, T, check, cross, main, pop, pulse, sh, spin, uid, wig  # noqa: E402
from popkit import stick  # noqa: E402

S = [
 # 画板 1：全景
 ("这是一座未来工厂。订单一进来，整座工厂就自己动起来。", "This is a factory of the future. An order comes in, and the whole plant starts moving on its own."),
 ("原料从立体仓库出库，每一箱都扫条码、扫二维码，无人车一路送到产线。", "Materials leave the automated warehouse, every tote scanned by barcode and QR code, and driverless carts carry them to the line."),
 ("机械臂接手：上料、拧紧、装配，一台接一台。", "Robot arms take over: loading, fastening, assembling, one after another."),
 ("每一件产品都要经过机器视觉质检站：拍照、测量、判定，一眨眼完成。", "Every product passes a machine-vision station: image, measure, decide, in the blink of an eye."),
 ("不合格的，自动推出产线；合格的，自动生成 FDA 要求的 UDI 标签：二维码加人能读的文字，贴上、扫码复核、发货。", "Rejects are pushed off the line; good parts get an automatically generated FDA UDI label, a 2D code plus human-readable text, then a verifying scan, and they ship."),
 ("所有设备的数据，都实时汇到同一个数据中枢。", "Data from every machine flows, live, into one data hub."),
 # 画板 2：机器视觉自动质检
 ("放大看质检站。相机在上，环形灯打光，零件从下面流过。", "Zoom in on the inspection station. Camera above, ring light on, parts flowing underneath."),
 ("系统先读零件上的二维码，知道它是哪一批；再把图像变成尺寸：孔径、孔距、划痕，一项项和图纸公差比。", "It first reads the 2D code on the part to know its lot, then turns the image into dimensions: hole size, spacing, scratches, each checked against the drawing."),
 ("全部合格，亮绿灯放行；有一项超差，推杆把它推进隔离箱。", "All in tolerance: green light, pass. One out: a pusher sends it into the quarantine bin."),
 ("每个测量值都画进控制图。趋势一偏，还没出废品，就先报警。", "Every reading goes onto a control chart. When the trend drifts, it alarms before a single bad part."),
 ("AI 起草不合格报告，但怎么处置，要工程师点头才生效。", "AI drafts the nonconformance report, but the disposition takes effect only when an engineer approves."),
 # 画板 3：数据中枢闭环
 ("最后看中枢：订单、库存、设备、质量，连成一张数据网。", "Finally, the hub: orders, inventory, machines and quality, in one connected web of data."),
 ("数字孪生把整座工厂实时画在屏幕上，哪里慢、哪里堵，一眼看到。", "A digital twin draws the whole plant live on screen: where it's slow, where it's jammed, at a glance."),
 ("发现问题，AI 给出建议：换刀、降速、补料。", "When something's off, AI suggests a fix: change the tool, slow down, restock."),
 ("人在关键处确认，机器人执行，结果再回到中枢，形成闭环。", "A person approves at the key step, robots carry it out, and the results flow back to the hub. A closed loop."),
 ("全集成，全自动。人从搬运和盯守里解放出来，专心做判断。", "Fully integrated, fully automated. People are freed from hauling and watching, to focus on judgment."),
]
TITLE = {"zh": "未来工厂：全集成、全自动", "en": "The future factory: fully integrated, fully automated"}
SAY = {"AI": "A I", "FDA": "F D A", "UDI": "U D I"}

C30, S30 = math.cos(math.pi / 6), 0.5
GRID, SHADE, BELT = "#b8c2cc", "#8a96a3", "#1f6f9f"


class Iso:
    """Isometric projection: X runs to the lower right, Y to the lower left, Z up. o = screen point of (0, 0, 0)."""

    def __init__(self, ox, oy, s):
        self.ox, self.oy, self.s = ox, oy, s

    def __call__(self, X, Y, Z=0.0):
        return (round(self.ox + (X - Y) * C30 * self.s, 1), round(self.oy + (X + Y) * S30 * self.s - Z * self.s, 1))

    def d(self, pts, close=True):
        q = [self(*p) for p in pts]
        return "M" + " L".join(f"{x},{y}" for x, y in q) + (" Z" if close else "")


def box(at, iso, X, Y, Z, dx, dy, dz, c="ink", w=4, idp=None, shade=True, top=None):
    """An isometric block: top, front-right and front-left faces; the right face hatched."""
    i = idp or uid("bx")
    E = [P(at, iso.d([(X, Y, Z + dz), (X + dx, Y, Z + dz), (X + dx, Y + dy, Z + dz), (X, Y + dy, Z + dz)]), c=top or c, w=w, idp=i),
         P(at, iso.d([(X + dx, Y, Z), (X + dx, Y + dy, Z), (X + dx, Y + dy, Z + dz), (X + dx, Y, Z + dz)]), c=c, w=w, idp=i),
         P(at, iso.d([(X, Y + dy, Z), (X + dx, Y + dy, Z), (X + dx, Y + dy, Z + dz), (X, Y + dy, Z + dz)]), c=c, w=w, idp=i)]
    if shade:
        n = max(2, int(dy * 3))
        hat = " ".join(iso.d([(X + dx, Y + dy * k / n, Z + dz * 0.12), (X + dx, Y + dy * k / n, Z + dz * 0.88)], close=False) for k in range(1, n))
        E.append(P(at, hat, c=SHADE, w=1.8, idp=i))
    return E, i


def ell(iso, X, Y, Z, r, n=28):
    """A horizontal circle (an ellipse on screen) as a path."""
    return iso.d([(X + r * math.cos(2 * math.pi * k / n), Y + r * math.sin(2 * math.pi * k / n), Z) for k in range(n)])


def cyl(at, iso, X, Y, Z, r, h, c="ink", w=4, idp=None):
    i = idp or uid("cy")
    a, b = iso(X - r * C30, Y + r * S30, Z), iso(X + r * C30, Y - r * S30, Z)   # the silhouette sides (screen left/right)
    a2, b2 = iso(X - r * C30, Y + r * S30, Z + h), iso(X + r * C30, Y - r * S30, Z + h)
    return [P(at, ell(iso, X, Y, Z + h, r), c=c, w=w, idp=i), P(at, ell(iso, X, Y, Z, r), c=c, w=w, idp=i),
            P(at, f"M{a[0]},{a[1]} L{a2[0]},{a2[1]} M{b[0]},{b[1]} L{b2[0]},{b2[1]}", c=c, w=w, idp=i)], i


def arm(at, iso, X, Y, k=1.0, c="ink", hz=0.6, amp=16, phase_id=None):
    """A six-axis robot arm on a round base: upper arm and forearm swing (the forearm about the elbow, then both about the shoulder)."""
    base, ib = cyl(at, iso, X, Y, 0, 0.7 * k, 0.45 * k, c=c, w=4.5)
    sx, sy = iso(X, Y, 0.45 * k + 0.25 * k)
    ex, ey = sx + 70 * k * iso.s / 50, sy - 120 * k * iso.s / 50
    hx, hy = ex + 95 * k * iso.s / 50, ey + 40 * k * iso.s / 50
    up, fo = uid("armu"), None
    fo = up + "f"
    j = max(9, 12 * k * iso.s / 50)
    E = base + [O(at, sx, sy, j, c=c, fill="gold", idp=up),
                P(at, f"M{sx - 10},{sy} L{ex - 9},{ey} M{sx + 10},{sy} L{ex + 9},{ey}", c=c, w=5, idp=up),
                O(at, ex, ey, j * 0.9, c=c, fill="gold", idp=fo),
                P(at, f"M{ex},{ey - 8} L{hx},{hy - 6} M{ex},{ey + 8} L{hx},{hy + 6}", c=c, w=5, idp=fo),
                P(at, f"M{hx},{hy} L{hx + 6},{hy + 24} M{hx + 6},{hy + 24} L{hx - 6},{hy + 38} M{hx + 6},{hy + 24} L{hx + 18},{hy + 38}", c="red", w=4, idp=fo)]
    E += [wig(at, fo, (ex, ey), amp * 1.3, hz * 1.4), wig(at, up + "*", (sx, sy), amp, hz)]   # elbow first, then shoulder
    return E, (hx, hy + 38)


def label(at, x, y, zh, en=None, c="ink", s=40, d=None, lead=None, align="center"):
    E = T(at, x, y, s, zh, c=c, d=d, align=align)
    if en:
        E += T(at, x, y + s * 0.95, int(s * 0.7), en, c="muted", d=d, align=align)
    if lead:
        E.append(P(at, f"M{lead[0][0]},{lead[0][1]} L{lead[1][0]},{lead[1][1]}", c="muted", w=2.4))
    return E


def qr(at, x, y, size, c="ink", idp=None, seed=7):
    """A drawn 2D code (decorative, not a real encoded symbol): frame, three finder squares, modules."""
    i = idp or uid("qr")
    m = size / 21
    E = [R(at, x, y, size, size, c=c, idp=i, sw=3)]
    for fx, fy in ((0, 0), (14, 0), (0, 14)):
        E += [R(at, x + fx * m + m * 0.5, y + fy * m + m * 0.5, 6 * m, 6 * m, c=c, idp=i, sw=3),
              R(at, x + fx * m + 2 * m, y + fy * m + 2 * m, 3 * m, 3 * m, c=c, fill=c, idp=i, sw=2)]
    d, r = [], seed
    for gy in range(21):
        for gx in range(21):
            if (gx < 8 and gy < 8) or (gx > 12 and gy < 8) or (gx < 8 and gy > 12):
                continue
            r = (r * 1103515245 + 12345) % 2147483648
            if r % 5 < 2:
                d.append(f"M{x + gx * m + m * 0.2:.1f},{y + gy * m + m / 2:.1f} L{x + gx * m + m * 0.8:.1f},{y + gy * m + m / 2:.1f}")
    E.append(P(at, " ".join(d), c=c, w=m * 0.75, idp=i))
    return E, i


def barcode(at, x, y, w, h, c="ink", idp=None):
    i = idp or uid("bc")
    widths, d, cx = (3, 1, 2, 1, 3, 2, 1, 1, 3, 1, 2, 2, 1, 3, 1, 2, 1, 3, 2, 1), [], x
    for k, wd in enumerate(widths):
        if k % 2 == 0:
            d.append(f"M{cx + wd * w / 80:.1f},{y} L{cx + wd * w / 80:.1f},{y + h}")
        cx += wd * w / 40
    return [P(at, " ".join(d), c=c, w=w / 30, idp=i)], i


def signal(at, ids, speed=260):
    return {"t": "move", "at": at, "kind": "signal", "targets": ids if isinstance(ids, list) else [ids], "speed": speed}


def flow(at, ids, speed=70):
    return {"t": "move", "at": at, "kind": "flow", "targets": ids if isinstance(ids, list) else [ids], "speed": speed}


def title(at, zh, en):
    return T(at, 110, 112, 60, zh, c="ink", align="left") + T(at, 114, 164, 38, en, c="muted", align="left")


B = []

# ============================================================== 画板 1：全景（等轴测）
iso = Iso(860, 300, 44)
E = title(0, "未来工厂 · 全景", "The future factory, at a glance")
# floor and grid
E.append(P(0, iso.d([(0, 0), (22, 0), (22, 13), (0, 13)]), c="ink", w=4.5))
E.append(P(0, " ".join(iso.d([(x, 0), (x, 13)], close=False) for x in range(2, 22, 2)) + " " +
           " ".join(iso.d([(0, y), (22, y)], close=False) for y in range(2, 13, 2)), c=GRID, w=1.6))
# back walls (glass curtain: just posts and a top rail)
E.append(P(0, iso.d([(0, 13, 0), (0, 13, 4.2), (0, 0, 4.2), (22, 0, 4.2), (22, 0, 0)], close=False), c="muted", w=3))
E.append(P(0, " ".join(iso.d([(0, y, 0), (0, y, 4.2)], close=False) for y in (4, 8)) + " " +
           " ".join(iso.d([(x, 0, 0), (x, 0, 4.2)], close=False) for x in (6, 12, 18)), c=GRID, w=2))
for k, (x, y) in enumerate(((5, 0), (11, 0), (17, 0))):     # skylight lamps on the back wall
    lid = uid("lamp")
    E += [P(0, iso.d([(x, y, 3.6), (x + 1.4, y, 3.6)], close=False), c="gold", w=7, idp=lid), pulse(0, lid, 0.3 + 0.3 * k)]
# 1 automated storage and retrieval: rack along the left wall + a stacker crane
rk, rid = box(1, iso, 0.4, 1.0, 0, 1.6, 8.0, 3.6, c="ink", w=4)
E += rk
E.append(P(1, " ".join(iso.d([(2.0, 1.0, z), (2.0, 9.0, z)], close=False) for z in (0.9, 1.8, 2.7)) + " " +
           " ".join(iso.d([(2.0, y, 0), (2.0, y, 3.6)], close=False) for y in (3, 5, 7)), c="ink", w=2.6, idp=rid))
for y in (1.5, 3.6, 5.5, 7.7):      # totes on the shelves
    for z in (0.15, 1.05, 1.95, 2.85):
        if (y * 10 + z * 7) % 3 < 2:
            E.append(P(1, iso.d([(2.0, y, z), (2.0, y + 1.0, z), (2.0, y + 1.0, z + 0.55), (2.0, y, z + 0.55)]), c="gold", w=2.6, idp=rid))
cr = uid("crane")
E += [P(1, iso.d([(2.5, 1.6, 3.9), (2.5, 8.8, 3.9)], close=False), c="blue", w=2.6),
      P(1, iso.d([(2.5, 2.0, 0), (2.5, 2.0, 3.9)], close=False), c="blue", w=5, idp=cr),
      P(1, iso.d([(2.3, 2.0, 1.6), (3.1, 2.0, 1.6), (3.1, 2.8, 1.6), (2.3, 2.8, 1.6)]), c="blue", w=4, idp=cr),
      sh(1, cr, -C30 * 44 * 5, S30 * 44 * 5, 0.4, 3.5)]
E += label(1, 320, 330, "立体仓库", "Automated warehouse", c="blue", s=40, d=0.2, lead=None)
# AGVs carrying totes from the warehouse to the line
for k, (x0, y0) in enumerate(((3.4, 8.6), (3.4, 10.4))):
    av, ai = box(1, iso, x0, y0, 0.08, 1.6, 1.0, 0.35, c="green", w=4)
    tote, _ = box(1, iso, x0 + 0.3, y0 + 0.15, 0.43, 0.9, 0.7, 0.45, c="gold", w=3, idp=ai, shade=False)
    E += av + tote + [O(1, *iso(x0 + 0.35, y0 + 1.0, 0.08), 6, c="ink", fill="ink", idp=ai), O(1, *iso(x0 + 1.25, y0 + 1.0, 0.08), 6, c="ink", fill="ink", idp=ai)]
    E.append(sh(1, ai + "*", C30 * 44 * (3.0 + 0.5 * k), S30 * 44 * (3.0 + 0.5 * k), 0.6 + 0.8 * k, 3.0))
gate = uid("gate")
E += [P(1, iso.d([(2.9, 8.3, 0), (2.9, 8.3, 1.6), (2.9, 11.6, 1.6), (2.9, 11.6, 0)], close=False), c="blue", w=4, idp=gate)]
beam = uid("beam")
E += [P(1, iso.d([(2.9, 9.0, 1.5), (2.9, 9.4, 0.7)], close=False) + " " + iso.d([(2.9, 10.6, 1.5), (2.9, 10.9, 0.7)], close=False), c="red", w=3, idp=beam),
      pulse(1, beam, 0.3), pulse(1, beam, 1.2), pulse(1, beam, 2.1)]
bc, bci = barcode(1, 120, 470, 120, 60)
q1, q1i = qr(1, 260, 465, 70, seed=3)
E += bc + q1 + [pop(1, bci, 0.6), pop(1, q1i, 0.9)]
E += T(1, 230, 580, 32, "扫码出入库 Scan in / out", c="blue", d=0.9)
path_agv = uid("route")
E += [P(1, iso.d([(3.2, 9.1), (9.4, 9.1), (9.4, 7.4)], close=False), c="green", w=3, idp=path_agv), flow(1, path_agv, 40)]
E += label(1, 300, 930, "无人车", "Driverless carts (AGV)", c="green", s=38, d=0.5)
# 2 the main conveyor along X (Y 6–7.2), belt line carries the parts (signal dots)
cv, cid = box(2, iso, 4.0, 6.0, 0, 16.5, 1.2, 0.75, c="ink", w=4)
E += cv
belt = uid("belt")
E += [P(2, iso.d([(4.2, 6.6, 0.76), (20.3, 6.6, 0.76)], close=False), c=BELT, w=4, idp=belt), flow(2, belt, 60), signal(2, belt, 170)]
E.append(P(2, " ".join(iso.d([(x, 6.0, 0), (x, 6.0, 0.75)], close=False) for x in range(5, 20, 2)), c=GRID, w=2))
# robot arms behind the belt
for k, X in enumerate((7.0, 9.6)):
    a_, tip = arm(2, iso, X, 4.6, k=1.0, hz=0.55 + 0.15 * k, amp=14)
    E += a_
for k, X in enumerate((8.3,)):   # one in front of the belt, facing it
    a_, tip = arm(2, iso, X, 8.6, k=0.9, hz=0.7, amp=12)
    E += a_
E += label(2, 980, 330, "机械臂", "Robot arms", c="ink", s=40, d=0.3, lead=((960, 380), iso(7.6, 4.6, 2.6)))
# 3 machine-vision station: a gantry over the belt, camera, scan cone
gx = 13.2
g = uid("gantry")
E += [P(3, iso.d([(gx, 5.3, 0), (gx, 5.3, 2.6), (gx, 7.9, 2.6), (gx, 7.9, 0)], close=False), c="ink", w=5, idp=g),
      P(3, iso.d([(gx + 0.8, 5.3, 0), (gx + 0.8, 5.3, 2.6), (gx + 0.8, 7.9, 2.6), (gx + 0.8, 7.9, 0)], close=False), c="ink", w=5, idp=g),
      P(3, iso.d([(gx, 5.3, 2.6), (gx + 0.8, 5.3, 2.6)], close=False) + " " + iso.d([(gx, 7.9, 2.6), (gx + 0.8, 7.9, 2.6)], close=False), c="ink", w=5, idp=g)]
cam, camid = box(3, iso, gx + 0.1, 6.25, 1.95, 0.6, 0.7, 0.55, c="blue", w=4, shade=False)
E += cam
cone = uid("cone")
E += [P(3, iso.d([(gx + 0.4, 6.6, 1.95), (gx - 0.4, 6.0, 0.78), (gx + 1.2, 6.0, 0.78), (gx + 0.4, 6.6, 1.95), (gx + 1.2, 7.2, 0.78),
                  (gx - 0.4, 7.2, 0.78), (gx + 0.4, 6.6, 1.95)], close=False), c="#4fb3e8", w=3, idp=cone),
      flow(3, cone, 90), pulse(3, camid, 0.4)]
E += [{"t": "move", "at": a, "kind": "pulse", "targets": [cone], "delay": 0.2 + 0.9 * a % 3, "dur": 0.5} for a in (3,)]
eye = uid("eye")
E += [{"t": "icon", "at": 3, "id": eye, "name": "eye", "x": 1450, "y": 300, "size": 90, "c": "blue"}, pop(3, eye, 0.2)]
E += label(3, 1450, 400, "机器视觉质检", "Machine-vision inspection", c="blue", s=42, d=0.4, lead=((1450, 450), iso(gx + 0.4, 6.0, 2.6)))
# 4 reject: pusher and quarantine bin in front of the belt; packing robot and outbound
bin_, bi = box(4, iso, gx + 1.3, 7.9, 0, 1.3, 1.1, 0.8, c="red", w=4)
E += bin_
rej = uid("rej")
E += [P(4, iso.d([(gx + 2.0, 6.2, 0.78), (gx + 2.6, 6.2, 0.78), (gx + 2.6, 6.8, 0.78), (gx + 2.0, 6.8, 0.78)]), c="red", w=4, idp=rej),
      sh(4, rej, -C30 * 44 * 1.6 - 10, S30 * 44 * 1.6 + 28, 0.3, 1.0)]
E += label(4, iso(gx + 1.3, 9.0)[0] - 10, iso(gx + 1.3, 9.0)[1] + 80, "隔离", "Quarantine", c="red", s=38, d=0.3)
pal, _ = box(4, iso, 18.9, 8.6, 0, 2.2, 2.2, 0.25, c="ink", w=3)
E += pal
for k, (dx, dy, dz) in enumerate(((0.1, 0.1, 0.25), (1.1, 0.1, 0.25), (0.1, 1.1, 0.25), (1.1, 1.1, 0.25), (0.1, 0.1, 1.05), (1.1, 0.1, 1.05))):
    pk, pki = box(4, iso, 18.9 + dx, 8.6 + dy, dz, 1.0, 1.0, 0.8, c="gold", w=3, shade=False)
    E += pk + [pop(4, pki, 0.5 + 0.25 * k)]
a_, _ = arm(4, iso, 18.0, 4.4, k=1.0, hz=0.8, amp=18)
E += a_
dock = uid("dock")
E += [P(4, iso.d([(22, 9.0, 0), (22, 9.0, 2.6), (22, 12.0, 2.6), (22, 12.0, 0)], close=False), c="ink", w=4),
      {"t": "arrow", "at": 4, "id": dock, "pts": [list(iso(20.5, 10.5)), list(iso(24.2, 10.5))], "c": "green", "w": 6}, pulse(4, dock, 0.6)]
E += label(4, 1700, 940, "打包 · 贴码 · 发货", "Pack, label, ship", c="green", s=38, d=0.8)
ux, uy = 1580, 100
udi = uid("udi")
E += [R(4, ux, uy, 330, 200, c="green", sw=4, idp=udi), pop(4, udi, 1.0)]
q2, q2i = qr(4, ux + 18, uy + 40, 120, seed=11)
E += q2 + [pop(4, q2i, 1.2)]
E += T(4, ux + 18, uy + 30, 24, "包装处 UDI 标签，自动生成", c="green", align="left", d=1.0)
for k, ln in enumerate(("(01) GTIN", "(17) 有效期 Exp.", "(10) 批号 Lot")):
    E += T(4, ux + 150, uy + 80 + 36 * k, 22, ln, c="ink", align="left", d=1.3 + 0.2 * k)
# 5 the data hub: a tower in the front corner; dashed data lines from every station, dots running in
hx, hy = 12.0, 12.2
hub, hid = box(5, iso, hx, hy - 1.0, 0, 1.6, 1.0, 3.0, c="red", w=5)
E += hub + [pulse(5, hid, 0.3)]
E.append(P(5, " ".join(iso.d([(hx + 1.6, hy - 1.0 + 0.15, z), (hx + 1.6, hy - 0.15, z)], close=False) for z in (0.6, 1.2, 1.8, 2.4)), c="red", w=3, idp=hid))
links = []
for src in ((2.0, 5.0, 3.6), (4.2, 9.2, 0.5), (7.0, 4.6, 1.2), (gx + 0.4, 6.6, 2.5), (gx + 2.2, 8.4, 0.8), (20.0, 9.7, 1.9)):
    li = uid("data")
    links.append(li)
    E.append(P(5, iso.d([src, (hx + 0.8, hy - 0.5, 3.0)], close=False), c="#e0882b", w=2.6, idp=li))
E += [flow(5, links, 80), signal(5, links, 300)]
E += label(5, iso(hx + 0.8, hy)[0], iso(hx + 0.8, hy)[1] + 90, "数据中枢", "Data hub", c="red", s=44, d=0.6)
B.append(E)

# ============================================================== 画板 2：机器视觉自动质检（放大）
iso = Iso(620, 330, 80)
a = 6
E = title(a, "机器视觉 · 自动质检", "Machine vision: automatic inspection")
cv, cid = box(a, iso, -1.0, 2.0, 0, 10.5, 1.6, 0.9, c="ink", w=5)
E += cv
belt = uid("belt")
E += [P(a, " ".join(iso.d([(x, 2.0, 0.91), (x, 3.6, 0.91)], close=False) for x in range(0, 10)), c=BELT, w=2.4, idp=belt), flow(a, belt, 50)]
for k, X in enumerate((-0.6, 1.5)):          # parts arriving: a block with two holes, sliding in
    pt, pid = box(a, iso, X, 2.35, 0.92, 1.3, 0.9, 0.45, c="ink", w=4, shade=True)
    E += pt + [P(a, ell(iso, X + 0.4, 2.8, 1.37, 0.18), c="ink", w=3, idp=pid), P(a, ell(iso, X + 0.95, 2.8, 1.37, 0.18), c="ink", w=3, idp=pid),
               sh(a, pid + "*", C30 * 80 * 0.7, S30 * 80 * 0.7, 0.5 + 0.6 * k, 2.4)]
# gantry, ring light, camera
gx = 4.4
g = uid("g")
E += [P(a, iso.d([(gx, 1.4, 0), (gx, 1.4, 3.6), (gx, 4.2, 3.6), (gx, 4.2, 0)], close=False), c="ink", w=6, idp=g),
      P(a, iso.d([(gx + 1.4, 1.4, 0), (gx + 1.4, 1.4, 3.6), (gx + 1.4, 4.2, 3.6), (gx + 1.4, 4.2, 0)], close=False), c="ink", w=6, idp=g),
      P(a, iso.d([(gx, 1.4, 3.6), (gx + 1.4, 1.4, 3.6)], close=False) + " " + iso.d([(gx, 4.2, 3.6), (gx + 1.4, 4.2, 3.6)], close=False), c="ink", w=6, idp=g)]
cam, camid = box(a, iso, gx + 0.35, 2.45, 2.75, 0.7, 0.7, 0.85, c="blue", w=5, shade=False)
E += cam + [P(a, ell(iso, gx + 0.7, 2.8, 2.75, 0.22), c="blue", w=4, idp=camid)]
ring = uid("ring")
E += [P(a, ell(iso, gx + 0.7, 2.8, 2.35, 0.55), c="gold", w=6, idp=ring), pulse(a, ring, 0.3)]
cone = uid("cone")
E += [P(a, iso.d([(gx + 0.7, 2.8, 2.3), (gx - 0.1, 2.2, 0.95), (gx + 1.5, 2.2, 0.95), (gx + 0.7, 2.8, 2.3), (gx + 1.5, 3.4, 0.95),
                  (gx - 0.1, 3.4, 0.95), (gx + 0.7, 2.8, 2.3)], close=False), c="#4fb3e8", w=3.4, idp=cone), flow(a, cone, 110)]
pt, pid = box(a, iso, gx + 0.05, 2.35, 0.92, 1.3, 0.9, 0.45, c="ink", w=4)   # the part being inspected
E += pt + [P(a, ell(iso, gx + 0.45, 2.8, 1.37, 0.18), c="ink", w=3, idp=pid), P(a, ell(iso, gx + 1.0, 2.8, 1.37, 0.18), c="ink", w=3, idp=pid)]
E.append(P(a, iso.d([(gx + 1.35, 2.5, 1.0), (gx + 1.35, 2.8, 1.0), (gx + 1.35, 2.8, 1.3), (gx + 1.35, 2.5, 1.3)]), c="ink", w=3, idp=pid))
E.append(P(a, " ".join(iso.d([(gx + 1.35, 2.5 + 0.06 * k, 1.04 + 0.05 * (k % 3)), (gx + 1.35, 2.53 + 0.06 * k, 1.04 + 0.05 * (k % 3))], close=False) for k in range(5)), c="ink", w=4, idp=pid))
E += label(a, 360, 300, "相机 + 环形灯", "Camera + ring light", c="blue", s=42, d=0.6, lead=((480, 330), iso(gx + 0.3, 2.45, 3.0)))
# 7 the measurement screen (flat, upper right): top view of the part with dimensions
a = 7
sx, sy, sw, sh_ = 1180, 230, 640, 400
E += [R(a, sx, sy, sw, sh_, c="ink", sw=5)]
E += T(a, sx + 24, sy + 50, 36, "测量结果  Measurements", c="muted", align="left")
E += [R(a, sx + 60, sy + 110, 260, 180, c="ink", sw=4), O(a, sx + 130, sy + 200, 30, c="ink", sw=4), O(a, sx + 250, sy + 200, 30, c="ink", sw=4)]
E.append(P(a, f"M{sx + 130},{sy + 310} L{sx + 250},{sy + 310} M{sx + 130},{sy + 298} L{sx + 130},{sy + 322} M{sx + 250},{sy + 298} L{sx + 250},{sy + 322}", c="blue", w=3))
scr = uid("scr")
E += [P(a, f"M{sx + 180},{sy + 130} L{sx + 220},{sy + 150}", c="red", w=4, idp=scr), pulse(a, scr, 1.6)]
rows = (("读码 Code", "已读 ✓", "blue"), ("孔径 Hole Ø", "合格 ✓", "green"), ("孔距 Spacing", "合格 ✓", "green"), ("划痕 Scratch", "超差 ✗", "red"))
for k, (n_, v, c_) in enumerate(rows):
    E += T(a, sx + 350, sy + 130 + 64 * k, 30, n_, c="ink", d=0.4 + 0.5 * k, align="left")
    E += T(a, sx + 545, sy + 130 + 64 * k, 30, v, c=c_, d=0.6 + 0.5 * k, align="left")
scan = uid("scan")
E += [P(a, f"M{sx + 60},{sy + 110} L{sx + 320},{sy + 110}", c="#4fb3e8", w=4, idp=scan), sh(a, scan, 0, 180, 0.2, 1.6)]
# 8 decide: green light pass / red pusher into quarantine
a = 8
lamp = uid("lamp")
E += [O(a, *iso(gx + 1.6, 1.4, 3.9), 22, c="green", fill="green", idp=lamp), pulse(a, lamp, 0.2)]
ok = iso(8.7, 3.0, 1.4)
E += check(a, ok[0], ok[1] - 40, c="green", d=0.3)
E += T(a, ok[0] + 70, ok[1] - 30, 40, "放行", c="green", d=0.3, align="left")
binx = 6.8
bn, bni = box(a, iso, binx, 4.6, 0, 1.5, 1.3, 1.0, c="red", w=5)
E += bn + T(a, iso(binx + 0.75, 5.9, 0)[0] + 40, iso(binx + 0.75, 5.9, 0)[1] + 70, 38, "隔离箱 Quarantine", c="red", d=0.4)
push = uid("push")
E += [P(a, iso.d([(binx + 0.4, 0.4, 1.1), (binx + 0.4, 1.9, 1.1)], close=False), c="red", w=7, idp=push),
      P(a, iso.d([(binx + 0.1, 1.9, 0.95), (binx + 0.7, 1.9, 0.95), (binx + 0.7, 1.9, 1.3), (binx + 0.1, 1.9, 1.3)]), c="red", w=5, idp=push),
      sh(a, push, -C30 * 80 * 0.9, S30 * 80 * 0.9, 0.6, 0.5)]
bad, badi = box(a, iso, binx, 2.3, 0.92, 1.0, 0.8, 0.4, c="red", w=4, shade=False)
E += bad + [sh(a, badi + "*", -C30 * 80 * 2.6, S30 * 80 * 2.6 + 30, 0.9, 0.9)]
E += cross(a, *iso(binx + 0.75, 5.25, 2.0), c="red", d=1.2)
# 9 control chart (flat, lower right): readings drift up → alarm before the limit
a = 9
cx0, cy0, cw, ch = 1180, 690, 640, 300
E += [R(a, cx0, cy0, cw, ch, c="ink", sw=4)]
E += T(a, cx0 + 24, cy0 + 44, 34, "控制图 Control chart", c="muted", align="left")
ucl, lcl, mid = cy0 + 90, cy0 + 260, cy0 + 175
E.append(P(a, f"M{cx0 + 30},{ucl} L{cx0 + cw - 30},{ucl} M{cx0 + 30},{lcl} L{cx0 + cw - 30},{lcl}", c="red", w=2.6))
E.append(P(a, f"M{cx0 + 30},{mid} L{cx0 + cw - 30},{mid}", c="muted", w=2))
ys = [0, 18, -14, 8, -6, 12, -10, 4, -20, -32, -44, -56]
pts = [(cx0 + 60 + 50 * k, mid - y * 1.2 - (0 if k < 8 else 0)) for k, y in enumerate([-v for v in ys])]
pts = [(x, mid + v * 1.2) for (x, _), v in zip(pts, ys)]
line_id = uid("cc")
E.append(P(a, "M" + " L".join(f"{x},{y}" for x, y in pts), c="blue", w=3.4, idp=line_id))
for k, (x, y) in enumerate(pts):
    di = uid("ccd")
    E += [O(a, x, y, 8, c="red" if k >= 9 else "blue", fill="red" if k >= 9 else "blue", idp=di), pop(a, di, 0.1 + 0.12 * k)]
bell = uid("alarm")
E += [{"t": "icon", "at": a, "id": bell, "name": "signal", "x": cx0 + cw - 70, "y": cy0 + 50, "size": 80, "c": "red"}, pop(a, bell, 1.6), pulse(a, bell, 2.0)]
E += T(a, cx0 + cw - 130, cy0 + 60, 30, "趋势报警", c="red", d=1.7, align="right")
# 10 AI drafts the nonconformance report, an engineer approves
a = 10
nx, ny = 60, 700
E += [R(a, nx, ny, 530, 300, c="ink", sw=4)]
E += T(a, nx + 24, ny + 52, 38, "不合格报告（AI 草稿）", c="ink", align="left", d=0.1)
E += T(a, nx + 24, ny + 100, 28, "Nonconformance report, AI draft", c="muted", align="left", d=0.1)
E += T(a, nx + 24, ny + 150, 30, "划痕超差 · 已隔离 1 件", c="ink", align="left", d=0.4)
btn = uid("btn")
E += [R(a, nx + 24, ny + 190, 300, 80, c="green", sw=4, idp=btn)] + T(a, nx + 174, ny + 243, 34, "工程师确认", c="green")
E += [pop(a, btn, 1.4)]
pp = stick(nx + 470, ny + 280, 0.65, a, idp=uid("eng"))
E += pp + check(a, nx + 470, ny + 40, c="green", d=1.8)
B.append(E)

# ============================================================== 画板 3：数据中枢闭环
iso = Iso(1000, 470, 62)
a = 11
E = title(a, "数据中枢 · 闭环", "The data hub: a closed loop")
layers = (("订单 Orders", "blue"), ("库存 Inventory", "green"), ("设备 Machines", "gold"), ("质量 Quality", "red"))
for k, (n_, c_) in enumerate(layers):
    ly, lid = box(a, iso, -1.6, -1.6, 0.75 * k, 3.2, 3.2, 0.45, c=c_, w=5, shade=False)
    E += ly + [pop(a, lid, 0.2 + 0.45 * k)]
    lx, ly_ = iso(1.6, -1.6, 0.22 + 0.75 * k)
    E += T(a, lx + 30, ly_ + 14, 34, n_, c=c_, d=0.3 + 0.45 * k, align="left")
core_ = uid("core")
E += [P(a, iso.d([(0, 0, 0.45), (0, 0, 3.4)], close=False), c="red", w=6, idp=core_), pulse(a, core_, 2.0)]
spokes = []
hubL = iso(-1.6, 1.6, 1.4)
for k, (ic, n_, x_, y_) in enumerate((("robot_arm", "机器人 Robots", 330, 290), ("eye", "视觉 Vision", 600, 290),
                                       ("building", "仓库 Warehouse", 330, 560), ("computer", "ERP", 600, 560))):
    ii = uid("ic")
    E += [{"t": "icon", "at": a, "id": ii, "name": ic, "x": x_, "y": y_, "size": 130, "c": "ink"}, pop(a, ii, 0.4 + 0.3 * k)]
    E += T(a, x_, y_ + 100, 30, n_, c="ink", d=0.5 + 0.3 * k)
    si = uid("sp")
    spokes.append(si)
    E.append(P(a, f"M{x_ + 70},{y_ + 10} L{hubL[0] - 10},{hubL[1]}", c="#e0882b", w=3, idp=si))
E += [flow(a, spokes, 80), signal(a, spokes, 240)]
# 12 digital twin screen (right): a tiny isometric plant with a red jam spot
a = 12
tx0, ty0 = 1420, 540
E += [R(a, tx0, ty0, 440, 290, c="blue", sw=5)]
E += T(a, tx0 + 20, ty0 + 44, 30, "数字孪生 Digital twin", c="blue", align="left")
mini = Iso(tx0 + 215, ty0 + 95, 14)
E.append(P(a, mini.d([(0, 0), (16, 0), (16, 9), (0, 9)]), c="ink", w=2.6))
for X in (2, 6, 10, 13):
    mb, _ = box(a, mini, X, 2.6, 0, 1.6, 1.6, 1.2, c="ink", w=2.4, shade=False)
    E += mb
mbelt = uid("mb")
E += [P(a, mini.d([(1, 5.5, 0.4), (15, 5.5, 0.4)], close=False), c=BELT, w=3, idp=mbelt), signal(a, mbelt, 90)]
jam = uid("jam")
E += [O(a, *mini(10.8, 5.5, 0.4), 22, c="red", sw=4, idp=jam), pulse(a, jam, 0.6), pulse(a, jam, 1.6), pulse(a, jam, 2.6)]
E += T(a, tx0 + 330, ty0 + 270, 28, "这里堵了 Jam", c="red", d=0.8)
twl = uid("twl")
E += [P(a, f"M{tx0 - 6},{ty0 + 60} L{iso(1.6, -1.6, 0)[0] + 10},{iso(1.6, -1.6, 0)[1] + 10}", c="blue", w=3, idp=twl), flow(a, twl, 60)]
# 13 AI suggests (card, lower left)
a = 13
E += [R(a, 160, 760, 440, 200, c="gold", sw=5)]
E += T(a, 185, 812, 36, "AI 建议 Suggestions", c="gold", align="left")
for k, s_ in enumerate(("换刀 Change tool", "降速 Slow down", "补料 Restock")):
    E += T(a, 200, 862 + 40 * k, 30, "· " + s_, c="ink", align="left", d=0.4 + 0.4 * k)
# 14 the loop: sense → analyse → suggest → approve → act → back (a ring of arrows with running dots)
a = 14
ring_ids = []
cx, cy, rx, ry = 1040, 860, 330, 110
steps = (("感知", "ink"), ("分析", "ink"), ("建议", "gold"), ("人确认", "red"), ("执行", "ink"))
for k in range(5):
    t0, t1 = 2 * math.pi * k / 5 - math.pi / 2 + 0.22, 2 * math.pi * (k + 1) / 5 - math.pi / 2 - 0.22
    q = [(cx + rx * math.cos(t0 + (t1 - t0) * j / 8), cy + ry * math.sin(t0 + (t1 - t0) * j / 8)) for j in range(9)]
    ai_ = uid("loop")
    ring_ids.append(ai_)
    E.append({"t": "arrow", "at": a, "id": ai_, "pts": [list(p) for p in q], "c": "ink", "w": 4, "head": 18})
for k, (n_, c_) in enumerate(steps):
    th = 2 * math.pi * k / 5 - math.pi / 2
    x_, y_ = cx + (rx + 8) * math.cos(th), cy + (ry + 4) * math.sin(th)
    E += T(a, x_, y_ + 13, 34, n_, c=c_, d=0.2 + 0.3 * k)
E += [signal(a, ring_ids, 320)]
# 15 closing line, inside the loop
a = 15
E += T(a, cx, cy + 6, 54, "全集成 · 全自动", c="red", d=0.2)
E += T(a, cx, cy + 56, 34, "人专心做判断", c="muted", d=0.8)
B.append(E)

if __name__ == "__main__":
    main(here, S, B, TITLE, "zh", say=SAY)
