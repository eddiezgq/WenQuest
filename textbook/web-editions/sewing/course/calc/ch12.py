"""Chapter 12 (automatic units & flexible cells): numbers for course/lessons/ch12.json (formulas of 12.3-12.6)."""
def tend(N, a, m, w):
    Tc = max(a + m, N * (a + w)); return Tc, 3600 * N / Tc, N * (a + w) / Tc, max(0, Tc - N * (a + w)), max(0, Tc - (a + m))
def show(a, m, w, Ns=(1, 2, 3, 4)):
    print(f"a={a} m={m} w={w}: N* = {(a + m) / (a + w):.3f}")
    for N in Ns:
        Tc, out, busy, idle, mwait = tend(N, a, m, w)
        print(f"  N={N}: Tc={Tc} s, out={out:.1f}/h, per machine {out / N:.1f}, operator busy {busy * 100:.1f}%, operator idle {idle} s, machine waits {mwait} s")
show(5, 12, 2); print("  loading share N=2:", round(2 * 5 / 17 * 100, 1), "% walking", round(2 * 2 / 17 * 100, 1), "%")
show(3.5, 12, 2, (2, 3)); print("  gains: +machine", round(tend(3,5,12,2)[1]-tend(2,5,12,2)[1]), " +fixture", round(tend(2,3.5,12,2)[1]-tend(2,5,12,2)[1]), " both", round(tend(3,3.5,12,2)[1]-tend(2,5,12,2)[1]))
show(6, 15, 1.5, (2, 3))
show(4, 20, 1, (3, 4, 5, 6))
print("3 vs 2 machines output +%.0f%%" % ((514.29 / 423.53 - 1) * 100))
print("pocket welter catalogue: s/pc", [round(8 * 3600 / x, 1) for x in (1600, 1900, 2300)])
# main rail
def rail(v, s, ops): cap = v / s * 60; return cap, cap / (ops + 1)
c, g = rail(12, 0.3, 6); print("rail 12 m/min 0.3 m: %d carriers/h; 7 legs x 120 = %d" % (c, 7 * 120))
c, g = rail(15, 0.25, 12); print("rail 15/0.25, 12 ops: %d carriers/h, %.1f garments/h, util at 150: %.1f%%" % (c, g, 150 / g * 100))
c, g = rail(10, 0.4, 8); print("rail 10/0.4, 8 ops: %d carriers/h, %.1f garments/h" % (c, g))
# Little
print("Little: 124/h x 1100 s =", round(124 * 1100 / 3600, 1), "; 50 at 120/h ->", 50 / 120 * 60, "min; 25 ->", 25 / 120 * 60)
print("WIP 30 at 126/h ->", round(30 / 126 * 60, 1), "min")
print("hem sleeves bottleneck 3600/(35/1.1) =", round(3600 / (35 / 1.1), 1))
print("set sleeves op4 eff1.0 alone: 3600/60 =", 3600 / 60)
print("standard total 260 s, 10 ops at eff 1 upper bound 36000/260 =", round(36000 / 260, 1))
# bucket brigade
def bb(v):
    S = sum(v); x = [sum(v[:i + 1]) / S for i in range(len(v) - 1)]; return x, [vi / S for vi in v], S, len(v) * min(v)
for v in ([0.5, 1.0, 1.5], [0.6, 0.8, 1.0, 1.6], [0.7, 0.9, 1.4], [0.8, 1.2, 2.0]):
    x, sh, S, fx = bb(v); print("bucket", v, "handoffs", [round(t, 4) for t in x], "shares", [round(t, 3) for t in sh], "throughput", S, "fixed", round(fx, 2))
print("WIP 20 at 126/h ->", round(20 / 126 * 60, 2), "min")
print("rail 10/0.4 util at 150/h:", round(150 / (1500 / 9) * 100, 1), "%")
print("Little coffee: 10 people / 2 per min =", 10 / 2, "min")
