"""Worked examples of Section 7.1.

Example 7.1.1: the difference quotient approaches the derivative. f(t) = t² at t = 1, quotients for h = 0.1, 0.01, 0.001; the error of the first-order Taylor approximation shrinks like h².
Example 7.1.2: first-order model of a joint motor, τ ω̇ + ω = K u. Time constant τ and gain K from the motor data, steady speed for a 12 V step;
            the analytic solution (7.1.6) checked against a high-accuracy numerical integration.
Example 7.1.3: the pendulum linearized at its two equilibria: eigenvalues of the Jacobian; the linear solution e^{At}x0 at θ = 0 checked against numerical integration.
Example 7.1.4: a link swinging freely once the brake is released (a pendulum): small-swing natural angular frequency and period; the exact period when released from
            horizontal (elliptic integral) checked against the period measured in a simulation.
Also: the energy (7.1.16) of the undamped pendulum is constant along the true trajectory.
"""
import math

import numpy as np
from scipy.integrate import solve_ivp
from scipy.linalg import expm

from _ode import MOTOR, G, link_params, motor_first_order, pend_energy, pend_exact_period, pend_f, rk4, run
from bookout import out, tex

# ---------------------------------------------------------------- Example 7.1.1 difference quotient
f = lambda t: t * t
dq = {h: (f(1 + h) - f(1)) / h for h in (0.1, 0.01, 0.001)}
for h, q in dq.items():
    assert abs(q - (2 + h)) < 1e-9                       # (the difference quotient of t² is exactly 2t + h)
# error of the first-order Taylor approximation e^{h} ≈ 1 + h: halve h and the error becomes about 1/4
taylor_err = {h: math.exp(h) - (1 + h) for h in (0.2, 0.1, 0.05)}
ratio_taylor = taylor_err[0.1] / taylor_err[0.05]
assert 3.8 < ratio_taylor < 4.2

# ---------------------------------------------------------------- Example 7.1.2 joint motor
m = MOTOR
tau, K = motor_first_order()
u = 12.0                                                 # step voltage, V
w_inf = K * u                                            # steady speed, rad/s
rpm = w_inf * 60 / (2 * math.pi)
frac1 = 1 - math.exp(-1)                                 # fraction reached at t = τ
frac3 = 1 - math.exp(-3)
den = m["R"] * m["b"] + m["Kt"] * m["Ke"]


def motor_rhs(t, x):                                     # Eq. (7.1.3) rearranged: J ω̇ = Kt (u − Ke ω)/R − b ω
    w = x[0]
    i = (u - m["Ke"] * w) / m["R"]
    return np.array([(m["Kt"] * i - m["b"] * w) / m["Jm"]])


t_chk = 0.05
w_exact = w_inf * (1 - math.exp(-t_chk / tau))           # Eq. (7.1.6)
w_num = run(rk4, motor_rhs, [0.0], t_chk, 1e-5)[0]
assert abs(w_num - w_exact) < 1e-8 * w_inf
i0 = u / m["R"]                                          # current at the instant of starting
i_inf = (u - m["Ke"] * w_inf) / m["R"]
dw0 = w_inf / tau                                        # angular acceleration at start = slope of the tangent
assert abs(dw0 - motor_rhs(0, [0.0])[0]) < 1e-6 * dw0

# ---------------------------------------------------------------- Example 7.1.4 the link as a pendulum (period, energy)
Jo, lc, wn2 = link_params()
wn = math.sqrt(wn2)
T0 = 2 * math.pi / wn                                    # small-swing period
th0 = math.pi / 2                                        # released from horizontal
T_ell = pend_exact_period(wn2, th0)
sol = solve_ivp(pend_f(wn2), (0, 3 * T_ell), [th0, 0.0], method="DOP853", rtol=1e-12, atol=1e-12,
                dense_output=True, events=lambda t, x: x[1])
ev = sol.t_events[0]                                     # instants where θ̇ = 0: one every half period
ev = ev[ev > 1e-6]
T_sim = ev[1]                                            # second zero of the velocity: back at the start, one period
assert abs(T_sim - T_ell) < 1e-8
ratio_T = T_ell / T0

# conservation of energy: E is constant along the true trajectory
ts = np.linspace(0, 3 * T_ell, 400)
E = pend_energy(sol.sol(ts).T, wn2)
assert np.ptp(E) < 1e-9 * E[0]
v_bottom = math.sqrt(2 * wn2 * (1 - math.cos(th0)))      # angular velocity at the bottom of the swing, rad/s

# ---------------------------------------------------------------- Example 7.1.3 linearization
A0 = np.array([[0, 1], [-wn2, 0]])                       # at θ = 0
Api = np.array([[0, 1], [wn2, 0]])                       # at θ = π
ev0 = np.linalg.eigvals(A0)
evpi = np.linalg.eigvals(Api)
assert np.allclose(sorted(ev0.imag), [-wn, wn]) and np.allclose(ev0.real, 0)
assert np.allclose(sorted(evpi.real), [-wn, wn])
# check the Jacobians by numerical differentiation
fp = pend_f(wn2)
eps = 1e-6
for xe, A in (([0.0, 0.0], A0), ([math.pi, 0.0], Api)):
    Jn = np.column_stack([(fp(0, np.array(xe) + eps * e) - fp(0, np.array(xe) - eps * e)) / (2 * eps) for e in np.eye(2)])
    assert np.allclose(Jn, A, atol=1e-6)
# small angle: linear solution e^{At} x0 versus the numerical solution of the nonlinear equation
x0s = np.array([math.radians(5), 0.0])
t1 = 1.0
x_lin = expm(A0 * t1) @ x0s
x_non = run(rk4, fp, x0s, t1, 1e-4)
x_lin_rk = run(rk4, lambda t, x: A0 @ x, x0s, t1, 1e-4)
assert np.allclose(x_lin, x_lin_rk, atol=1e-12)          # matrix exponential and numerical integration agree
lin_gap_deg = math.degrees(abs(x_lin[0] - x_non[0]))     # difference caused by linearizing (small at 5°)
# with damping: b/J_o = 1 1/s
c = 1.0
Ad = np.array([[0, 1], [-wn2, -c]])
evd = np.linalg.eigvals(Ad)
assert np.allclose(evd.real, -c / 2)

out(
    dq1=dq[0.1], dq2=dq[0.01], dq3=dq[0.001],
    te1=taylor_err[0.1], te2=taylor_err[0.05], ratio_taylor=ratio_taylor,
    tau=tau, tau_ms=tau * 1e3, K=K, den=den, w_inf=w_inf, rpm=rpm, frac1=frac1, frac3=frac3,
    t_chk_ms=t_chk * 1e3, w_chk=w_exact, i0=i0, i_inf=i_inf, dw0=dw0,
    Jo=Jo, lc=lc, wn2=wn2, wn=wn, T0=T0, T_ell=T_ell, T_sim=T_sim, ratio_T=ratio_T, v_bottom=v_bottom,
    E0=float(E[0]), Eptp=float(np.ptp(E)),
    A0=tex(A0, 2), Api=tex(Api, 2), ev_wn=wn, evd_re=float(evd.real[0]), evd_im=float(abs(evd.imag[0])),
    lin_gap_deg=lin_gap_deg, x_lin_deg=math.degrees(x_lin[0]), x_non_deg=math.degrees(x_non[0]),
    g=G,
)
