# 录屏工具：1920×1080，假鼠标（headless 不画光标），慢动作，关键帧，webm→mp4
import json, os, subprocess, time, urllib.request
from playwright.sync_api import sync_playwright

HUB = "http://localhost:8100"
OUT = "/var/tmp/footage/out"
RAW = "/var/tmp/footage/raw"
CURSOR = r"""
(() => {
  if (window.__wqc) return; window.__wqc = 1;
  const mk = () => {
    const c = document.createElement('div');
    c.id = '__cursor';
    c.innerHTML = '<svg width="26" height="26" viewBox="0 0 26 26"><path d="M3 2 L3 21 L8 16.5 L11.5 24 L15 22.5 L11.5 15 L18 15 Z" fill="#111" stroke="#fff" stroke-width="1.6" stroke-linejoin="round"/></svg>';
    Object.assign(c.style, {position: 'fixed', left: '0px', top: '0px', zIndex: 2147483647, pointerEvents: 'none', transform: 'translate(-3px,-2px)'});
    const ring = document.createElement('div'); ring.id = '__ring';
    Object.assign(ring.style, {position: 'fixed', width: '34px', height: '34px', borderRadius: '50%', border: '3px solid rgba(240,140,0,.9)', zIndex: 2147483646, pointerEvents: 'none', opacity: 0, transition: 'opacity .25s, transform .25s', transform: 'translate(-17px,-17px) scale(.4)'});
    document.body.appendChild(ring); document.body.appendChild(c);
    document.addEventListener('mousemove', (e) => { c.style.left = e.clientX + 'px'; c.style.top = e.clientY + 'px'; ring.style.left = e.clientX + 'px'; ring.style.top = e.clientY + 'px'; }, true);
    document.addEventListener('mousedown', () => { ring.style.opacity = 1; ring.style.transform = 'translate(-17px,-17px) scale(1)'; setTimeout(() => { ring.style.opacity = 0; ring.style.transform = 'translate(-17px,-17px) scale(.4)'; }, 350); }, true);
  };
  if (document.body) mk(); else document.addEventListener('DOMContentLoaded', mk);
})();
"""


def login(name="演示厂长", role="manager", mode="teach"):
    r = urllib.request.Request(HUB + "/api/login", data=json.dumps({"name": name, "role": role, "mode": mode}).encode(),
                               headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(r).read())


def api(method, path, body=None, tok=None):
    r = urllib.request.Request(HUB + path, method=method, data=json.dumps(body).encode() if body is not None else None,
                               headers={"Content-Type": "application/json", **({"x-wq-token": tok} if tok else {})})
    return json.loads(urllib.request.urlopen(r, timeout=300).read() or b"null")


class Shot:
    def __init__(self, name, role="manager", user="演示厂长", mode="teach"):
        self.name, self.t = name, login(user, role, mode)
        self.pw = sync_playwright().start()
        self.b = self.pw.chromium.launch(args=["--use-gl=swiftshader", "--enable-webgl", "--ignore-gpu-blocklist"])
        d = os.path.join(RAW, name)
        os.makedirs(d, exist_ok=True)
        for f in os.listdir(d):
            os.remove(os.path.join(d, f))
        self.ctx = self.b.new_context(viewport={"width": 1920, "height": 1080}, record_video_dir=d,
                                      record_video_size={"width": 1920, "height": 1080}, accept_downloads=True)
        sess = json.dumps({"token": self.t["token"], "user": self.t["user"]})
        self.ctx.add_init_script("try{if(!localStorage.getItem('wq-rec-sw'))localStorage.setItem('wq-df-session', %s)}catch(e){}" % json.dumps(sess))
        self.ctx.add_init_script(CURSOR)
        self.pg = self.ctx.new_page()
        self.errs = []
        self.pg.on("pageerror", lambda e: self.errs.append(str(e)))
        self.t0 = time.time()
        self.start = None
        self.x, self.y = 960, 540
        self.lines, self._due = [], 0.0
        self.cuts = []

    def cut(self, a, b):
        """剪掉 [a, b]（镜头内秒数）这段等待"""
        if b - a > 0.5:
            self.cuts.append((a, b))

    def prep(self, texts):
        """先把这个镜头的旁白都合成好（录制时不卡）"""
        import hashlib
        from tts import tts
        os.makedirs("/var/tmp/footage/voice", exist_ok=True)
        self.cache = {}
        for t in texts:
            f = "/var/tmp/footage/voice/%s.wav" % hashlib.md5(t.encode()).hexdigest()[:12]
            if not os.path.exists(f + ".len"):
                d = tts(t, f)
                open(f + ".len", "w").write(str(d))
            self.cache[t] = (f, float(open(f + ".len").read()))

    def now(self):
        return time.time() - self.t0 - (self.start or 0)

    def hold(self):
        """等上一句旁白说完"""
        left = self._due - self.now()
        if left > 0:
            self.pg.wait_for_timeout(int(left * 1000))

    def say(self, text):
        self.hold()
        f, d = self.cache[text]
        at = self.now()
        self.lines.append((at, d, text, f))
        self._due = at + d + 0.35

    def switch(self, user, role, mode="teach"):
        t = login(user, role, mode)
        self.pg.evaluate("t => { localStorage.setItem('wq-rec-sw', '1'); localStorage.setItem('wq-df-session', t); }",
                         json.dumps({"token": t["token"], "user": t["user"]}))
        return t

    def go(self, path, wait=4000):
        self.pg.goto(HUB + path)
        self.pg.wait_for_timeout(wait)
        self.pg.mouse.move(self.x, self.y)

    def begin(self):
        """从这里开始算镜头（之前的加载截掉）"""
        self.start = time.time() - self.t0

    def wait(self, ms):
        self.pg.wait_for_timeout(ms)

    def to(self, x, y, steps=14, pause=500):
        self.pg.mouse.move(x, y, steps=steps)
        self.x, self.y = x, y
        self.pg.wait_for_timeout(pause)

    def mark(self, tag):
        print("  [%.1f] %s" % (self.now(), tag), flush=True)

    def hover(self, loc, pause=700, dx=0.5, dy=0.5):
        loc = self.pg.locator(loc) if isinstance(loc, str) else loc
        loc.first.scroll_into_view_if_needed()
        bb = loc.first.bounding_box()
        self.to(bb["x"] + bb["width"] * dx, bb["y"] + bb["height"] * dy, pause=pause)

    def click(self, loc, pause=900, **kw):
        self.hover(loc, pause=350, **kw)
        l = self.pg.locator(loc) if isinstance(loc, str) else loc
        bb = l.first.bounding_box()
        l.first.click(position={"x": bb["width"] * kw.get("dx", 0.5), "y": bb["height"] * kw.get("dy", 0.5)})
        self.pg.wait_for_timeout(pause)

    def type(self, loc, text, delay=110, clear=True):
        self.click(loc, pause=200)
        if clear:
            self.pg.keyboard.press("Control+A")
        self.pg.keyboard.type(text, delay=delay)
        self.pg.wait_for_timeout(500)

    def scroll(self, dy, steps=20, pause=600):
        for _ in range(steps):
            self.pg.mouse.wheel(0, dy / steps)
            self.pg.wait_for_timeout(40)
        self.pg.wait_for_timeout(pause)

    def key(self, png=None):
        """关键帧（不带假鼠标）"""
        hide = "for (const id of ['__cursor','__ring']) { const e = document.getElementById(id); if (e) e.style.visibility = '%s'; }"
        self.pg.evaluate(hide % "hidden")
        self.pg.screenshot(path=os.path.join(OUT, (png or self.name) + ".png"))
        self.pg.evaluate(hide % "visible")

    def end(self, max_s=600):
        self.hold()
        for i in range(6):                      # 静止时浏览器不出新帧，动一下鼠标让最后的画面录进去
            self.pg.mouse.move(self.x + (i % 2), self.y)
            self.pg.wait_for_timeout(400)
        dur = time.time() - self.t0 - (self.start or 0)
        vid = self.pg.video.path()
        self.ctx.close(); self.b.close(); self.pw.stop()
        mp4 = os.path.join(OUT, self.name + ".mp4")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "%.2f" % (self.start or 0), "-i", vid, "-t", "%.2f" % min(dur, max_s),
                        "-r", "30", "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-pix_fmt", "yuv420p", "-an", "-movflags", "+faststart", mp4], check=True)
        out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=width,height,r_frame_rate", "-of", "csv=p=0", mp4],
                             capture_output=True, text=True).stdout.split()
        if self.cuts:
            expr = "+".join("between(t,%.2f,%.2f)" % c for c in self.cuts)
            tmp = mp4 + ".tmp.mp4"
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp4, "-vf", "select='not(%s)',setpts=N/30/TB" % expr, "-r", "30",
                            "-t", "%.2f" % (min(dur, max_s) - sum(b - a for a, b in self.cuts)),
                            "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-pix_fmt", "yuv420p", "-an", "-movflags", "+faststart", tmp], check=True)
            os.replace(tmp, mp4)

            def shift(x):
                return x - sum(min(b, x) - a for a, b in self.cuts if a < x)
            self.lines = [(shift(at), d, t, f) for at, d, t, f in self.lines]
            dur -= sum(b - a for a, b in self.cuts)
        if self.lines and getattr(self, "squeeze", True):
            # 旁白之间超过 4 秒的空档快进成约 2.5 秒（操作照样看得见，只是快一些）
            n = int(subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", mp4],
                                   capture_output=True, text=True).stdout.strip() or 0)
            total = n / 30.0
            marks = [(at, at + d) for at, d, t, f in self.lines]
            gaps = []
            for i, (a, b) in enumerate(marks):
                g0 = b + 0.4
                g1 = (marks[i + 1][0] - 0.3) if i + 1 < len(marks) else total - 0.5
                if g1 - g0 > 4:
                    gaps.append((g0, g1, min(6.0, (g1 - g0) / 2.5)))
            if gaps:
                pts, t0, parts = [], 0.0, []
                for g0, g1, k in gaps:
                    parts.append((t0, g0, 1.0)); parts.append((g0, g1, k)); t0 = g1
                parts.append((t0, total, 1.0))
                parts = [p for p in parts if p[1] - p[0] > 0.05]
                lst = mp4 + ".parts.txt"
                with open(lst, "w") as fp:
                    for i, (a0, b0, k) in enumerate(parts):
                        pf = "%s.p%02d.mp4" % (mp4, i)
                        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "%.3f" % a0, "-to", "%.3f" % b0, "-i", mp4,
                                        "-vf", "setpts=(PTS-STARTPTS)/%.4f" % k, "-r", "30", "-c:v", "libx264", "-preset", "slow", "-crf", "20",
                                        "-pix_fmt", "yuv420p", "-an", pf], check=True)
                        fp.write("file '%s'\n" % pf)
                tmp = mp4 + ".sq.mp4"
                subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", "-movflags", "+faststart", tmp], check=True)
                for i in range(len(parts)):
                    os.remove("%s.p%02d.mp4" % (mp4, i))
                os.remove(lst)
                os.replace(tmp, mp4)

                def remap(x):
                    y = 0.0
                    for a, b, k in parts:
                        if x >= b:
                            y += (b - a) / k
                        elif x > a:
                            y += (x - a) / k
                    return y
                self.lines = [(remap(at), d, t, f) for at, d, t, f in self.lines]
                dur = remap(total)
        if self.lines:
            ins, flt = [], []
            for i, (at, d, t, f) in enumerate(self.lines):
                ins += ["-i", f]
                flt.append("[%d:a]adelay=%d:all=1[a%d]" % (i + 1, int(at * 1000), i))
            mix = ";".join(flt) + ";" + "".join("[a%d]" % i for i in range(len(self.lines))) + \
                "amix=inputs=%d:normalize=0,apad[aout]" % len(self.lines)
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp4] + ins + ["-filter_complex", mix, "-map", "0:v", "-map", "[aout]",
                            "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-shortest", "-movflags", "+faststart",
                            os.path.join(OUT, self.name + "_voice.mp4")], check=True)
            def ts(x):
                return "%02d:%02d:%02d,%03d" % (x // 3600, x % 3600 // 60, int(x % 60), int(x * 1000) % 1000)
            with open(os.path.join(OUT, self.name + ".srt"), "w", encoding="utf-8") as fp:
                for i, (at, d, t, f) in enumerate(self.lines):
                    fp.write("%d\n%s --> %s\n%s\n\n" % (i + 1, ts(at), ts(at + d), t))
        print(self.name, "时长", round(dur, 1), "→", out, "旁白", len(self.lines), "句，错误", self.errs[:3])
