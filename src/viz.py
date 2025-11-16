import json
import math
import networkx as nx
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from typing import Dict, Any

def render_network_3d(network, out_path: str = None):
    # simple 3D layout using spring layout in 2D then z from node id
    G = network.graph
    pos2d = nx.spring_layout(G, dim=2, seed=42)
    xs = []
    ys = []
    zs = []
    edges_x = []
    edges_y = []
    edges_z = []
    for n, p in pos2d.items():
        xs.append(p[0])
        ys.append(p[1])
        zs.append(n * 0.02)
    for u, v in G.edges():
        edges_x += [pos2d[u][0], pos2d[v][0], None]
        edges_y += [pos2d[u][1], pos2d[v][1], None]
        edges_z += [u * 0.02, v * 0.02, None]

    edge_trace = go.Scatter3d(x=edges_x, y=edges_y, z=edges_z, mode='lines', line=dict(width=2, color='rgba(100,100,100,0.6)'), hoverinfo='none')
    node_trace = go.Scatter3d(x=xs, y=ys, z=zs, mode='markers+text', marker=dict(size=6, color='blue'), text=[str(n) for n in G.nodes()])

    fig = go.Figure(data=[edge_trace, node_trace])
    fig.update_layout(scene=dict(xaxis=dict(showbackground=False), yaxis=dict(showbackground=False), zaxis=dict(showbackground=False)))
    if out_path:
        fig.write_html(out_path)
    return fig

def render_radar(metrics_snapshot: Dict[str, Any], out_path: str = None):
    categories = ["coherence", "synchronization", "complexity", "entropy", "potential"]
    values = [metrics_snapshot.get(c, 0) for c in categories]
    # close the loop
    values += values[:1]
    categories += categories[:1]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=values, theta=categories, fill='toself'))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True)))
    if out_path:
        fig.write_html(out_path)
    return fig

def render_report_html(state: Dict[str, Any], out_path: str):
    metrics = state.get("metrics", {})
    snapshots = metrics.get("snapshots", [])
    latest = snapshots[-1] if snapshots else {}
    # create simple HTML
    html = f"<html><head><title>Cog5 Report</title></head><body><h1>Cog5 Report</h1><pre>{json.dumps(latest, indent=2)}</pre></body></html>"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    return out_path