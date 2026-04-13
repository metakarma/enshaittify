"""Core simulation: monthly steps over 8 years (calendar t in years; equations unchanged)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from app.consumer_types import (
    DEFAULT_CONSUMER_TYPES,
    ConsumerTypeSpec,
    bass_arrival_weights,
    compute_time_shifts,
    prob_open,
    prob_switch_open_to_platform,
    prob_switch_platform_to_open,
    utility_open,
    utility_platform,
)
from app.dynamics import (
    ModelParams,
    agent_friction_reduction,
    commons_signal_quality,
    enshittification_factor,
    institutional_maturity,
    lock_in_disutility,
    platform_signal_quality,
    update_dominance_clock,
    update_enshit_start,
    values_premium,
)


@dataclass
class SimulationResult:
    df: pd.DataFrame
    params: ModelParams


def run_simulation(
    params: ModelParams,
    consumer_types: Optional[Tuple[ConsumerTypeSpec, ...]] = None,
    horizon_years: float = 8.0,
    dt: float = 1.0 / 12.0,
) -> SimulationResult:
    cts = consumer_types if consumer_types is not None else DEFAULT_CONSUMER_TYPES
    time_shifts = compute_time_shifts(cts)
    n_types = len(cts)

    n_steps = int(round(horizon_years / dt))
    years = np.arange(n_steps, dtype=float) * dt

    # Precompute normalised arrival weights per type, scale by population share
    arrival_matrix = np.zeros((n_types, n_steps))
    for i, ct in enumerate(cts):
        w = bass_arrival_weights(years, ct.p, ct.q, time_shifts[i])
        arrival_matrix[i, :] = ct.population_share * w

    # Installed base by type and architecture (sum_i S_open[i] + S_plat[i] = adopters so far)
    S_open = np.zeros(n_types, dtype=float)
    S_plat = np.zeros(n_types, dtype=float)

    T_platform = 0.0
    dominance_started_at: Optional[float] = None
    t_enshit_start: Optional[float] = None

    rows: List[Dict[str, Any]] = []
    lam = float(params.choice_lambda)

    for k in range(n_steps):
        t = float(years[k])

        N_open = float(S_open.sum())
        N_platform = float(S_plat.sum())

        T_platform, dominance_started_at = update_dominance_clock(
            t, N_platform, N_open, T_platform, dominance_started_at, params
        )
        t_enshit_start = update_enshit_start(
            t, N_platform, N_open, t_enshit_start, params
        )

        L = lock_in_disutility(T_platform, params)
        F = institutional_maturity(t, N_open, params)
        A = agent_friction_reduction(t, params)
        V = values_premium(t, params)

        E = enshittification_factor(
            t, N_platform, N_open, t_enshit_start, params
        )
        Q_plat = platform_signal_quality(N_platform, E, params)
        Q_op = commons_signal_quality(N_open, F, params)

        step_arrivals = arrival_matrix[:, k]
        total_arriving = float(step_arrivals.sum())

        new_open_by_type = np.zeros(n_types)
        new_plat_by_type = np.zeros(n_types)

        # --- Phase 1: new arrivals (utilities at start of month) ---
        for i, ct in enumerate(cts):
            arr = float(step_arrivals[i])
            if arr <= 0:
                continue
            u_o = utility_open(
                ct.alpha,
                ct.beta,
                ct.epsilon,
                ct.zeta,
                Q_op,
                N_open,
                N_platform,
                A,
                V,
            )
            u_p = utility_platform(
                ct.alpha,
                ct.beta,
                ct.gamma,
                ct.delta,
                Q_plat,
                N_platform,
                L,
                E,
            )
            if k < params.platform_entry_delay_months:
                p_open = 1.0
            else:
                p_open = prob_open(u_o - u_p, lam)
            new_open_by_type[i] = arr * p_open
            new_plat_by_type[i] = arr * (1.0 - p_open)

        S_open = S_open + new_open_by_type
        S_plat = S_plat + new_plat_by_type

        d_open = float(new_open_by_type.sum())
        d_plat = float(new_plat_by_type.sum())

        N_open_post = float(S_open.sum())
        N_platform_post = float(S_plat.sum())

        # Post-arrival signal state for switching decisions
        E_sw = enshittification_factor(
            t, N_platform_post, N_open_post, t_enshit_start, params
        )
        Q_plat_sw = platform_signal_quality(N_platform_post, E_sw, params)
        Q_op_sw = commons_signal_quality(N_open_post, F, params)

        switch_o_to_p = np.zeros(n_types)
        switch_p_to_o = np.zeros(n_types)

        # --- Phase 2: switching (only after platform entry; arrivals first) ---
        if k >= params.platform_entry_delay_months:
            for i, ct in enumerate(cts):
                u_o = utility_open(
                    ct.alpha,
                    ct.beta,
                    ct.epsilon,
                    ct.zeta,
                    Q_op_sw,
                    N_open_post,
                    N_platform_post,
                    A,
                    V,
                )
                u_p = utility_platform(
                    ct.alpha,
                    ct.beta,
                    ct.gamma,
                    ct.delta,
                    Q_plat_sw,
                    N_platform_post,
                    L,
                    E_sw,
                )
                p_op = prob_switch_open_to_platform(
                    u_o, u_p, ct.leave_open_cost, lam
                )
                p_po = prob_switch_platform_to_open(
                    u_o, u_p, ct.leave_platform_cost, lam
                )
                switch_o_to_p[i] = float(S_open[i]) * p_op
                switch_p_to_o[i] = float(S_plat[i]) * p_po

            S_open = S_open - switch_o_to_p + switch_p_to_o
            S_plat = S_plat + switch_o_to_p - switch_p_to_o
            S_open = np.maximum(S_open, 0.0)
            S_plat = np.maximum(S_plat, 0.0)

        N_open = float(S_open.sum())
        N_platform = float(S_plat.sum())

        total = N_open + N_platform
        plat_share = N_platform / total if total > 1e-12 else 0.0
        open_share = N_open / total if total > 1e-12 else 0.0

        E_end = enshittification_factor(
            t, N_platform, N_open, t_enshit_start, params
        )
        Q_plat_end = platform_signal_quality(N_platform, E_end, params)
        Q_op_end = commons_signal_quality(N_open, F, params)

        row: Dict[str, Any] = {
            "step": k,
            "year": t,
            "platform_agents_available": float(
                1 if k >= params.platform_entry_delay_months else 0
            ),
            "N_open": N_open,
            "N_platform": N_platform,
            "platform_share": plat_share,
            "open_share": open_share,
            "total_adopters": total,
            "Q_platform": Q_plat_end,
            "Q_open": Q_op_end,
            "F": F,
            "L": L,
            "E": E_end,
            "A": A,
            "V": V,
            "arriving_total": total_arriving,
            "new_open": d_open,
            "new_platform": d_plat,
            "switch_open_to_platform": float(switch_o_to_p.sum()),
            "switch_platform_to_open": float(switch_p_to_o.sum()),
            "T_platform": T_platform,
        }
        for i, ct in enumerate(cts):
            row[f"arriving_{ct.key}"] = float(step_arrivals[i])
            row[f"new_open_{ct.key}"] = float(new_open_by_type[i])
            row[f"new_platform_{ct.key}"] = float(new_plat_by_type[i])
        rows.append(row)

    df = pd.DataFrame(rows)
    return SimulationResult(df=df, params=params)
