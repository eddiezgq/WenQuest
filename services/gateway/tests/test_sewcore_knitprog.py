"""第 70 轮：横机意匠图——读文件（文字表、提花色码图）、编译（和教材虚拟实验 17-2 逐趟一致）、按真实花型算一片用时。"""
import base64
import io
import json
from pathlib import Path

import pytest

from app.sewcore import flatknit as F
from app.sewcore import knit_samples as KS
from app.sewcore import knitprog as K
from app.sewcore import optimize as OPT
from tests.test_course_pack import client  # noqa: F401
from tests.test_sewing_cae import cae  # noqa: F401

# 虚拟实验 17-2 的四种预设花型（罗纹、两色提花、绞花、收针）用实验页里的编译器在 node 里跑出来的逐趟结果
LAB = json.loads((Path(__file__).parent / "data" / "knitprog_lab17_2.json").read_text())
FRONT = KS.front_text()


@pytest.mark.parametrize("name", sorted(LAB))
def test_compiler_matches_lab_17_2(name):
    d = LAB[name]
    C = K.compile(K.parse_text("\n".join(d["rows"])))
    mine = [[c["row"], c["type"], c["dir"], c["carrier"], c["rack"]] for c in C["courses"]]
    lab = [[r, "knit" if t == "编织" else "empty" if t == "空行" else "xfer", dr, ca, rk] for r, t, dr, ca, rk in d["courses"]]
    assert mine == lab and not [m for m in C["msgs"] if m["t"] == "err"]


def test_compile_errors_and_formats():
    # 空针翻针：第一行就要翻；摇床 5 针超行程；移出针床
    C = K.compile(K.parse_text(">,K,K\n"))
    assert any("空针翻针" in m["zh"] for m in C["msgs"]) and (0, 0) in C["err_cells"]
    C = K.compile(K.parse_text("K,K,K,K,K,K\n<,K,K,K,K,K\n"))
    assert any("针床外" in m["zh"] for m in C["msgs"])
    # 一个字符一格、颜色号、注释、短行补“不织”
    rows = K.parse_text("# x\nKPKP\nK2,K,P\n")
    assert rows[0][1] == ("P", 1) and rows[1][0] == ("K", 2) and rows[1][3] == (".", 1)
    with pytest.raises(K.KnitFileError):
        K.parse_text("K,Q,K\n")
    with pytest.raises(K.KnitFileError):
        K.parse_text("...\n...\n")
    # 色码图：最下面一行先织，用得多的颜色是 1 号纱嘴，透明不织
    from PIL import Image
    im = Image.new("RGBA", (4, 2), (255, 255, 255, 255))
    im.putpixel((0, 1), (200, 0, 0, 255))
    im.putpixel((3, 0), (0, 0, 0, 0))
    b = io.BytesIO()
    im.save(b, "PNG")
    rows = K.load(png_b64=base64.b64encode(b.getvalue()).decode())
    assert rows[0] == [("K", 2), ("K", 1), ("K", 1), ("K", 1)] and rows[1][3] == (".", 1)
    many = Image.new("RGB", (8, 1))
    for i in range(8):
        many.putpixel((i, 0), (i * 30, 0, 0))
    b = io.BytesIO()
    many.save(b, "PNG")
    with pytest.raises(K.KnitFileError):
        K.parse_png(b.getvalue())
    assert K.parse_text(K.to_text(rows)) == rows
    # 六种颜色一行：五个空行之后第 6 号纱嘴照样织（不能漏）
    C = K.compile(K.parse_text("K1,K2,K3,K4,K5,K6\n"))
    assert [c["carrier"] for c in C["courses"] if c["type"] == "knit"] == [1, 2, 3, 4, 5, 6]
    # 表格软件里的空白格当“不织”，不让针位错位
    assert K.parse_text(",,K,K\n")[0] == [(".", 1), (".", 1), ("K", 1), ("K", 1)]
    # 很大的图先看尺寸就拒，不解码
    big = Image.new("1", (1200, 4000))
    b = io.BytesIO()
    big.save(b, "PNG")
    with pytest.raises(K.KnitFileError):
        K.parse_png(b.getvalue())


def test_manual_mode_unchanged_17_8():
    """不上传意匠图时和第 54 轮一样：17.8 节算例 760 趟、一片约 11.4 分钟"""
    R = F.analyze({})
    assert R["production"]["passes"] == 760 and R["production"]["t_piece_min"] == pytest.approx(11.4, abs=0.05)
    assert "design" not in R and F.analyze({"src": "file"})["params"]["src"] == "manual"


def test_front_piece_from_design():
    """示例前片：240 针 × 460 行；袖窿收针以后行变窄、翻针横列降速，都按趟算进去"""
    R = F.analyze({"src": "file", "knit": FRONT})
    d = R["design"]
    assert (d["W"], d["H"], d["colors"], d["xfer"], d["errors"]) == (240, 460, 2, 45, 0)
    assert R["params"]["N"] == 240 and "knit" not in R["params"]
    PT = F.program_time(F.clean({"src": "file", "knit": FRONT}))
    xf = [x for x in PT["passes"] if x[0] == "xfer"]
    assert xf and all(v == 0.4 for _, _, v, _, _ in xf)
    first = next(x[1] for x in PT["passes"] if x[0] == "knit" and x[4] == 1)
    last = next(x[1] for x in PT["passes"][::-1] if x[0] == "knit" and x[4] == 460 and x[1] > 700)
    assert first - last == pytest.approx(2 * 15 * 25.4 / 12, abs=0.01)                  # 两边各收 15 针，最后一行窄 30 针
    # 翻针按设计速度算会更快；两系统把两色合进一趟，趟数少很多
    fast = F.production(F.clean({"src": "file", "knit": FRONT, "vx": 1.2}))["t_piece"]
    assert fast < R["production"]["t_piece"]
    two = F.analyze({"src": "file", "knit": FRONT, "sys": 2})
    assert two["production"]["passes"] < 0.7 * R["production"]["passes"]
    kinds = [c["kind"] for c in R["charts"]]
    assert kinds[:2] == ["knitgrid", "line"] and R["tables"][0]["key"] == "program"


def test_bad_design_red_not_crash():
    R = F.analyze({"src": "file", "knit": "K,Q\n"})
    assert [c["key"] for c in R["checks"] if c["state"] == "bad"] == ["file"] and R["params"]["src"] == "manual"
    R = F.analyze({"src": "file", "knit": ">,K\nK,K\n"})
    assert next(c for c in R["checks"] if c["key"] == "program")["state"] == "bad"
    assert "knit" not in F.clean({"src": "manual", "knit": FRONT})


def test_drive_rms_and_optimizer_follow_the_design():
    assert F.drive(F.clean({"src": "file", "knit": FRONT, "sys": 2}))["Trms"] > 0       # 不经 analyze（参数是小数）也能算——CAE 电机选型就这样调
    m = F.drive(F.clean({}))
    f = F.drive(F.clean({"src": "file", "knit": FRONT}))
    assert f["Tpk"] == pytest.approx(m["Tpk"]) and f["Trms"] != m["Trms"]
    r = OPT.run("flatknit", {"src": "file", "knit": FRONT}, "time")
    assert r["candidates"] and r["candidates"][0]["bad"] == 0
    base = F.production(F.clean({"src": "file", "knit": FRONT}))["t_piece"] / 60
    assert r["candidates"][0]["value"] < base


def test_gateway_sample_and_export(cae):  # noqa: F811
    c, h, _ = cae
    s = c.get("/api/v1/sewing/flatknit/sample").json()
    assert s["name"].endswith(".csv") and s["knit"] == FRONT
    r = c.post("/api/v1/sewing/analyze", json={"machine": "flatknit", "params": {"src": "file", "knit": s["knit"], "fname": s["name"]}}).json()
    assert r["design"]["fname"] == "wq-front.csv" and "knit" not in r["params"]
    j = c.post("/api/v1/sewing/export/json", json={"machine": "flatknit", "params": {"src": "file", "knit": s["knit"]}}, headers=h).json()
    assert j["params"]["knit"] == s["knit"]
    for kind in ("report", "params"):
        assert c.post(f"/api/v1/sewing/export/{kind}", json={"machine": "flatknit", "params": {"src": "file", "knit": s["knit"]}}, headers=h).status_code == 200
