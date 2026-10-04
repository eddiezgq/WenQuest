"""52.7 节：典型夹具。算例 52.7.1 车床角铁式夹具的不平衡力与平衡块；算例 52.7.2 加工中心多工位夹具（立柱式）对单件工时的影响。"""
import _mfg as M
from bookout import out

FX = M.fx()
# 算例 52.7.1：轴承座在角铁上车 Ø52 孔，工件 + 角铁共 12 kg，重心偏离主轴轴线 60 mm，转速 600 r/min（教学示意值）
m, e, n = 12.0, 60.0, 600.0
F = FX.unbalance_force(m, e, n)
r_cw = 120.0
m_cw = FX.counterweight(m, e, r_cw)
F_1200 = FX.unbalance_force(m, e, 2 * n)
# 平衡后残余偏心 2 mm（重心位置估得不准）时的残余不平衡力
F_res = FX.unbalance_force(m + m_cw, 2.0, n)

# 算例 52.7.2：箱盖类小零件在加工中心上，每件切削 4.0 min；单件装夹（装卸 1.2 min，机床等待）与
# 四面立柱夹具（每面 2 件，共 8 件；在机外的第二个托盘上装卸，换托盘 0.3 min）比较（教学示意值）
t_cut, t_load = 4.0, 1.2
single = t_cut + t_load
n_parts, t_swap = 8, 0.3
tomb = t_cut + t_swap / n_parts            # 装卸在机外与切削并行
util_single = t_cut / single
util_tomb = t_cut / tomb
out(m=m, e=e, n=n, F=F, r_cw=r_cw, m_cw=m_cw, F_1200=F_1200, F_res=F_res, G=m * 9.81, F_over_G=F / (m * 9.81),
    t_cut=t_cut, t_load=t_load, single=single, tomb=tomb, util_single=util_single, util_tomb=util_tomb,
    gain=single / tomb, n_parts=n_parts, t_swap=t_swap)
