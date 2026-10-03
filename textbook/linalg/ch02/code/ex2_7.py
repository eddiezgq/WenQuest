"""2.7 节：n 维向量——振动信号、维修记录的词频向量、减速器的检测记录；标准化与余弦相似度。"""
import math

import numpy as np

from bookout import out, tex, vec
from ex2_7_data import FAULTS, ITEMS, MU, RECORDS, SIGMA, cos, z

# 振动信号：1 ms 采样一次的 8 个值（m/s²），它的长度与均方根值
t = np.arange(8) * 1e-3
x = np.round(2.0 * np.sin(2 * math.pi * 125 * t) + 0.5 * np.sin(2 * math.pi * 250 * t), 2)
out(sig=vec(x, 2), sig_norm=float(np.linalg.norm(x)), sig_rms=float(np.linalg.norm(x) / math.sqrt(len(x))))
# 维修记录的词频：词表（轴承, 异响, 温度, 齿轮, 跳动, 更换）
docs = np.array([[2, 1, 1, 0, 0, 1], [0, 1, 0, 2, 2, 0], [6, 3, 4, 0, 0, 3]], float)
out(d1=vec(docs[0], 0), d2=vec(docs[1], 0), d3=vec(docs[2], 0),
    c12=cos(docs[0], docs[1]), c13=cos(docs[0], docs[2]), c23=cos(docs[1], docs[2]),
    dist13=float(np.linalg.norm(docs[2] - docs[0])), dist12=float(np.linalg.norm(docs[1] - docs[0])), dist23=float(np.linalg.norm(docs[2] - docs[1])))
# 检测记录：先不标准化，直接比较记录 2 与记录 5 —— 余弦几乎是 1，被数值大的“噪声”一项主宰
r2, r5 = RECORDS[1], RECORDS[4]
out(r2=vec(r2, 2), r5=vec(r5, 2), raw25=cos(r2, r5))
# 标准化：z = (x − μ)/σ，各项都变成“偏离了几个标准差”
out(mu=vec(MU, 1), sigma=vec(SIGMA, 2), z2=vec(z(r2), 2), z5=vec(z(r5), 2), z25=cos(z(r2), z(r5)),
    z2n=float(np.linalg.norm(z(r2))), z5n=float(np.linalg.norm(z(r5))))
# 每份记录与三种故障特征方向的余弦相似度
names = list(FAULTS)
S = np.array([[cos(z(r), FAULTS[f]) for f in names] for r in RECORDS])
norms = np.linalg.norm((RECORDS - MU) / SIGMA, axis=1)
best = [names[int(np.argmax(S[i]))] if norms[i] > 2.5 else "正常" for i in range(len(RECORDS))]
out(S=tex(S, 2), norms=vec(norms, 2), best="、".join(f"记录 {i + 1}：{b}" for i, b in enumerate(best)),
    s2=float(S[1, 0]), s3=float(S[2, 1]), s4=float(S[3, 2]), n1=float(norms[0]), n2=float(norms[1]),
    s1g=float(S[0, 1]), s8=float(S[7, 2]), n8=float(norms[7]))
# 欧氏距离与余弦的区别：记录 6 与记录 2 方向相近、程度不同
out(c26=cos(z(RECORDS[5]), z(RECORDS[1])), d26=float(np.linalg.norm(z(RECORDS[5]) - z(RECORDS[1]))), n6=float(norms[5]))
