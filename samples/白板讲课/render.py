import json, os, subprocess
from playwright.sync_api import sync_playwright
FPS=30; total=json.load(open('times.json'))['total']; n=int(total*FPS)
ff=subprocess.Popen(['ffmpeg','-v','error','-y','-f','image2pipe','-framerate',str(FPS),'-c:v','mjpeg','-i','-','-i','voice.wav',
  '-c:v','libx264','-pix_fmt','yuv420p','-crf','20','-preset','medium','-c:a','aac','-b:a','128k','-shortest','白板讲课样片.mp4'],stdin=subprocess.PIPE)
with sync_playwright() as pw:
  b=pw.chromium.launch(); p=b.new_page(viewport={'width':1920,'height':1080})
  p.goto('file://'+os.path.abspath('page.html'))
  for i in range(n):
    p.evaluate(f'seek({i/FPS})'); ff.stdin.write(p.screenshot(type='jpeg',quality=92))
  b.close()
ff.stdin.close(); ff.wait(); print('frames',n)
