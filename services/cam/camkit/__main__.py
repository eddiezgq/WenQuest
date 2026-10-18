"""python -m camkit project.json — print the checks of a cam project (第 39 轮)."""

import json
import sys

from camkit import analyse

MARK = {"pass": "合格", "fail": "不合格", "unknown": "未知", "na": "不适用", "info": "—"}


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("usage: python -m camkit project.json")
        return 2
    with open(argv[0], encoding="utf-8") as f:
        r = analyse(json.load(f))
    print(f"总体：{MARK[r['status']]}")
    for c in r["checks"]:
        v = "" if c["value"] is None else f"{c['value']:.4g}"
        lim = "" if c["limit"] is None else f" / 限值 {c['limit']:.4g}"
        note = f"（{c['note']}）" if c["note"] else ""
        print(f"  {MARK[c['status']]:<4} {c['zh']}：{v} {c['unit']}{lim}{note}")
    return 0 if r["status"] != "fail" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
