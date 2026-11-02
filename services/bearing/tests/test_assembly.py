"""Round 64 step 5 part 3: selective assembly against exhaustive search, and the grouping method for comparison."""

import random

import pytest

from bearingkit import assembly as AS


def batch(seed, n=4):
    rnd = random.Random(seed)
    inner = [(f"I{k}", round(rnd.gauss(35.5, 0.004), 4)) for k in range(n)]
    outer = [(f"O{k}", round(rnd.gauss(52.52, 0.004), 4)) for k in range(n)]
    groups = [{"id": "a", "Dw": 8.499, "qty": 20, "sets": 2}, {"id": "b", "Dw": 8.501, "qty": 30, "sets": 3}]
    return inner, outer, groups


@pytest.mark.parametrize("seed", range(8))
def test_piecewise_is_optimal(seed):
    inner, outer, groups = batch(seed)
    pmin, pmax, pt = 0.012, 0.024, 0.018
    pw = AS.piecewise(inner, outer, groups, pmin, pmax, pt)
    n, dev = AS.brute_force(inner, outer, groups, pmin, pmax, pt)
    assert pw["count"] == n
    assert sum(abs(s["P"] - pt) for s in pw["sets"]) == pytest.approx(dev, abs=1e-9)
    for s in pw["sets"]:
        assert pmin - 1e-9 <= s["P"] <= pmax + 1e-9
    assert len({s["inner"] for s in pw["sets"]}) == pw["count"] == len({s["outer"] for s in pw["sets"]})


def test_ball_groups_limit_the_sets():
    inner = [(f"I{k}", 35.5) for k in range(5)]
    outer = [(f"O{k}", 52.52) for k in range(5)]
    groups = [{"id": "a", "Dw": 8.501, "qty": 20, "sets": 2}]  # 20 balls, 10 per bearing: two sets only
    assert AS.piecewise(inner, outer, groups, 0.01, 0.03, 0.02)["count"] == 2


def test_run_with_synthetic_data_beats_grouping():
    data = AS.synthetic(120, 35.5, 52.52, 8.5, 10, seed=3)
    r = AS.run({**data, "P_min": 0.012, "P_max": 0.024})
    pw, gp = r["piecewise"], r["grouped"]
    assert pw["count"] >= gp["count"]  # piece by piece never does worse
    assert all(0.012 <= s["P"] <= 0.024 for s in pw["sets"])
    assert r["stats"]["min"] >= 0.012 and r["P_target"] == pytest.approx(0.018)
    used = sum(g["used"] for g in r["groups"])
    assert used == pw["count"] and all(g["used"] <= g["sets_max"] for g in r["groups"])
    assert len(r["left_inner"]) == 120 - pw["count"]
    assert {x["why"] for x in r["left_inner"]} <= {"taken", "none"}


@pytest.mark.parametrize(
    "bad, msg",
    [
        ({"Z": 2}, "number of balls"),
        ({"P_min": None}, "clearance range"),
        ({"P_max": 0.01}, "largest is above"),
        ({"inner": []}, "measured inner"),
        ({"inner": [{"id": "x", "d": 35.5}, {"id": "x", "d": 35.5}]}, "repeat"),
    ],
)
def test_bad_input(bad, msg):
    p = {**AS.synthetic(5, 35.5, 52.52, 8.5, 10), "P_min": 0.012, "P_max": 0.024, **bad}
    with pytest.raises(AS.AssemblyError, match=msg):
        AS.run(p)


def test_short_groups_lagrange_close_to_exact():
    d = AS.synthetic(60, 35.5, 52.52, 8.5, 10, seed=7)
    inner = [(r["id"], r["d"]) for r in d["inner"]]
    outer = [(r["id"], r["d"]) for r in d["outer"]]
    groups = [{**g, "sets": g["qty"] // 10} for g in d["groups"]]
    exact = AS.piecewise(inner, outer, groups, 0.012, 0.024, 0.018)
    assert exact["method"] == "milp" and exact["optimal"]
    lag = AS._lagrange(inner, outer, groups, 0.012, 0.024, 0.018)
    assert len(lag) == exact["count"]  # the same number of sets
    use = {}
    for *_, g, P in lag:
        use[g] = use.get(g, 0) + 1
        assert 0.012 - 1e-9 <= P <= 0.024 + 1e-9
    assert all(use[g] <= groups[g]["sets"] for g in use)
