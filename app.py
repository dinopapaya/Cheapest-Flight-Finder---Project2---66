"""Streamlit front-end for the Cheapest Flight Finder project."""
from __future__ import annotations
from itertools import product
import time
from typing import Callable, Dict, List, Sequence, Tuple

import folium
import pandas as pd
import streamlit as st
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


def _find_best_route(
    graph: Graph,
    start_airports: Sequence[str],
    end_airports: Sequence[str],
    solver: AlgorithmSolver,
) -> Tuple[float, List[str], Tuple[str, str] | None]:

    best_cost = float("inf")
    best_path: List[str] = []
    best_pair: Tuple[str, str] | None = None

    for origin, destination in product(start_airports, end_airports):
        cost, path = solver(graph, origin, destination)
        if path and cost < best_cost:
            best_cost = cost
            best_path = path
            best_pair = (origin, destination)

    if not best_path:
        return float("inf"), [], None

    return best_cost, best_path, best_pair


def _execute_solver(
    graph: Graph,
    solver: AlgorithmSolver,
    origin_airports: Sequence[str],
    destination_airports: Sequence[str],
    auto_select: bool,
) -> Tuple[float, List[str], Tuple[str, str] | None, float]:

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
        rows.append(
            {
                "From": f"{segment.origin_city} ({segment.origin_airport})",
                "To": f"{segment.destination_city} ({segment.destination_airport})",
                "Fare": segment.fare,
                "Primary Carrier": segment.primary_carrier or "—",
                "Passengers": segment.passengers,
                "Distance (miles)": segment.miles,
            }
        )

    frame = pd.DataFrame(rows)

    if not frame.empty:
        frame["Fare"] = frame["Fare"].map(lambda value: f"${value:,.2f}")
        frame["Passengers"] = frame["Passengers"].map(lambda v: f"{v:,.0f}" if pd.notna(v) else "—")
        frame["Distance (miles)"] = frame["Distance (miles)"].map(
            lambda v: f"{v:,.0f}" if pd.notna(v) else "—"
        )

    return frame

def _build_route_map(path: Sequence[str]) -> folium.Map | None:
    directory = load_airport_directory()
    coordinates: List[Tuple[float, float]] = []

    for airport_code in path:
        record = directory.get(airport_code)
        if not record:
            continue
        coordinates.append((record["lat"], record["lon"], record.get("name"), record.get("city")))

    if len(coordinates) < 2:
        return None

    avg_lat = sum(lat for lat, *_ in coordinates) / len(coordinates)
    avg_lon = sum(lon for _, lon, *_ in coordinates) / len(coordinates)

    route_map = folium.Map(location=(avg_lat, avg_lon), zoom_start=4)
    folium.PolyLine([(lat, lon) for lat, lon, *_ in coordinates], color="blue", weight=4).add_to(route_map)

    for airport_code, (lat, lon, name, city) in zip(path, coordinates):
        tooltip = f"{airport_code} — {city or 'Unknown city'}"
        popup_lines = [name or "Unknown airport"]
        if city:
            popup_lines.append(city)
        folium.Marker((lat, lon), tooltip=tooltip, popup="\n".join(popup_lines)).add_to(route_map)

    return route_map


def main():
    st.set_page_config(page_title="Cheapest Flight Finder", page_icon="✈️", layout="wide")
    st.title("Cheapest Flight Finder")

    st.markdown(
        """
        Use this tool to explore the most affordable itineraries across the United States.
        The dataset aggregates average fares between airports, and you can compare
        different shortest-path algorithms to see how they perform on the same request.
        """
    )

    _dataframe, graph, metadata, city_lookup = load_graph_assets(DATASET_PATH)
    airports = sorted(graph.keys())
    cities = sorted(city_lookup.keys())

    with st.sidebar:
        st.header("Route options")

        mode = st.radio("How would you like to search?", ("Airport to airport", "City to city"))
        auto_select = False
        origin_city = ""
        destination_city = ""

        algorithm_labels = [entry["label"] for entry in ALGORITHMS.values()]
        label_to_key = {entry["label"]: key for key, entry in ALGORITHMS.items()}

        if mode == "Airport to airport":
            origin_airports = [
                st.selectbox(
                    "Origin airport",
                    airports,
                    index=airports.index("ABE") if "ABE" in airports else 0,
                )
            ]
            destination_airports = [
                st.selectbox(
                    "Destination airport",
                    airports,
                    index=airports.index("PIE") if "PIE" in airports else min(len(airports) - 1, 1),
                )
            ]
            origin_label_base = origin_airports[0]
            destination_label_base = destination_airports[0]

        else:
            origin_city = st.selectbox("Origin city", cities)
            destination_city = st.selectbox(
                "Destination city",
                cities,
                index=cities.index(origin_city) if origin_city in cities else 0,
            )

            origin_options = city_lookup.get(origin_city, [])
            destination_options = city_lookup.get(destination_city, [])

            if not origin_options or not destination_options:
                st.error("The selected cities do not have airports in the dataset.")
                st.stop()

            auto_select = st.checkbox(
                "Automatically choose the cheapest airport combination",
                value=True,
            )

            if auto_select:
                origin_airports = origin_options
                destination_airports = destination_options
            else:
                origin_airports = [
                    st.selectbox(
                        "Origin airport",
                        origin_options,
                        key="origin_airport_manual",
                    )
                ]
                destination_airports = [
                    st.selectbox(
                        "Destination airport",
                        destination_options,
                        key="destination_airport_manual",
                    )
                ]

            origin_label_base = origin_city
            destination_label_base = destination_city

        selected_label = st.selectbox("Primary algorithm", algorithm_labels, index=0)
        selected_algorithm_key = label_to_key[selected_label]


    if not auto_select:
        origin_code = origin_airports[0]
        destination_code = destination_airports[0]

        if origin_code == destination_code:
            st.info("Select two different airports to compute a route.")
            st.stop()


    algorithm_results = {}

    for key, entry in ALGORITHMS.items():
        cost, path, pair, runtime = _execute_solver(
            graph,
            entry["solver"],
            origin_airports,
            destination_airports,
            auto_select,
        )

        algorithm_results[key] = {
            "label": entry["label"],
            "cost": cost,
            "path": path,
            "pair": pair,
            "runtime": runtime,
        }

    selected_result = algorithm_results[selected_algorithm_key]

    if not selected_result["path"] or selected_result["pair"] is None:
        st.error("No route could be found with the selected parameters. Try different airports or cities.")
        st.stop()


    if mode == "City to city":
        origin_label = f"{origin_label_base} ({selected_result['pair'][0]})"
        destination_label = f"{destination_label_base} ({selected_result['pair'][1]})"
    else:
        origin_label = selected_result["pair"][0]
        destination_label = selected_result["pair"][1]


    st.subheader("Itinerary summary")

    st.write(
        f"Cheapest route from **{origin_label}** to **{destination_label}**: "
        f"{_format_money(selected_result['cost'])}"
        f" using {selected_result['label']}"
    )


    segments = summarise_path(selected_result["path"], metadata)
    summary_table = _build_route_table(segments)
    st.dataframe(summary_table, use_container_width=True)


    st.subheader("Algorithm comparison")

    comparison_columns = st.columns(len(ALGORITHMS))
    for column, (key, result) in zip(comparison_columns, algorithm_results.items()):
        with column:
            column.markdown(f"**{result['label']}**")

            if result["path"]:
                column.metric("Total fare", _format_money(result["cost"]))
                column.metric("Runtime", f"{result['runtime'] * 1000:.2f} ms")

                if result["pair"]:
                    column.caption(f"Route: {result['pair'][0]} → {result['pair'][1]}")
            else:
                column.write("No route found.")


    st.subheader("Interactive map")

    route_map = _build_route_map(selected_result["path"])

    if route_map is None:
        st.info("Unable to render the map because one or more airports were missing from the reference database.")
    else:
        st_folium(route_map, width=None, height=500)


if __name__ == "__main__":
    main()
