"""State variable evolution for the agentic web adoption model."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np


def sigmoid(x: float) -> float:
    if x >= 35:
        return 1.0
    if x <= -35:
        return 0.0
    return float(1.0 / (1.0 + np.exp(-x)))


@dataclass
class ModelParams:
    # Q_platform
    Q_plat_base: float = 0.8
    Q_plat_max: float = 0.99
    k_plat: float = 14.0
    plat_threshold: float = 0.24
    enshit_quality_drag: float = 0.26

    # Q_open
    Q_open_base: float = 0.05
    mu: float = 0.22

    # F(t) institutional maturity
    F_max: float = 0.68
    k_F: float = 0.2
    # Effective k_F = k_F * (1 + k_F_open_coupling * N_open): institutions mature faster when the
    # open installed base is larger (funding, participation, data to steward). 0 = legacy exogenous F.
    k_F_open_coupling: float = 1.0
    t_F_inflection: float = 5.0

    # Lock-in
    L_max: float = 0.38
    k_L: float = 0.3

    # Enshittification (threshold is platform share *among adopters*, not cumulative TAM share)
    E_max: float = 0.48
    k_E: float = 12.0
    enshit_threshold: float = 0.6
    enshit_ramp_years: float = 5.0

    # Agent friction
    A_max: float = 0.32
    k_A: float = 0.3

    # Values / autonomy
    V_base: float = 0.05
    V_awareness: float = 0.18
    k_V: float = 0.4
    t_V_inflection: float = 6.0

    # Choice
    choice_lambda: float = 15.0

    # Market timing: months before platform incumbents offer agentic products (all arrivals → open until then)
    platform_entry_delay_months: int = 14

    # Dominance threshold for lock-in clock (platform share)
    dominance_share_threshold: float = 0.49


def institutional_maturity(t: float, N_open: float, params: ModelParams) -> float:
    """Logistic F(t); steepness scales with open adoption when k_F_open_coupling > 0."""
    n = max(float(N_open), 0.0)
    k_eff = params.k_F * (1.0 + params.k_F_open_coupling * n)
    return params.F_max * sigmoid(k_eff * (t - params.t_F_inflection))


def agent_friction_reduction(t: float, params: ModelParams) -> float:
    return params.A_max * (1.0 - np.exp(-params.k_A * t))


def values_premium(t: float, params: ModelParams) -> float:
    return params.V_base + params.V_awareness * sigmoid(
        params.k_V * (t - params.t_V_inflection)
    )


def platform_signal_quality(
    N_platform: float,
    E: float,
    params: ModelParams,
) -> float:
    sig = sigmoid(params.k_plat * (N_platform - params.plat_threshold))
    q = params.Q_plat_base + (params.Q_plat_max - params.Q_plat_base) * sig
    q -= E * params.enshit_quality_drag
    return float(np.clip(q, 0.0, 1.0))


def commons_signal_quality(
    N_open: float,
    F: float,
    params: ModelParams,
) -> float:
    q = params.Q_open_base + params.mu * F * np.log(1.0 + max(N_open, 0.0))
    return float(np.clip(q, 0.0, 1.0))


def lock_in_disutility(
    T_platform: float,
    params: ModelParams,
) -> float:
    return float(params.L_max * (1.0 - np.exp(-params.k_L * max(T_platform, 0.0))))


def competitive_brake_factor(N_open: float) -> float:
    """Slow enshittification when open ecosystem stays viable."""
    return 1.0 - 0.5 * min(1.0, N_open / 0.3)


def platform_share_among_adopters(N_platform: float, N_open: float) -> float:
    """Installed-base split: platform share among users who have adopted either architecture."""
    total = N_platform + N_open
    if total <= 1e-12:
        return 0.0
    return float(N_platform / total)


def enshittification_factor(
    t: float,
    N_platform: float,
    N_open: float,
    t_enshit_start: Optional[float],
    params: ModelParams,
) -> float:
    s_plat = platform_share_among_adopters(N_platform, N_open)
    raw = params.E_max * sigmoid(
        params.k_E * (s_plat - params.enshit_threshold)
    )
    if t_enshit_start is None or s_plat < params.enshit_threshold:
        time_ramp = 0.0
    else:
        time_ramp = min(1.0, (t - t_enshit_start) / params.enshit_ramp_years)
    E = raw * time_ramp * competitive_brake_factor(N_open)
    return float(np.clip(E, 0.0, params.E_max))


def update_dominance_clock(
    t: float,
    N_platform: float,
    N_open: float,
    T_platform: float,
    dominance_started_at: Optional[float],
    params: ModelParams,
) -> Tuple[float, Optional[float]]:
    """
    T_platform: years platform has been "dominant" (share > threshold).
    Returns (new_T_platform, new_dominance_started_at).
    """
    total = N_platform + N_open
    if total <= 1e-12:
        return 0.0, dominance_started_at
    share_plat = N_platform / total
    if share_plat > params.dominance_share_threshold:
        if dominance_started_at is None:
            dominance_started_at = t
        elapsed = t - dominance_started_at
        return max(0.0, elapsed), dominance_started_at
    return 0.0, None


def update_enshit_start(
    t: float,
    N_platform: float,
    N_open: float,
    t_enshit_start: Optional[float],
    params: ModelParams,
) -> Optional[float]:
    if t_enshit_start is not None:
        return t_enshit_start
    s_plat = platform_share_among_adopters(N_platform, N_open)
    if s_plat >= params.enshit_threshold:
        return t
    return None
