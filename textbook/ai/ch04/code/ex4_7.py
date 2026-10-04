"""算例 4.7.1、4.7.2：共享内存的存储体冲突（GPU 执行模拟器部分 ④）；矩阵转置各版本的显存扇区数（部分 ③）。"""
from bookout import out
from gpusim import addresses, bank_words, banks, coalesce

ways = {f"s{k}": banks(bank_words(kind="stride", k=k))["ways"] for k in (1, 2, 3, 4, 8, 16, 32)}
col0 = banks(bank_words(kind="column", pad=0))["ways"]
col1 = banks(bank_words(kind="column", pad=1))["ways"]
same = banks(bank_words(kind="same"))["ways"]
# 转置 8192×8192：一个线程束按行读 A（32 个相邻的 float），朴素版按列写 B（相隔 n 个 float）
n = 8192
read = coalesce(addresses(kind="contiguous"))["sectors"]
write_naive = coalesce(addresses(kind="stride", k=n))["sectors"]
traffic_naive = (read + write_naive) / (2 * read)              # 朴素版的扇区数是理想的几倍（不计 L2 缓存的合并）
smem_bytes = 32 * 32 * 4
smem_pad = 32 * 33 * 4
out(**ways, col0=col0, col1=col1, same=same, n=n, read=read, write_naive=write_naive, traffic_naive=traffic_naive,
    smem_KB=smem_bytes / 1024, smem_pad_B=smem_pad - smem_bytes)
