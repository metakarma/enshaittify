# enshAIttification — Agentic Web Platformisation Simulation

A **Streamlit** web application that runs a parametrized logistic choice model of adoption dynamics for the **agentic web**. The model contrasts **open / commons-based** signal processing (institutions loyal to members, e.g. data unions / FIDU-like stewards) with **platformised**, proprietary signal processing.

## Quick start (local)

```bash
cd agentic-web-sim
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app/main.py --server.port=8501
```

Open http://localhost:8501

## Docker

```bash
cd agentic-web-sim
docker compose up --build
```

The app listens on **8501**. The compose file mounts `./app` into the container for development convenience.

## Project layout

- `app/main.py` — Streamlit UI
- `app/model.py` — Simulation loop (96 monthly steps over 8 years; calendar `t` in years)
- `app/dynamics.py` — State variables (Q, F, L, E, A, V, etc.)
- `app/consumer_types.py` — Consumer segments, utilities, shifted Bass arrivals
- `app/scenarios.py` — Named presets
- `app/visualisation.py` — Plotly figures
- `.streamlit/config.toml` — Theme and client defaults

## Model summary

- **Horizon:** **8 years** at **monthly** resolution (calendar time in equations is still years). The short horizon is intentional: agentic adoption moves fast; **commons institutions** move slowly—so **k_F** and early **N_open** matter under time pressure.
- **Four consumer types** (editable in the sidebar): mix weights, Bass **p/q**, peak timing, and utility **α–ζ** per segment; defaults match the original spec.
- **Key lever:** **k_F** — speed of commons institutional maturity **F(t)** in commons signal quality.
- **Feedback:** platform base quality, network effects, lock-in after dominance, enshittification past a share threshold (with a competitive brake when open adoption stays viable).

## Licence

Use and modify for research and commentary; no warranty.
