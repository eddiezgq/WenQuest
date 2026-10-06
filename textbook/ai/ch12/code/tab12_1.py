"""12.99 节“公开发表的数字”那张表里的每个数。

数据全部来自 conventions/asr_history.py（只收论文正文或官方技术报告给出的原始数字）。
这个程序不做计算，只把它们交给正文——这样表里的数字不是手打的，改一处就只改数据那一处。
唯一算出来的几个量是“与该论文自己的真人基准之间的差距”“两个人类基准之间的差距”，
因为 MOS 与“人类水平”都只在各自那一批测试里可比。
"""
from asr_history import (AISHELL1_CHAIN, AISHELL1_GMM, AISHELL1_HOURS, AISHELL1_SPK, AISHELL1_TDNN,
                         AISHELL2_CHAIN, AISHELL2_HOURS, AISHELL2_TRI3, CH_HUMAN_IBM, CH_HUMAN_MS,
                         CH_IBM_2017, CH_MS_2016, LS_CONFORMER_LM, LS_CONFORMER_NOLM, LS_DNN_2015,
                         LS_GMM_2015, LS_W2V2_10MIN, LS_W2V2_LM, LS_W2V2_NOLM, LS_WHISPER_ZS,
                         MOS_REAL_TACOTRON2, MOS_REAL_WAVENET, MOS_TACOTRON2, MOS_WAVENET,
                         SWB_DNN_2011, SWB_GMM_2011, SWB_HUMAN_IBM, SWB_HUMAN_MS, SWB_IBM_2017,
                         SWB_MS_2016, TIMIT_BLSTM, TIMIT_DBN, WHISPER_CH_ZS, WHISPER_HOURS,
                         WHISPER_HOURS_MULTI, WHISPER_HOURS_X2EN, WHISPER_LANGS, WHISPER_SWB_ZS)
from bookout import out

v = {
    # 英文电话对话（Switchboard / CallHome，词错率）
    "swb_gmm_2011": SWB_GMM_2011, "swb_dnn_2011": SWB_DNN_2011,
    "swb_ms_2016": SWB_MS_2016, "ch_ms_2016": CH_MS_2016,
    "swb_human_ms": SWB_HUMAN_MS, "ch_human_ms": CH_HUMAN_MS,
    "swb_ibm_2017": SWB_IBM_2017, "ch_ibm_2017": CH_IBM_2017,
    "swb_human_ibm": SWB_HUMAN_IBM, "ch_human_ibm": CH_HUMAN_IBM,
    # 英文朗读（LibriSpeech，test-clean / test-other）
    "ls_gmm_c": LS_GMM_2015[0], "ls_gmm_o": LS_GMM_2015[1],
    "ls_dnn_c": LS_DNN_2015[0], "ls_dnn_o": LS_DNN_2015[1],
    "ls_w2v2_c": LS_W2V2_NOLM[0], "ls_w2v2_o": LS_W2V2_NOLM[1],
    "ls_w2v2lm_c": LS_W2V2_LM[0], "ls_w2v2lm_o": LS_W2V2_LM[1],
    "ls_w2v2_10min_c": LS_W2V2_10MIN[0], "ls_w2v2_10min_o": LS_W2V2_10MIN[1],
    "ls_conf_c": LS_CONFORMER_NOLM[0], "ls_conf_o": LS_CONFORMER_NOLM[1],
    "ls_conflm_c": LS_CONFORMER_LM[0], "ls_conflm_o": LS_CONFORMER_LM[1],
    "ls_whisper_c": LS_WHISPER_ZS[0], "ls_whisper_o": LS_WHISPER_ZS[1],
    "whisper_swb": WHISPER_SWB_ZS, "whisper_ch": WHISPER_CH_ZS,
    "whisper_h": WHISPER_HOURS, "whisper_h_multi": WHISPER_HOURS_MULTI,
    "whisper_h_x2en": WHISPER_HOURS_X2EN, "whisper_langs": WHISPER_LANGS,
    # 中文朗读（AISHELL，字错率）
    "as1_gmm": AISHELL1_GMM[1], "as1_tdnn": AISHELL1_TDNN[1], "as1_chain": AISHELL1_CHAIN[1],
    "as1_spk": AISHELL1_SPK, "as1_hours": AISHELL1_HOURS,
    "as2_tri3": AISHELL2_TRI3[0], "as2_chain": AISHELL2_CHAIN[0], "as2_hours": AISHELL2_HOURS,
    # 音素错误率（TIMIT）
    "timit_dbn": TIMIT_DBN, "timit_blstm": TIMIT_BLSTM,
    # 合成的自然度（MOS）
    "mos_wavenet": MOS_WAVENET[0], "mos_wavenet_zh": MOS_WAVENET[1],
    "mos_real_wavenet": MOS_REAL_WAVENET[0],
    "mos_tacotron2": MOS_TACOTRON2, "mos_real_tacotron2": MOS_REAL_TACOTRON2,
}
# MOS 只在同一批听测内可比，所以记录“与本论文自己的真人基准差多少”，而不是跨论文比绝对分
v["mos_gap_wavenet"] = MOS_REAL_WAVENET[0] - MOS_WAVENET[0]
v["mos_gap_tacotron2"] = MOS_REAL_TACOTRON2 - MOS_TACOTRON2
# 两个人类基准之间差多少——“人类水平”取决于转写流程投入多少，不是常数
v["human_spread_swb"] = SWB_HUMAN_MS - SWB_HUMAN_IBM
v["human_spread_ch"] = CH_HUMAN_MS - CH_HUMAN_IBM
# 同一个模型从朗读换到电话对话，词错率翻几倍（零样本，归一化规则一致，所以这个倍数可比）
v["whisper_domain_x"] = WHISPER_CH_ZS / LS_WHISPER_ZS[0]
out(**v)
