"""52.1 节：键槽铣夹具 JJ-301-50 的组成——夹具总图（图 52.1.5）由数字工厂的三维模型投影生成（factory/digital/drawings/jj30150.py），
主视图、俯视图、A–A 剖视、零件序号、明细栏和技术要求都取自同一份夹具数据 std/JJ-301-50_fixture.yaml；核对工序 50 登记的夹具编号，
统计各类元件。"""
import _mfg as M
from bookout import out
from drawings import jj30150 as D

fx = M.fixture_data()
p = M.plan()
o50 = M.op(p, 50)
assert o50.get("fixture_id") == fx["id"], "工序 50 登记的夹具编号与夹具数据不一致"
M.r3d().save_svg("fig52_1_5", D.svg())

kinds = {"定位元件": [3, 4], "夹紧装置": [5, 6, 7, 8, 9], "对刀元件": [10, 12], "连接元件": [2], "夹具体": [1], "其他": [11]}
g = M.m3d()[2].geometry()
out(n_parts=len(fx["parts"]), n_req=len(fx["requirements"]), dof=fx["locating"]["dof"], key_spacing=fx["keys"]["spacing"],
    axis_h=g["zc"] + 30, **{f"k_{i}": len(v) for i, v in enumerate(kinds.values())})
