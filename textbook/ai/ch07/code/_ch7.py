"""第 7 章共用（以下划线开头，构建时不单独运行）：实测所用显卡 A10 的规格、第 2 章的小型 Transformer 的尺寸，
以及按“急切执行”（逐个运算发出核函数）时一层前向计算的运算清单——7.1 节估算时间花在哪里、7.6 节估算激活占的显存、
7.8 节估算融合省下的流量，都从这一份清单出发。"""
from gpus import GPUS

A10 = dict(GPUS["a10"])
A10["tf32t"] = 62.5e12           # 数据手册：TF32 张量核心（稠密）

# 第 2 章的小型 Transformer（2.9 节）与 2.9 节、第 6 章用的训练批
V, T, D, L, H, F = 2048, 256, 384, 6, 6, 1536
DH = D // H
B = 32
PARAMS = 11532288                # 2.9 节：参数个数（程序 2.9.1 逐一核对过）


def layer_ops(b=B, t=T):
    """一层前向（前置层归一化，与 2.9 节相同；注意力按 2.9.2 节的写法，用矩阵乘法、缩放、掩码、softmax 逐步算），
    PyTorch 急切执行时发出的运算。每项：(名称, 类别, 读的元素数, 写的元素数, 乘加以外的说明)。
    类别 gemm 是矩阵乘法（交给 cuBLAS），其余是逐元素运算、归约与复制（各一个核函数）。
    线性层的偏置在 cuBLAS 的矩阵乘法里一并加上（PyTorch 的 addmm），不单列。
    注意力的 q、k、v 由 (b, t, h, d_h) 转置成 (b, h, t, d_h)，批量矩阵乘法要求每批之间步长相同，转置后的视图不满足，要先复制一份（7.2.4 节）。"""
    btd, s, btf = b * t * D, b * H * t * t, b * t * F
    return [
        ("ln1", "norm", btd, btd),
        ("qkv", "gemm", 0, 0),                      # 矩阵乘法的运算量另算，见 gemm_flop
        ("q 转置复制", "copy", btd, btd),                # q·kᵀ 之前复制 q、k；加权求和之前复制 v：各一个核函数
        ("k 转置复制", "copy", btd, btd),
        ("q·kᵀ", "gemm", 0, 0),
        ("缩放", "elem", s, s),
        ("因果掩码", "elem", s, s),
        ("softmax", "norm", s, s),
        ("v 转置复制", "copy", btd, btd),
        ("加权求和", "gemm", 0, 0),
        ("合并各头", "copy", btd, btd),
        ("输出投影", "gemm", 0, 0),
        ("残差 1", "elem", 2 * btd, btd),
        ("ln2", "norm", btd, btd),
        ("ff1", "gemm", 0, 0),
        ("GELU", "elem", btf, btf),
        ("ff2", "gemm", 0, 0),
        ("残差 2", "elem", 2 * btd, btd),
    ]


def gemm_flop(b=B, t=T):
    """一层前向各矩阵乘法的运算量（次）。"""
    n = b * t
    return {"qkv": 2 * n * D * 3 * D, "q·kᵀ": 2 * b * H * t * t * DH, "加权求和": 2 * b * H * t * t * DH,
            "输出投影": 2 * n * D * D, "ff1": 2 * n * D * F, "ff2": 2 * n * F * D}


def head_ops(b=B, t=T, loss=True):
    """各层之外：开头的词元嵌入加位置编码；最后的层归一化、输出层；loss 为真时再加损失——取前 t − 1 个位置的得分
    （切片后不连续，复制一份）、log_softmax（读写一遍）、按标签取值求平均（读的很少，按一个核函数计）。"""
    n = b * t
    ops = [("嵌入 + 位置编码", "elem", n * D, n * D), ("ln_f", "norm", n * D, n * D), ("输出层", "gemm", 0, 0)]
    if loss:
        m = b * (t - 1)
        ops += [("得分切片复制", "copy", m * V, m * V), ("log_softmax", "norm", m * V, m * V), ("nll_loss", "elem", m, 1)]
    return ops, 2 * n * D * V


def fused_layer_ops(b=B, t=T):
    """同一层交给图编译器（7.8 节）后的粗略估计：相邻的逐元素运算与归约合成一个核函数，中间结果不写回显存。
    残差加法与紧接着的层归一化合成一个（读残差流与子层输出，写新的残差流与归一化的结果）；缩放、掩码、softmax 合成一个；
    q、k、v 的转置复制假定合成一个核函数（流量不变）；GELU 不并进 cuBLAS 的矩阵乘法（编译器的默认做法），仍单独一个。
    第一层的 ln1 单独一个；以后各层的 ln1 与上一层的残差 2 合并——这里按“每层一份”计，合并的那一份记在残差 2 上。"""
    btd, s, btf = b * t * D, b * H * t * t, b * t * F
    return [
        ("q,k,v 转置复制", "copy", 3 * btd, 3 * btd),
        ("缩放+掩码+softmax", "norm", s, s),
        ("合并各头", "copy", btd, btd),
        ("残差 1 + ln2", "norm", 2 * btd, 2 * btd),
        ("GELU", "elem", btf, btf),
        ("残差 2 + 下一层 ln1", "norm", 2 * btd, 2 * btd),
    ]


def saved_activations(b=B, t=T):
    """训练时一层为反向保存的张量（元素个数），按 PyTorch 各运算的反向公式需要什么来列（7.6 节）。
    缩放（乘常数）与因果掩码（反向只要掩码本身，形状 t×t，很小）不存激活。
    同一块存储只计一次：q、k、v 的转置复制供 q·kᵀ 与加权求和使用；softmax 的输出既是它自己反向要用的，也是加权求和的输入。"""
    btd, s, btf, bt = b * t * D, b * H * t * t, b * t * F, b * t
    return [
        ("ln1 的输入 x（残差流）", btd),
        ("ln1 的均值与标准差倒数", 2 * bt),
        ("ln1 的输出（qkv 的输入）", btd),
        ("q、k、v 的复制", 3 * btd),
        ("softmax 的输出 P", s),
        ("合并各头的输出（输出投影的输入）", btd),
        ("ln2 的输入（残差流）", btd),
        ("ln2 的均值与标准差倒数", 2 * bt),
        ("ln2 的输出（ff1 的输入）", btd),
        ("ff1 的输出（GELU 的输入）", btf),
        ("GELU 的输出（ff2 的输入）", btf),
    ]


def saved_head(b=B, t=T):
    """全部层之后保存的：ln_f 的输入与统计量、ln_f 的输出（输出层的输入）、log_softmax 的输出。"""
    bt = b * t
    return [("ln_f 的输入、均值与标准差倒数", bt * D + 2 * bt), ("ln_f 的输出（输出层的输入）", bt * D), ("log_softmax 的输出", bt * V)]
