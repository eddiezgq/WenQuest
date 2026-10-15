import json, sys, numpy as np, soundfile as sf, sherpa_onnx as so
d="../kokoro-int8-multi-lang-v1_0/"
tts=so.OfflineTts(so.OfflineTtsConfig(model=so.OfflineTtsModelConfig(kokoro=so.OfflineTtsKokoroModelConfig(
  model=d+"model.int8.onnx",voices=d+"voices.bin",tokens=d+"tokens.txt",data_dir=d+"espeak-ng-data",dict_dir=d+"dict",
  lexicon=d+"lexicon-us-en.txt,"+d+"lexicon-zh.txt"),num_threads=4),
  rule_fsts=d+"date-zh.fst,"+d+"number-zh.fst,"+d+"phone-zh.fst",max_num_sentences=1))
beats=json.load(open("beats.json"))
sid=int(sys.argv[1]) if len(sys.argv)>1 else 49
out=[];t=0.6;sr=None;times=[]
pad=lambda s:np.zeros(int(sr*s),dtype=np.float32)
for b in beats:
    a=tts.generate(b["say"],sid=sid,speed=0.95); sr=a.sample_rate; x=np.array(a.samples,dtype=np.float32)
    if not out: out.append(pad(0.6))
    times.append({"start":round(t,3),"dur":round(len(x)/sr,3)})
    out.append(x); gap=b.get("pause",0.5); out.append(pad(gap)); t+=len(x)/sr+gap
out.append(pad(1.5)); t+=1.5
sf.write("voice.wav",np.concatenate(out),sr); json.dump({"beats":times,"total":round(t,3)},open("times.json","w"),indent=1); print(times, t)
