"""Long-form tooltip copy for Streamlit widgets (help=...). Plain text; σ denotes sigmoid σ(x)=1/(1+e^{-x})."""

from __future__ import annotations

# --- Key levers (also overwritten by non-Custom scenario presets) ---

K_F = (
    "Speed at which commons-based institutions mature: data unions, FIDU-like stewards, and "
    "ecosystem-level signal processors that are loyal to members rather than shareholders. "
    "The model runs on an 8-year clock while adoption moves month-by-month—so a low k_F "
    "often means institutions never catch up in time. "
    "Higher values mean institutional capacity catches up to adoption faster, improving commons "
    "signal quality for a given installed base.\n\n"
    "Math: F(t) = F_max · σ(k_F · (t − t_F_inflection)). Here F(t) enters "
    "Q_open = clip(Q_open_base + μ · F(t) · ln(1 + N_open), 0, 1). "
    "So k_F scales how quickly F(t) approaches F_max in calendar time t (years), before any log "
    "network term."
)

Q_PLAT_BASE = (
    "Baseline quality of proprietary signal processing (trust, discovery, security) before the "
    "installed-base sigmoid and before enshittification drag. Captures incumbents’ head start from "
    "existing products and data moats.\n\n"
    "Math: Let s_N = σ(k_plat · (N_platform − plat_threshold)). Then "
    "Q_platform = clip(Q_plat_base + (Q_plat_max − Q_plat_base) · s_N − E · enshit_quality_drag, 0, 1). "
    "Q_plat_base is the intercept when s_N → 0 (and E = 0)."
)

ENSHIT_THRESHOLD = (
    "Platform dominance (among people who have already adopted either architecture) at which "
    "rent-extraction dynamics can turn on. Below this share, the enshittification time ramp is "
    "zero; the sigmoid in E still depends on the same share s_plat.\n\n"
    "Math: s_plat = N_platform / (N_open + N_platform) (0 if no adopters). "
    "Let t* be the first time s_plat ≥ enshit_threshold. For t ≥ t* and s_plat ≥ enshit_threshold, "
    "time_ramp = min(1, (t − t*) / enshit_ramp_years); else time_ramp = 0. "
    "E = clip(E_max · σ(k_E · (s_plat − enshit_threshold)) · time_ramp · brake, 0, E_max) with "
    "brake = 1 − 0.5 · min(1, N_open / 0.3). "
    "This θ is enshit_threshold."
)

A_MAX = (
    "How much AI agents reduce the hassle of using decentralised protocols over time—distinct "
    "from institutional maturity F(t). Models the idea that the agentic web may be easier for "
    "users than the human-open-web was.\n\n"
    "Math: A(t) = A_max · (1 − exp(−k_A · t)) with t in years. "
    "Each consumer type i gets utility term ε_i · A(t) in U_open (not in U_platform)."
)

PLATFORM_ENTRY_DELAY = (
    "Months before incumbent platforms are assumed to ship agentic products at scale. Until "
    "then, every arriving adopter joins the open side, building N_open and letting F(t) advance "
    "without platform competition. On a compressed 8-year horizon, this window is precious for "
    "commons institutions to mature.\n\n"
    "Math: monthly step index k = 0,1,…. If k < platform_entry_delay_months then "
    "P_open_i = 1 for all types i; otherwise "
    "P_open_i = 1 / (1 + exp(−λ · (U_open_i − U_platform_i))) (logistic in utility difference)."
)

# --- Scenario preset selectbox ---

SCENARIO_PRESET = (
    "Narrative bundles that overwrite the four Key Lever sliders: k_F, Q_plat_base, A_max, "
    "and enshit_threshold. All other parameters (delays, advanced sliders, μ, E_max, etc.) stay "
    "at their current values unless you change them. Custom leaves Key Levers unchanged.\n\n"
    "Math (what each preset sets): "
    "Platform Capture → k_F=0.2, Q_plat_base=0.6, A_max=0.3, enshit_threshold=0.5. "
    "Protocol Window → k_F=1.2, Q_plat_base=0.5, A_max=0.7, enshit_threshold=0.6. "
    "Federated Equilibrium → k_F=0.6, Q_plat_base=0.45, A_max=0.5, enshit_threshold=0.75. "
    "Late Reversal → k_F=0.4, Q_plat_base=0.55, A_max=0.65, enshit_threshold=0.68. "
    "Those symbols enter the equations exactly as in the Key Lever tooltips (F, Q_platform, A(t), E)."
)

# --- Advanced: institutional & commons ---

MU = (
    "Scales how much institutional maturity F(t) turns open adoption N_open into commons signal "
    "quality—strength of data unions / stewards in converting scale into trust and coordination.\n\n"
    "Math: Q_open = clip(Q_open_base + μ · F(t) · ln(1 + N_open), 0, 1)."
)

Q_OPEN_BASE = (
    "Starting commons signal quality when adoption and institutions are still weak.\n\n"
    "Math: intercept in Q_open = clip(Q_open_base + μ · F(t) · ln(1 + N_open), 0, 1)."
)

F_MAX = (
    "Ceiling on institutional maturity F(t) as calendar time and k_F allow.\n\n"
    "Math: F(t) = F_max · σ(k_F · (t − t_F_inflection)), with F ∈ [0, F_max]."
)

T_F_INFLECTION = (
    "Calendar time (years) around which commons institutions are halfway to their ceiling in the "
    "logistic sense.\n\n"
    "Math: F(t) = F_max · σ(k_F · (t − t_F_inflection))."
)

# --- Platform quality curve ---

Q_PLAT_MAX = (
    "Asymptotic platform signal quality when the installed-base sigmoid saturates, before "
    "subtracting enshittification drag.\n\n"
    "Math: Q_platform = clip(Q_plat_base + (Q_plat_max − Q_plat_base) · "
    "σ(k_plat · (N_platform − plat_threshold)) − E · enshit_quality_drag, 0, 1)."
)

K_PLAT = (
    "Steepness of how fast platform quality rises with cumulative platform adopters N_platform.\n\n"
    "Math: same σ(k_plat · (N_platform − plat_threshold)) term inside Q_platform above."
)

PLAT_THRESHOLD = (
    "Cumulative platform share-of-TAM level at which the platform quality sigmoid is centered "
    "(inflection in N_platform). Note: N_platform is normalised to total addressable market.\n\n"
    "Math: argument of σ in Q_platform is k_plat · (N_platform − plat_threshold)."
)

ENSHIT_QUALITY_DRAG = (
    "Linear penalty to platform signal quality per unit of enshittification E.\n\n"
    "Math: subtract E · enshit_quality_drag inside Q_platform before clipping to [0,1]. "
    "Also U_platform_i includes −δ_i · E separately."
)

# --- Lock-in & dominance ---

L_MAX = (
    "Maximum lock-in disutility for platform users once dominance has persisted.\n\n"
    "Math: L = L_max · (1 − exp(−k_L · T_platform)). "
    "T_platform is years since s_plat first exceeded dominance_share_threshold; resets if dominance "
    "is lost. U_platform_i includes −γ_i · L."
)

K_L = (
    "Rate at which lock-in disutility approaches L_max once the platform is dominant.\n\n"
    "Math: L = L_max · (1 − exp(−k_L · T_platform))."
)

DOMINANCE_SHARE_THRESHOLD = (
    "Installed-base share s_plat = N_platform/(N_open+N_platform) above which the lock-in clock "
    "runs and T_platform accumulates.\n\n"
    "Math: if s_plat > this threshold, T_platform = t − t_dom_start (else clock and T reset). "
    "Used only for L, not for E (E uses enshit_threshold)."
)

# --- Enshittification dynamics ---

E_MAX = (
    "Scale of the rent-extraction / quality-degradation state when the sigmoid and time ramp are "
    "fully on and the competitive brake is 1.\n\n"
    "Math: E = clip(E_max · σ(k_E · (s_plat − enshit_threshold)) · time_ramp · brake, 0, E_max). "
    "brake = 1 − 0.5·min(1, N_open/0.3); time_ramp from enshit_ramp_years tooltip."
)

K_E = (
    "How sharply E responds as platform share s_plat crosses the enshittification threshold.\n\n"
    "Math: σ(k_E · (s_plat − enshit_threshold)) in E above."
)

ENSHIT_RAMP_YEARS = (
    "Years after enshittification first becomes eligible (s_plat ≥ enshit_threshold and clock "
    "started) for the time_ramp factor to go from 0 to 1.\n\n"
    "Math: if eligible, time_ramp = min(1, (t − t*) / enshit_ramp_years) where t* is first crossing "
    "time; else 0."
)

# --- Agents & values ---

K_A = (
    "Speed at which A(t) approaches A_max as calendar time progresses.\n\n"
    "Math: A(t) = A_max · (1 − exp(−k_A · t)) in U_open via ε_i · A(t)."
)

V_BASE = (
    "Baseline utility from values alignment / steward loyalty, before the awareness sigmoid.\n\n"
    "Math: V(t) = V_base + V_awareness · σ(k_V · (t − t_V_inflection)); enters U_open as zeta_i · V(t)."
)

V_AWARENESS = (
    "Extra values premium as public understanding of steward loyalty grows.\n\n"
    "Math: added to V(t) as V_awareness · σ(k_V · (t − t_V_inflection))."
)

K_V = (
    "Steepness of the awareness sigmoid in calendar time.\n\n"
    "Math: inside V(t) = V_base + V_awareness · σ(k_V · (t − t_V_inflection))."
)

T_V_INFLECTION = (
    "Calendar midpoint (years) for the values-awareness logistic.\n\n"
    "Math: argument (t − t_V_inflection) inside σ for V(t)."
)

# --- Choice ---

CHOICE_LAMBDA = (
    "Inverse temperature of the logit: higher λ makes small utility differences swing choice; "
    "lower λ adds noise / inertia.\n\n"
    "Math: for k ≥ platform_entry_delay_months, "
    "P_open_i = 1 / (1 + exp(−λ · (U_open_i − U_platform_i))). "
    "U_open_i = α_i Q_open + β_i N_open + ε_i A + zeta_i · V; "
    "U_platform_i = α_i Q_platform + β_i N_platform − γ_i L − δ_i E."
)

# --- Consumer segments ---

CONSUMER_MIX_WEIGHT = (
    "Relative size of this consumer segment. The four mix weights you set are **renormalized** "
    "so they sum to 1 (population shares).\n\n"
    "Math: type i gets population_share_i after normalization; arrivals_i(t) = population_share_i · "
    "bass_pdf weights over the horizon."
)

CONSUMER_BASS_P = (
    "Bass **innovation** coefficient: external / advertising-driven adoption. Higher p tends to "
    "pull adoption earlier.\n\n"
    "Math: used in Bass cumulative f(t) and arrival weights for this type."
)

CONSUMER_BASS_Q = (
    "Bass **imitation** coefficient: word-of-mouth / social contagion. Higher q makes the S-curve steeper.\n\n"
    "Math: used with p in the same Bass f(t) for this type."
)

CONSUMER_PEAK_YEAR = (
    "Target calendar year where this type’s **arrival rate** should peak (via a time shift on its Bass curve).\n\n"
    "Math: shift_i = max(0, peak_year − t_peak_natural(p,q)) in bass_arrival_weights."
)

CONSUMER_ALPHA = (
    "Weight on **signal quality** Q in both U_open and U_platform for this type.\n\n"
    "Math: α_i · Q in each utility."
)

CONSUMER_BETA = (
    "Weight on **installed base** (network effect): N_open in U_open, N_platform in U_platform.\n\n"
    "Math: β_i · N_open or β_i · N_platform."
)

CONSUMER_GAMMA = (
    "Weight on **lock-in disutility** L in U_platform (aversion to being locked in).\n\n"
    "Math: −γ_i · L in U_platform only."
)

CONSUMER_DELTA = (
    "Weight on **enshittification** E in U_platform (aversion to rent extraction).\n\n"
    "Math: −δ_i · E in U_platform only."
)

CONSUMER_EPSILON = (
    "Weight on **agent friction reduction** A(t) in U_open.\n\n"
    "Math: ε_i · A(t) in U_open only."
)

CONSUMER_ZETA = (
    "Weight on **values / autonomy premium** V(t) in U_open.\n\n"
    "Math: zeta_i · V(t) in U_open only."
)
