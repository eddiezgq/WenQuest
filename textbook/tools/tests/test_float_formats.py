"""《人工智能》第 8 章：浏览器实验 8.1（lab8_1.js）把实数舍入到各种浮点格式的写法，与书中的 Python 参考版
（ch08/code/_ch8.round_to）逐个数相同；半精度与 NumPy 的 float16 相同。"""
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[3]
AI = ROOT / "textbook" / "ai"
sys.path[:0] = [str(AI / "conventions"), str(ROOT / "textbook" / "tools")]
spec = importlib.util.spec_from_file_location("_ch8", AI / "ch08" / "code" / "_ch8.py")
ch8 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ch8)

RUN = """
let L; global.WQ = { lab(o) { L = o; } };
require(process.argv[1]);
const xs = JSON.parse(require("fs").readFileSync(0, "utf8"));
const out = {};
for (let i = 0; i < 7; i++) { const f = L.fmt(i); out[f.name] = xs.map((x) => L.round(x, f)); }
process.stdout.write(JSON.stringify(out, (k, v) => (v === Infinity ? "inf" : v === -Infinity ? "-inf" : v)));
"""


def sample():
    rng = np.random.default_rng(1)
    return list(rng.standard_normal(3000) * 10.0 ** rng.integers(-9, 6, 3000)) + [0.1, 70000, 1e-6, 1e-8, 500, 448, 464, 65520, 65519,
                                                                                 0.265625, 2.5, 5, 6.5, -0.75]


def test_fp16_matches_numpy():
    x = np.array(sample())
    with np.errstate(over="ignore"):
        assert np.array_equal(ch8.round_to(x, ch8.FMTS["FP16"]), x.astype(np.float16).astype(np.float64))


def test_js_and_python_agree():
    if not shutil.which("node"):
        pytest.skip("node is not installed")
    xs = sample()
    r = subprocess.run(["node", "-e", RUN, str(AI / "ch08" / "lab" / "lab8_1.js")], input=json.dumps(xs), capture_output=True,
                       text=True, check=True)
    js = json.loads(r.stdout)
    for name, f in ch8.FMTS.items():
        with np.errstate(over="ignore"):
            py = ch8.round_to(np.array(xs), f)
        j = np.array([np.inf if v == "inf" else -np.inf if v == "-inf" else v for v in js[name]], dtype=float)
        assert np.array_equal(py, j), name


def test_format_constants():
    F = ch8.FMTS
    assert F["FP16"].max == 65504 and F["FP8 E4M3"].max == 448 and F["FP8 E5M2"].max == 57344 and F["FP4 E2M1"].max == 6
    assert F["BF16"].min_normal == F["FP32"].min_normal == 2.0 ** -126
    assert sorted(set(np.abs(ch8.round_to(np.linspace(-7, 7, 2001), F["FP4 E2M1"])))) == [0, 0.5, 1, 1.5, 2, 3, 4, 6]
