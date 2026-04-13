"""Long-form tooltip copy for Streamlit widgets (help=...).

Streamlit **help** tooltips support GitHub-Flavored Markdown and the same LaTeX rules as
``st.markdown``: inline ``$...$`` and display math with ``$$`` on its own line.
Use Python raw strings for constants so TeX backslashes are preserved.
"""

from __future__ import annotations

# --- Summary metrics (top of main page) ---

METRIC_OPEN_SHARE_CUMULATIVE = r"""
**Intuition:** Share of the **total addressable market (TAM)** that has **ever adopted** the open /
decentralised architecture by the **end of the 8-year** horizon. This is **not** “open share among
adopters only”—it counts everyone on the open side as a fraction of the whole market (including
people who have not adopted either architecture yet).

**Math**

Let $N_{\mathrm{open}}(t)$ be cumulative open adopters as a share of TAM at calendar time $t$ (years).
The metric is
$$
N_{\mathrm{open}}(T),\quad T=8.
$$
Each month, new entrants and switchers update per-type stocks; $N_{\mathrm{open}}$ is their sum over types.
"""

METRIC_PLATFORM_SHARE_AMONG_ADOPTERS = r"""
**Intuition:** Among people who have **already adopted** either open **or** platform, what fraction
ended up on the **platform** side at **$t=8$** years? If almost everyone who adopts chooses the
platform, this number is near **100%** even if many people never adopt at all.

**Math**

Let $N_{\mathrm{open}}$ and $N_{\mathrm{platform}}$ be cumulative adopter shares (of TAM) on each side at $t=8$.
Among adopters only,
$$
s_{\mathrm{plat}} = \frac{N_{\mathrm{platform}}}{N_{\mathrm{open}}+N_{\mathrm{platform}}},
$$
defined as $0$ if $N_{\mathrm{open}}+N_{\mathrm{platform}}=0$. This is the same $s_{\mathrm{plat}}$ that drives
enshittification and lock-in timing elsewhere in the model.
"""

METRIC_PEAK_ENSHITTIFICATION = r"""
**Intuition:** **Enshittification** $E(t)$ is the model’s “rent extraction / quality degradation”
intensity once the platform is **dominant among adopters**. It hurts platform signal quality and
platform-side utility. This KPI is the **maximum** of $E(t)$ over the whole run—the worst the
dynamics get, not the value at $t=8$ alone.

**Math**

With $s_{\mathrm{plat}} = N_{\mathrm{platform}}/(N_{\mathrm{open}}+N_{\mathrm{platform}})$ among adopters,
$\sigma(x)=1/(1+e^{-x})$, threshold $\theta=$ **enshit_threshold**, and ramp / brake as in the sidebar,
$$
E(t) = \mathrm{clip}\!\Bigl(
E_{\max}\,\sigma\!\bigl(k_E(s_{\mathrm{plat}}(t)-\theta)\bigr)\,\mathrm{ramp}(t)\,\mathrm{brake}(t),\,
0,\,E_{\max}\Bigr).
$$
The metric reports $\displaystyle \max_t E(t)$.
"""

# --- Key levers (also overwritten by non-Custom scenario presets: includes λ) ---

K_F = r"""
Speed at which commons-based institutions mature: data unions, FIDU-like stewards, and
ecosystem-level signal processors that are loyal to members rather than shareholders.
The model runs on an **8-year** clock while adoption moves month-by-month, so a low **k_F**
often means institutions never catch up in time. Higher values mean institutional capacity
catches up to adoption faster, improving commons signal quality for a given installed base.

**Math**

Effective logistic steepness depends on **φ** (advanced slider **φ — F speed scales with N_open**):
$$
k_F^{\mathrm{eff}} = k_F\bigl(1 + \varphi\,N_{\mathrm{open}}\bigr).
$$
$$
F(t) = F_{\max}\,\sigma\!\left(k_F^{\mathrm{eff}} (t - t_{F,\mathrm{inflect}})\right),
\quad \sigma(x)=\frac{1}{1+e^{-x}}.
$$
$N_{\mathrm{open}}$ is cumulative open adoption (TAM share) at the **start** of each month.

**F(t)** enters
$\;Q_{\mathrm{open}} = \mathrm{clip}\!\bigl(Q_{\mathrm{open,base}} + \mu\, F(t)\,\ln(1+N_{\mathrm{open}}),\,0,\,1\bigr)$.
If $\varphi=0$, **$k_F^{\mathrm{eff}}=k_F$** always (legacy exogenous schedule).
"""

Q_PLAT_BASE = r"""
Baseline quality of proprietary signal processing (trust, discovery, security) before the
installed-base sigmoid and before enshittification drag. Captures incumbents' head start from
existing products and data moats.

**Math**

Let $\;s_N = \sigma\!\bigl(k_{\mathrm{plat}}(N_{\mathrm{platform}} - \theta_{\mathrm{plat}})\bigr)$.
Then
$$
Q_{\mathrm{platform}} = \mathrm{clip}\!\bigl(Q_{\mathrm{plat,base}} + (Q_{\mathrm{plat,max}}-Q_{\mathrm{plat,base}})\,s_N - E\,\delta_E,\,0,\,1\bigr)
$$
where $\delta_E$ is **enshit_quality_drag**. **Q_plat_base** is the intercept when $s_N\approx 0$ and $E=0$.
"""

ENSHIT_THRESHOLD = r"""
Platform dominance (among people who have already adopted either architecture) at which
rent-extraction dynamics can turn on. Below this share, the enshittification **time ramp** is
zero; the sigmoid in **E** still depends on the same share $s_{\mathrm{plat}}$.

**Math — share among adopters**

$$
s_{\mathrm{plat}} = \frac{N_{\mathrm{platform}}}{N_{\mathrm{open}}+N_{\mathrm{platform}}}
$$
(use $0$ if there are no adopters).

Let $t^\star$ be the first time $\;s_{\mathrm{plat}} \geq \theta$, where $\theta$ is **enshit_threshold** (this slider).

**Time ramp** (with $T_{\mathrm{ramp}}=$ **enshit_ramp_years**). If $t\ge t^\star$ and $s_{\mathrm{plat}}\ge \theta$:

$$
\mathrm{ramp}(t)= \min\!\left(1,\frac{t-t^\star}{T_{\mathrm{ramp}}}\right).
$$

Otherwise $\mathrm{ramp}(t)=0$.

**Enshittification** (with $\sigma(x)=\frac{1}{1+e^{-x}}$):

$$
E = \mathrm{clip}\!\Bigl(E_{\max}\,\sigma\!\bigl(k_E(s_{\mathrm{plat}}-\theta)\bigr)\,\mathrm{ramp}(t)\,\mathrm{brake},\,0,\,E_{\max}\Bigr)
$$

$$
\mathrm{brake} = 1 - \tfrac{1}{2}\min\!\left(1,\frac{N_{\mathrm{open}}}{0.3}\right).
$$

$\mathrm{clip}(x,a,b)$ clamps $x$ to $[a,b]$. In notes, $\theta$ is often written **theta**.
"""

A_MAX = r"""
How much AI agents reduce the hassle of using decentralised protocols over time, distinct from
institutional maturity $F(t)$. Models the idea that the agentic web may be easier for users than
the human-open-web was.

**Math**

$$
A(t) = A_{\max}\bigl(1 - e^{-k_A t}\bigr),
$$
with $t$ in years. Each consumer type $i$ gets $\epsilon_i\,A(t)$ in $U_{\mathrm{open}}$ (not in $U_{\mathrm{platform}}$).
"""

PLATFORM_ENTRY_DELAY = r"""
Months before incumbent platforms are assumed to ship agentic products at scale. Until then,
every arriving adopter joins the open side, building $N_{\mathrm{open}}$ and letting $F(t)$ advance
without platform competition. Existing adopters do not switch to the platform until the same
threshold (no platform product to switch to).

**Math**

Monthly step index $k=0,1,\ldots\;$ If **k** < **platform_entry_delay_months** then
$P_{\mathrm{open},i}=1$ for all new arrivals $i$; switching flows are zero. Otherwise arrivals use the
usual logit; post-arrival switching uses asymmetric leave costs (see consumer-type help).
"""

SCENARIO_PRESET = r"""
Narrative bundles that overwrite the **Key lever** sliders: **k_F**, **Q_plat_base**,
**A_max**, **enshit_threshold**, and **λ** (logit inverse temperature). At very high **λ**, small
changes in the first four barely move cumulative open share — presets therefore set **λ** per story
so scenarios diverge in the headline charts. **Non-Custom** presets also reset **advanced** expander
sliders (platform delay, μ, enshittification, platform curve, etc.) to **model defaults**; **Decentralisation Scenario**
then replaces them with a sweep-tuned bundle aimed at **~60% cumulative open share**. **Custom** leaves all sliders unchanged.

**Preset values (same symbols as in the equations elsewhere)**

- **Pre-agent web (email-like):** $k_F=0.2$, $Q_{\mathrm{plat,base}}=0.8$, $A_{\max}=0.32$, $\theta=0.6$, $\lambda=12$
- **Platform Capture:** $k_F=0.2$, $Q_{\mathrm{plat,base}}=0.6$, $A_{\max}=0.3$, $\theta=0.5$, $\lambda=14$
- **Decentralisation Scenario:** $k_F=1.85$, $Q_{\mathrm{plat,base}}=0.52$, $A_{\max}=0.72$, $\theta=0.37$, $\lambda=1.9$ (plus advanced: long platform entry delay, high $\mu$ / $Q_{\mathrm{open,base}}$ / $F_{\max}$ / $\varphi$, stronger $E$ dynamics and platform quality drag, slower $k_{\mathrm{plat}}$ — see app after selecting the preset)
- **Federated Equilibrium:** $k_F=0.65$, $Q_{\mathrm{plat,base}}=0.44$, $A_{\max}=0.55$, $\theta=0.76$, $\lambda=0.95$ (~**30%** open TAM at 8y under default advanced sliders)
- **Late Reversal:** $k_F=0.4$, $Q_{\mathrm{plat,base}}=0.55$, $A_{\max}=0.65$, $\theta=0.68$, $\lambda=5$
"""

# --- Advanced: institutional & commons ---

MU = r"""
Scales how much institutional maturity $F(t)$ turns open adoption $N_{\mathrm{open}}$ into commons
signal quality: strength of data unions / stewards in converting scale into trust and coordination.

**Math**

$$
Q_{\mathrm{open}} = \mathrm{clip}\!\bigl(Q_{\mathrm{open,base}} + \mu\,F(t)\,\ln(1+N_{\mathrm{open}}),\,0,\,1\bigr).
$$
"""

Q_OPEN_BASE = r"""
Starting commons signal quality when adoption and institutions are still weak.

**Math**

Intercept in
$\;Q_{\mathrm{open}} = \mathrm{clip}\!\bigl(Q_{\mathrm{open,base}} + \mu F(t)\ln(1+N_{\mathrm{open}}),\,0,\,1\bigr)$.
"""

F_MAX = r"""
Ceiling on institutional maturity $F(t)$ as calendar time and effective steepness allow.

**Math**

$\;F(t) = F_{\max}\,\sigma(k_F^{\mathrm{eff}}(t-t_{F,\mathrm{inflect}}))$, with $F\in[0,F_{\max}]$ and
$k_F^{\mathrm{eff}} = k_F(1+\varphi N_{\mathrm{open}})$.
"""

T_F_INFLECTION = r"""
Calendar time (years) around which commons institutions are halfway to their ceiling in the
logistic sense (using $k_F^{\mathrm{eff}}$).

**Math**

$\;F(t) = F_{\max}\,\sigma(k_F^{\mathrm{eff}}(t-t_{F,\mathrm{inflect}}))$.
"""

K_F_OPEN_COUPLING = r"""
**Supply-side / institutional funding loop (φ).** In the real world, FIDU-like institutions need
**members, funding, and data to steward** to mature quickly—a **chicken-and-egg** with adoption.
This slider makes the **logistic schedule** for $F(t)$ **steeper when $N_{\mathrm{open}}$ is larger**:
more open users → faster institutional development → higher $Q_{\mathrm{open}}$ (together with the
existing $\ln(1+N_{\mathrm{open}})$ term). If open adoption **stalls early**, institutions stay on a
slow track unless calendar time alone saves them.

**Math**

$\;k_F^{\mathrm{eff}} = k_F\bigl(1 + \varphi\,N_{\mathrm{open}}\bigr)$ with $N_{\mathrm{open}}$ at month start.
**φ = 0** recovers the old model (pure calendar-time $F$). Larger **φ** strengthens the
**open adoption → F → quality → open adoption** feedback.
"""

# --- Platform quality curve ---

Q_PLAT_MAX = r"""
Asymptotic platform signal quality when the installed-base sigmoid saturates, before subtracting
enshittification drag.

**Math**

$$
Q_{\mathrm{platform}} = \mathrm{clip}\!\bigl(Q_{\mathrm{plat,base}} + (Q_{\mathrm{plat,max}}-Q_{\mathrm{plat,base}})\,\sigma(k_{\mathrm{plat}}(N_{\mathrm{platform}}-\theta_{\mathrm{plat}})) - E\,\delta_E,\,0,\,1\bigr).
$$
"""

K_PLAT = r"""
Steepness of how fast platform quality rises with cumulative platform adopters $N_{\mathrm{platform}}$.

**Math**

Same $\;\sigma(k_{\mathrm{plat}}(N_{\mathrm{platform}}-\theta_{\mathrm{plat}}))$ term inside $Q_{\mathrm{platform}}$ above.
"""

PLAT_THRESHOLD = r"""
Cumulative platform share-of-TAM level at which the platform-quality sigmoid is centered
(inflection in $N_{\mathrm{platform}}$). Note: $N_{\mathrm{platform}}$ is normalised to TAM.

**Math**

Argument of the sigmoid in $Q_{\mathrm{platform}}$ is $\;k_{\mathrm{plat}}(N_{\mathrm{platform}}-\theta_{\mathrm{plat}})$.
"""

ENSHIT_QUALITY_DRAG = r"""
Linear penalty to platform signal quality per unit of enshittification $E$.

**Math**

Subtract $\;E\cdot\delta_E$ inside $Q_{\mathrm{platform}}$ before clipping to $[0,1]$ (**enshit_quality_drag** $=\delta_E$).
Also $U_{\mathrm{platform},i}$ includes $-\delta_i E$ separately.
"""

# --- Lock-in & dominance ---

L_MAX = r"""
Maximum lock-in disutility for platform users once dominance has persisted.

**Math**

$$
L = L_{\max}\bigl(1 - e^{-k_L T_{\mathrm{platform}}}\bigr).
$$
$T_{\mathrm{platform}}$ is years since $s_{\mathrm{plat}}$ first exceeded **dominance_share_threshold**; it resets if dominance is lost.
$U_{\mathrm{platform},i}$ includes $-\gamma_i L$.
"""

K_L = r"""
Rate at which lock-in disutility approaches **L_max** once the platform is dominant.

**Math**

$\;L = L_{\max}\bigl(1 - e^{-k_L T_{\mathrm{platform}}}\bigr)$.
"""

DOMINANCE_SHARE_THRESHOLD = r"""
Installed-base share $\;s_{\mathrm{plat}} = N_{\mathrm{platform}}/(N_{\mathrm{open}}+N_{\mathrm{platform}})$
above which the lock-in clock runs and $T_{\mathrm{platform}}$ accumulates.

**Math**

If $s_{\mathrm{plat}} >$ this threshold, $T_{\mathrm{platform}} = t - t_{\mathrm{dom,start}}$ (else clock and $T$ reset).
Used only for $L$, not for $E$ (**E** uses **enshit_threshold**).
"""

# --- Enshittification dynamics ---

E_MAX = r"""
Scale of the rent-extraction / quality-degradation state when the sigmoid and time ramp are fully
on and the competitive brake is $1$.

**Math**

$\;E = \mathrm{clip}\bigl(E_{\max}\,\sigma(k_E(s_{\mathrm{plat}}-\theta))\,\mathrm{ramp}\,\mathrm{brake},\,0,\,E_{\max}\bigr)$
with **brake** and **ramp** as in the **enshit_threshold** tooltip.
"""

K_E = r"""
How sharply **E** responds as platform share $s_{\mathrm{plat}}$ crosses the enshittification threshold.

**Math**

$\;\sigma\!\bigl(k_E(s_{\mathrm{plat}}-\theta)\bigr)$ inside $E$ above.
"""

ENSHIT_RAMP_YEARS = r"""
Years after enshittification first becomes eligible ($s_{\mathrm{plat}}\ge\theta$ and clock started)
for the ramp factor to go from $0$ to $1$.

**Math**

If eligible, $\;\mathrm{ramp}(t)=\min\!\bigl(1,(t-t^\star)/T_{\mathrm{ramp}}\bigr)$ with $t^\star$ the first crossing time; else $0$.
"""

# --- Agents & values ---

K_A = r"""
Speed at which $A(t)$ approaches **A_max** as calendar time progresses.

**Math**

$\;A(t) = A_{\max}(1-e^{-k_A t})$ in $U_{\mathrm{open}}$ via $\epsilon_i A(t)$.
"""

V_BASE = r"""
Baseline utility from values alignment / steward loyalty, before the awareness sigmoid.

**Math**

$\;V(t) = V_{\mathrm{base}} + V_{\mathrm{aware}}\,\sigma(k_V(t-t_{V,\mathrm{inflect}}))$; enters $U_{\mathrm{open}}$ as $\zeta_i V(t)$.
"""

V_AWARENESS = r"""
Extra values premium as public understanding of steward loyalty grows.

**Math**

Added to $V(t)$ as $\;V_{\mathrm{aware}}\,\sigma(k_V(t-t_{V,\mathrm{inflect}}))$.
"""

K_V = r"""
Steepness of the awareness sigmoid in calendar time.

**Math**

Inside $\;V(t) = V_{\mathrm{base}} + V_{\mathrm{aware}}\,\sigma(k_V(t-t_{V,\mathrm{inflect}}))$.
"""

T_V_INFLECTION = r"""
Calendar midpoint (years) for the values-awareness logistic.

**Math**

Argument $\;(t-t_{V,\mathrm{inflect}})$ inside the sigmoid for $V(t)$.
"""

# --- Choice ---

CHOICE_LAMBDA = r"""
Inverse temperature of the logit: higher **lambda** makes small utility differences swing choice;
lower **lambda** adds noise / inertia.

**Math**

For $k \ge$ **platform_entry_delay_months**,
$$
P_{\mathrm{open},i}=\frac{1}{1+\exp\!\bigl(-\lambda\,(U_{\mathrm{open},i}-U_{\mathrm{platform},i})\bigr)}.
$$
$\;U_{\mathrm{open},i} = \alpha_i Q_{\mathrm{open}} + \beta_i N_{\mathrm{open}} + \epsilon_i A + \zeta_i V$;
$\;U_{\mathrm{platform},i} = \alpha_i Q_{\mathrm{platform}} + \beta_i N_{\mathrm{platform}} - \gamma_i L - \delta_i E$.
"""

# --- Consumer segments ---

CONSUMER_MIX_WEIGHT = r"""
Relative size of this consumer segment. The four mix weights you set are renormalised so they sum
to $1$ (population shares).

**Math**

Type $i$ gets population share $\omega_i$ after normalization;
$\mathrm{arrivals}_i(t)=\omega_i$ times the Bass arrival weights for this type.
"""

CONSUMER_BASS_P = r"""
Bass innovation coefficient: external / advertising-driven adoption. Higher **p** tends to pull adoption earlier.

**Math**

Used in Bass cumulative $f(t)$ and arrival weights for this type.
"""

CONSUMER_BASS_Q = r"""
Bass imitation coefficient: word-of-mouth / social contagion. Higher **q** makes the S-curve steeper.

**Math**

Used with **p** in the same Bass $f(t)$ for this type.
"""

CONSUMER_PEAK_YEAR = r"""
Target calendar year where this type's arrival rate should peak (via a time shift on its Bass curve).

**Math**

$S_i = \max\bigl(0,\; y - t_{\mathrm{peak,natural}}(p,q)\bigr)$ where $y$ is **peak_year** (this slider); used in **bass_arrival_weights**.
"""

CONSUMER_ALPHA = r"""
Weight on signal quality $Q$ in both $U_{\mathrm{open}}$ and $U_{\mathrm{platform}}$ for this type.

**Math**

$\;\alpha_i Q$ in each utility.
"""

CONSUMER_BETA = r"""
Weight on installed base (network effect): $N_{\mathrm{open}}$ in $U_{\mathrm{open}}$,
$N_{\mathrm{platform}}$ in $U_{\mathrm{platform}}$.

**Math**

$\;\beta_i N_{\mathrm{open}}$ or $\;\beta_i N_{\mathrm{platform}}$.
"""

CONSUMER_GAMMA = r"""
Weight on lock-in disutility $L$ in $U_{\mathrm{platform}}$ (aversion to being locked in).

**Math**

$\;-\gamma_i L$ in $U_{\mathrm{platform}}$ only.
"""

CONSUMER_DELTA = r"""
Weight on enshittification $E$ in $U_{\mathrm{platform}}$ (aversion to rent extraction).

**Math**

$\;-\delta_i E$ in $U_{\mathrm{platform}}$ only.
"""

CONSUMER_EPSILON = r"""
Weight on agent friction reduction $A(t)$ in $U_{\mathrm{open}}$.

**Math**

$\;\epsilon_i A(t)$ in $U_{\mathrm{open}}$ only.
"""

CONSUMER_ZETA = r"""
Weight on values / autonomy premium $V(t)$ in $U_{\mathrm{open}}$.

**Math**

$\;\zeta_i V(t)$ in $U_{\mathrm{open}}$ only.
"""

CONSUMER_LEAVE_OPEN = r"""
Extra utility hurdle (same units as $U_{\mathrm{open}},U_{\mathrm{platform}}$) for an existing open user of
this type to switch to the platform, after new arrivals are allocated each month. Higher values mean
users stay on open unless platform utility is clearly better.

**Math**

$\;P(\mathrm{open}\!\to\!\mathrm{platform}) = \sigma\!\bigl(\lambda\,(U_{\mathrm{platform}}-U_{\mathrm{open}}-c_i^{\mathrm{open}})\bigr)$,
$\;\sigma(x)=\frac{1}{1+e^{-x}}$. Distinct from global lock-in $L$ in $U_{\mathrm{platform}}$.
"""

CONSUMER_LEAVE_PLATFORM = r"""
Extra utility hurdle for an existing platform user of this type to switch back to open. Higher values
capture data lock-in, habit, or switching hassle on the platform side.

**Math**

$\;P(\mathrm{platform}\!\to\!\mathrm{open}) = \sigma\!\bigl(\lambda\,(U_{\mathrm{open}}-U_{\mathrm{platform}}-c_i^{\mathrm{plat}})\bigr)$.
"""
