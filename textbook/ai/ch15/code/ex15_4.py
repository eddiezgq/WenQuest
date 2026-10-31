"""算例 15.4.1—15.4.3：去掉人类棋谱，再去掉规则（15.4 节）。

（1）三代系统的账：学了什么、要多少自我对弈、要多少机器。
（2）"搜得少却下得好"：AlphaZero 每秒看的局面比 Stockfish 少三个数量级。
（3）MuZero 把规则也换成学出来的模型，而且在 Atari 上每步只搜 50 次。
"""
import numpy as np

from bookout import out
from rl_facts import ALPHAGO, ALPHAGO_ZERO, ALPHAZERO_ARXIV, ALPHAZERO_SCIENCE, MUZERO

v = {}
# ---------- （1）三代的账
v["ag_kgs_games_w"] = ALPHAGO["kgs_games"] / 1e4
v["agz_games_3d_w"] = ALPHAGO_ZERO["selfplay_games_3d"] / 1e4
v["agz_games_40d_w"] = ALPHAGO_ZERO["selfplay_games_40d"] / 1e4
v["agz_days_3d"], v["agz_days_40d"] = ALPHAGO_ZERO["days_3d"], ALPHAGO_ZERO["days_40d"]
v["agz_batches_w"] = ALPHAGO_ZERO["batches_3d"] / 1e4
v["agz_batch"] = ALPHAGO_ZERO["batch"]
v["agz_positions_yi"] = ALPHAGO_ZERO["batches_3d"] * ALPHAGO_ZERO["batch"] / 1e8   # 折算：看过多少个局面（亿）
v["agz_vs_lee"] = f"{ALPHAGO_ZERO['vs_lee'][0]}:{ALPHAGO_ZERO['vs_lee'][1]}"
v["agz_vs_master"] = f"{ALPHAGO_ZERO['vs_master'][0]}:{ALPHAGO_ZERO['vs_master'][1]}"
v["agz_tpu_play"], v["lee_tpu"] = ALPHAGO_ZERO["tpu_play"], ALPHAGO_ZERO["lee_tpu"]
v["tpu_ratio"] = ALPHAGO_ZERO["lee_tpu"] / ALPHAGO_ZERO["tpu_play"]
v["agz_tpu_train_known"] = ALPHAGO_ZERO["tpu_train"] is not None
assert not v["agz_tpu_train_known"], "训练用多少 TPU，论文没给——只给了对局用 4 块"
# 一个反直觉的事实：自对弈网络预测人类下一手的准确率反而更低
v["acc_selfplay"], v["acc_supervised"] = ALPHAGO_ZERO["acc_zero40"], ALPHAGO_ZERO["acc_supervised"]
v["acc_gap"] = v["acc_supervised"] - v["acc_selfplay"]
assert v["acc_gap"] > 0, "监督网络更会猜人类的下一手，棋力却不如自对弈出来的"

# ---------- （2）搜得少却下得好（Science 版口径）
v["az_nps_chess"] = ALPHAZERO_SCIENCE["nps_chess"]
v["sf_nps"] = ALPHAZERO_SCIENCE["nps_stockfish"]
v["nps_ratio"] = v["sf_nps"] / v["az_nps_chess"]                 # 折算：论文只给两个绝对值
v["az_sims_train"] = ALPHAZERO_ARXIV["sims_per_move"]
v["az_hours_chess"] = ALPHAZERO_SCIENCE["hours_chess"]
v["az_tpu_selfplay"] = ALPHAZERO_SCIENCE["tpu_selfplay"]
v["az_tpu_train_sci"], v["az_tpu_train_arxiv"] = ALPHAZERO_SCIENCE["tpu_train"], ALPHAZERO_ARXIV["tpu_train"]
v["az_go_days_sci"], v["az_go_hours_arxiv"] = ALPHAZERO_SCIENCE["days_go"], ALPHAZERO_ARXIV["hours_go"]
v["az_go_ratio"] = ALPHAZERO_SCIENCE["days_go"] * 24 / ALPHAZERO_ARXIV["hours_go"]   # 两版差多少倍
assert v["az_go_ratio"] > 5, "同一件事，两版论文给的围棋训练时长差了好几倍——引用必须说明是哪一版"
v["az_vs_sf_win"], v["az_vs_sf_loss"] = ALPHAZERO_SCIENCE["vs_stockfish_1000"]
v["az_vs_sf_draw"] = 1000 - v["az_vs_sf_win"] - v["az_vs_sf_loss"]

# ---------- （3）MuZero：连规则都不给
v["mz_sims_board"], v["mz_sims_atari"] = MUZERO["sims_board"], MUZERO["sims_atari"]
v["mz_sims_ratio"] = MUZERO["sims_board"] / MUZERO["sims_atari"]
v["mz_mean"], v["mz_median"] = MUZERO["mean_human_norm"], MUZERO["median_human_norm"]
v["r2d2_mean"], v["r2d2_median"] = MUZERO["r2d2_mean"], MUZERO["r2d2_median"]
v["mz_games"] = MUZERO["atari_games"]
v["mz_frames_yi"] = MUZERO["frames_atari"] / 1e8                 # 亿帧
v["mz_hours"] = MUZERO["hours_atari"]
v["mz_tpu_train"], v["mz_tpu_selfplay"] = MUZERO["tpu_train_board"], MUZERO["tpu_selfplay_board"]
v["mz_tpu_ratio"] = MUZERO["tpu_selfplay_board"] / MUZERO["tpu_train_board"]
v["mz_reanalyze_frames_yi"] = MUZERO["reanalyze_frames"] / 1e8
v["mz_reanalyze_median"] = MUZERO["reanalyze_median"]
v["mz_data_ratio"] = MUZERO["frames_atari"] / MUZERO["reanalyze_frames"]
v["mz_median_drop"] = MUZERO["median_human_norm"] / MUZERO["reanalyze_median"]
assert v["mz_tpu_ratio"] > 10, "自我对弈才是算力的大头：造数据的机器比训练的多得多"
v["mz_elo_known"] = MUZERO["elo_board"] is not None
assert not v["mz_elo_known"], "棋类的 Elo，论文没给"
out(**v)
