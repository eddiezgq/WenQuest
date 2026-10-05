"""算例 7.6.1、7.6.2：训练时显存花在哪里；重计算（激活检查点）省多少、多花多少。
小型 Transformer，B = 32，T = 256，单精度，AdamW。
（1）参数、梯度、优化器状态（AdamW 每个参数两个数：一阶矩与二阶矩）；
（2）为反向保存的激活：按 _ch7.saved_activations 逐项相加（每层），乘以层数，加上最后的层归一化与输出层；
（3）重计算：每层只保存它的输入（残差流），反向到这一层时重新做一遍这一层的前向。保存的激活降为每层一份残差流，
    外加反向时正在重计算的那一层的全部激活；运算量多一次前向（训练一步约为三次前向的运算量，变成四次）。"""
from _ch7 import B, D, L, PARAMS, T, saved_activations, saved_head
from bookout import out

MB = 1e6
state = PARAMS * 4 * (1 + 1 + 2)                           # 参数、梯度、两份 AdamW 状态
per_layer = {k: v * 4 for k, v in saved_activations()}
layer = sum(per_layer.values())
head = sum(v for _, v in saved_head()) * 4
act = L * layer + head
P_share = per_layer["softmax 的输出 P"] / layer
ff_share = (per_layer["ff1 的输出（GELU 的输入）"] + per_layer["GELU 的输出（ff2 的输入）"]) / layer
ckpt = L * B * T * D * 4 + layer + head                     # 每层一份残差流 + 正在重计算的一层 + 头部
total = state + act
total_ckpt = state + ckpt

out(state_MB=state / MB, params_MB=PARAMS * 4 / MB, layer_MB=layer / MB, act_MB=act / MB, head_MB=head / MB,
    P_pct=100 * P_share, ff_pct=100 * ff_share, total_MB=total / MB, act_ratio=act / state,
    ckpt_MB=ckpt / MB, total_ckpt_MB=total_ckpt / MB, saving=act / ckpt, extra_pct=100 / 3)
