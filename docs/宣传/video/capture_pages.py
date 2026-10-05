"""Stills for the video, from the local platform (localhost:8088): textbook pages (tall screenshots for a smooth scroll),
the phone edition, the Chinese/English switch, the dashboard, the AI course studio and a course page.
Usage: python3 capture_pages.py <work dir> [name ...]     (names: book_toc book_121 book_41 book_42 phone zh_en
dashboard studio course; none = all). Accounts: student1 / teacher1 / admin of the local test environment.
Note: "studio" presses 新建课程项目, which adds an empty project for teacher1."""
import asyncio
import os
import sys

from playwright.async_api import async_playwright

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from record import CHROME_ARGS  # noqa: E402

W = sys.argv[1]
WEB = os.environ.get("WEB_URL", "http://localhost:8088")
BOOK = os.environ.get("BOOK_URL", "http://127.0.0.1:8701")
USER, PASS = os.environ.get("WQ_USER", "student1"), os.environ.get("WQ_PASS", "Test#2026")


async def login(b, w, h, dsf, mobile=False, user=None, pw=None):
    ctx = await b.new_context(viewport={"width": w, "height": h}, device_scale_factor=dsf, locale="zh-CN",
                              is_mobile=mobile, has_touch=mobile)
    pg = await ctx.new_page()
    await pg.goto(WEB + "/pages/login/login")
    await pg.wait_for_timeout(1500)
    i = pg.locator("input")
    await i.nth(0).fill(user or USER)
    await i.nth(1).fill(pw or PASS)
    await pg.locator(".submit").click()
    await pg.wait_for_timeout(2500)
    return ctx, pg


async def book(pg, sec, wait=4500):
    await pg.goto(f"{WEB}/pages/textbook/textbook?book=robotics&s={sec}")
    await pg.wait_for_timeout(wait)


async def shots(b, names):
    want = lambda n: not names or n in names  # noqa: E731
    if want("book_121") or want("book_41") or want("book_42") or want("book_toc"):
        ctx, pg = await login(b, 1440, 810, 4 / 3)
        if want("book_toc"):
            await book(pg, "4.0")
            await pg.screenshot(path=f"{W}/st_book_toc.png")
        if want("book_121"):
            await pg.set_viewport_size({"width": 1440, "height": 2400})
            await book(pg, "12.1")
            await pg.screenshot(path=f"{W}/st_book_121.png")
        if want("book_41"):
            await pg.set_viewport_size({"width": 1440, "height": 3200})
            await book(pg, "4.1")
            await pg.screenshot(path=f"{W}/st_book_41.png")
        if want("book_42"):
            await pg.set_viewport_size({"width": 1440, "height": 810})
            await book(pg, "4.2", 6000)
            v = pg.locator("video").first
            await v.scroll_into_view_if_needed()
            await pg.evaluate("() => { const v = document.querySelector('video'); v.pause(); v.currentTime = 0; v.removeAttribute('controls'); window.scrollBy(0, v.getBoundingClientRect().top - 150); }")
            await pg.wait_for_timeout(800)
            box = await v.bounding_box()
            src = await v.get_attribute("src")
            await pg.screenshot(path=f"{W}/st_book_42.png")
            with open(f"{W}/st_book_42.txt", "w") as f:
                f.write(f"{box['x']} {box['y']} {box['width']} {box['height']}\n{src}\n")
        await ctx.close()
    if want("phone"):
        ctx, pg = await login(b, 375, 2400, 3, mobile=True)
        await book(pg, "12.1")
        await pg.screenshot(path=f"{W}/st_phone_121.png")
        await ctx.close()


async def platform(b, names):
    want = lambda n: not names or n in names  # noqa: E731
    if want("zh_en"):    # 中英一键切换: the interface language (EN, lower left) and the text language together
        ctx, pg = await login(b, 1440, 810, 4 / 3)
        await book(pg, "4.1", 4000)
        await pg.screenshot(path=f"{W}/zh41.png")
        await pg.get_by_text("EN", exact=True).last.click()
        await pg.wait_for_timeout(2500)
        await pg.get_by_text("English", exact=True).first.click()
        await pg.wait_for_timeout(4500)
        await pg.screenshot(path=f"{W}/en41d.png")
        await ctx.close()
    if want("course"):
        ctx, pg = await login(b, 1440, 810, 4 / 3)
        await pg.goto(WEB + "/pages/courses/courses")
        await pg.wait_for_timeout(3000)
        await pg.get_by_text("WQ-20260928-5").first.click()     # 大学物理A（上）
        await pg.wait_for_timeout(4000)
        await pg.screenshot(path=f"{W}/pr_course.png")
        await ctx.close()
    if want("dashboard"):
        ctx, pg = await login(b, 1440, 810, 4 / 3, user="admin", pw=os.environ.get("WQ_ADMIN_PASS", "Admin#2026"))
        await pg.goto(WEB + "/pages/courses/courses")
        await pg.wait_for_timeout(3000)
        await pg.screenshot(path=f"{W}/pr_courses.png")
        await ctx.close()
    if want("studio"):
        ctx, pg = await login(b, 1440, 810, 4 / 3, user="teacher1")
        await pg.goto(WEB + "/pages/studio/studio")
        await pg.wait_for_timeout(3000)
        await pg.screenshot(path=f"{W}/pr_studio1.png")
        await pg.get_by_text("新建课程项目").first.click()
        await pg.wait_for_timeout(3000)
        await pg.screenshot(path=f"{W}/pr_studio2.png")
        await ctx.close()


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=CHROME_ARGS)
        await shots(b, sys.argv[2:])
        await platform(b, sys.argv[2:])
        await b.close()

asyncio.run(main())
