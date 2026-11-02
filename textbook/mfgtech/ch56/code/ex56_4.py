"""算例 56.4.1–56.4.3：SH-101 的精基准。
56.4.1 基准重合：齿轮左端面的轴向位置按“轴承定位轴肩到齿轮左端面 8 ± 0.1”标注，数控车程序从左端面编（基准不重合）与从轴肩编（重合）；
56.4.2 基准统一：齿顶圆径向圆跳动（对 A–B 公共轴线，0.03）在三种基准方案下的定位误差（卡盘跳动等为示意值）；
56.4.3 铣键槽用 V 形块定位轴伸外圆：键槽深 d − t₁ 的定位误差与对称度（第 51 章 hub/tolerance.py）。画图 56.4.3。"""
import _mfg as M
from bookout import T, figure, out, style

TL = M.tol()
P = M.part101()
# ---- 56.4.1 基准重合与不重合（轴向）
L_end_sh = 36 + 20 + 17               # 左端面 → 左轴承定位轴肩（承靠轴承的端面）
L_end_g = L_end_sh + 8                # 左端面 → 齿轮左端面
t_turn = 0.1                          # 数控车一个轴向尺寸的经济公差 ±0.1（示意）
links = [TL.Link("左端面→齿轮左端面", L_end_g, t_turn, -t_turn, +1), TL.Link("左端面→轴肩", L_end_sh, t_turn, -t_turn, -1)]
r = TL.extreme(links)
dB = TL.datum_mismatch([links[1]])
need = 0.1                            # 图纸 8 ± 0.1
t_need = (2 * need - dB) / 2          # 基准不重合时，左端面→齿轮左端面必须收紧到 ±t_need
# ---- 56.4.2 基准统一：齿顶圆对 A–B 的径向圆跳动
center = 0.002                        # 中心孔锥面的圆度与两中心孔的同轴误差引起的轴线偏移（示意，修研后）
chuck = 0.03                          # 三爪卡盘的定心跳动 TIR（示意）
x_clamp, x_c, x_g = 18.0, 136.0, 96.0  # 一夹一顶：卡盘夹轴伸中部，尾顶尖在右端；齿轮中点
schemes = [
    (T("A 两端中心孔贯穿始终（精车、滚齿、磨都用它）", "A centres throughout"), 2 * center),
    (T("B 精车齿顶圆一夹一顶（夹轴伸），磨轴承位用两顶尖", "B chuck + centre for turning, centres for grinding"),
     TL.chuck_runout_error(chuck) * (x_c - x_g) / (x_c - x_clamp)),
    (T("C 精车齿顶圆时三爪卡盘夹轴承位（调头车）", "C chucked on the bearing seat"), TL.chuck_runout_error(chuck)),
]
tol_c8 = 0.03
# ---- 56.4.3 铣键槽：V 形块（α = 90°）定位轴伸外圆 Ø20.4（0/−0.05，精车后）
Td = 0.05
e_depth = TL.v_block(Td, 90, "bottom")          # 槽深从下母线量起时的定位误差
e_center = TL.v_block(Td, 90, "center")
tol_depth = 0.1

plt = style()
fig, ax = plt.subplots(figsize=(6.4, 2.4))
ys = range(len(schemes))[::-1]
for y, (name, e) in zip(ys, schemes):
    ax.barh(y, e * 1000, color=M.GREEN if e <= tol_c8 / 3 else (M.WARM if e <= tol_c8 else M.RED), height=0.55)
    ax.text(e * 1000 + 0.6, y, f"{e * 1000:.1f} µm", va="center", fontsize=7.5)
ax.axvline(tol_c8 * 1000, color=M.RED, ls="--", lw=0.8)
ax.axvline(tol_c8 * 1000 / 3, color=M.MUTED, ls=":", lw=0.8)
ax.text(tol_c8 * 1000, len(schemes) - 0.45, T("公差 0.03", "tol. 0.03"), fontsize=7, color=M.RED, ha="center")
ax.text(tol_c8 * 1000 / 3, len(schemes) - 0.45, T("公差的 1/3", "1/3 of tol."), fontsize=7, color=M.MUTED, ha="center")
ax.set_yticks(list(ys)); ax.set_yticklabels([s[0] for s in schemes], fontsize=7)
ax.set_xlabel(T("齿顶圆对 A–B 径向圆跳动中由基准引起的部分 / µm", "runout from the datum scheme / µm")); ax.set_xlim(0, 36)
ax.grid(lw=0.3, alpha=0.5, axis="x")
figure(fig, "fig56_4_3")

out(L_end_sh=L_end_sh, L_end_g=L_end_g, t_turn=t_turn, r_max=r.max, r_min=r.min, r_T=r.max - r.min, dB=dB, t_need=t_need,
    center_um=center * 1000, chuck=chuck, eA_um=schemes[0][1] * 1000, eB_um=schemes[1][1] * 1000, eC_um=schemes[2][1] * 1000,
    Td=Td, e_depth=e_depth, e_center=e_center, tol_depth=tol_depth, depth_ok=bool(TL.ok_against(tol_depth, e_depth)))
