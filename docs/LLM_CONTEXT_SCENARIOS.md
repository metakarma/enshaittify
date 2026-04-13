# Enshait — narrative LLM context: scenario presets and the decentralisation story

Use this alongside **`docs/LLM_CONTEXT.md`** when chats should explain **why** the app offers these story bundles, not only the equations. Presets live in **`app/scenarios.py`**; each overwrites five **Key levers**: **`k_F`**, **`Q_plat_base`**, **`A_max`**, **`enshit_threshold`**, and **λ** (**choice_lambda**). **Non-Custom** presets also reset **advanced** expander sliders to **model defaults**; **Decentralisation Scenario** then applies a sweep-tuned bundle (platform delay, μ, enshittification, platform curve, etc.) aimed at **~60% cumulative open TAM** at 8y. **Custom** leaves all sliders unchanged. **Consumer-type** sliders are never reset by presets.

---

## The through-line: from email to agentic capture

The model’s default story preset is **“Pre-agent web (email-like)”**. It is meant to evoke something readers already know: **open protocols got there first** (SMTP, IMAP, the early web), then **integrated products** won most users on **convenience, polish, and default choices**—not because standards vanished, but because **most people rationally take the path of least friction**. A **minority** remains on **non-platform** routes (self-hosting, stubborn standards-first tooling). The app text describes that residue as on the order of **~10%** of adopters staying on open-leaning paths in the **8-year monthly** run under that calibration—an **illustrative** number, not an empirical forecast.

The **agentic** twist is the same structural temptation **sped up**: if proprietary **signal processing** (routing, memory, identity, payments) is **good enough fast enough**, and **commons institutions** (data unions, steward loyalty, enforceable member-first rules) mature **slowly**, the window where **decentralisation is competitive** can **close** before **F(t)** and **N_open** make the open side credibly attractive. **Agents** are double-edged in the model: **`A(t)`** lowers friction for **using open protocols**, but if platforms keep a **quality lead** (**`Q_plat_base`**, the installed-base sigmoid on **`N_platform`**), the net story can still be **platform-led**.

With **φ > 0**, **$F(t)$** is not on a fixed calendar schedule alone: **institutions mature faster when $N_{\mathrm{open}}$ is larger**, tightening the **open adoption ↔ institutional capacity** feedback (and making **early stall** on the open side harder to recover from without time or other levers). That supports narratives about **FIDU-like investment before narrow “rational” adoption** to escape a chicken-and-egg trap; **φ = 0** turns that coupling off for comparison.

So the presets are ordered arguments in that drama: **how fast institutions catch up** (**`k_F`**), **how strong the platform’s head start feels** (**`Q_plat_base`**), **how much agents help the open experience** (**`A_max`**), **how much dominance platforms need before rent extraction ramps** (**`enshit_threshold`**, among adopters—not TAM share), and **how sharply users lock onto the better-looking option** (**`choice_lambda`** — low λ means noisier, more exploratory adoption).

---

## Preset by preset (what the story claims)

**Pre-agent web (email-like)** — **`k_F=0.2`**, **`Q_plat_base=0.8`**, **`A_max=0.32`**, **`enshit_threshold=0.6`**, **`choice_lambda=12`**.  
The **baseline parable**: strong incumbent platform quality, **slow** institutional maturation, moderate agents, enshittification only after **substantial** platform share among adopters. Outcomes should feel like **“platforms own the default, open survives at the margins.”**

**Platform Capture** — **`k_F=0.2`**, **`Q_plat_base=0.6`**, **`A_max=0.3`**, **`enshit_threshold=0.5`**, **`choice_lambda=14`**.  
The **stark** reading of the same slow-institutions world: **lower** baseline platform quality than the email preset (slightly less “overwhelming” head start), but **weaker** agent relief for open and **earlier** enshittification (lower threshold). The narrative is **incumbency + timing + rent extraction** reinforcing each other—**decentralisation is possible in principle** but **loses on the clock**.

**Decentralisation Scenario** — **`k_F=1.85`**, **`Q_plat_base=0.52`**, **`A_max=0.72`**, **`enshit_threshold=0.37`**, **`choice_lambda=1.9`**, plus advanced settings (e.g. **~57-month** platform entry delay, **μ=1**, higher **$Q_{\mathrm{open,base}}$** and **$F_{\max}$**, **$\varphi=2.85$**, stronger **$E$** / quality drag, slower **$k_{\mathrm{plat}}$** / higher **plat_threshold**).  
Sweep-calibrated for **~60% decentralised cumulative share** at 8y: **strong commons / social signal**, **credible fear of platform enshittification** (earlier θ, more bite from **$E$** on **$Q_{\mathrm{platform}}$**), and **slow incumbent platformisation** (long open-only phase, moderated proprietary quality curve).

**Federated Equilibrium** — **`k_F=0.6`**, **`Q_plat_base=0.45`**, **`A_max=0.5`**, **`enshit_threshold=0.75`**, **`choice_lambda=7`**.  
A **middle world**: institutions move at a **credible** pace, platforms are **not** given the strongest intercept, agents help **moderately**, **enshittification is delayed** until platforms are **very** dominant among adopters, and choices are **somewhat** softer than the email preset. The name signals **coexistence** and **contestability**—not automatic decentralisation, but **rules and norms** that keep extraction **in check** until late.

**Late Reversal** — **`k_F=0.4`**, **`Q_plat_base=0.55`**, **`A_max=0.65`**, **`enshit_threshold=0.68`**, **`choice_lambda=5`**.  
**Path dependence**: institutions are **not** as fast as in the Decentralisation Scenario, but **agents are strong**, **enshittification is relatively late**, and **`choice_lambda` is moderate**. The story is **“bad early dynamics, possible belated correction”**—useful when the user wants to discuss **policy or technology shocks** that **lengthen** the window or **shift** **`A`** and **`F`** mid-horizon (the preset alone is a static bundle; the narrative invites that kind of follow-on).

**Custom** — does **not** overwrite levers; it’s the **“hold my sliders”** option for manual exploration.

---

## How an LLM should use this file

- Treat presets as **paired narratives and parameter vectors**, not guarantees about the real world.  
- When comparing **decentralisation-friendly** vs **capture** stories, anchor on **`k_F`** (baseline institutional speed), **`Q_plat_base`** (incumbent appeal), **`A_max`** (agents on open), **`enshit_threshold`** (when extraction politics “switch on”), and **`choice_lambda`** (how sharply the logit favours the higher-utility side); add **φ** when discussing **supply-side** loops and whether **$F$** tracks **$N_{\mathrm{open}}$**.  
- Remind users that **consumer-type mix** is outside preset bundles; **platform entry delay** and **φ** are reset to defaults for most presets and **explicitly tuned** for Decentralisation.

---

*For equations and KPI definitions, see **`LLM_CONTEXT.md`**.*
