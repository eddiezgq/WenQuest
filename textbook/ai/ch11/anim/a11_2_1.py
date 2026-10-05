"""动画 11.2.1（配图 11.2.1）：卷积网络的各层在看什么——从边缘到部件到物体。
第一层的卷积核响应的是边缘与方向；往后几层把边缘拼成角、弧与纹理；再往后拼成零件的局部（轴肩、键槽、倒角）；
最后几层的特征已经对应整个物体，分类器只需在这些特征上画一条界线。
动画用一张零件表面的图像演示前几层的响应，并说明"为什么加深有用"：每深一层，一个神经元能看到的范围（感受野）就大一圈。"""
from manim import *
from wq_anim import *


class Lesson(Base):
    def construct(self):
        self.title("11.2", "卷积网络各层在看什么", "What each layer of a convnet sees")

        # 一张示意的零件表面：横向纹理 + 一道斜划痕
        img = VGroup()
        for i in range(10):
            for j in range(10):
                sq = Square(0.38, stroke_width=0.6, color=GREY_B, fill_opacity=0.25, fill_color=GREY_B)
                sq.move_to([-5.2 + j * 0.4, 1.6 - i * 0.4, 0])
                img.add(sq)
        for d in range(6):                                  # 一道划痕
            img[(2 + d) * 10 + (2 + d)].set_fill(GREY_E, 0.85)
        self.play(FadeIn(img))
        self.caption("输入：零件表面的一小块，中间有一道划痕", "Input: a patch of the part surface with a scratch")

        stages = [("边缘与方向", "edges and orientations", BLUE),
                  ("角、弧与纹理", "corners, arcs, textures", GREEN),
                  ("零件的局部：轴肩、键槽", "part structures: shoulders, keyways", YELLOW),
                  ("整个缺陷：这是一道划痕", "the whole defect: a scratch", RED)]
        maps = VGroup()
        for i, (zh_t, en_t, col) in enumerate(stages):
            n = 8 - 2 * i                                   # 特征图越来越小
            g = VGroup()
            for r in range(n):
                for c in range(n):
                    sq = Square(2.4 / n, stroke_width=0.5, color=GREY_B, fill_opacity=0.15, fill_color=col)
                    sq.move_to([-1.6 + i * 1.9 + (c - n / 2) * 2.4 / n, 0.9 - (r - n / 2) * 2.4 / n, 0])
                    g.add(sq)
            maps.add(g)
        for i, (g, (zh_t, en_t, col)) in enumerate(zip(maps, stages)):
            self.play(FadeIn(g), run_time=0.5)
            hot = [g[k] for k in range(len(g)) if (k % max(len(g) // 6, 1)) == i % 3]
            self.play(*[s.animate.set_fill(col, 0.8) for s in hot], run_time=0.5)
            lab = bi([zh_t, en_t], 20)
            lab.next_to(g, DOWN, buff=0.25)
            self.play(FadeIn(lab), run_time=0.35)
            if i == 0:
                self.caption("第一层：每个卷积核只看 3×3 的小窗口，响应的是边缘与方向（2.8 节）",
                             "Layer 1: each 3×3 kernel responds to edges and orientations", wait=0.4)
            if i == 2:
                self.caption("越往后，一个神经元能看到的范围（感受野）越大，特征也越抽象",
                             "Deeper layers see a larger receptive field and more abstract features", wait=0.4)
        self.caption("最后几层的特征已经对应整个缺陷，分类器只需在这些特征上画一条界线",
                     "The last layers encode the whole defect; the classifier just draws a boundary there")
        self.card([["卷积网络为什么要深", "Why convnets are deep"],
                   ["每层只看一个小窗口，叠加后感受野线性变大，配上池化与步长则成倍扩大", "Each layer sees a small window; stacking grows the receptive field, pooling grows it faster"],
                   ["浅层的特征通用（边缘、纹理），深层的特征专用（这类零件的这种缺陷）",
                    "Shallow features are generic (edges, textures); deep ones are task-specific"],
                   ["这正是迁移学习管用的原因：换任务时多半只需换掉最后几层（11.1.3 节）",
                    "That is why transfer learning works: usually only the last layers need replacing"]])
