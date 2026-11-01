"""Elastohydrodynamic film thickness at a ball–raceway contact (round 64, step 1).

Hamrock & Dowson (Ball Bearing Lubrication, Wiley, 1981; J. Lubr. Technol. 99 (1977) 264–276), fully flooded,
isothermal, elliptical contacts:
    H_min = h_min/R_x = 3.63 U^0.68 G^0.49 W^−0.073 (1 − e^(−0.68 k))
    H_c   = h_c/R_x   = 2.69 U^0.67 G^0.53 W^−0.067 (1 − 0.61 e^(−0.73 k))
    U = η₀ u / (E′ R_x),  G = α_p E′,  W = Q / (E′ R_x²),  k = 1.0339 (R_y/R_x)^0.636 (their ellipticity fit)
with E′ = 2 / Σ (1 − ν²)/E, R_x the effective radius in the rolling direction, R_y across it, u the mean entraining
speed. Pure rolling, outer ring fixed, inner ring at ω: u = ω d_m (1 − γ²) / 4 (Harris & Kotzalas vol. 1 ch. 8).

Plain code: no AI, no network. Inputs mm, N, Pa·s, 1/Pa, r/min; film thickness in mm.
"""

from __future__ import annotations

import math

from bearingkit import hertz as H


def film(
    Q: float, rho: tuple[float, float, float, float], Es: float, eta0: float, alpha_p: float, u_mm_s: float
) -> dict:
    """Minimum and central film thickness (mm). E* (MPa) as in hertz.py; η₀ in Pa·s, α_p in 1/Pa, u in mm/s."""
    Rx = 1 / (rho[0] + rho[2])
    Ry = 1 / (rho[1] + rho[3])
    E_prime = 2 * Es * 1e6  # Pa
    Rx_m, u = Rx * 1e-3, u_mm_s * 1e-3
    U = eta0 * u / (E_prime * Rx_m)
    G = alpha_p * E_prime
    W = Q / (E_prime * Rx_m * Rx_m)
    k = 1.0339 * (Ry / Rx) ** 0.636
    hmin = 3.63 * U**0.68 * G**0.49 * W**-0.073 * (1 - math.exp(-0.68 * k)) * Rx_m
    hc = 2.69 * U**0.67 * G**0.53 * W**-0.067 * (1 - 0.61 * math.exp(-0.73 * k)) * Rx_m
    return {"h_min": hmin * 1e3, "h_c": hc * 1e3, "U": U, "G": G, "W": W, "k": k, "Rx": Rx, "Ry": Ry}


def entraining_speed(dm: float, gamma: float, n_rpm: float) -> float:
    """Mean entraining speed (mm/s) at the contacts, pure rolling, one ring fixed."""
    w = n_rpm * 2 * math.pi / 60
    return w * dm * (1 - gamma * gamma) / 4


__all__ = ["film", "entraining_speed", "H"]
