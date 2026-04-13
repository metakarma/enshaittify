"""Preset scenario configurations for the sidebar."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class Scenario:
    name: str
    description: str
    k_F: float
    Q_plat_base: float
    A_max: float
    enshit_threshold: float
    # Logit inverse temperature; at high λ the four fields above barely move outcomes — presets set λ per story.
    choice_lambda: float
    # Optional advanced overrides (None = use ModelParams defaults after preset reset).
    platform_entry_delay_months: Optional[int] = None
    mu: Optional[float] = None
    Q_open_base: Optional[float] = None
    F_max: Optional[float] = None
    k_F_open_coupling: Optional[float] = None
    E_max: Optional[float] = None
    k_E: Optional[float] = None
    enshit_quality_drag: Optional[float] = None
    enshit_ramp_years: Optional[float] = None
    k_plat: Optional[float] = None
    plat_threshold: Optional[float] = None
    Q_plat_max: Optional[float] = None


SCENARIOS: List[Scenario] = [
    Scenario(
        name="Pre-agent web (email-like)",
        description=(
            "Analogue to **email and the early web**: open protocols lead briefly, then integrated "
            "platforms win on convenience and quality; ~**10%** of adopters stay on non-platform paths "
            "(self-hosting, standards-first). Calibrated on the 8y monthly run."
        ),
        k_F=0.2,
        Q_plat_base=0.8,
        A_max=0.32,
        enshit_threshold=0.6,
        choice_lambda=12.0,
    ),
    Scenario(
        name="Platform Capture",
        description="Slow commons institutions, strong platform incumbency, limited agent leverage, early rent extraction.",
        k_F=0.2,
        Q_plat_base=0.6,
        A_max=0.3,
        enshit_threshold=0.5,
        choice_lambda=14.0,
    ),
    Scenario(
        name="Decentralisation Scenario",
        description=(
            "Calibrated to **~60% cumulative open (decentralised) TAM share** at 8 years: **strong open-side "
            "signal** (commons institutions and Q_open), **salient fear of platform enshittification** "
            "(earlier onset, sharper E, more quality drag), and **slow platform capture of the space** "
            "(long entry delay, moderated proprietary baseline and installed-base curve). "
            "Selecting any non-Custom preset resets **advanced** sliders to model defaults, then this scenario "
            "replaces them with the sweep-tuned bundle below."
        ),
        k_F=1.85,
        Q_plat_base=0.52,
        A_max=0.72,
        enshit_threshold=0.37,
        choice_lambda=1.9,
        platform_entry_delay_months=57,
        mu=1.0,
        Q_open_base=0.21,
        F_max=0.76,
        k_F_open_coupling=2.85,
        E_max=0.79,
        k_E=19.0,
        enshit_quality_drag=0.49,
        enshit_ramp_years=2.5,
        k_plat=6.5,
        plat_threshold=0.50,
        Q_plat_max=0.93,
    ),
    Scenario(
        name="Federated Equilibrium",
        description=(
            "Balanced **coexistence** narrative: sweep-tuned for **~30% cumulative open TAM** at 8y (vs ~6% for "
            "Platform Capture) — credible commons institutions, modest proprietary head start, **late** "
            "enshittification onset, and **softer** logit choices (lower λ) so the open side stays contestable."
        ),
        k_F=0.65,
        Q_plat_base=0.44,
        A_max=0.55,
        enshit_threshold=0.76,
        choice_lambda=0.95,
    ),
    Scenario(
        name="Late Reversal",
        description="Slow early institutions, but strong agent friction reduction and delayed enshittification allow a belated open tilt.",
        k_F=0.4,
        Q_plat_base=0.55,
        A_max=0.65,
        enshit_threshold=0.68,
        choice_lambda=5.0,
    ),
    Scenario(
        name="Custom",
        description="Use sidebar sliders as-is (no preset overwrite).",
        k_F=0.5,
        Q_plat_base=0.5,
        A_max=0.5,
        enshit_threshold=0.6,
        choice_lambda=15.0,
    ),
]


def scenario_by_name(name: str) -> Scenario:
    for s in SCENARIOS:
        if s.name == name:
            return s
    return SCENARIOS[-1]


def scenario_options() -> Dict[str, str]:
    return {s.name: s.description for s in SCENARIOS}
