"""Chapter 4 (thread take-up): numbers used in course/lessons/ch04.json.
Port of the model in Section 4.4-4.5 / virtual lab 4-1 (src/zh/labs/takeup.html)."""
import math
DEG = math.pi / 180
RN, LN = 15.5, 55.0
def xN(f):
    a = f * DEG; l = RN / LN
    return RN * (1 - math.cos(a)) - LN * (1 - math.sqrt(1 - (l * math.sin(a)) ** 2))
RH, RC, EYE_TDC = 13.5, 11.0, 20.0
YP = xN(206) - 8
def hull_perim(pts):
    p = sorted(set((round(a, 12), round(b, 12)) for a, b in pts))
    if len(p) < 2: return 0.0
    cr = lambda o, a, b: (a[0]-o[0])*(b[1]-o[1]) - (a[1]-o[1])*(b[0]-o[0])
    lo, up = [], []
    for q in p:
        while len(lo) >= 2 and cr(lo[-2], lo[-1], q) <= 0: lo.pop()
        lo.append(q)
    for q in reversed(p):
        while len(up) >= 2 and cr(up[-2], up[-1], q) <= 0: up.pop()
        up.append(q)
    h = lo[:-1] + up[:-1]
    return sum(math.dist(h[i], h[(i+1) % len(h)]) for i in range(len(h)))
smooth = lambda u: (lambda u: u*u*(3-2*u))(min(1, max(0, u)))
def loop_pts(f, t, phc):
    x = xN(f); e = EYE_TDC - t - x; F = (0, YP + t); th = (90 - 2*(f - phc)) * DEG
    pts = [F, (RH*math.cos(th), RH*math.sin(th))]; sw = 2*(f - phc); a = 0
    while a < sw:
        q = (90 - a) * DEG; pts.append((RC*math.cos(q), RC*math.sin(q))); a += 1
    if e < 0: pts.append((0, YP + t + e))
    return pts, e, x
def demand_raw(f, t, phc):
    x = xN(f); e = EYE_TDC - t - x
    if f < phc: return 2 * max(0, -e)
    pts, e, x = loop_pts(f, t, phc); P = hull_perim(pts)
    tail = P + e if e < 0 else e + P
    return x + tail - (EYE_TDC - t)
def demand(f, t, s, phc):
    bot, off, c = phc + 90, phc + 135, s + t
    if f <= bot: return demand_raw(f, t, phc)
    if f <= off:
        Lb = demand_raw(bot, t, phc); u = smooth((f - bot) / (off - bot)); return Lb*(1-u) + c*u
    return c
LK0 = dict(r=20.7, d=-6.8, Qz=21.5, Qy=-45.5, a=43.4, b=40.9, c=65.7, al=2.8)
AC = (122.2, -45.7); ADIR = (math.cos(285.2*DEG), math.sin(285.2*DEG)); B = (66.4, -117.7)
def link_pose(f, lk=LK0):
    q = (f + lk['d']) * DEG; P = (-lk['r']*math.sin(q), -lk['r']*math.cos(q)); Q = (lk['Qz'], lk['Qy'])
    dz, dy = Q[0]-P[0], Q[1]-P[1]; D = math.hypot(dz, dy)
    tt = (lk['a']**2 - lk['b']**2 + D*D) / (2*D); h2 = lk['a']**2 - tt*tt
    if not h2 > 0: return None
    h = math.sqrt(h2); mz, my = P[0]+tt*dz/D, P[1]+tt*dy/D; M = (mz - h*dy/D, my + h*dz/D)
    uz, uy = (M[0]-P[0])/lk['a'], (M[1]-P[1])/lk['a']; ca, sa = math.cos(lk['al']*DEG), math.sin(lk['al']*DEG)
    E = (P[0] + lk['c']*(uz*ca - uy*sa), P[1] + lk['c']*(uz*sa + uy*ca))
    w1 = (P[0]-M[0], P[1]-M[1]); w2 = (Q[0]-M[0], Q[1]-M[1])
    mu = math.acos(max(-1, min(1, (w1[0]*w2[0]+w1[1]*w2[1])/lk['a']/lk['b']))) / DEG
    return P, M, E, mu
def compute(t=1.5, s=3.0, phc=206, u=0.0, rpm=5000, lk=LK0):
    A = (AC[0] + u*ADIR[0], AC[1] + u*ADIR[1]); Lp, mus = [], []
    for i in range(360):
        p = link_pose(i, lk)
        if p is None: return None
        E = p[2]; mus.append(p[3]); Lp.append(math.dist(E, A) + math.dist(E, B))
    mx = max(Lp); S = [mx - v for v in Lp]
    top = min(range(360), key=lambda i: S[i]); bot = max(range(360), key=lambda i: S[i])
    c = s + t
    D = [c if i < top else demand(i, t, s, phc) for i in range(360)]
    sl = [S[i] - D[i] for i in range(360)]
    fin = 0
    while fin < 180 and xN(fin) < EYE_TDC - t: fin += 1
    rng = range(phc, min(359, phc + 135) + 1)
    at = min(rng, key=lambda i: sl[i]); margin = sl[at]
    waste = max(sl[i] for i in range(phc, min(359, phc + 90) + 1))
    pre = max(sl[i] for i in range(top, fin + 1))
    neg = max([0] + [-sl[i] for i in range(fin, phc)])
    w = rpm * 2 * math.pi / 60
    acc = max(abs((S[(i+1) % 360] - 2*S[i] + S[i-1]) / (DEG*DEG)) for i in range(360)) * w*w / 1000  # m/s^2
    return dict(S=S, D=D, sl=sl, top=top, bot=bot, Lmax=mx, Lmin=min(Lp), fin=fin, margin=margin, at=at,
                waste=waste, pre=pre, neg=neg, acc=acc, mu=(min(mus), max(mus)), c=c, Lp=Lp)

if __name__ == "__main__":
    for f in (0, 90, 150):
        P, M, E, mu = link_pose(f)
        print(f"phi={f}: P=({P[0]:.2f},{P[1]:.2f}) M=({M[0]:.2f},{M[1]:.2f}) E=({E[0]:.2f},{E[1]:.2f}) mu={mu:.1f}")
    Ey = [link_pose(f)[2][1] for f in range(360)]
    print("eye highest at", max(range(360), key=lambda i: Ey[i]), "lowest at", min(range(360), key=lambda i: Ey[i]),
          "height range", round(max(Ey) - min(Ey), 1))
    R = compute()
    print(f"Lmax {R['Lmax']:.1f} at {R['top']}, Lmin {R['Lmin']:.1f} at {R['bot']}, Smax {R['Lmax']-R['Lmin']:.1f}")
    print(f"L(150)={R['Lp'][150]:.1f}, S(150)={R['S'][150]:.1f}")
    print(f"mu range {R['mu'][0]:.1f}-{R['mu'][1]:.1f}")
    print(f"eye enters fabric at {R['fin']}, point enters ~102")
    print(f"surplus at 102: {R['sl'][102]:.1f}, pre(max before eye in) {R['pre']:.1f}")
    lo = min(range(R['fin'], 206), key=lambda i: R['sl'][i]); print(f"min surplus between eye-in and catch: {R['sl'][lo]:.1f} at {lo}")
    print(f"surplus at catch 206: {R['sl'][206]:.1f}; waste {R['waste']:.1f}; margin {R['margin']:.1f} at {R['at']}")
    print(f"D at 180 {R['D'][180]:.1f}, at 206 {R['D'][206]:.1f}, at 250 {R['D'][250]:.1f}, at 296 {R['D'][296]:.1f}")
    print(f"acc {R['acc']/1000:.1f} km/s^2, neg {R['neg']:.2f}, q={R['c']}")
    R3 = compute(t=3.0)
    print(f"t=3: margin {R3['margin']:.1f}, neg {R3['neg']:.1f}, pre {R3['pre']:.1f}")
    for u in (11, 12):
        Ru = compute(t=3.0, u=u)
        print(f"t=3,u={u}: margin {Ru['margin']:.1f}, neg {Ru['neg']:.1f}, pre {Ru['pre']:.1f}, waste {Ru['waste']:.1f}")
    for phc in (198, 214, 216):
        Rp = compute(phc=phc)
        print(f"phc={phc}: waste {Rp['waste']:.1f}, margin {Rp['margin']:.1f}")
    # thread consumption estimates
    q = 3 + 1.5; n = 500 / 3
    print(f"50 cm seam: {n:.1f} stitches -> {math.ceil(n)} x {q} = {math.ceil(n)*q/10:.1f} cm; +15% = {math.ceil(n)*q*1.15/10:.1f} cm")
    print("thread-supplier rule: 2.5 cm per cm; needle thread 1.25 per cm; t for s=10/7:", round(12.5/7 - 10/7, 3))
    # problem numbers: shirt seam 80 cm, s=2.5, t=2 (thick) etc
    for (L_, s_, t_, loss) in ((80, 2.5, 1.0, 0.12), (60, 3.0, 2.0, 0.15)):
        n_ = math.ceil(L_*10/s_); qq = s_ + t_
        print(f"seam {L_} cm s={s_} t={t_}: {n_} stitches x {qq} = {n_*qq/10:.1f} cm, +{loss*100:.0f}% = {n_*qq*(1+loss)/10:.1f} cm")
    # acceleration at other speeds
    for rpm in (4000, 6000):
        print(rpm, "acc", round(compute(rpm=rpm)['acc']/1000, 1), "km/s^2")
    # thickness 2.0 and 2.5
    for t in (2.0, 2.5):
        Rt = compute(t=t); print(f"t={t}: margin {Rt['margin']:.1f}, neg {Rt['neg']:.1f}, pre {Rt['pre']:.1f}")
    # small quiz/exam items
    a, b = 43.4, 40.9
    for d in (50.0, 60.0):
        print(f"transmission angle a={a} b={b} d={d}: {math.degrees(math.acos((a*a+b*b-d*d)/(2*a*b))):.1f} deg")
    # demand before the hook catches at BDC: D = 2*(x(180) - e0), e0 = 20 - t
    for t in (1.5, 3.0):
        print(f"D at BDC, t={t}: {2*(xN(180)-(20-t)):.1f} mm")
    print("S(150) = 210.2 - 189.4 =", round(210.2 - 189.4, 1))
    # assignment: shirt with 6 m of lockstitch seams, s = 2.5, t = 1.0, waste 12 %
    n_ = round(6000 / 2.5); per = n_ * 3.5 * 1.12 / 1000
    print(f"shirt: {n_} stitches, {per:.3f} m per shirt incl. waste, cone 5000 m -> {int(5000 // per)} shirts")
    # exercise 1 intermediate values at phi = 90
    lk = LK0; q = (90 + lk['d']) * DEG; P_ = (-lk['r']*math.sin(q), -lk['r']*math.cos(q))
    D_ = math.dist(P_, (lk['Qz'], lk['Qy'])); p_ = (lk['a']**2 - lk['b']**2 + D_**2) / (2*D_)
    print(f"phi=90: d={D_:.2f} p={p_:.2f} h={math.sqrt(lk['a']**2-p_**2):.2f}")
    # exam: 80 cm, s=2.5, t=1.0, 12 %
    print("exam 80 cm:", round(320 * 3.5 * 1.12 / 10, 1), "cm")
