# -*- coding: utf-8 -*-
"""刺绣花样文件（第 69 轮）：读 DST 和 CSV 针位表，写 DST（生成示例花样、测试用）。

DST（教材 16.5 节）：512 字节的文件头之后每条记录 3 个字节，记一针相对上一针的位移 Δx、Δy，单位 0.1 mm，
每个方向最大 ±121（12.1 mm）；标志位区分普通针、跳步、换色，另有结束记录。位的排法是公开的通用格式：
  Δx：字节 0 的位 0/1/2/3 = +1/−1/+9/−9，字节 1 的位 0/1/2/3 = +3/−3/+27/−27，字节 2 的位 2/3 = +81/−81；
  Δy：字节 0 的位 7/6/5/4 = +1/−1/+9/−9，字节 1 的位 7/6/5/4 = +3/−3/+27/−27，字节 2 的位 5/4 = +81/−81；
  字节 2 的位 0、1 总是 1；位 7 = 跳步，位 7 + 位 6 = 换色，0xF3 = 结束。
CSV 针位表：每行 x, y（mm，绝对坐标），可选第三列：0 或 s = 针，1 或 j = 跳步，2 或 c = 换色（在这一点换下一种颜色）。

读出来统一成记录表 [(dx, dy, kind)]，kind：'s' 针、'j' 跳步、'c' 换色；单位 mm。
"""
import base64
import binascii
import math

DST_MAX = 12.1
MAX_RECORDS = 150000          # 约 45 万字节的 DST（常见的大花样几万针）；再大的请拆开——每次计算要逐针调速
MAX_BYTES = 600_000           # DST 文件
MAX_TEXT = 900_000            # 网页传来的文字（DST 的 base64 或 CSV 原文）

_X = ((0, 0, 1), (0, 1, -1), (0, 2, 9), (0, 3, -9), (1, 0, 3), (1, 1, -3), (1, 2, 27), (1, 3, -27), (2, 2, 81), (2, 3, -81))
_Y = ((0, 7, 1), (0, 6, -1), (0, 5, 9), (0, 4, -9), (1, 7, 3), (1, 6, -3), (1, 5, 27), (1, 4, -27), (2, 5, 81), (2, 4, -81))


class StitchFileError(ValueError):
    """文件读不出来；zh / en 两句话给界面"""
    def __init__(self, zh, en):
        super().__init__(en)
        self.zh, self.en = zh, en


def _decode(b):
    dx = sum(v for i, bit, v in _X if b[i] >> bit & 1)
    dy = sum(v for i, bit, v in _Y if b[i] >> bit & 1)
    return dx, dy


def read_dst(data: bytes):
    if len(data) < 512 + 3:
        raise StitchFileError("文件太短，不是 DST 花样文件。", "The file is too short to be a DST design.")
    if len(data) > MAX_BYTES:
        raise StitchFileError("花样文件太大（超过 600 KB），请拆成几个花样。", "The design file is too large (over 600 KB); split it.")
    head = data[:512]
    if not head.startswith(b"LA:"):
        raise StitchFileError("文件头不对，不是 DST 花样文件；请在制版软件里另存为 DST。",
                              "The header is wrong, this is not a DST file; save it as DST in the digitising software.")
    recs = []
    for o in range(512, len(data) - 2, 3):
        b = data[o:o + 3]
        if b[2] == 0xF3:                           # 结束记录（只看第 3 个字节，和常见的读取程序一样）
            break
        if b[2] & 0x03 != 0x03:                    # 跳过一条坐标就全错位了：直接报错
            raise StitchFileError(f"第 {(o - 512) // 3 + 1} 条记录格式不对，文件可能已损坏。",
                                  f"Record {(o - 512) // 3 + 1} is malformed; the file may be damaged.")
        dx, dy = _decode(b)
        if b[2] & 0xC3 == 0xC3:
            kind = "c"
        elif b[2] & 0x83 == 0x83:
            kind = "j"
        else:
            kind = "s"
        recs.append((dx / 10, dy / 10, kind))
        if len(recs) > MAX_RECORDS:
            raise StitchFileError("针数太多（超过 15 万条记录），请拆成几个花样。", "Too many records (over 150 000); split the design.")
    if not any(k == "s" for _, _, k in recs):
        raise StitchFileError("文件里没有针。", "The file has no stitches.")
    return recs


def read_csv(text: str):
    if len(text) > MAX_TEXT:
        raise StitchFileError("针位表太大，请拆成几个花样。", "The stitch list is too large; split the design.")
    pts = []
    for line in text.splitlines():
        parts = [q.strip() for q in line.replace("\t", ",").replace(";", ",").split(",")]
        parts = [q for q in parts if q]
        if len(parts) < 2:
            continue
        try:
            x, y = float(parts[0]), float(parts[1])
        except ValueError:
            continue                                   # 表头
        if not (math.isfinite(x) and math.isfinite(y) and abs(x) < 5000 and abs(y) < 5000):
            continue
        f = parts[2].lower() if len(parts) > 2 else "0"
        kind = "j" if f in ("1", "j", "jump") else ("c" if f in ("2", "c", "color", "colour") else "s")
        pts.append((x, y, kind))
        if len(pts) > MAX_RECORDS:
            raise StitchFileError("针数太多（超过 15 万针），请拆成几个花样。", "Too many stitches (over 150 000); split the design.")
    if len(pts) < 2:
        raise StitchFileError("针位表里至少要有两针（每行 x, y，单位 mm）。", "The stitch list needs at least two rows (x, y in mm).")
    recs = []
    for i in range(1, len(pts)):
        recs.append((round(pts[i][0] - pts[i - 1][0], 3), round(pts[i][1] - pts[i - 1][1], 3), pts[i][2]))
    if not any(k == "s" for _, _, k in recs):
        raise StitchFileError("针位表里没有针（全是跳步或换色）。", "The stitch list has no stitches (only jumps or colour changes).")
    return recs


def load(dst_b64=None, csv_text=None):
    """前端传来的：DST 用 base64，CSV 用原文。返回记录表；都没有返回 None"""
    if dst_b64:
        if len(dst_b64) > MAX_TEXT:
            raise StitchFileError("花样文件太大（超过 600 KB），请拆成几个花样。", "The design file is too large (over 600 KB); split it.")
        try:
            data = base64.b64decode(dst_b64, validate=False)
        except (binascii.Error, ValueError):
            raise StitchFileError("文件内容传输出错，请重新选择文件。", "The file did not arrive intact; choose it again.")
        return read_dst(data)
    if csv_text:
        if not isinstance(csv_text, str):
            raise StitchFileError("针位表格式不对（每行 x, y，单位 mm）。", "The stitch list is malformed (x, y per row, mm).")
        return read_csv(csv_text)
    return None


def stats(recs):
    """针数、跳步、换色、最长针、外框；超过 12.1 mm 的针（要拆成几条记录、在机器上是几针）"""
    x = y = 0.0
    xs, ys = [0.0], [0.0]
    n_s = n_j = n_c = 0
    smax = dmax = 0.0
    over = 0
    for dx, dy, k in recs:
        x += dx
        y += dy
        xs.append(x)
        ys.append(y)
        if k == "s":
            n_s += 1
            a = max(abs(dx), abs(dy))
            smax = max(smax, a)
            dmax = max(dmax, math.hypot(dx, dy))
            if a > DST_MAX + 1e-9:
                over += 1
        elif k == "j":
            n_j += 1
        else:
            n_c += 1
    return dict(stitches=n_s, jumps=n_j, colors=n_c, records=len(recs), s_max=smax, d_max=dmax, over=over,
                w=max(xs) - min(xs), h=max(ys) - min(ys))


# ---------------------------------------------------------------- 写 DST（示例花样、测试）
def _encode(dx, dy, flag=0x03):
    b = [0, 0, flag]
    for val, table in ((dx, _X), (dy, _Y)):
        # 平衡三进制：81、27、9、3、1 各取 −1 / 0 / +1
        for w in (81, 27, 9, 3, 1):
            if val >= (w + 1) // 2:
                d = 1
            elif val <= -((w + 1) // 2):
                d = -1
            else:
                d = 0
            if d:
                i, bit, _ = next(t for t in table if t[2] == d * w)
                b[i] |= 1 << bit
                val -= d * w
    return bytes(b)


def _sgn(v):
    return f"{'+' if v >= 0 else '-'}{abs(v):>5}"


def write_dst(recs, label="WQ"):
    """记录表（mm）→ DST 字节。单方向超过 12.1 mm 的移动拆成几条跳步（普通针）或几条同类记录"""
    out = bytearray()
    n = 0
    ex = ey = 0.0            # 取整误差带到下一条，不累积
    for dx, dy, k in recs:
        tx, ty = dx * 10 + ex, dy * 10 + ey
        ix, iy = round(tx), round(ty)
        ex, ey = tx - ix, ty - iy
        parts = max(1, math.ceil(max(abs(ix), abs(iy)) / 121))
        for j in range(parts):
            px = round(ix * (j + 1) / parts) - round(ix * j / parts)
            py = round(iy * (j + 1) / parts) - round(iy * j / parts)
            last = j == parts - 1
            if k == "c" and last:
                flag = 0xC3
            elif k == "j" or (k == "s" and not last) or k == "c":
                flag = 0x83
            else:
                flag = 0x03
            out += _encode(px, py, flag)
            n += 1
    out += bytes([0, 0, 0xF3])
    st = stats(recs)
    x = y = 0.0
    xs, ys = [0.0], [0.0]
    for dx, dy, _ in recs:
        x += dx
        y += dy
        xs.append(x)
        ys.append(y)
    ext = [round(max(xs) * 10), round(-min(xs) * 10), round(max(ys) * 10), round(-min(ys) * 10)]     # 外框（0.1 mm），有的机器靠它居中
    head = (f"LA:{label[:16]:<16}\rST:{n:>7}\rCO:{st['colors']:>3}\r+X:{ext[0]:>5}\r-X:{ext[1]:>5}\r+Y:{ext[2]:>5}\r-Y:{ext[3]:>5}\r"
            f"AX:{_sgn(round(x * 10))}\rAY:{_sgn(round(y * 10))}\rMX:+{0:>5}\rMY:+{0:>5}\rPD:******\r\x1a").encode("ascii")
    head = head + b" " * (512 - len(head))
    return bytes(head) + bytes(out)
