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
from app.scenarios import SCENARIOS, Scenario, scenario_by_name
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


def _advanced_session_from_model(mp: ModelParams) -> dict:
    """Sidebar session keys for non-consumer-type sliders (synced when applying a preset)."""
    return {
        "sv_platform_entry_delay_months": int(mp.platform_entry_delay_months),
        "sv_mu": float(mp.mu),
        "sv_Q_open_base": float(mp.Q_open_base),
        "sv_F_max": float(mp.F_max),
        "sv_t_F_inflection": float(mp.t_F_inflection),
        "sv_k_F_open_coupling": float(mp.k_F_open_coupling),
        "sv_Q_plat_max": float(mp.Q_plat_max),
        "sv_k_plat": float(mp.k_plat),
        "sv_plat_threshold": float(mp.plat_threshold),
        "sv_enshit_quality_drag": float(mp.enshit_quality_drag),
        "sv_L_max": float(mp.L_max),
        "sv_k_L": float(mp.k_L),
        "sv_dominance_share_threshold": float(mp.dominance_share_threshold),
        "sv_E_max": float(mp.E_max),
        "sv_k_E": float(mp.k_E),
        "sv_enshit_ramp_years": float(mp.enshit_ramp_years),
        "sv_k_A": float(mp.k_A),
        "sv_V_base": float(mp.V_base),
        "sv_V_awareness": float(mp.V_awareness),
        "sv_k_V": float(mp.k_V),
        "sv_t_V_inflection": float(mp.t_V_inflection),
    }


def _scenario_apply_advanced_overrides(sc: Scenario) -> None:
    mapping = (
        ("platform_entry_delay_months", "sv_platform_entry_delay_months", int),
        ("mu", "sv_mu", float),
        ("Q_open_base", "sv_Q_open_base", float),
        ("F_max", "sv_F_max", float),
        ("k_F_open_coupling", "sv_k_F_open_coupling", float),
        ("E_max", "sv_E_max", float),
        ("k_E", "sv_k_E", float),
        ("enshit_quality_drag", "sv_enshit_quality_drag", float),
        ("enshit_ramp_years", "sv_enshit_ramp_years", float),
        ("k_plat", "sv_k_plat", float),
        ("plat_threshold", "sv_plat_threshold", float),
        ("Q_plat_max", "sv_Q_plat_max", float),
    )
    for attr, skey, cast in mapping:
        v = getattr(sc, attr)
        if v is not None:
            st.session_state[skey] = cast(v)


def _init_state() -> None:
    defaults = {
        "sv_k_F": 0.2,
        "sv_Q_plat_base": 0.8,
        "sv_A_max": 0.32,
        "sv_enshit_threshold": 0.6,
        "sv_choice_lambda": 12.0,
        "scenario_preset": "Pre-agent web (email-like)",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
    mp = ModelParams()
    for k, v in _advanced_session_from_model(mp).items():
        if k not in st.session_state:
            st.session_state[k] = v


def _apply_preset() -> None:
    name = st.session_state.get("scenario_preset", "Custom")
    if name == "Custom":
        return
    mp = ModelParams()
    for k, v in _advanced_session_from_model(mp).items():
        st.session_state[k] = v
    sc = scenario_by_name(name)
    st.session_state["sv_k_F"] = float(sc.k_F)
    st.session_state["sv_Q_plat_base"] = float(sc.Q_plat_base)
    st.session_state["sv_A_max"] = float(sc.A_max)
    st.session_state["sv_enshit_threshold"] = float(sc.enshit_threshold)
    st.session_state["sv_choice_lambda"] = float(sc.choice_lambda)
    _scenario_apply_advanced_overrides(sc)


st.set_page_config(
    page_title="Agentic Web — Platformisation Sim",
    layout="wide",
    initial_sidebar_state="expanded",
)

_init_state()
# Legacy preset label (rename Decentralisation Scenario)
if st.session_state.get("scenario_preset") == "The Protocol Window":
    st.session_state["scenario_preset"] = "Decentralisation Scenario"
    _apply_preset()

st.markdown(
    """
    <style>
    footer[data-testid="stFooter"] { visibility: hidden; height: 0; }
    /* KaTeX in st.markdown and in widget help popovers (same $ / $$ parsing) */
    div[data-testid="stMarkdownContainer"] .katex-display,
    div[data-baseweb="popover"] .katex-display {
        overflow-x: auto;
        overflow-y: hidden;
        padding: 0.35em 0;
        max-width: 100%;
    }
    div[data-testid="stMarkdownContainer"] .katex { font-size: 1.05em; }
    div[data-baseweb="popover"] .katex { font-size: 0.98em; }
    div[data-baseweb="popover"] { max-width: min(440px, 92vw); }
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

# --- Sidebar: scenario first (applies before key-lever widgets read session state) ---
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
        f"k_F=`{sc.k_F}`, "
        f"Q_plat_base=`{sc.Q_plat_base}`, "
        f"A_max=`{sc.A_max}`, "
        f"enshit_threshold=`{sc.enshit_threshold}`, "
        f"λ=`{sc.choice_lambda}` (logit sensitivity — low λ spreads adoption across outcomes). "
        f"**Non-Custom presets** also reset **advanced** expander sliders to model defaults "
        f"(Decentralisation then applies its sweep-tuned bundle). "
        f"Full list: **?** on the scenario control."
    )

st.sidebar.markdown("### Key levers")
st.sidebar.caption(
    "Streamlit shows a **?** next to each control’s label. Click or hover **?** for the long description "
    "and the exact equations (same for advanced sliders below)."
)
st.sidebar.slider(
    "Commons institutional development speed (k_F)",
    min_value=0.1,
    max_value=2.5,
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
st.sidebar.slider(
    "λ — choice sensitivity (logit)",
    min_value=0.5,
    max_value=15.0,
    step=0.1,
    key="sv_choice_lambda",
    help=uh.CHOICE_LAMBDA,
)
platform_entry_delay_months = st.sidebar.slider(
    "Open adoption lead — platform entry delay (months)",
    min_value=0,
    max_value=96,
    step=1,
    key="sv_platform_entry_delay_months",
    help=uh.PLATFORM_ENTRY_DELAY,
)

k_F = float(st.session_state["sv_k_F"])
Q_plat_base = float(st.session_state["sv_Q_plat_base"])
A_max = float(st.session_state["sv_A_max"])
enshit_threshold = float(st.session_state["sv_enshit_threshold"])
choice_lambda = float(st.session_state["sv_choice_lambda"])

with st.sidebar.expander("Institutional & commons (Q_open)", expanded=False):
    mu = st.sidebar.slider(
        "μ — institutional effectiveness",
        0.1,
        1.0,
        step=0.01,
        key="sv_mu",
        help=uh.MU,
    )
    Q_open_base = st.sidebar.slider(
        "Q_open_base", 0.05, 0.4, step=0.01, key="sv_Q_open_base", help=uh.Q_OPEN_BASE
    )
    F_max = st.sidebar.slider(
        "F_max", 0.2, 1.0, step=0.01, key="sv_F_max", help=uh.F_MAX
    )
    t_F_inflection = st.sidebar.slider(
        "t_F_inflection (years)",
        1.0,
        15.0,
        step=0.25,
        key="sv_t_F_inflection",
        help=uh.T_F_INFLECTION,
    )
    k_F_open_coupling = st.sidebar.slider(
        "φ — F speed scales with N_open (supply-side loop)",
        0.0,
        3.0,
        step=0.05,
        key="sv_k_F_open_coupling",
        help=uh.K_F_OPEN_COUPLING,
    )

with st.sidebar.expander("Platform quality curve", expanded=False):
    Q_plat_max = st.sidebar.slider(
        "Q_plat_max", 0.7, 1.0, step=0.01, key="sv_Q_plat_max", help=uh.Q_PLAT_MAX
    )
    k_plat = st.sidebar.slider(
        "k_plat (sigmoid steepness)",
        1.0,
        20.0,
        step=0.5,
        key="sv_k_plat",
        help=uh.K_PLAT,
    )
    plat_threshold = st.sidebar.slider(
        "plat_threshold",
        0.1,
        0.6,
        step=0.01,
        key="sv_plat_threshold",
        help=uh.PLAT_THRESHOLD,
    )
    enshit_quality_drag = st.sidebar.slider(
        "enshit_quality_drag",
        0.0,
        1.0,
        step=0.01,
        key="sv_enshit_quality_drag",
        help=uh.ENSHIT_QUALITY_DRAG,
    )

with st.sidebar.expander("Lock-in & dominance", expanded=False):
    L_max = st.sidebar.slider(
        "L_max", 0.1, 0.8, step=0.01, key="sv_L_max", help=uh.L_MAX
    )
    k_L = st.sidebar.slider(
        "k_L", 0.05, 1.0, step=0.01, key="sv_k_L", help=uh.K_L
    )
    dominance_share_threshold = st.sidebar.slider(
        "Platform dominance share (lock-in clock)",
        0.4,
        0.7,
        step=0.01,
        key="sv_dominance_share_threshold",
        help=uh.DOMINANCE_SHARE_THRESHOLD,
    )

with st.sidebar.expander("Enshittification dynamics", expanded=False):
    E_max = st.sidebar.slider(
        "E_max", 0.2, 1.0, step=0.01, key="sv_E_max", help=uh.E_MAX
    )
    k_E = st.sidebar.slider(
        "k_E (sharpness)", 1.0, 30.0, step=0.5, key="sv_k_E", help=uh.K_E
    )
    enshit_ramp_years = st.sidebar.slider(
        "enshit_ramp_years",
        1.0,
        15.0,
        step=0.5,
        key="sv_enshit_ramp_years",
        help=uh.ENSHIT_RAMP_YEARS,
    )

with st.sidebar.expander("Agents & values", expanded=False):
    k_A = st.sidebar.slider(
        "k_A (agent friction ramp)",
        0.05,
        1.0,
        step=0.01,
        key="sv_k_A",
        help=uh.K_A,
    )
    V_base = st.sidebar.slider(
        "V_base", 0.0, 0.3, step=0.01, key="sv_V_base", help=uh.V_BASE
    )
    V_awareness = st.sidebar.slider(
        "V_awareness",
        0.0,
        0.6,
        step=0.01,
        key="sv_V_awareness",
        help=uh.V_AWARENESS,
    )
    k_V = st.sidebar.slider(
        "k_V", 0.1, 1.0, step=0.01, key="sv_k_V", help=uh.K_V
    )
    t_V_inflection = st.sidebar.slider(
        "t_V_inflection (years)",
        1.0,
        15.0,
        step=0.25,
        key="sv_t_V_inflection",
        help=uh.T_V_INFLECTION,
    )

with st.sidebar.expander("Consumer types & mix", expanded=False):
    st.sidebar.caption(
        "Four segments: **Bass** timing (p, q, peak year), **utility** weights α–ζ, and **asymmetric "
        "leave costs** for switching after arrivals. Mix weights **renormalize** to 1. Use **?** for equations."
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
        leave_open = st.sidebar.slider(
            "Leave-open cost (open → platform)",
            0.0,
            2.0,
            float(ct.leave_open_cost),
            0.05,
            key=f"clo_{ct.key}",
            help=uh.CONSUMER_LEAVE_OPEN,
        )
        leave_plat = st.sidebar.slider(
            "Leave-platform cost (platform → open)",
            0.0,
            2.0,
            float(ct.leave_platform_cost),
            0.05,
            key=f"clp_{ct.key}",
            help=uh.CONSUMER_LEAVE_PLATFORM,
        )
        built.append(
            (
                p,
                q,
                peak_year,
                alpha,
                beta,
                gamma,
                delta,
                epsilon,
                zeta,
                leave_open,
                leave_plat,
            )
        )

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
            leave_open_cost=built[i][9],
            leave_platform_cost=built[i][10],
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
    k_F_open_coupling=k_F_open_coupling,
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
c1.metric(
    "Open share (cumulative, T=8y)",
    f"{metrics['final_open']:.1%}",
    help=uh.METRIC_OPEN_SHARE_CUMULATIVE,
)
c2.metric(
    "Platform share among adopters (T=8y)",
    f"{metrics['final_platform_share_among_adopters']:.1%}",
    help=uh.METRIC_PLATFORM_SHARE_AMONG_ADOPTERS,
)
c3.metric(
    "Peak enshittification E",
    f"{metrics['peak_E']:.2f}",
    help=uh.METRIC_PEAK_ENSHITTIFICATION,
)

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
        r"""
#### 1. Architecture (what the simulation is)

The model is a **discrete-time stock–flow system** on a **fixed total market** (TAM = 1). Each month, **new adopters** arrive and choose **open** or **platform**; **existing** adopters may **switch** (after arrivals) once platforms are in the market, with per-type **asymmetric leave costs** in utility units. Cumulative stocks are $N_{open}(t)$ and $N_{platform}(t)$; **platform share among adopters** is $s_{plat} = N_{platform}/(N_{open}+N_{platform})$.

**Heterogeneity:** users differ by **consumer type** $i$ (four segments). Each type has its own **diffusion timing** (shifted Bass) and its own **tastes** $(\alpha_i,\ldots,\zeta_i)$ in utility. **Mix weights** in the sidebar are renormalised to population shares $\omega_i$ so $\sum_i \omega_i = 1$.

**Latent state (same for everyone each month):** before choices, the code updates **institutional maturity** $F(t)$, **agent-friction relief** $A(t)$, **values / autonomy premium** $V(t)$, **platform signal quality** $Q_{platform}$, **commons signal quality** $Q_{open}$, **lock-in disutility** $L$, and **enshittification intensity** $E$. These enter **utilities** and therefore **choice probabilities**.

**Flow:** arrivals $\rightarrow$ **logit** split $\rightarrow$ update per-type stocks on each side $\rightarrow$ (once platforms exist) **switching** logit with asymmetric leave costs $\rightarrow$ end-of-month $N_{open}, N_{platform}$.

---

#### 2. Time grid and horizon

- **Horizon:** 8 **years**; **monthly** steps ($\Delta t = 1/12$ year, 96 periods).
- **Calendar time** $t$ passed into $F, A, V, \ldots$ is always **years since start** (step index $\times$ $\Delta t$).
- **Why short and monthly:** the app stresses **speed asymmetry**: agentic adoption and platform feedback can move month-to-month, while **commons institutions** ($F$) move through $F(t)$ on the same calendar clock—so **$k_F$** and **inflection timing** feel urgent.

---

#### 3. Sigmoid / logistic building blocks

Several pieces use the **logistic sigmoid**
$$
\sigma(x) = \frac{1}{1 + e^{-x}}
$$
clipped for numerical stability at large $|x|$. In this model $\sigma$ is **not** a demand curve by itself; it is a **smooth switch** between regimes:

| Where | Role |
|-------|------|
| $F(t)$, $V(t)$ | **S-curves in time** (institutions / norms turning “on”) |
| $Q_{platform}(N_{platform})$ | **Quality vs scale**: platform experience improves as installed base crosses a threshold |
| Onset of $E$ vs $s_{plat}$ | **Enshittification** turns on when platform **share among adopters** crosses $\theta$ |

**Choice** uses the same mathematical family: the probability of choosing open is a **logistic (logit)** in the **utility gap**, i.e. a **random utility model** where $\lambda$ scales how sharply small differences in utility translate into market shares. Large $\lambda$ $\Rightarrow$ **winner-take-most** split; small $\lambda$ $\Rightarrow$ **mixed** split even when one side is somewhat better.

---

#### 4. Arrivals (shifted Bass, per type)

Each type $i$ follows a **Bass diffusion** in continuous time with innovation $p_i$ and imitation $q_i$, **time-shifted** so its adoption-rate peak sits near its **peak arrival year**. For each month, the code takes the **increment** of the Bass cumulative curve on that interval, **normalises** so type $i$’s total arrival mass over the horizon equals $\omega_i$, and builds per-step weights $a_{i,k}$ (arrivals of type $i$ in step $k$). Total arrivals in step $k$ sum to the global diffusion pace implied by those curves (not necessarily 1 in one step—mass accumulates to full TAM over the run).

---

#### 5. Latent dynamics (equations in code)

**Institutions:** with effective steepness $k_F^{\mathrm{eff}} = k_F\bigl(1 + \varphi\,N_{open}\bigr)$,
$$
F(t) = F_{max}\,\sigma\!\big(k_F^{\mathrm{eff}} (t - t_F^\*)\big).
$$
Set $\varphi=0$ for the legacy schedule (no dependence on open adoption); $\varphi>0$ makes institutional maturity **faster when the open ecosystem is larger** (funding, participation, stewardship scale).

**Agent friction (open-side convenience):** $A(t) = A_{max}\big(1 - e^{-k_A t}\big)$ (exponential **saturation**, not a sigmoid).

**Values / autonomy:** $V(t) = V_{base} + V_{awareness}\,\sigma\!\big(k_V (t - t_V^\*)\big)$.

**Commons signal quality:**  
$$
Q_{open} = \mathrm{clip}\!\Big(Q_{open}^{base} + \mu\,F(t)\,\log(1+N_{open}),\,0,\,1\Big).
$$  
So open quality rises with **institutional maturity** and **open installed base** (log congestion / ecosystem depth).

**Platform signal quality:** let $n^\dagger$ denote the **plat threshold** parameter (the installed-base level in the code). With $\sigma_{plat} = \sigma\!\big(k_{plat}(N_{platform} - n^\dagger)\big)$,  
$$
Q_{platform} = \mathrm{clip}\!\Big(Q_{plat}^{base} + (Q_{plat}^{max}-Q_{plat}^{base})\,\sigma_{plat} - E \cdot d_{enshit},\,0,\,1\Big).
$$  
So quality rises with **platform scale**, then is dragged down by **enshittification** $E$ with strength $d_{enshit}$ (`enshit_quality_drag` in the sidebar).

**Lock-in:** Let $s_{plat}$ be share among adopters. If $s_{plat}$ exceeds a **dominance** threshold, a clock records **how long** dominance has held; $T_{platform}$ is that elapsed **dominance time** (years). Then  
$$
L = L_{max}\big(1 - e^{-k_L\,T_{platform}}\big).
$$  
If not dominant, $T_{platform}$ is reset to 0, so **lock-in disutility** does not accumulate.

**Enshittification:** Let $s_{plat} = N_{platform}/(N_{open}+N_{platform})$. A **potential** intensity is  
$$
E_{raw} = E_{max}\,\sigma\!\big(k_E (s_{plat} - \theta_{enshit})\big).
$$  
When $s_{plat}$ first reaches $\theta_{enshit}$, the model **starts a timer** $t_{enshit}^{start}$. A **time ramp** (0 to 1 over `enshit_ramp_years`) multiplies $E_{raw}$ so $E$ does not jump to full strength instantly. A **competitive brake** $\mathrm{brake}(N_{open}) = 1 - \tfrac{1}{2}\min(1,\,N_{open}/0.3)$ slows enshittification when the open side still has **material** installed base. Finally $E = \mathrm{clip}(E_{raw}\cdot\text{ramp}\cdot\text{brake},\,0,\,E_{max})$.

---

#### 6. Utilities (why two different formulas)

Per type $i$, **open** utility rewards signal quality, **open** network size, agent friction relief, and values—all things the narrative ties to **commons + tools**:

$$
U_{open,i} = \alpha_i Q_{open} + \beta_i N_{open} + \epsilon_i A + \zeta_i V.
$$

**Platform** utility rewards platform quality and **platform** network size, and is penalised by lock-in and enshittification (tastes $\gamma_i, \delta_i$):

$$
U_{platform,i} = \alpha_i Q_{platform} + \beta_i N_{platform} - \gamma_i L - \delta_i E.
$$

**Interpretation:** $\alpha_i$ is **quality sensitivity**; $\beta_i$ is **direct network effect** on each side; $\epsilon_i, \zeta_i$ matter only for open; $\gamma_i, \delta_i$ only for platform pain. The **same** $\alpha_i, \beta_i$ appear on both sides so “quality” and “scale” are comparable—but **$Q_{open}$** and **$Q_{platform}$** follow **different** state equations.

---

#### 7. Logit choice and split of arrivals

After platform entry (see below), for each arriving mass of type $i$,

$$
p_{open,i} = \frac{1}{1 + e^{-\lambda\,(U_{open,i} - U_{platform,i})}}.
$$

Then $\Delta N_{open,i} = a_{i,k}\, p_{open,i}$, $\Delta N_{platform,i} = a_{i,k}\, (1-p_{open,i})$ in step $k$. **$\lambda$** is the sidebar “choice sensitivity”: it is the **steepness** of the logistic in **utility difference** (formally, random-utility scale).

---

#### 8. Platform entry delay

For the first **$D$** months (sidebar: **platform entry delay**), the model sets $p_{open}=1$: incumbents are treated as **not yet** offering the agentic product, so **all** arrivals go open. This builds early $N_{open}$ and lets $F(t)$ advance—analogous to **protocols and grassroots tooling ahead of big-platform agents at scale**.

---

#### 9. Switching (existing users, after arrivals)

The model keeps **per-type** installed mass on open and on platform: $S^{open}_i$, $S^{plat}_i$. Each month, **arrivals are allocated first**. Then utilities are recomputed using **post-arrival** $N_{open}, N_{platform}$ (and the corresponding $Q_{open}, Q_{platform}, E$). **Only after platform entry** ($k \ge D$), existing users may switch:

$$
\mathbb{P}(O\!\to\!P) = \sigma\big(\lambda\,(U_{platform,i} - U_{open,i} - \kappa^{O\to P}_i)\big), \quad
\mathbb{P}(P\!\to\!O) = \sigma\big(\lambda\,(U_{open,i} - U_{platform,i} - \kappa^{P\to O}_i)\big).
$$

Higher **leave-open cost** $\kappa^{O\to P}_i$ makes moving **to** the platform harder; higher **leave-platform cost** $\kappa^{P\to O}_i$ makes **defecting** back to open harder (**asymmetric** switching friction). Expected flows: $S^{open}_i$ loses mass $\mathbb{P}(O\!\to\!P)\,S^{open}_i$ and gains $\mathbb{P}(P\!\to\!O)\,S^{plat}_i$ (and the converse on the platform side). This is distinct from the global lock-in term $L(t)$ in $U_{platform}$, which is an **ecosystem** disutility from dominance timing.

---

#### 10. How to read the plots

- **Open / platform stocks:** cumulative $N_{open}, N_{platform}$ (must sum to adopters so far; TAM 1 when fully adopted).
- **Share among adopters:** $s_{plat}$ vs $1-s_{plat}$—this is the object used for **dominance**, **enshittification onset**, and the headline **~90/10** style splits.
- **$F, A, V, Q, L, E$:** show which **latent** forces are binding when the logit tilts toward one architecture.
- **Monthly flows:** **New → open / platform** are arrivals only; **Switch →** bars are existing users moving architecture after arrivals.

The **Commons institutional development speed** slider is **$k_F$** in $F(t)=F_{max}\,\sigma(k_F^{\mathrm{eff}}(t-t_F^\*))$ with $k_F^{\mathrm{eff}}=k_F(1+\varphi N_{open})$: higher $k_F$ or $\varphi$ speeds institutions along the logistic, raising $Q_{open}$ and strengthening the **open adoption $\to$ institutions $\to$ quality** feedback when $\varphi>0$.
        """
    )
