import streamlit as st
import json
from pathlib import Path
st.set_page_config(page_title="cog5 Scaffold — Evolution Explorer", layout="wide")
st.title("Evolution Explorer")
data_path = st.sidebar.text_input("Metrics JSON path", value="output/evolution_metrics.json")
if Path(data_path).exists():
    data = json.loads(Path(data_path).read_text(encoding="utf-8"))
    gen_options = [g["generation"] for g in data]
    sel = st.sidebar.select_slider("Generation", options=gen_options, value=gen_options[-1])
    gen = next(g for g in data if g["generation"] == sel)
    st.header(f"Generation {sel}")
    st.write("Metrics:", gen.get("metrics"))
    pop = gen.get("population", [])
    # simple table including pareto info
    st.dataframe([{
        "id": p["id"],
        "fitness": p.get("fitness"),
        "genotype": p.get("genotype"),
        "pareto_rank": p.get("pareto_rank"),
        "crowding_distance": p.get("crowding_distance"),
    } for p in pop])
else:
    st.warning("No metrics JSON found at path. Run evolution to generate output.")
