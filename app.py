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

def _format_money(value: float) -> str:
    return f"${value:,.2f}"

def _find_best_route(graph: Graph, start_airports: Sequence[str],
                     end_airports: Sequence[str], solver: AlgorithmSolver):
    best_cost = float("inf")
    best_path: List[str] = []
    best_pair = None
    for origin, destination in product(start_airports, end_airports):
        cost, path = solver(graph, origin, destination)
        if path and cost < best_cost:
            best_cost, best_path, best_pair = cost, path, (origin, destination)
    if not best_path:
        return float("inf"), [], None
    return best_cost, best_path, best_pair

def _execute_solver(graph: Graph, solver: AlgorithmSolver,
                    origin_airports: Sequence[str],
                    destination_airports: Sequence[str],
                    auto_select: bool):
    start_time = time.perf_counter()
    if auto_select:
        cost, path, pair = _find_best_route(graph, origin_airports, destination_airports, solver)
    else:
        origin = origin_airports[0]
        destination = destination_airports[0]
        cost, path = solver(graph, origin, destination)
        pair = (origin, destination) if path else None
    runtime = time.perf_counter() - start_time
    return cost, path, pair, runtime
