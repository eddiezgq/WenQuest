"""语音识别与合成的公开发表数字（全书共用；第 12 章用）。

规矩：**只收论文正文或官方技术报告给出的原始数字**，排行榜与二手概括不收；每条都注明来源。
这些数字彼此不可直接比较——测试集、解码配置、训练数据量、是否零样本、归一化规则都不同，
详见 `docs/教材/人工智能/参考/第12章_语音历史数字资料_2026-10.md`。
"""

# ---------------------------------------------------------------- 英文电话对话（Switchboard / Hub5'00，词错率 %）
# Seide, Li, Yu. Conversational Speech Transcription Using Context-Dependent Deep Neural Networks.
# Interspeech 2011（论文正文，309 小时训练）
SWB_GMM_2011 = 27.4                 # 判别训练 GMM-HMM 基线
SWB_DNN_2011 = 18.5                 # CD-DNN-HMM（同一篇论文）

# Xiong et al. Achieving Human Parity in Conversational Speech Recognition.
# MSR-TR-2016-71 / arXiv:1610.05256（**2017-02 修订版**；初版数字不同，引用必须注明版本）
SWB_MS_2016 = 5.8                   # NIST 2000 CTS：Switchboard 子集
CH_MS_2016 = 11.0                   # 同上：CallHome 子集
SWB_HUMAN_MS = 5.9                  # 该论文测得的人类基准（Switchboard）
CH_HUMAN_MS = 11.3                  # 同上（CallHome）

# Saon et al. English Conversational Telephone Speech Recognition by Humans and Machines.
# Interspeech 2017 / arXiv:1703.02136（论文正文）
SWB_IBM_2017 = 5.5
CH_IBM_2017 = 10.3
SWB_HUMAN_IBM = 5.1                 # 投入更大的多人转写流程测得的人类基准
CH_HUMAN_IBM = 6.8

# ---------------------------------------------------------------- 英文朗读（LibriSpeech，词错率 %，test-clean / test-other）
# Panayotov, Chen, Povey, Khudanpur. LibriSpeech. ICASSP 2015（数据集论文基线，960 h + 4-gram full LM）
LS_GMM_2015 = (8.01, 22.49)         # SAT（GMM-HMM）；test-clean 的小数位另有 8.04 读数，待按 IEEE 正式版复核
LS_DNN_2015 = (5.51, 13.97)         # 同论文的 DNN 基线

# Baevski, Zhou, Mohamed, Auli. wav2vec 2.0. NeurIPS 2020 / arXiv:2006.11477（论文正文）
LS_W2V2_NOLM = (2.8, 6.3)           # LV-60k 预训练 + 960 h 微调，不用语言模型
LS_W2V2_LM = (2.0, 4.1)             # 同上 + Transformer 语言模型
LS_W2V2_10MIN = (4.8, 8.2)          # **只用 10 分钟**有标注数据 + Transformer 语言模型

# Gulati et al. Conformer. Interspeech 2020 / arXiv:2005.08100（论文正文，118.8 M 参数）
LS_CONFORMER_NOLM = (2.1, 4.3)
LS_CONFORMER_LM = (1.9, 3.9)

# Radford et al. Robust Speech Recognition via Large-Scale Weak Supervision. arXiv:2212.04356 / ICML 2023
LS_WHISPER_ZS = (2.7, 5.2)          # large-v2，**零样本**（未在 LibriSpeech 训练集上训练）
WHISPER_SWB_ZS = 13.8               # 同一模型在 Switchboard 上的零样本词错率
WHISPER_CH_ZS = 17.6                # 同上，CallHome
WHISPER_HOURS = 680_000             # 弱监督音频总时长（小时）
WHISPER_HOURS_MULTI = 117_000       # 其中非英语识别部分
WHISPER_HOURS_X2EN = 125_000        # X→英语翻译部分
WHISPER_LANGS = 96                  # 非英语部分覆盖的语言数（英语之外）

# ---------------------------------------------------------------- 中文朗读（AISHELL，字错率 %，dev / test）
# Bu, Du, Na, Wu, Zheng. AISHELL-1. O-COCOSDA 2017 / arXiv:1709.05522（论文正文）
AISHELL1_GMM = (10.43, 12.23)       # MLLT+SAT（GMM-HMM）
AISHELL1_TDNN = (7.23, 8.42)
AISHELL1_CHAIN = (6.44, 7.62)       # LF-MMI，该论文最优基线
AISHELL1_SPK, AISHELL1_HOURS = 400, 170

# Du, Na, Liu, Bu. AISHELL-2. arXiv:1808.10583（论文正文，test 三路采音：iOS / Android / 高保真麦克风）
AISHELL2_TRI3 = (19.77, 21.00, 21.10)
AISHELL2_CHAIN = (8.81, 9.59, 10.87)
AISHELL2_HOURS, AISHELL2_SPK = 1000, 1991

# ---------------------------------------------------------------- 音素错误率（TIMIT core test，%）
TIMIT_DBN = 20.7                    # Mohamed, Dahl, Hinton. Acoustic Modeling using Deep Belief Networks. TASLP 2012
TIMIT_HMM_BMMI = 22.7               # 同表的判别训练三音素 HMM 对照
TIMIT_BLSTM = 17.7                  # Graves, Mohamed, Hinton. ICASSP 2013 / arXiv:1303.5778（RNN-T + 预训练）

# ---------------------------------------------------------------- 合成的自然度（MOS，5 分制）
# van den Oord et al. WaveNet. arXiv:1609.03499（论文正文；英语 / 普通话，括号内为 95% 置信半宽）
MOS_WAVENET = (4.21, 4.08)
MOS_LSTM_PARAM = (3.67, 3.79)       # LSTM-RNN 参数合成
MOS_CONCAT = (3.86, 3.47)           # HMM 驱动拼接合成
MOS_REAL_WAVENET = (4.55, 4.21)     # 真人录音（16 位线性 PCM），**该论文自己的上限**

# Shen et al. Natural TTS Synthesis by Conditioning WaveNet on Mel Spectrogram Predictions.
# ICASSP 2018 / arXiv:1712.05884（论文正文，英文单说话人）
MOS_TACOTRON2 = 4.526
MOS_REAL_TACOTRON2 = 4.582          # 该论文自己的真人录音基准
MOS_TACOTRON1 = 4.001               # Tacotron + Griffin-Lim
MOS_PARAM_T2 = 3.492                # 参数合成对照
