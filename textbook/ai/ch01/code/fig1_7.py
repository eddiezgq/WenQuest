"""1.7 节的示意图。

图 1.7.1：全书路线图：上篇三个部分（第 1–10 章）与下篇六个部分（第 11–32 章）；箭头表示下篇各部分主要依赖的上篇内容。
"""
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

from bookout import COLORS, T, figure, style

plt = style()
C = COLORS

fig, ax = plt.subplots(figsize=(10.6, 6.0))
ax.set_xlim(0, 10.6)
ax.set_ylim(0, 6.2)
ax.axis("off")


def box(x, y, w, h, title, body, fc, ec):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc=fc, ec=ec, lw=1.3))
    ax.text(x + 0.12, y + h - 0.2, title, fontsize=10, weight="bold", color=ec, va="top")
    ax.text(x + 0.12, y + h - 0.55, body, fontsize=8.4, color=C["ink"], va="top", linespacing=1.45)


ax.text(0.2, 5.95, T("上篇　人工智能与 CUDA（第 1–10 章）", "Part One  AI and CUDA (Chapters 1–10)"), fontsize=12, weight="bold", color=C["z"])
up = [(T("基础与原理", "Foundations"), T("1 概论\n2 深度学习基础\n3 GPU 体系结构", "1 Introduction\n2 Deep learning basics\n3 GPU architecture")),
      (T("CUDA 编程", "CUDA programming"), T("4 编程模型与内存层次\n5 并行模式与矩阵乘法\n6 流、多 GPU 与调优", "4 Model and memory\n5 Patterns and GEMM\n6 Streams, multi-GPU, tuning")),
      (T("CUDA 上的 AI 系统", "AI systems on CUDA"), T("7 CUDA 库与框架内幕\n8 混合精度、量化、Triton\n9 大模型训练与推理\n10 异构算力与国产生态",
                                                   "7 Libraries and frameworks\n8 Precision, quantization, Triton\n9 LLM training and inference\n10 Heterogeneous and domestic"))]
for k, (t, b) in enumerate(up):
    box(0.2 + 3.45 * k, 3.75, 3.25, 2.0, t, b, "#eef3f8", C["z"])
for k in range(2):
    ax.add_patch(FancyArrowPatch((3.45 + 3.45 * k, 4.75), (3.65 + 3.45 * k, 4.75), arrowstyle="-|>", mutation_scale=14, lw=1.4,
                                 color=C["z"]))
ax.text(0.2, 3.35, T("下篇　人工智能典型与成功应用（第 11–32 章）", "Part Two  Landmark AI applications (Chapters 11–32)"), fontsize=12,
        weight="bold", color=C["accent"])
down = [(T("感知与语言", "Perception and language"), T("11 计算机视觉　12 语音\n13 大语言模型　14 多模态", "11 vision   12 speech\n13 large language models   14 multimodal")),
        (T("决策与生成", "Decision and generation"), T("15 博弈与强化学习　16 生成式 AI\n17 编程助手与智能体", "15 games and RL   16 generative AI\n17 coding assistants and agents")),
        (T("科学与工程", "Science and engineering"), T("18 生命科学　19 地球科学　20 材料\n21 智能制造　22 能源与工业控制", "18 life   19 earth   20 materials\n21 manufacturing   22 energy and control")),
        (T("移动与具身", "Mobility and embodiment"), T("23 自动驾驶　24 机器人与具身智能\n25 无人机与智能物流", "23 driving   24 robots, embodied AI\n25 drones and logistics")),
        (T("社会与服务", "Society and services"), T("26 医疗　27 金融　28 推荐\n29 智慧教育　30 智慧城市", "26 health   27 finance   28 recommendation\n29 education   30 cities")),
        (T("展望与治理", "Outlook and governance"), T("31 安全、伦理与治理\n32 人工智能的未来", "31 safety, ethics, governance\n32 the future of AI"))]
for k, (t, b) in enumerate(down):
    x = 0.2 + 3.45 * (k % 3)
    y = 1.85 if k < 3 else 0.55
    box(x, y, 3.25, 1.15, t, b, "#fdf3dc", C["accent"])
ax.add_patch(FancyArrowPatch((9.9, 3.7), (9.9, 3.05), arrowstyle="<|-|>", mutation_scale=16, lw=1.6, color=C["muted"]))
ax.text(9.75, 3.37, T("互相回扣", "traced back"), fontsize=8.8, color=C["muted"], va="center", ha="right")
ax.text(0.2, 0.2, T("贯穿全书：零件库机器人与数字工厂数据；一个约一千万参数的小型 Transformer；浏览器实验 + 云端 GPU 实验",
                    "Throughout: library robots and digital-factory data; a ~10M-parameter Transformer; browser labs + cloud-GPU labs"),
        fontsize=8.8, color=C["ink"])
figure(fig, "fig1_7_1")
plt.close(fig)
