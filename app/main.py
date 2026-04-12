"""
Streamlit entry: agentic web platformisation simulation.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure project root is importable when Streamlit loads app/main.py
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st

from app.consumer_types import DEFAULT_CONSUMER_TYPES, ConsumerTypeSpec
from app.dynamics import ModelParams
from app.model import run_simulation
from app.scenarios import SCENARIOS, scenario_by_name
from app import ui_help as uh
from app.visualisation import (
    fig_adoption_shares,
    fig_arrivals,
    fig_flows,
    fig_institutions_and_friction,
    fig_share_of_adopters,
    fig_signal_quality,
    summary_metrics,
)


def _init_state() -> None:
    defaults = {
        "sv_k_F": 0.5,
        "sv_Q_plat_base": 0.5,
        "sv_A_max": 0.5,
        "sv_enshit_threshold": 0.6,
        "scenario_preset": "Custom",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def _apply_preset() -> None:
    name = st.session_state.get("scenario_preset", "Custom")
    if name == "Custom":
        return
    sc = scenario_by_name(name)
    st.session_state["sv_k_F"] = float(sc.k_F)
    st.session_state["sv_Q_plat_base"] = float(sc.Q_plat_base)
    st.session_state["sv_A_max"] = float(sc.A_max)
    st.session_state["sv_enshit_threshold"] = float(sc.enshit_threshold)


st.set_page_config(
    page_title="Agentic Web — Platformisation Sim",
    layout="wide",
    initial_sidebar_state="expanded",
)

_init_state()

st.markdown(
    """
    <style>
    footer[data-testid="stFooter"] { visibility: hidden; height: 0; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("The Agentic Web: Will It Platformise?")
st.markdown(
    "*A simulation model exploring whether the agentic ecosystem stays open or gets "
    "captured by platforms — and what determines the outcome. "
    "The **8-year monthly** horizon stresses speed: institutions must mature **before** platform dynamics close the window.*"
)
st.markdown(
    "This app runs a **logistic discrete-choice model** over **8 years** in **monthly** steps—deliberately "
    "compressed to reflect how **fast** agentic adoption and platform competition are moving relative to "
    "the **slow** work of building **commons institutions** (data unions, FIDU-like stewards, loyal signal "
    "processors). The same structural equations apply as in a longer run; the shorter horizon stresses **urgency**: "
    "if **F(t)** and open adoption do not advance quickly enough, platform feedback loops can still lock in. "
    "By default, **platform incumbents enter after a delay** (open-only months), reflecting decentralised "
    "tooling ahead of big-platform agents at scale."
)

# --- Sidebar: key levers first (not in expanders) ---
st.sidebar.markdown("### Key levers")
st.sidebar.caption(
    "Streamlit shows a **?** next to each control’s label. Click or hover **?** for the long description "
    "and the exact equations (same for advanced sliders below)."
)
st.sidebar.slider(
    "Commons institutional development speed (k_F)",
    min_value=0.1,
    max_value=2.0,
    step=0.05,
    key="sv_k_F",
    help=uh.K_F,
)
st.sidebar.slider(
    "Platform head start (Q_plat_base)",
    min_value=0.2,
    max_value=0.8,
    step=0.01,
    key="sv_Q_plat_base",
    help=uh.Q_PLAT_BASE,
)
st.sidebar.slider(
    "Enshittification onset — share among adopters (θ)",
    min_value=0.3,
    max_value=0.9,
    step=0.01,
    key="sv_enshit_threshold",
    help=uh.ENSHIT_THRESHOLD,
)
st.sidebar.slider(
    "Agent friction ceiling (A_max)",
    min_value=0.0,
    max_value=1.0,
    step=0.01,
    key="sv_A_max",
    help=uh.A_MAX,
)
platform_entry_delay_months = st.sidebar.slider(
    "Open adoption lead — platform entry delay (months)",
    min_value=0,
    max_value=96,
    value=24,
    step=1,
    help=uh.PLATFORM_ENTRY_DELAY,
)

st.sidebar.markdown("### Scenario presets")
scenario_names = [s.name for s in SCENARIOS]
st.sidebar.selectbox(
    "Scenario preset",
    options=scenario_names,
    key="scenario_preset",
    on_change=_apply_preset,
    help=uh.SCENARIO_PRESET,
)

preset_name = st.session_state["scenario_preset"]
if preset_name != "Custom":
    sc = scenario_by_name(preset_name)
    st.sidebar.info(
        f"{sc.description}\n\n"
        f"**Preset overwrites (Key levers):** "
        f"k_F=`{sc.k_F}` (in F(t)=F_max*sigmoid(k_F*(t-t_F*))), "
        f"Q_plat_base=`{sc.Q_plat_base}` (Q_platform baseline term), "
        f"A_max=`{sc.A_max}` (in A(t)=A_max*(1-exp(-k_A*t))), "
        f"enshit_threshold=`{sc.enshit_threshold}` (E uses s_plat vs this theta). "
        f"Full preset list: **?** help on the scenario control above."
    )

k_F = float(st.session_state["sv_k_F"])
Q_plat_base = float(st.session_state["sv_Q_plat_base"])
A_max = float(st.session_state["sv_A_max"])
enshit_threshold = float(st.session_state["sv_enshit_threshold"])

with st.sidebar.expander("Institutional & commons (Q_open)", expanded=False):
    mu = st.sidebar.slider(
        "μ — institutional effectiveness", 0.1, 1.0, 0.45, 0.01, help=uh.MU
    )
    Q_open_base = st.sidebar.slider(
        "Q_open_base", 0.05, 0.4, 0.15, 0.01, help=uh.Q_OPEN_BASE
    )
    F_max = st.sidebar.slider("F_max", 0.2, 1.0, 0.8, 0.01, help=uh.F_MAX)
    t_F_inflection = st.sidebar.slider(
        "t_F_inflection (years)", 1.0, 15.0, 5.0, 0.25, help=uh.T_F_INFLECTION
    )

with st.sidebar.expander("Platform quality curve", expanded=False):
    Q_plat_max = st.sidebar.slider(
        "Q_plat_max", 0.7, 1.0, 0.95, 0.01, help=uh.Q_PLAT_MAX
    )
    k_plat = st.sidebar.slider(
        "k_plat (sigmoid steepness)", 1.0, 20.0, 8.0, 0.5, help=uh.K_PLAT
    )
    plat_threshold = st.sidebar.slider(
        "plat_threshold", 0.1, 0.6, 0.35, 0.01, help=uh.PLAT_THRESHOLD
    )
    enshit_quality_drag = st.sidebar.slider(
        "enshit_quality_drag", 0.0, 1.0, 0.35, 0.01, help=uh.ENSHIT_QUALITY_DRAG
    )

with st.sidebar.expander("Lock-in & dominance", expanded=False):
    L_max = st.sidebar.slider("L_max", 0.1, 0.8, 0.4, 0.01, help=uh.L_MAX)
    k_L = st.sidebar.slider("k_L", 0.05, 1.0, 0.3, 0.01, help=uh.K_L)
    dominance_share_threshold = st.sidebar.slider(
        "Platform dominance share (lock-in clock)",
        0.4,
        0.7,
        0.5,
        0.01,
        help=uh.DOMINANCE_SHARE_THRESHOLD,
    )

with st.sidebar.expander("Enshittification dynamics", expanded=False):
    E_max = st.sidebar.slider("E_max", 0.2, 1.0, 0.6, 0.01, help=uh.E_MAX)
    k_E = st.sidebar.slider("k_E (sharpness)", 1.0, 30.0, 12.0, 0.5, help=uh.K_E)
    enshit_ramp_years = st.sidebar.slider(
        "enshit_ramp_years", 1.0, 15.0, 5.0, 0.5, help=uh.ENSHIT_RAMP_YEARS
    )

with st.sidebar.expander("Agents & values", expanded=False):
    k_A = st.sidebar.slider(
        "k_A (agent friction ramp)", 0.05, 1.0, 0.3, 0.01, help=uh.K_A
    )
    V_base = st.sidebar.slider("V_base", 0.0, 0.3, 0.1, 0.01, help=uh.V_BASE)
    V_awareness = st.sidebar.slider(
        "V_awareness", 0.0, 0.6, 0.3, 0.01, help=uh.V_AWARENESS
    )
    k_V = st.sidebar.slider("k_V", 0.1, 1.0, 0.4, 0.01, help=uh.K_V)
    t_V_inflection = st.sidebar.slider(
        "t_V_inflection (years)", 1.0, 15.0, 6.0, 0.25, help=uh.T_V_INFLECTION
    )

with st.sidebar.expander("Choice & diffusion", expanded=False):
    choice_lambda = st.sidebar.slider(
        "λ — choice sensitivity", 0.5, 15.0, 5.0, 0.5, help=uh.CHOICE_LAMBDA
    )

with st.sidebar.expander("Consumer types & mix", expanded=False):
    st.sidebar.caption(
        "Four segments with their own **Bass** timing (p, q, peak year) and **utility** weights α–ζ. "
        "Mix weights are **renormalized** to sum to 1. Use **?** on each control for equations."
    )
    raw_weights: list[float] = []
    built: list[tuple] = []
    for ct in DEFAULT_CONSUMER_TYPES:
        st.sidebar.markdown(f"#### {ct.label}")
        raw_weights.append(
            st.sidebar.slider(
                "Mix weight (normalized across types)",
                0.02,
                0.95,
                float(ct.population_share),
                0.01,
                key=f"cw_{ct.key}",
                help=uh.CONSUMER_MIX_WEIGHT,
            )
        )
        p = st.sidebar.slider(
            "Bass p (innovation)",
            0.005,
            0.2,
            float(ct.p),
            0.005,
            key=f"cp_{ct.key}",
            help=uh.CONSUMER_BASS_P,
        )
        q = st.sidebar.slider(
            "Bass q (imitation)",
            0.05,
            0.8,
            float(ct.q),
            0.01,
            key=f"cq_{ct.key}",
            help=uh.CONSUMER_BASS_Q,
        )
        peak_year = st.sidebar.slider(
            "Peak arrival year",
            0.5,
            11.0,
            float(min(ct.peak_year, 11.0)),
            0.25,
            key=f"cpeak_{ct.key}",
            help=uh.CONSUMER_PEAK_YEAR,
        )
        alpha = st.sidebar.slider(
            "α — signal quality",
            0.0,
            1.2,
            float(ct.alpha),
            0.05,
            key=f"ca_{ct.key}",
            help=uh.CONSUMER_ALPHA,
        )
        beta = st.sidebar.slider(
            "β — network",
            0.0,
            1.2,
            float(ct.beta),
            0.05,
            key=f"cb_{ct.key}",
            help=uh.CONSUMER_BETA,
        )
        gamma = st.sidebar.slider(
            "γ — lock-in aversion",
            0.0,
            1.2,
            float(ct.gamma),
            0.05,
            key=f"cg_{ct.key}",
            help=uh.CONSUMER_GAMMA,
        )
        delta = st.sidebar.slider(
            "δ — enshittification aversion",
            0.0,
            1.2,
            float(ct.delta),
            0.05,
            key=f"cd_{ct.key}",
            help=uh.CONSUMER_DELTA,
        )
        epsilon = st.sidebar.slider(
            "ε — agent friction value",
            0.0,
            1.2,
            float(ct.epsilon),
            0.05,
            key=f"ce_{ct.key}",
            help=uh.CONSUMER_EPSILON,
        )
        zeta = st.sidebar.slider(
            "ζ — values premium",
            0.0,
            1.2,
            float(ct.zeta),
            0.05,
            key=f"cz_{ct.key}",
            help=uh.CONSUMER_ZETA,
        )
        built.append((p, q, peak_year, alpha, beta, gamma, delta, epsilon, zeta))

    tw = sum(raw_weights)
    if tw <= 1e-9:
        tw = 1.0
    norm_weights = [w / tw for w in raw_weights]
    consumer_types = tuple(
        ConsumerTypeSpec(
            key=ct.key,
            label=ct.label,
            population_share=norm_weights[i],
            p=built[i][0],
            q=built[i][1],
            peak_year=built[i][2],
            alpha=built[i][3],
            beta=built[i][4],
            gamma=built[i][5],
            delta=built[i][6],
            epsilon=built[i][7],
            zeta=built[i][8],
        )
        for i, ct in enumerate(DEFAULT_CONSUMER_TYPES)
    )

params = ModelParams(
    Q_plat_base=Q_plat_base,
    Q_plat_max=Q_plat_max,
    k_plat=k_plat,
    plat_threshold=plat_threshold,
    enshit_quality_drag=enshit_quality_drag,
    Q_open_base=Q_open_base,
    mu=mu,
    F_max=F_max,
    k_F=k_F,
    t_F_inflection=t_F_inflection,
    L_max=L_max,
    k_L=k_L,
    E_max=E_max,
    k_E=k_E,
    enshit_threshold=enshit_threshold,
    enshit_ramp_years=enshit_ramp_years,
    A_max=A_max,
    k_A=k_A,
    V_base=V_base,
    V_awareness=V_awareness,
    k_V=k_V,
    t_V_inflection=t_V_inflection,
    choice_lambda=choice_lambda,
    platform_entry_delay_months=int(platform_entry_delay_months),
    dominance_share_threshold=dominance_share_threshold,
)

result = run_simulation(params, consumer_types=consumer_types)
df = result.df
metrics = summary_metrics(df)

c1, c2, c3 = st.columns(3)
c1.metric("Open share (cumulative, T=8y)", f"{metrics['final_open']:.1%}")
c2.metric("Platform share among adopters (T=8y)", f"{metrics['final_platform_share_among_adopters']:.1%}")
c3.metric("Peak enshittification E", f"{metrics['peak_E']:.2f}")

st.plotly_chart(fig_adoption_shares(df), use_container_width=True)
left, right = st.columns(2)
with left:
    st.plotly_chart(fig_share_of_adopters(df), use_container_width=True)
with right:
    st.plotly_chart(fig_signal_quality(df), use_container_width=True)

st.plotly_chart(fig_institutions_and_friction(df), use_container_width=True)

flow_l, flow_r = st.columns(2)
with flow_l:
    st.plotly_chart(fig_flows(df), use_container_width=True)
with flow_r:
    st.plotly_chart(fig_arrivals(df), use_container_width=True)

with st.expander("Model notes (equations & interpretation)"):
    st.markdown(
        """
        - **Horizon:** **8 years**, **monthly** steps (96 periods). Calendar time \\(t\\) in all dynamics is still **years**; only the step grid is finer. TAM = 1.
        - **Why 8 years / monthly:** The agentic layer is moving quickly; institutions are not. A compressed horizon makes **lag in F(t)** and **k_F** feel urgent—small delays in commons capacity can dominate outcomes.
        - **Consumer types (sidebar):** Four segments; **mix weights** renormalize to population shares. Each has **Bass** \\(p_i, q_i\\) and **peak arrival year** (time shift), plus **utility** weights \\(α_i…ζ_i\\) in \\(U_{open,i}\\), \\(U_{platform,i}\\).
        - **Arrivals:** Each consumer type follows a **shifted Bass** curve; weights normalise over the horizon so each type's total mass equals its population share.
        - **Choice:** Logistic probability with sensitivity λ on utility difference (open minus platform).
        - **Commons quality** \\(Q_{open}\\) scales with **F(t)** (institutional maturity) and \\(\\log(1+N_{open})\\), capped at 1.
        - **Platform quality** rises with platform installed base, then suffers from enshittification drag.
        - **Lock-in** \\(L\\) accumulates only after platform **share among adopters** exceeds the dominance threshold.
        - **Enshittification** ramps after **platform share among adopters** crosses the onset threshold; **competitive brake** slows it when \\(N_{open}\\) stays viable. **E** reduces \\(U_{platform}\\) via \\(-\\delta_i E\\) and lowers \\(Q_{platform}\\).
        - **Platform entry delay:** until that many **months** have passed, platforms are treated as not offering agents; all arrivals go open. That builds \\(N_{open}\\) and gives \\(F(t)\\) time to grow—critical when the clock is only 8 years.

        The **Commons Institutional Development Speed** slider controls **k_F** in
        \\(F(t)=F_{max}\\,\\sigma(k_F(t-t_F^*))\\) — the main lever for whether commons signal
        processing can catch up **in time** before platform feedback loops lock in.
        """
    )
