"""15.1 节：压装工位简图（图 15.1.1）；从虚拟设备的 I/O 表数出输入、输出点数（控制要求说明的 I/O 一览）。"""
import json
import shutil
import subprocess
from pathlib import Path

from bookout import figure, out
from _draw15 import press_sketch

kit = Path(__file__).resolve().parents[4] / "services" / "gateway" / "app" / "production" / "labkit" / "plants.js"
io = json.loads(subprocess.run([shutil.which("node"), "-e", f"process.stdout.write(JSON.stringify(require({json.dumps(str(kit))}).press().io))"],
                               capture_output=True, text=True, check=True).stdout)
di = [x for x in io if x["dir"] == "in" and x["addr"].startswith("%IX")]
ai = [x for x in io if x["dir"] == "in" and x["addr"].startswith("%IW")]
do = [x for x in io if x["dir"] == "out"]
figure(press_sketch(), "fig15_1_1")
out(n_di=len(di), n_ai=len(ai), n_do=len(do), n_io=len(io))
