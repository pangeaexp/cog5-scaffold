import json
import click
from .core import CogSystem
from .logger import configure_logging
from .viz import render_network_3d, render_radar, render_report_html

@click.group()
def main():
    """cog5 CLI"""
    pass

@main.command()
@click.option("--nodes", default=36, help="Number of nodes")
@click.option("--out", default="cog_state.json", help="Output path for state")
def init(nodes, out):
    """Initialize system"""
    configure_logging()
    cs = CogSystem(n_nodes=nodes)
    cs.initialize()
    cs.save_state(out)
    click.echo(f"Initialized with {nodes} nodes -> {out}")

@main.command()
@click.option("--generations", default=1, help="Number of generations")
@click.option("--state", required=True, help="Input state file")
@click.option("--out", default="evolved_state.json", help="Output state file")
def evolve(generations, state, out):
    configure_logging()
    cs = CogSystem.load_state(state)
    history = cs.step_evolution(generations)
    cs.save_state(out)
    click.echo(f"Evolved for {generations} generations -> {out}")

@main.command()
@click.option("--state", required=True, help="State file to report on")
@click.option("--out", default="report.html", help="HTML output")
def report(state, out):
    configure_logging()
    with open(state, "r", encoding="utf-8") as f:
        s = json.load(f)
    render_report_html(s, out)
    click.echo(f"Report generated -> {out}")

if __name__ == "__main__":
    main()
