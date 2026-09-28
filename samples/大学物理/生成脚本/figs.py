import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, FancyArrowPatch, Rectangle, Circle
from matplotlib import font_manager as fm
fm.fontManager.addfont("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
plt.rcParams["font.sans-serif"] = [fm.FontProperties(fname="/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc").get_name()]; plt.rcParams["axes.unicode_minus"] = False
INK="#1f2d3a"; A="#c0392b"; B="#1f6f8b"; C="#2e7d5b"; D="#b7791f"

# 1. projectile trajectories, v0 = 20 m/s, g = 9.8
fig, ax = plt.subplots(figsize=(7,4), dpi=200)
g, v0 = 9.8, 20.0
for th, col in [(15,B),(30,C),(45,A),(60,D),(75,"#6b4fa0")]:
    t = np.linspace(0, 2*v0*np.sin(np.radians(th))/g, 200)
    ax.plot(v0*np.cos(np.radians(th))*t, v0*np.sin(np.radians(th))*t-0.5*g*t**2, color=col, lw=2, label=f"θ = {th}°")
R = v0**2/g
ax.annotate(f"45° 射程最大 ≈ {R:.1f} m", xy=(R,0.1), xytext=(21.2,0.6), arrowprops=dict(arrowstyle="->", color=INK), fontsize=9, color=INK)
ax.set_xlabel("x / m"); ax.set_ylabel("y / m"); ax.set_title("不同抛射角的抛体轨迹（$v_0$ = 20 m/s，忽略空气阻力）", fontsize=11)
ax.set_xlim(0, 44); ax.set_ylim(0, 20); ax.grid(alpha=.3); ax.legend(frameon=False, fontsize=9)
ax.text(30.6, 10.5, "15° 与 75°、30° 与 60°\n射程相同", fontsize=9, color="#555")
fig.tight_layout(); fig.savefig("fig/抛体运动轨迹.png"); plt.close(fig)

# 2. incline free-body diagram
fig, ax = plt.subplots(figsize=(6,4), dpi=200); ax.set_aspect("equal"); ax.axis("off")
th = np.radians(30); L = 6
ax.add_patch(Polygon([[0,0],[L*np.cos(th),0],[0,L*np.sin(th)]], closed=True, fc="#e8eef0", ec=INK, lw=1.5))
cx, cy = 1.9*np.cos(th), L*np.sin(th) - 1.9*np.sin(th)  # point on the slope
# block
w, h = 1.0, 0.6
rot = np.array([[np.cos(-th), -np.sin(-th)],[np.sin(-th), np.cos(-th)]])
corners = np.array([[-w/2,0],[w/2,0],[w/2,h],[-w/2,h]]) @ rot.T + [cx, cy]
ax.add_patch(Polygon(corners, fc="#f2b705", ec=INK, lw=1.5))
mx, my = (np.array([0,h/2]) @ rot.T) + [cx, cy]
def arrow(dx, dy, col, label, off=(0.1,0.1)):
    ax.add_patch(FancyArrowPatch((mx,my),(mx+dx,my+dy), arrowstyle="-|>", mutation_scale=14, color=col, lw=2))
    ax.text(mx+dx+off[0], my+dy+off[1], label, color=col, fontsize=12)
arrow(0,-2.0,A,"mg",( 0.1,-0.3))
arrow(1.4*np.sin(th),1.4*np.cos(th),B,"N")
arrow(-1.2*np.cos(th),1.2*np.sin(th),C,"f",(-0.4,0.05))
ax.annotate("", xy=(L*np.cos(th)-1.2,0.02), xytext=(L*np.cos(th)-1.2+0.01,0.02))
ax.text(L*np.cos(th)-1.4, 0.15, "θ", fontsize=12, color=INK)
ax.text(0.2, -0.6, "斜面上物体的受力分析：重力 mg、支持力 N、摩擦力 f", fontsize=10, color=INK)
ax.set_xlim(-0.5, 6); ax.set_ylim(-0.9, 4)
fig.tight_layout(); fig.savefig("fig/斜面受力分析.png"); plt.close(fig)

# 3. collision schematic
fig, axs = plt.subplots(2,1, figsize=(6.5,3.2), dpi=200)
for ax, (title, v1, v2) in zip(axs, [("碰撞前", "$v_{10}$", "$v_{20}$"), ("碰撞后", "$v_1$", "$v_2$")]):
    ax.axis("off"); ax.set_xlim(0,10); ax.set_ylim(0,2)
    ax.plot([0,10],[0.3,0.3], color=INK, lw=1)
    ax.add_patch(Circle((2.5,0.9),0.6, fc="#1f6f8b", ec=INK)); ax.text(2.5,0.9,"$m_1$",color="white",ha="center",va="center",fontsize=11)
    ax.add_patch(Circle((6.5,0.9),0.6, fc="#f2b705", ec=INK)); ax.text(6.5,0.9,"$m_2$",color=INK,ha="center",va="center",fontsize=11)
    ax.add_patch(FancyArrowPatch((3.2,1.7),(4.4,1.7), arrowstyle="-|>", mutation_scale=12, color=A)); ax.text(3.4,1.75,v1,color=A,fontsize=10)
    ax.add_patch(FancyArrowPatch((7.2,1.7),(8.2,1.7), arrowstyle="-|>", mutation_scale=12, color=A)); ax.text(7.4,1.75,v2,color=A,fontsize=10)
    ax.text(0.1,1.6,title,fontsize=11,color=INK)
fig.suptitle("两球对心碰撞：系统水平方向动量守恒", fontsize=11, color=INK)
fig.tight_layout(); fig.savefig("fig/动量守恒-碰撞示意.png"); plt.close(fig)

# 4. simple pendulum
fig, ax = plt.subplots(figsize=(3.6,4.2), dpi=200); ax.set_aspect("equal"); ax.axis("off")
ax.plot([-1.2,1.2],[0,0], color=INK, lw=3)
phi = np.radians(12); Lp = 3.2
bx, by = Lp*np.sin(phi), -Lp*np.cos(phi)
ax.plot([0,0],[0,-Lp], ls="--", color="#999", lw=1)
ax.plot([0,bx],[0,by], color=INK, lw=1.5)
ax.add_patch(Circle((bx,by),0.22, fc="#1f6f8b", ec=INK))
ax.text(0.06,-1.3,"θ",fontsize=12); ax.text(bx/2+0.12,by/2,"L",fontsize=12,color=INK)
ax.text(-1.3,-4.0,"单摆：T = 2π√(L/g)（θ < 5°）",fontsize=10,color=INK)
ax.set_xlim(-1.5,1.5); ax.set_ylim(-4.3,0.3)
fig.tight_layout(); fig.savefig("fig/单摆示意.png"); plt.close(fig)

# 5. circular motion acceleration components
fig, ax = plt.subplots(figsize=(4.2,4.2), dpi=200); ax.set_aspect("equal"); ax.axis("off")
t = np.linspace(0, 2*np.pi, 200); ax.plot(2*np.cos(t), 2*np.sin(t), color="#999", lw=1)
p = np.radians(40); px, py = 2*np.cos(p), 2*np.sin(p)
ax.plot(0,0,"o",color=INK); ax.add_patch(Circle((px,py),0.09,fc=INK))
def arr(x,y,dx,dy,col,lab,o=(0.08,0.05)):
    ax.add_patch(FancyArrowPatch((x,y),(x+dx,y+dy), arrowstyle="-|>", mutation_scale=12, color=col, lw=2)); ax.text(x+dx+o[0],y+dy+o[1],lab,color=col,fontsize=11)
arr(px,py,-1.0*np.sin(p),1.0*np.cos(p),B,"$v,\ a_t$")
arr(px,py,-1.1*np.cos(p),-1.1*np.sin(p),A,"$a_n = v^2/R$",(-0.2,-0.35))
ax.text(-1.9,-2.6,"切向加速度改变速率，法向加速度改变方向",fontsize=9,color=INK)
ax.set_xlim(-2.6,2.8); ax.set_ylim(-2.8,2.8)
fig.tight_layout(); fig.savefig("fig/圆周运动加速度.png"); plt.close(fig)
print("figures done")
