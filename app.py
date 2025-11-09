"""Streamlit front-end for the Cheapest Flight Finder project."""
import streamlit as st

def main():
    st.set_page_config(page_title="Cheapest Flight Finder", page_icon="✈️")
    st.title("Cheapest Flight Finder")
    st.write("Welcome! This app will help you find the cheapest flights between U.S. airports.")

if __name__ == "__main__":
    main()

from __future__ import annotations
from itertools import product
import time
from typing import Callable, Dict, List, Sequence, Tuple

import folium
import pandas as pd
from airportsdata import load as load_airports
from streamlit_folium import st_folium
from flight_graph import (
    Graph,
    bellman_ford,
    build_city_airport_lookup,
    build_graph,
    dijkstra,
    load_route_dataframe,
    summarise_path,
)

DATASET_PATH = "Aviation.csv"

AlgorithmSolver = Callable[[Graph, str, str], Tuple[float, List[str]]]

ALGORITHMS: Dict[str, Dict[str, object]] = {
    "dijkstra": {"label": "Dijkstra's algorithm", "solver": dijkstra},
    "bellman-ford": {"label": "Bellman–Ford", "solver": bellman_ford},
}

@st.cache_data(show_spinner=False)
def load_dataset(path: str = DATASET_PATH) -> pd.DataFrame:
    return load_route_dataframe(path)

@st.cache_data(show_spinner=False)
def load_graph_assets(path: str = DATASET_PATH):
    dataframe = load_dataset(path)
    graph, metadata = build_graph(dataframe)
    city_lookup = build_city_airport_lookup(dataframe)
    graph = {node: dict(edges) for node, edges in graph.items()}
    return dataframe, graph, metadata, city_lookup

@st.cache_resource(show_spinner=False)
def load_airport_directory():
    return load_airports("IATA")
