"""本地去重库（SQLite）：同一条公告只在第一次发现时标记为 new。"""
import hashlib
import sqlite3


class Store:
    def __init__(self, path):
        self.db = sqlite3.connect(path)
        self.db.execute("CREATE TABLE IF NOT EXISTS seen (id TEXT PRIMARY KEY, first_seen TEXT, title TEXT, url TEXT)")

    @staticmethod
    def key(item):
        return hashlib.sha1((item["url"] or item["title"]).encode("utf-8")).hexdigest()[:16]

    def first_seen(self, item, today):
        k = self.key(item)
        row = self.db.execute("SELECT first_seen FROM seen WHERE id=?", (k,)).fetchone()
        if row:
            return k, row[0]
        self.db.execute("INSERT INTO seen VALUES (?,?,?,?)", (k, today, item["title"], item["url"]))
        self.db.commit()
        return k, today
