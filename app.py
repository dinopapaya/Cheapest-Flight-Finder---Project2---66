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

def _build_route_table(segments) -> pd.DataFrame:
    rows = []
    for segment in segments:
        rows.append({
            "From": f"{segment.origin_city} ({segment.origin_airport})",
            "To": f"{segment.destination_city} ({segment.destination_airport})",
            "Fare": segment.fare,
            "Primary Carrier": segment.primary_carrier or "—",
            "Passengers": segment.passengers,
            "Distance (miles)": segment.miles,
        })
    frame = pd.DataFrame(rows)
    if not frame.empty:
        frame["Fare"] = frame["Fare"].map(lambda v: f"${v:,.2f}")
        frame["Passengers"] = frame["Passengers"].map(lambda v: f"{v:,.0f}" if pd.notna(v) else "—")
        frame["Distance (miles)"] = frame["Distance (miles)"].map(lambda v: f"{v:,.0f}" if pd.notna(v) else "—")
    return frame

def _build_route_map(path: Sequence[str]) -> folium.Map | None:
    directory = load_airport_directory()
    coordinates: List[Tuple[float, float]] = []
    for airport_code in path:
        record = directory.get(airport_code)
        if record:
            coordinates.append((record["lat"], record["lon"], record.get("name"), record.get("city")))
    if len(coordinates) < 2:
        return None
    avg_lat = sum(lat for lat, *_ in coordinates) / len(coordinates)
    avg_lon = sum(lon for _, lon, *_ in coordinates) / len(coordinates)
    route_map = folium.Map(location=(avg_lat, avg_lon), zoom_start=4)
    folium.PolyLine([(lat, lon) for lat, lon, *_ in coordinates], color="blue", weight=4).add_to(route_map)
    for code, (lat, lon, name, city) in zip(path, coordinates):
        tooltip = f"{code} — {city or 'Unknown city'}"
        popup = "\n".join(filter(None, [name, city]))
        folium.Marker((lat, lon), tooltip=tooltip, popup=popup).add_to(route_map)
    return route_map

def main():
    st.set_page_config(page_title="Cheapest Flight Finder", page_icon="✈️", layout="wide")
    st.title("Cheapest Flight Finder")
    st.markdown("Use this tool to explore the most affordable itineraries across the U.S.")

    _dataframe, graph, metadata, city_lookup = load_graph_assets(DATASET_PATH)
    airports = sorted(graph.keys())
    cities = sorted(city_lookup.keys())

    with st.sidebar:
        st.header("Route Options")
        mode = st.radio("Search by:", ("Airport to airport", "City to city"))
        auto_select = False
        origin_city = destination_city = ""
        algorithm_labels = [a["label"] for a in ALGORITHMS.values()]
        label_to_key = {a["label"]: k for k, a in ALGORITHMS.items()}

        if mode == "Airport to airport":
            origin_airports = [st.selectbox("Origin airport", airports)]
            destination_airports = [st.selectbox("Destination airport", airports)]
            origin_label_base, destination_label_base = origin_airports[0], destination_airports[0]
        else:
            origin_city = st.selectbox("Origin city", cities)
            destination_city = st.selectbox("Destination city", cities)
            origin_options = city_lookup.get(origin_city, [])
            destination_options = city_lookup.get(destination_city, [])
            if not origin_options or not destination_options:
                st.error("The selected cities do not have airports in the dataset.")
                st.stop()
            auto_select = st.checkbox("Automatically pick cheapest combination", value=True)
            if auto_select:
                origin_airports, destination_airports = origin_options, destination_options
            else:
                origin_airports = [st.selectbox("Origin airport", origin_options)]
                destination_airports = [st.selectbox("Destination airport", destination_options)]
            origin_label_base, destination_label_base = origin_city, destination_city

        selected_label = st.selectbox("Primary algorithm", algorithm_labels, index=0)
        selected_algorithm_key = label_to_key[selected_label]
