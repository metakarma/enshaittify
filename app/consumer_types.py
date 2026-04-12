"""Consumer type definitions and utility parameters."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

import numpy as np


@dataclass(frozen=True)
class ConsumerTypeSpec:
    key: str
    label: str
    population_share: float
    p: float  # Bass innovation
    q: float  # Bass imitation
    peak_year: float # target peak for curve positioning
    alpha: float  # signal quality
    beta: float  # network effects
    gamma: float  # lock-in aversion
    delta: float  # enshittification aversion
    epsilon: float  # agent friction value
    zeta: float  # values/autonomy premium


DEFAULT_CONSUMER_TYPES: Tuple[ConsumerTypeSpec, ...] = (
    ConsumerTypeSpec(
        key="sovereigntists",
        label="Sovereigntists",
        population_share=0.10,
        p=0.08,
        q=0.3,
        peak_year=2.0,
        alpha=0.3,
        beta=0.2,
        gamma=0.9,
        delta=0.8,
        epsilon=0.3,
        zeta=1.0,
    ),
    ConsumerTypeSpec(
        key="pragmatic_techies",
        label="Pragmatic Techies",
        population_share=0.20,
        p=0.05,
        q=0.35,
        peak_year=4.0,
        alpha=0.7,
        beta=0.4,
        gamma=0.5,
        delta=0.5,
        epsilon=0.5,
        zeta=0.4,
    ),
    ConsumerTypeSpec(
        key="convenience_seekers",
        label="Convenience Seekers",
        population_share=0.50,
        p=0.03,
        q=0.4,
        peak_year=6.0,
        alpha=1.0,
        beta=0.5,
        gamma=0.1,
        delta=0.2,
        epsilon=0.3,
        zeta=0.05,
    ),
    ConsumerTypeSpec(
        key="reluctant_adopters",
        label="Reluctant Adopters",
        population_share=0.20,
        p=0.02,
        q=0.3,
        peak_year=10.0,
        alpha=0.4,
        beta=0.9,
        gamma=0.05,
        delta=0.1,
        epsilon=0.2,
        zeta=0.02,
    ),
)

# Backward-compatible alias
CONSUMER_TYPES = DEFAULT_CONSUMER_TYPES


def bass_cumulative_fraction(t: np.ndarray, p: float, q: float) -> np.ndarray:
    """Bass diffusion cumulative adoption fraction f(t) in [0, 1), t >= 0."""
    t = np.maximum(t, 0.0)
    # Avoid division issues at t=0
    pq = p + q
    exp_term = np.exp(-pq * t)
    num = 1.0 - exp_term
    den = 1.0 + (q / p) * exp_term
    return num / den


def _bass_peak_time(p: float, q: float) -> float:
    """Time of maximum adoption rate for continuous Bass (years)."""

    def rate(tt: float) -> float:
        f = bass_cumulative_fraction(np.array([tt]), p, q)[0]
        return (p + q * f) * (1.0 - f)

    # Grid search — sufficient for tuning shift
    ts = np.linspace(0.01, 25.0, 5000)
    vals = np.array([rate(float(x)) for x in ts])
    return float(ts[int(np.argmax(vals))])


def compute_time_shifts(types: Tuple[ConsumerTypeSpec, ...]) -> Tuple[float, ...]:
    """Shift each type's Bass curve so its peak aligns near peak_year."""
    shifts: List[float] = []
    for ct in types:
        t_peak_natural = _bass_peak_time(ct.p, ct.q)
        shifts.append(max(0.0, ct.peak_year - t_peak_natural))
    return tuple(shifts)


def bass_arrival_weights(
    years: np.ndarray,
    p: float,
    q: float,
    shift: float,
) -> np.ndarray:
    """
    Normalised weights per step so sum equals 1.0 over the horizon.
    years: array of step start times in [0, T_horizon).
    """
    dt = float(years[1] - years[0]) if len(years) > 1 else 1.0 / 12.0
    # Step k covers [years[k], years[k]+dt)
    tau_start = np.maximum(0.0, years - shift)
    tau_end = np.maximum(0.0, years + dt - shift)
    c0 = bass_cumulative_fraction(tau_start, p, q)
    c1 = bass_cumulative_fraction(tau_end, p, q)
    w = np.maximum(c1 - c0, 0.0)
    total = w.sum()
    if total <= 0:
        return np.ones_like(w) / len(w)
    return w / total


def utility_open(
    alpha: float,
    beta: float,
    epsilon: float,
    zeta: float,
    Q_open: float,
    N_open: float,
    N_platform: float,
    A: float,
    V: float,
) -> float:
    return (
        alpha * Q_open
        + beta * N_open
        + epsilon * A
        + zeta * V
    )


def utility_platform(
    alpha: float,
    beta: float,
    gamma: float,
    delta: float,
    Q_platform: float,
    N_platform: float,
    L: float,
    E: float,
) -> float:
    return (
        alpha * Q_platform
        + beta * N_platform
        - gamma * L
        - delta * E
    )


def prob_open(utility_diff: float, lam: float) -> float:
    """Logistic choice probability for open vs platform."""
    x = lam * utility_diff
    if x > 35:
        return 1.0
    if x < -35:
        return 0.0
    return float(1.0 / (1.0 + np.exp(-x)))
