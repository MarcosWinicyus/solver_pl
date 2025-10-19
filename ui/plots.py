from typing import List

import numpy as np
import plotly.graph_objects as go


def feasible_region_2d(c: List[float], A: List[List[float]], b: List[float]):
    if len(c) != 2:
        return None
    x = np.linspace(0, 10, 400)
    y = np.linspace(0, 10, 400)
    X, Y = np.meshgrid(x, y)
    feas = np.ones_like(X, bool)
    for a, rhs in zip(A, b):
        feas &= a[0] * X + a[1] * Y <= rhs + 1e-9
    fig = go.Figure(
        go.Contour(
            x=x,
            y=y,
            z=feas.astype(int),
            colorscale=[[0, "rgba(0,0,0,0)"], [1, "rgba(0,100,255,0.15)"]],
            showscale=False,
            contours=dict(start=0.5, end=1, size=0.5),
        )
    )
    colors = ["red", "green", "orange", "purple"]
    for idx, (a, rhs) in enumerate(zip(A, b)):
        if abs(a[1]) < 1e-9:
            continue
        x_line = np.linspace(0, 10, 100)
        fig.add_trace(
            go.Scatter(
                x=x_line,
                y=(rhs - a[0] * x_line) / a[1],
                mode="lines",
                line=dict(color=colors[idx % len(colors)]),
                name=f"{a[0]:.1f}x₁ + {a[1]:.1f}x₂ = {rhs}",
            )
        )
    # CORREÇÃO: Removidos width e height para permitir que o Streamlit controle o tamanho.
    fig.update_layout(xaxis_title="x₁", yaxis_title="x₂")
    return fig
