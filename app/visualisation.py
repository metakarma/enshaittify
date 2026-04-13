"""Plotly charts for the Streamlit app."""

from __future__ import annotations

from typing import List

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def _arriving_type_keys(df: pd.DataFrame) -> List[str]:
    return [
        c[len("arriving_") :]
        for c in df.columns
        if c.startswith("arriving_") and c != "arriving_total"
    ]


def _hex_to_rgba(hex_color: str, alpha: float) -> str:
    h = hex_color.strip().lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


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
    """Stacked monthly entrants: per type, bottom = → open (opaque), top = → platform (lighter fill).

    Plotly Scatter only accepts string ``fillcolor`` in many versions—no pattern dict—so platform
    slices use a translucent rgba of the same hue plus a dashed line for contrast.
    """
    keys = _arriving_type_keys(df)
    palette = [
        "#37474f",
        "#0277bd",
        "#558b2f",
        "#6a1b9a",
        "#c62828",
        "#ef6c00",
        "#00838f",
    ]
    fig = go.Figure()
    for i, key in enumerate(keys):
        col_o = f"new_open_{key}"
        col_p = f"new_platform_{key}"
        col_a = f"arriving_{key}"
        if col_o not in df.columns:
            continue
        lab = key.replace("_", " ").title()
        c = palette[i % len(palette)]
        if col_p in df.columns:
            y_open = df[col_o].astype(float)
            y_plat = df[col_p].astype(float)
        else:
            y_open = df[col_o].astype(float)
            if col_a in df.columns:
                y_plat = (df[col_a] - df[col_o]).astype(float)
            else:
                y_plat = pd.Series(0.0, index=df.index)
        # Solid fill: entrants choosing open
        fig.add_trace(
            go.Scatter(
                x=df["year"],
                y=y_open,
                mode="lines",
                name=f"{lab} → open",
                stackgroup="one",
                line=dict(width=0.5, color=c),
                fillcolor=c,
                opacity=0.9,
                hovertemplate=f"{lab} → open: %{{y:.4f}}<extra></extra>",
            )
        )
        # Platform slice: same hue, translucent fill + dashed upper edge (pattern not supported on Scatter fillcolor in Plotly 5.x)
        fig.add_trace(
            go.Scatter(
                x=df["year"],
                y=y_plat,
                mode="lines",
                name=f"{lab} → platform",
                stackgroup="one",
                line=dict(width=0.65, color=c, dash="dash"),
                fillcolor=_hex_to_rgba(c, 0.38),
                opacity=1.0,
                hovertemplate=f"{lab} → platform: %{{y:.4f}}<extra></extra>",
            )
        )
    fig.update_layout(
        title=dict(
            text="New entrants by type: open (opaque) vs platform (lighter fill, dashed edge), stacked",
            x=0.5,
            xref="paper",
            xanchor="center",
            y=0.97,
            yref="paper",
            yanchor="top",
        ),
        xaxis_title="Year",
        yaxis_title="Arrivals (share of TAM per month)",
        hovermode="x unified",
        template="plotly_white",
        legend=dict(
            orientation="v",
            x=0.99,
            y=0.99,
            xanchor="right",
            yanchor="top",
            bgcolor="rgba(255,255,255,0.82)",
            bordercolor="rgba(0,0,0,0.12)",
            borderwidth=1,
            font=dict(size=10),
        ),
        margin=dict(l=50, r=24, t=56, b=50),
    )
    fig.update_xaxes(**_axis_template())
    fig.update_yaxes(**_axis_template())
    return fig


def fig_sankey_open_to_platform(df: pd.DataFrame) -> go.Figure:
    """Cumulative mass that switched open → platform, by consumer type."""
    keys = _arriving_type_keys(df)
    pairs = [(k, float(df[f"switch_OtoP_{k}"].sum())) for k in keys if f"switch_OtoP_{k}" in df.columns]
    pairs = [(k, v) for k, v in pairs if v > 1e-15]
    if not pairs:
        fig = go.Figure()
        fig.add_annotation(
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            text="No open → platform switching over the horizon",
            showarrow=False,
            font=dict(size=14, color="#666"),
        )
        fig.update_layout(
            title="Cumulative switchers: open → platform (by type)",
            height=340,
            template="plotly_white",
            margin=dict(l=40, r=40, t=50, b=40),
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
        )
        return fig
    n_left = len(pairs)
    labels = [f"{k.replace('_', ' ').title()}<br>(on open)" for k, _ in pairs] + ["Platform<br>(all types)"]
    sources = list(range(n_left))
    targets = [n_left] * n_left
    values = [v for _, v in pairs]
    fig = go.Figure(
        data=[
            go.Sankey(
                arrangement="snap",
                node=dict(
                    pad=20,
                    thickness=18,
                    line=dict(color="#333", width=0.5),
                    label=labels,
                    color=[
                        *[f"rgba(46, 125, 50, {0.35 + 0.12 * i})" for i in range(n_left)],
                        "rgba(198, 40, 40, 0.45)",
                    ],
                ),
                link=dict(
                    source=sources,
                    target=targets,
                    value=values,
                    color=[f"rgba(100, 100, 100, 0.35)" for _ in values],
                ),
            )
        ]
    )
    fig.update_layout(
        title="Cumulative switchers: open → platform (by type)",
        height=400,
        font=dict(size=12),
        template="plotly_white",
        margin=dict(l=24, r=24, t=48, b=24),
    )
    return fig


def fig_sankey_platform_to_open(df: pd.DataFrame) -> go.Figure:
    """Cumulative mass that switched platform → open, by consumer type."""
    keys = _arriving_type_keys(df)
    pairs = [(k, float(df[f"switch_PtoO_{k}"].sum())) for k in keys if f"switch_PtoO_{k}" in df.columns]
    pairs = [(k, v) for k, v in pairs if v > 1e-15]
    if not pairs:
        fig = go.Figure()
        fig.add_annotation(
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            text="No platform → open switching over the horizon",
            showarrow=False,
            font=dict(size=14, color="#666"),
        )
        fig.update_layout(
            title="Cumulative switchers: platform → open (by type)",
            height=340,
            template="plotly_white",
            margin=dict(l=40, r=40, t=50, b=40),
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
        )
        return fig
    n_right = len(pairs)
    labels = ["Platform<br>(all types)"] + [
        f"{k.replace('_', ' ').title()}<br>(to open)" for k, _ in pairs
    ]
    sources = [0] * n_right
    targets = list(range(1, n_right + 1))
    values = [v for _, v in pairs]
    fig = go.Figure(
        data=[
            go.Sankey(
                arrangement="snap",
                node=dict(
                    pad=20,
                    thickness=18,
                    line=dict(color="#333", width=0.5),
                    label=labels,
                    color=["rgba(198, 40, 40, 0.45)"]
                    + [f"rgba(21, 101, 192, {0.35 + 0.1 * i})" for i in range(n_right)],
                ),
                link=dict(
                    source=sources,
                    target=targets,
                    value=values,
                    color=[f"rgba(100, 100, 100, 0.35)" for _ in values],
                ),
            )
        ]
    )
    fig.update_layout(
        title="Cumulative switchers: platform → open (by type)",
        height=400,
        font=dict(size=12),
        template="plotly_white",
        margin=dict(l=24, r=24, t=48, b=24),
    )
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
    if "switch_open_to_platform" in df.columns:
        fig.add_trace(
            go.Bar(
                x=df["year"],
                y=df["switch_open_to_platform"],
                name="Switch open → platform",
                marker_color="#81c784",
                opacity=0.75,
            )
        )
    if "switch_platform_to_open" in df.columns:
        fig.add_trace(
            go.Bar(
                x=df["year"],
                y=df["switch_platform_to_open"],
                name="Switch platform → open",
                marker_color="#ef9a9a",
                opacity=0.75,
            )
        )
    fig.update_layout(
        title="Monthly flows (arrivals then switching)",
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
