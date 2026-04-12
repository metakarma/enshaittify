"""Plotly charts for the Streamlit app."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def _axis_template():
    return dict(
        gridcolor="rgba(0,0,0,0.08)",
        linecolor="rgba(0,0,0,0.2)",
        title_font=dict(size=13),
        tickfont=dict(size=11),
    )


def fig_adoption_shares(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["year"],
            y=df["N_open"],
            mode="lines",
            name="Open / decentralised (cumulative)",
            line=dict(color="#2e7d32", width=2.5),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["year"],
            y=df["N_platform"],
            mode="lines",
            name="Platformised (cumulative)",
            line=dict(color="#c62828", width=2.5),
        )
    )
    fig.update_layout(
        title="Cumulative adoption (share of addressable market)",
        xaxis_title="Year",
        yaxis_title="Cumulative share",
        yaxis=dict(range=[0, 1.05], tickformat=".0%"),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template="plotly_white",
        margin=dict(l=50, r=30, t=60, b=50),
    )
    fig.update_xaxes(**_axis_template())
    fig.update_yaxes(**_axis_template())
    return fig


def fig_share_of_adopters(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["year"],
            y=df["open_share"],
            mode="lines",
            name="Open share of adopters",
            line=dict(color="#1565c0", width=2),
            stackgroup=None,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["year"],
            y=df["platform_share"],
            mode="lines",
            name="Platform share of adopters",
            line=dict(color="#6a1b9a", width=2, dash="dot"),
        )
    )
    fig.update_layout(
        title="Composition of installed base (among those who have adopted)",
        xaxis_title="Year",
        yaxis_title="Share",
        yaxis=dict(range=[0, 1.05], tickformat=".0%"),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template="plotly_white",
        margin=dict(l=50, r=30, t=60, b=50),
    )
    fig.update_xaxes(**_axis_template())
    fig.update_yaxes(**_axis_template())
    return fig


def fig_signal_quality(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["year"],
            y=df["Q_platform"],
            name="Platform signal quality",
            line=dict(color="#c62828", width=2),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["year"],
            y=df["Q_open"],
            name="Commons signal quality (FIDU variable)",
            line=dict(color="#2e7d32", width=2),
        )
    )
    fig.update_layout(
        title="Signal quality dynamics",
        xaxis_title="Year",
        yaxis_title="Quality (0–1)",
        yaxis=dict(range=[0, 1.05]),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template="plotly_white",
        margin=dict(l=50, r=30, t=60, b=50),
    )
    fig.update_xaxes(**_axis_template())
    fig.update_yaxes(**_axis_template())
    return fig


def fig_institutions_and_friction(df: pd.DataFrame) -> go.Figure:
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.12,
        subplot_titles=(
            "Institutional maturity F(t) and values premium V(t)",
            "Lock-in L(t), enshittification E(t), agent friction A(t)",
        ),
    )
    fig.add_trace(
        go.Scatter(x=df["year"], y=df["F"], name="F (institutions)", line=dict(color="#00695c")),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(x=df["year"], y=df["V"], name="V (values)", line=dict(color="#ef6c00")),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(x=df["year"], y=df["L"], name="L (lock-in)", line=dict(color="#5d4037")),
        row=2,
        col=1,
    )
    fig.add_trace(
        go.Scatter(x=df["year"], y=df["E"], name="E (enshittification)", line=dict(color="#ad1457")),
        row=2,
        col=1,
    )
    fig.add_trace(
        go.Scatter(x=df["year"], y=df["A"], name="A (agent friction↓)", line=dict(color="#283593")),
        row=2,
        col=1,
    )
    fig.update_yaxes(range=[0, 1.05], row=1, col=1)
    fig.update_yaxes(range=[0, max(0.65, float(df[["L", "E", "A"]].max().max()) * 1.1)], row=2, col=1)
    fig.update_xaxes(title_text="Year", row=2, col=1)
    fig.update_layout(
        height=640,
        template="plotly_white",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1),
        margin=dict(l=50, r=30, t=80, b=50),
    )
    return fig


def fig_arrivals(df: pd.DataFrame) -> go.Figure:
    keys = [
        c[len("arriving_") :]
        for c in df.columns
        if c.startswith("arriving_") and c != "arriving_total"
    ]
    palette = [
        "#37474f",
        "#0277bd",
        "#558b2f",
        "#6a1b9a",
        "#c62828",
        "#ef6c00",
        "#6a1b9a",
        "#00838f",
    ]
    fig = go.Figure()
    for i, key in enumerate(keys):
        col = f"arriving_{key}"
        if col in df.columns:
            lab = key.replace("_", " ").title()
            c = palette[i % len(palette)]
            fig.add_trace(
                go.Scatter(
                    x=df["year"],
                    y=df[col],
                    mode="lines",
                    name=lab,
                    stackgroup="one",
                    line=dict(width=0.35, color=c),
                    fillcolor=c,
                    opacity=0.82,
                )
            )
    fig.update_layout(
        title="New market entrants by consumer type (Bass diffusion, stacked)",
        xaxis_title="Year",
        yaxis_title="Arrivals (share of TAM per month)",
        hovermode="x unified",
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=50, r=30, t=60, b=50),
    )
    fig.update_xaxes(**_axis_template())
    fig.update_yaxes(**_axis_template())
    return fig


def fig_flows(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Bar(x=df["year"], y=df["new_open"], name="New → open", marker_color="#2e7d32", opacity=0.85)
    )
    fig.add_trace(
        go.Bar(
            x=df["year"],
            y=df["new_platform"],
            name="New → platform",
            marker_color="#c62828",
            opacity=0.85,
        )
    )
    fig.update_layout(
        title="Monthly adoption flows",
        xaxis_title="Year",
        yaxis_title="Share of TAM",
        barmode="group",
        template="plotly_white",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=50, r=30, t=60, b=50),
    )
    fig.update_xaxes(**_axis_template())
    fig.update_yaxes(**_axis_template())
    return fig


def summary_metrics(df: pd.DataFrame) -> dict:
    last = df.iloc[-1]
    return {
        "final_open": float(last["N_open"]),
        "final_platform": float(last["N_platform"]),
        "final_platform_share_among_adopters": float(last["platform_share"]),
        "mid_horizon_open": float(df.loc[df["year"] <= 4.001, "N_open"].iloc[-1])
        if (df["year"] <= 4).any()
        else float("nan"),
        "peak_E": float(df["E"].max()),
        "peak_Q_open": float(df["Q_open"].max()),
    }
