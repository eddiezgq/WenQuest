import sys, sherpa_onnx, soundfile as sf
D = "/var/tmp/vits-melo-tts-zh_en/"
_tts = None
def tts(text, out, speed=1.0, sid=0):
    global _tts
    if _tts is None:
        cfg = sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(vits=sherpa_onnx.OfflineTtsVitsModelConfig(
            model=D + "model.onnx", lexicon=D + "lexicon.txt", tokens=D + "tokens.txt", dict_dir=D + "dict"), num_threads=2),
            rule_fsts=D + "date.fst," + D + "phone.fst," + D + "number.fst", max_num_sentences=1)
        _tts = sherpa_onnx.OfflineTts(cfg)
    text = text.replace("：", "，").replace("；", "，").replace("“", "").replace("”", "").replace("（", "，").replace("）", "，")
    a = _tts.generate(text, sid=sid, speed=speed)
    sf.write(out, a.samples, a.sample_rate)
    return len(a.samples) / a.sample_rate
if __name__ == "__main__":
    print(tts(sys.argv[1], sys.argv[2]))
