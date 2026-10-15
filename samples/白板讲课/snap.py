import sys
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
  b=pw.chromium.launch(); p=b.new_page(viewport={'width':1920,'height':1080})
  p.goto('file://'+__import__('os').path.abspath('page.html'))
  for t in map(float,sys.argv[1:]):
    p.evaluate(f'seek({t})'); p.screenshot(path=f'snap_{t}.png')
  b.close()
