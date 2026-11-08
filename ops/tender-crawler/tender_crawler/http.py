"""礼貌访问：同站限速、遵守 robots.txt、遇到验证码 / 拦截立即停止该来源（不重试、不绕过）。"""
import logging
import random
import time
import urllib.robotparser
from urllib.parse import urlsplit

import requests

log = logging.getLogger(__name__)

BLOCK_MARKERS = ("验证码", "滑动验证", "安全验证", "访问过于频繁", "captcha", "请输入验证", "人机验证", "频繁访问")


class BlockedError(Exception):
    """来源拒绝访问（403/412/429 或出现验证码页面）。当天停止访问该来源。"""


class PoliteSession:
    def __init__(self, cfg):
        p = cfg.get("politeness", {})
        self.min_interval = float(p.get("min_interval_seconds", 4))
        self.jitter = float(p.get("jitter_seconds", 2))
        self.timeout = float(p.get("timeout_seconds", 20))
        self.respect_robots = bool(p.get("respect_robots_txt", True))
        self.s = requests.Session()
        self.s.headers.update({
            "User-Agent": p.get("user_agent", "Mozilla/5.0 (compatible; TenderWatch/1.0)"),
            "Accept-Language": "zh-CN,zh;q=0.9",
        })
        self._last = {}
        self._robots = {}
        self.requests = 0

    def _host(self, url):
        return urlsplit(url).netloc

    def _wait(self, host):
        last = self._last.get(host)
        if last is not None:
            gap = self.min_interval + random.uniform(0, self.jitter) - (time.monotonic() - last)
            if gap > 0:
                time.sleep(gap)
        self._last[host] = time.monotonic()

    def allowed(self, url):
        if not self.respect_robots:
            return True
        parts = urlsplit(url)
        root = f"{parts.scheme}://{parts.netloc}"
        if root not in self._robots:
            rp = urllib.robotparser.RobotFileParser()
            try:
                self._wait(parts.netloc)
                r = self.s.get(root + "/robots.txt", timeout=self.timeout)
                rp.parse(r.text.splitlines() if r.status_code == 200 else [])
            except requests.RequestException:
                rp.parse([])
            self._robots[root] = rp
        return self._robots[root].can_fetch(self.s.headers["User-Agent"], url)

    def request(self, method, url, **kw):
        if not self.allowed(url):
            raise BlockedError(f"robots.txt 不允许访问 {url}")
        self._wait(self._host(url))
        self.requests += 1
        r = self.s.request(method, url, timeout=self.timeout, **kw)
        if r.status_code in (401, 403, 412, 429):
            raise BlockedError(f"HTTP {r.status_code} {url}")
        r.raise_for_status()
        if not r.encoding or r.encoding.lower() == "iso-8859-1":
            r.encoding = r.apparent_encoding
        head = r.text[:4000].lower()
        if any(m.lower() in head for m in BLOCK_MARKERS) and len(r.text) < 20000:
            raise BlockedError(f"出现验证页面 {url}")
        return r

    def get(self, url, **kw):
        return self.request("GET", url, **kw)

    def post(self, url, **kw):
        return self.request("POST", url, **kw)
