"""算例 11.1.1—11.1.3：图像分类的三个数（11.1、11.2 节）。

（1）ImageNet 之难：1000 个类、128 万张训练图。随机猜的正确率、“前五名里有一个对”的随机正确率，
    以及 2012 年前后的错误率对照——AlexNet 的 top-5 错误率比上一年的冠军低了多少个百分点。
（2）各代网络的参数量与运算量：AlexNet、VGG-16、ResNet-50、ViT-B/16 处理一张 224×224 的图要多少次乘加、多少参数。
    卷积层按 2·K·C·R·S·H′·W′ 计（一次乘加算两次运算），全连接层按 2·输入·输出；ViT 按 Transformer 的公式（2.10 节）。
    这些数都由结构算出，不抄厂商或论文的概数。
（3）每秒 60 帧、3840×2160 的检测工位上，这几个网络各要多少算力；A10 的半精度峰值够不够（第 3 章的屋顶线）。
"""
import numpy as np

from bookout import out

from _ch11 import MODELS, TOP1, V, IMGS
from ilsvrc import ALEX_2012_ONLY, ALEX_2012_SECOND, ILSVRC

v = {"V": V, "imgs": IMGS, "rand1": 100 / V, "rand5": 500 / V}
# （1）2012 年的突破：ILSVRC 2011 冠军 top-5 错误率 25.8%，2012 年 AlexNet 16.4%
# ILSVRC 各年的 top-5 错误率与第 1 章共用同一张表（_ch1.ILSVRC），避免同一本书给出两个数
v["err2011"] = dict((y, e) for y, e, _ in ILSVRC)[2011]
v["err2012"] = dict((y, e) for y, e, _ in ILSVRC)[2012]             # 夺冠提交（用了额外数据）
v["err2012_only"] = ALEX_2012_ONLY                                  # 只用竞赛数据的那次提交
v["err2012_second"] = ALEX_2012_SECOND                              # 当年第二名的传统方法
v["gain"] = v["err2012_second"] - v["err2012"]
v["err2015"] = dict((y, e) for y, e, _ in ILSVRC)[2015]
for k, (f, p) in MODELS.items():
    v[k + "_GF"] = f / 1e9                                          # 一张图的运算量（GFLOP）
    v[k + "_M"] = p / 1e6                                           # 参数量（百万）
    v[k + "_top1"] = TOP1[k]
# （3）检测工位：每秒 60 帧
from gpus import GPUS                                                # 全书共用的硬件规格表
FPS, A10_FP16 = 60, GPUS["a10"]["fp16t"]
for k, (f, _) in MODELS.items():
    v[k + "_util"] = f * FPS / A10_FP16 * 100                       # 占 A10 半精度峰值的百分之几
v["fps"] = FPS
v["vgg_over_alex"] = MODELS["vgg"][0] / MODELS["alex"][0]           # VGG-16 的运算量是 AlexNet 的几倍
out(**v)
