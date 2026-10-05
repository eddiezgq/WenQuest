import os, re, subprocess, sys, json
sys.path.insert(0, "/var/tmp/footage")
from tts import tts
OUT = "/var/tmp/footage/out"; T = "/var/tmp/footage/tmp"; os.makedirs(T, exist_ok=True)
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
def run(*a): subprocess.run(list(a), check=True)
def frames(f): return int(subprocess.run(["ffprobe","-v","error","-count_frames","-show_entries","stream=nb_read_frames","-select_streams","v","-of","csv=p=0",f],capture_output=True,text=True).stdout.strip())
# 1 修正无声版容器时长
for f in sorted(os.listdir(OUT)):
    if f.endswith(".mp4") and not f.endswith("_voice.mp4") and f.startswith("f") and not f.startswith("f00"):
        p = os.path.join(OUT, f); d = frames(p) / 30
        run("ffmpeg","-y","-loglevel","error","-i",p,"-t","%.3f" % d,"-c","copy","-movflags","+faststart",p + ".fix.mp4"); os.replace(p + ".fix.mp4", p)
def srt(name):
    out = []
    for blk in open(os.path.join(OUT, name + ".srt"), encoding="utf-8").read().strip().split("\n\n"):
        ls = blk.split("\n"); a, b = ls[1].split(" --> ")
        sec = lambda s: int(s[:2]) * 3600 + int(s[3:5]) * 60 + float(s[6:].replace(",", "."))
        out.append((sec(a), sec(b), ls[2]))
    return out
# 2 片头片尾
def card(name, title, sub, text):
    wav = os.path.join(T, name + ".wav"); d = tts(text, wav) + 1.2
    vf = ("color=c=0x0E3B43:s=1920x1080:d=%.2f,drawtext=fontfile=%s:text='%s':fontcolor=white:fontsize=96:x=(w-text_w)/2:y=420,"
          "drawtext=fontfile=%s:text='%s':fontcolor=0xF2C14E:fontsize=44:x=(w-text_w)/2:y=580") % (d, FONT, title, FONT, sub)
    run("ffmpeg","-y","-loglevel","error","-f","lavfi","-i",vf,"-i",wav,"-filter_complex","[1:a]adelay=500:all=1,apad[a]","-map","0:v","-map","[a]","-t","%.2f" % d,
        "-r","30","-c:v","libx264","-pix_fmt","yuv420p","-c:a","aac","-b:a","160k","-ar","44100",os.path.join(T, name + ".mp4"))
card("intro", "问渠数字工厂", "一张订单 · 从设计、仿真到制造和服务", "问渠数字工厂。一张减速器订单，从设计、仿真到制造、质量和售后服务，全部在一个平台上完成。")
card("outro", "问渠数字工厂", "CAD · CAE · CFD · MBD · CAM · ERP · MES · 数字孪生", "设计、仿真、制造、服务，用真实的工业软件和数据，在浏览器里学、在工厂里用。")
# 3 串联版：每个镜头取最有代表性的一句
PICK = [("f01_home", 0), ("f02_library", 1), ("f04_cad", 2), ("f06_cae", 3), ("f09_cfd", 3), ("f10_mbd", 2),
        ("f12_cam", 2), ("f13_mrp", 1), ("f14_mes", 2), ("f16_quality", 0), ("f18_twin", 1)]
parts = [os.path.join(T, "intro.mp4")]
for name, k in PICK:
    a, b, t = srt(name)[k]
    p = os.path.join(T, "%s_%d.mp4" % (name, k))
    run("ffmpeg","-y","-loglevel","error","-ss","%.2f" % max(0, a - 0.2),"-to","%.2f" % (b + 0.5),"-i",os.path.join(OUT, name + "_voice.mp4"),
        "-r","30","-c:v","libx264","-preset","slow","-crf","20","-pix_fmt","yuv420p","-c:a","aac","-b:a","160k","-ar","44100",p)
    parts.append(p)
parts.append(os.path.join(T, "outro.mp4"))
lst = os.path.join(T, "list.txt"); open(lst, "w").write("".join("file '%s'\n" % p for p in parts))
run("ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",lst,"-c","copy","-movflags","+faststart",os.path.join(OUT, "f00_overview_voice.mp4"))
run("ffmpeg","-y","-loglevel","error","-i",os.path.join(OUT, "f00_overview_voice.mp4"),"-an","-c:v","copy","-movflags","+faststart",os.path.join(OUT, "f00_overview.mp4"))
print("overview", frames(os.path.join(OUT, "f00_overview.mp4")) / 30)
