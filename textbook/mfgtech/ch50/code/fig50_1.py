"""50.1 节：SH-301 的国标零件图（图 50.1.1）与毛坯图（图 50.1.2）。由数字工厂的三维模型投影生成（factory/digital/drawings/sh301.py），
尺寸、公差、形位公差、粗糙度和技术要求取自工艺规程 std/SH-301_process.yaml 的 part、characteristics，与 PLM 里的图是同一份。"""
import _mfg as M
from bookout import out
from drawings import sh301 as D

R = M.r3d()
R.save_svg("fig50_1_1", D.part_sheet().svg())
R.save_svg("fig50_1_2", D.blank_sheet().svg())
p = M.plan()
out(n_chars=len(p["characteristics"]), n_key=sum(1 for c in p["characteristics"] if c.get("key")))
