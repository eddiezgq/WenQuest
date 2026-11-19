"""动画 22.2.1（配图 22.2.1）：预测误差怎样一步步传进调度成本。

五段：
1. 一天的光伏：真值与预测——**预测偏高了一点点**；
2. 按预测排计划：什么时候充、什么时候放，申报的购电曲线由它定下来；
3. 真的出力到了：预测偏高的那几个时段出现缺口，电网要临时补；
4. 结算：补进来的电按高价买，多发的电只能贱卖——**同样大的误差，两个方向价钱不一样**；
5. 于是最省钱的申报不是最准的申报：**把预测往低压一点，总账反而更小**。

渲染服务只允许 manim、wq_anim、numpy、math、random，所以曲线与结算都在这里重算一遍。
"""
import numpy as np
from manim import *
from wq_anim import *

N = 48                      # 半小时一个点，画一天
PEAK = 400.0
UP, DOWN = 1.6, 0.5         # 少发按 1.6 倍买、多发按 0.5 倍卖（与算例 22.2 同一套假设）


def day_curves():
    t = np.arange(N) / N * 24.0
    shape = np.cos((t - 12.0) / 12.0 * np.pi / 2.0 * 2.0)
    clear = PEAK * np.clip(np.where((t >= 6) & (t <= 18), shape, 0.0), 0, None)
    cloud = np.ones(N)
    cloud[int(N * 13 / 24):int(N * 16 / 24)] = 0.45      # 下午真的来了一片厚云
    rng = np.random.default_rng(7)
    truth = np.maximum(clear * cloud * (1.0 + 0.10 * rng.normal(0.0, 1.0, N)), 0.0)
    fc_cloud = np.ones(N)
    fc_cloud[int(N * 13 / 24):int(N * 16 / 24)] = 0.80   # 预报只看见薄薄一层
    fc = np.maximum(clear * fc_cloud, 0.0)
    return t, truth, fc


def price_curve(t):
    p = np.full(N, 0.62)
    p[(t >= 8) & (t < 11)] = 1.05
    p[(t >= 18) & (t < 21)] = 1.05
    p[(t < 7) | (t >= 23)] = 0.28
    return p


def settle(truth, fc, price, bias=0.0):
    declared = np.maximum(fc + bias, 0.0)
    d = truth - declared
    short = np.maximum(-d, 0.0)
    over = np.maximum(d, 0.0)
    dt = 24.0 / N
    return float(np.sum(short * price * UP + over * price * DOWN) * dt)


class Lesson(Base):
    def construct(self):
        t, truth, fc = day_curves()
        price = price_curve(t)
        self.title("22.2", "预测误差怎样变成钱",
                   "How a forecast error turns into money")

        # ---------------- 一、真值与预测
        self.caption("下午来了一片厚云，预报只看见薄薄一层——于是报多了",
                     "The afternoon cloud came in thicker than forecast: the declaration was too high",
                     wait=1.4)
        ax = Axes(x_range=[0, 24, 6], y_range=[0, PEAK * 1.15, 100],
                  x_length=10.0, y_length=3.0,
                  axis_config={"include_tip": False, "color": MUTED}).shift(UP * 0.6)
        c_fc = ax.plot_line_graph(t, fc, line_color=STEEL, add_vertex_dots=False,
                                  stroke_width=3)["line_graph"]
        c_tr = ax.plot_line_graph(t, truth, line_color=INK, add_vertex_dots=False,
                                  stroke_width=3)["line_graph"]
        lab_fc = zh("预报（申报用的就是它）", 26, STEEL).next_to(ax, UP, buff=0.15)
        lab_tr = zh("实际出力", 26, INK).next_to(lab_fc, RIGHT, buff=0.8)
        self.play(Create(ax), run_time=0.8)
        self.play(Create(c_fc), FadeIn(lab_fc), run_time=1.2)
        self.play(Create(c_tr), FadeIn(lab_tr), run_time=1.2)

        band = VGroup(*[Line(ax.c2p(t[i], truth[i]), ax.c2p(t[i], fc[i]),
                             color=C_F, stroke_width=4)
                        for i in range(N) if fc[i] - truth[i] > 1.0])
        self.play(Create(band), run_time=1.2)
        self.caption("这一段红色就是误差：报了却没发出来的电",
                     "The red band is the error: power declared but never produced",
                     wait=1.8)
        self.clear_stage()

        # ---------------- 二、两个方向的价钱不一样
        self.caption("电网不按“差了多少”罚你，按“差在哪个方向”算账",
                     "The grid does not charge by size of error, but by its direction",
                     wait=1.6)
        bar_ax = Axes(x_range=[0, 3, 1], y_range=[0, 2.0, 0.5],
                      x_length=7.0, y_length=3.0,
                      axis_config={"include_tip": False, "color": MUTED})
        under = Rectangle(width=1.5, height=3.0 / 2.0 * UP, color=C_F,
                          fill_opacity=0.75, stroke_width=0)
        over = Rectangle(width=1.5, height=3.0 / 2.0 * DOWN, color=STEEL,
                         fill_opacity=0.75, stroke_width=0)
        under.move_to(LEFT * 2.2, aligned_edge=DOWN).align_to(bar_ax, DOWN)
        over.move_to(RIGHT * 2.2, aligned_edge=DOWN).align_to(bar_ax, DOWN)
        t1 = zh(f"少发 1 kWh：按 {UP:.1f} 倍电价买回来", 26, C_F).next_to(under, UP, buff=0.2)
        t2 = zh(f"多发 1 kWh：按 {DOWN:.1f} 倍电价贱卖", 26, STEEL).next_to(over, UP, buff=0.2)
        self.play(FadeIn(under), FadeIn(t1), run_time=1.0)
        self.play(FadeIn(over), FadeIn(t2), run_time=1.0)
        self.caption(f"同样大小的误差，往高报要贵 {UP / DOWN:.1f} 倍",
                     f"The same error costs {UP / DOWN:.1f}× more when you over-declare",
                     wait=2.0)
        self.clear_stage()

        # ---------------- 三、把申报往低压一点
        self.caption("既然两边不对称，最省钱的申报就不是最准的申报",
                     "Because the two sides differ, the cheapest declaration is not the truest",
                     wait=1.6)
        biases = np.arange(-150, 41, 5.0)
        costs = np.array([settle(truth, fc, price, b) for b in biases])
        rmses = np.array([float(np.sqrt(np.mean((np.maximum(fc + b, 0.0) - truth) ** 2)))
                          for b in biases])
        ax2 = Axes(x_range=[-150, 40, 50], y_range=[0, float(costs.max()) * 1.15, 200],
                   x_length=9.0, y_length=3.2,
                   axis_config={"include_tip": False, "color": MUTED}).shift(DOWN * 0.3)
        cc = ax2.plot_line_graph(biases, costs, line_color=C_F, add_vertex_dots=False,
                                 stroke_width=4)["line_graph"]
        self.play(Create(ax2), Create(cc), run_time=1.6)
        i_c, i_r = int(np.argmin(costs)), int(np.argmin(rmses))
        d_cost = Dot(ax2.c2p(biases[i_c], costs[i_c]), radius=0.12, color=YELLOW)
        d_rmse = Dot(ax2.c2p(biases[i_r], costs[i_r]), radius=0.12, color=STEEL)
        l1 = zh(f"成本最低：{biases[i_c]:+.0f} kW", 26, YELLOW).next_to(d_cost, DOWN, buff=0.3)
        l2 = zh(f"误差最低：{biases[i_r]:+.0f} kW", 26, STEEL).next_to(d_rmse, UP, buff=0.3)
        self.play(FadeIn(d_cost), FadeIn(l1), run_time=0.8)
        self.play(FadeIn(d_rmse), FadeIn(l2), run_time=0.8)
        self.caption(f"照成本调，这一天省 {(1 - costs[i_c] / costs[i_r]) * 100:.0f}%，"
                     f"代价是预测“更不准”了",
                     "Tuning on cost is cheaper, at the price of a worse-looking RMSE",
                     wait=2.2)

        self.card(["预测误差不是终点，账单才是",
                   "罚金不对称时，最优申报要往便宜的那一侧偏",
                   "“该报多少”的答案在电价规则里，不在模型里"], wait=3.2)
