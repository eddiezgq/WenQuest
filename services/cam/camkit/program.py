"""Motion programs (第 39 轮): a cam cycle of 360° made of rises, dwells and returns, or a table of points.

Displacement s is in mm for a translating follower and in rad for an oscillating one; θ is the cam angle in rad.
Derivatives are with respect to θ: s1 = ds/dθ, s2 = d²s/dθ², s3 = d³s/dθ³. Multiply by ω, ω², ω³ for time.

The joints between segments are checked: a jump in velocity is a rigid impact (刚性冲击), a jump in acceleration a
soft impact (柔性冲击). Plain code: no AI, no network.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import isfinite, pi, radians

import numpy as np

from camkit.laws import LAWS

KINDS = ("rise", "dwell", "return")


class ProgramError(ValueError):
    pass


@dataclass
class Segment:
    kind: str  # rise | dwell | return
    beta: float  # cam angle of the segment, rad
    h: float = 0.0  # lift of a rise or return (mm or rad), > 0
    law: str = "cycloidal"


@dataclass
class Program:
    segments: list[Segment] = field(default_factory=list)
    table: tuple[np.ndarray, np.ndarray] | None = None  # (θ rad, s) for a program given by points
    unit: str = "mm"  # mm (translating) or rad (oscillating)
    advance: float = 0.0  # net advance per cycle (indexing: the output does not come back; mm or rad)

    # ------------------------------------------------------------ construction

    @classmethod
    def from_dict(cls, d: dict) -> Program:
        """{"unit": "mm", "segments": [{"kind": "rise", "deg": 120, "h": 18, "law": "cycloidal"}, ...]}
        or {"unit": "mm", "table": {"deg": [...], "s": [...]}}. Angles in degrees at the edge; oscillating lifts in
        degrees too ("h_deg")."""
        unit = d.get("unit", "mm")
        if unit not in ("mm", "rad"):
            raise ProgramError("the unit of a program is mm (translating follower) or rad (oscillating follower)")
        adv = d.get("advance_deg") if unit == "rad" else None
        advance = radians(float(adv)) if adv not in (None, "") else float(d.get("advance") or 0.0)
        if not isfinite(advance):
            raise ProgramError("numbers must be finite")
        if d.get("table"):
            t = d["table"]
            th = np.radians(np.asarray(t.get("deg", []), dtype=float))
            s = np.asarray(t.get("s", []), dtype=float)
            if unit == "rad" and "s_deg" in t:
                s = np.radians(np.asarray(t["s_deg"], dtype=float))
            if len(th) < 8 or len(th) != len(s):
                raise ProgramError("a table needs at least 8 points, an angle and a displacement for each")
            if np.any(np.diff(th) <= 0) or th[0] < 0 or th[-1] >= 2 * pi:
                raise ProgramError("table angles rise strictly within 0° ≤ θ < 360°")
            return cls(table=(th, s), unit=unit, advance=advance)
        segs = []
        for k, x in enumerate(d.get("segments") or [], 1):
            kind = x.get("kind")
            if kind not in KINDS:
                raise ProgramError(f"segment {k}: rise, dwell or return")
            beta = radians(float(x.get("deg", 0)))
            if not (beta > 0 and isfinite(beta)):
                raise ProgramError(f"segment {k}: its cam angle is more than 0°")
            h = (
                float(x.get("h_deg")) * pi / 180
                if unit == "rad" and x.get("h_deg") is not None
                else float(x.get("h", 0) or 0)
            )
            law = x.get("law") or "cycloidal"
            if kind != "dwell":
                if not h > 0:
                    raise ProgramError(f"segment {k}: a {kind} has a lift more than 0")
                if law not in LAWS:
                    raise ProgramError(f"segment {k}: unknown motion law {law}")
            segs.append(Segment(kind, beta, h if kind != "dwell" else 0.0, law))
        p = cls(segments=segs, unit=unit, advance=advance)
        p.validate()
        return p

    def validate(self) -> None:
        if self.table is not None:
            return
        if not self.segments:
            raise ProgramError("a program has at least one segment")
        total = sum(s.beta for s in self.segments)
        if abs(total - 2 * pi) > 1e-6:
            raise ProgramError(f"the segments add up to {np.degrees(total):.3f}°, not 360°")
        level = 0.0
        for k, s in enumerate(self.segments, 1):
            level += s.h if s.kind == "rise" else -s.h if s.kind == "return" else 0
            if level < -1e-9 and self.advance == 0:
                raise ProgramError(f"segment {k}: the follower would go below its lowest position")
        if abs(level - self.advance) > 1e-9 and self.advance != 0:
            raise ProgramError(
                "the net movement over a cycle differs from the index advance by "
                f"{level - self.advance:.6g} {self.unit}"
            )
        if abs(level) > 1e-9 and self.advance == 0:
            raise ProgramError(
                "the follower does not come back to where it started: rises and returns differ by "
                f"{level:.6g} {self.unit}"
            )

    # ------------------------------------------------------------ evaluation

    def eval(self, theta) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """(s, s1, s2, s3) at cam angles θ (rad, any; taken modulo 2π)."""
        th = np.mod(np.asarray(theta, dtype=float), 2 * pi)
        if self.table is not None:
            return self._eval_table(th)
        s, s1, s2, s3 = (np.zeros_like(th) for _ in range(4))
        start, level = 0.0, 0.0
        for k, seg in enumerate(self.segments):
            end = start + seg.beta
            last = k == len(self.segments) - 1
            m = (th >= start) & ((th <= end) if last else (th < end))
            if seg.kind == "dwell":
                s[m] = level
            else:
                f, v, a, j = LAWS[seg.law].eval((th[m] - start) / seg.beta)
                sg = 1.0 if seg.kind == "rise" else -1.0
                s[m] = level + sg * seg.h * f
                s1[m] = sg * seg.h * v / seg.beta
                s2[m] = sg * seg.h * a / seg.beta**2
                s3[m] = sg * seg.h * j / seg.beta**3
                level += sg * seg.h
            start = end
        return s, s1, s2, s3

    def position(self, theta) -> np.ndarray:
        """s at cam angles θ continued past one turn: an indexing program keeps advancing (s(θ + 2π) = s(θ) +
        advance), unlike eval, which repeats the first turn."""
        th = np.asarray(theta, dtype=float)
        return self.eval(th)[0] + self.advance * np.floor(th / (2 * pi))

    def _eval_table(self, th):
        from scipy.interpolate import CubicSpline  # noqa: PLC0415

        t, s = self.table
        k = self.advance / (2 * pi)  # an indexing table: spline the part that repeats, add the steady advance back
        tt = np.concatenate([t, [t[0] + 2 * pi]])
        ss = np.concatenate([s - k * t, [s[0] - k * t[0]]])
        cs = CubicSpline(tt, ss, bc_type="periodic")
        x = np.where(th < t[0], th + 2 * pi, th)
        base = cs(x) + k * x
        base = np.where(th < t[0], base - self.advance, base)
        return base, cs(x, 1) + k, cs(x, 2), cs(x, 3)

    def lift(self) -> float:
        s, *_ = self.eval(np.linspace(0, 2 * pi, 3601))
        return float(np.max(s) - np.min(s))

    # ------------------------------------------------------------ joints

    def joints(self, tol: float = 1e-6) -> list[dict]:
        """Jumps of velocity (rigid impact) and acceleration (soft impact) where one segment ends and the next begins
        (the last joins the first), per rad and per rad² of cam angle. A table is a periodic cubic spline: smooth to
        acceleration, so no joints are reported."""
        if self.table is not None:
            return []
        out, start = [], 0.0
        n = len(self.segments)
        # (an indexing program joins its last segment to the first one of the next cycle in the same way)
        lift = max(self.lift(), 1e-12)
        for k in range(n):
            a, b = self.segments[k], self.segments[(k + 1) % n]
            start += a.beta
            v0, a0 = self._ends(a, 1.0)
            v1, a1 = self._ends(b, 0.0)
            deg = round(float(np.degrees(start)) % 360.0, 6)
            if abs(v1 - v0) > tol * lift:
                out.append(
                    {
                        "deg": deg,
                        "kind": "velocity",
                        "jump": float(v1 - v0),
                        "zh": "速度突变：刚性冲击",
                        "en": "velocity jump: rigid impact",
                    }
                )
            elif abs(a1 - a0) > tol * lift:
                out.append(
                    {
                        "deg": deg,
                        "kind": "acceleration",
                        "jump": float(a1 - a0),
                        "zh": "加速度突变：柔性冲击",
                        "en": "acceleration jump: soft impact",
                    }
                )
        return out

    @staticmethod
    def _ends(seg: Segment, u: float) -> tuple[float, float]:
        """ds/dθ and d²s/dθ² of a segment at its start (u = 0) or end (u = 1)."""
        if seg.kind == "dwell":
            return 0.0, 0.0
        _, v, a, _ = LAWS[seg.law].eval(np.array([u]))
        sg = 1.0 if seg.kind == "rise" else -1.0
        return float(sg * seg.h * v[0] / seg.beta), float(sg * seg.h * a[0] / seg.beta**2)
