"""Add glossary terms safely while several writers work at once (file lock).

    python3 textbook/tools/addterm.py "2|特征值|eigenvalue" "2|奇异值分解|singular value decomposition (SVD)"

Format: 首次出现章|中文|English. A term already in the glossary is left as it is (and printed).
"""
import csv
import fcntl
import sys
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "robotics" / "conventions" / "术语表.csv"


def main(args: list[str]) -> None:
    with open(P.with_suffix(".lock"), "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        rows = list(csv.reader(P.open(encoding="utf-8")))
        have = {r[1]: r for r in rows[1:]}
        for a in args:
            ch, zh, en = [x.strip() for x in a.split("|")]
            if zh in have:
                print("已有", have[zh])
                continue
            rows.append([ch, zh, en, ""])
            have[zh] = rows[-1]
            print("加入", zh, en)
        head, body = rows[0], rows[1:]
        body.sort(key=lambda r: int(r[0]))
        with P.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(head)
            w.writerows(body)


if __name__ == "__main__":
    main(sys.argv[1:])
