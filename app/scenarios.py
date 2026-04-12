"""Preset scenario configurations for the sidebar."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class Scenario:
    name: str
    description: str
    k_F: float
    Q_plat_base: float
    A_max: float
    enshit_threshold: float


SCENARIOS: List[Scenario] = [
    Scenario(
        name="Platform Capture",
        description="Slow commons institutions, strong platform incumbency, limited agent leverage, early rent extraction.",
        k_F=0.2,
        Q_plat_base=0.6,
        A_max=0.3,
        enshit_threshold=0.5,
    ),
    Scenario(
        name="The Protocol Window",
        description="Fast institutional development and high agent-mediated usability; a credible open path.",
        k_F=1.2,
        Q_plat_base=0.5,
        A_max=0.7,
        enshit_threshold=0.6,
    ),
    Scenario(
        name="Federated Equilibrium",
        description="Balanced development; platforms need very high share before enshittification bites.",
        k_F=0.6,
        Q_plat_base=0.45,
        A_max=0.5,
        enshit_threshold=0.75,
    ),
    Scenario(
        name="Late Reversal",
        description="Slow early institutions, but strong agent friction reduction and delayed enshittification allow a belated open tilt.",
        k_F=0.4,
        Q_plat_base=0.55,
        A_max=0.65,
        enshit_threshold=0.68,
    ),
    Scenario(
        name="Custom",
        description="Use sidebar sliders as-is (no preset overwrite).",
        k_F=0.5,
        Q_plat_base=0.5,
        A_max=0.5,
        enshit_threshold=0.6,
    ),
]


def scenario_by_name(name: str) -> Scenario:
    for s in SCENARIOS:
        if s.name == name:
            return s
    return SCENARIOS[-1]


def scenario_options() -> Dict[str, str]:
    return {s.name: s.description for s in SCENARIOS}
