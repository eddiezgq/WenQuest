"""算例 1.1.1：同一个测试集上，两个垃圾邮件过滤器的准确率、精确率与召回率。

测试集 10 000 封邮件，其中垃圾邮件 2000 封（占 20%）。
过滤器甲：一律判为“正常邮件”。
过滤器乙：混淆矩阵 TP = 1800（垃圾判为垃圾），FN = 200，FP = 150（正常判为垃圾），TN = 7850。
式 (1.1.3)～(1.1.6)：准确率、精确率、召回率、F1。
"""
from bookout import out

n, spam = 10000, 2000
ham = n - spam


def scores(tp, fn, fp, tn):
    acc = (tp + tn) / (tp + fn + fp + tn)
    prec = tp / (tp + fp) if tp + fp else float("nan")       # 甲从不判“垃圾”，精确率无定义
    rec = tp / (tp + fn)
    f1 = 2 * prec * rec / (prec + rec) if tp else 0.0
    return acc, prec, rec, f1


acc_a, prec_a, rec_a, f1_a = scores(0, spam, 0, ham)
tp, fn, fp, tn = 1800, 200, 150, 7850
assert tp + fn == spam and fp + tn == ham
acc_b, prec_b, rec_b, f1_b = scores(tp, fn, fp, tn)

# 误判正常邮件的代价：若每误删一封正常邮件损失 10 元，每漏过一封垃圾邮件损失 0.1 元
cost_fp, cost_fn = 10.0, 0.1
cost_a = 0 * cost_fp + spam * cost_fn
cost_b = fp * cost_fp + fn * cost_fn

out(spam_pct=spam / n * 100, acc_a_pct=acc_a * 100, rec_a_pct=rec_a * 100,
    acc_b_pct=acc_b * 100, prec_b_pct=prec_b * 100, rec_b_pct=rec_b * 100, f1_b=f1_b,
    cost_a=cost_a, cost_b=cost_b)
