"""Command line helpers for the Cheapest Flight Finder project."""
from __future__ import annotations

import argparse
import time
from typing import Iterable

from flight_graph import (
    bellman_ford,
    build_graph,
    dijkstra,
    load_route_dataframe,
    summarise_path,
)

ALGORITHMS = {
    "dijkstra": ("Dijkstra's algorithm", dijkstra),
    "bellman-ford": ("Bellman–Ford", bellman_ford),
}

def format_segment(segment) -> str:
    carrier = f" via {segment.primary_carrier}" if segment.primary_carrier else ""
    distance = f" ({segment.miles:.0f} miles)" if segment.miles is not None else ""
    return (
        f"{segment.origin_airport} → {segment.destination_airport}: ${segment.fare:,.2f}"
        f"{carrier}{distance}"
    )

def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Find the cheapest flight between two airports.")
    parser.add_argument("origin", help="IATA code of the origin airport (e.g. ABE)")
    parser.add_argument("destination", help="IATA code of the destination airport (e.g. PIE)")
    parser.add_argument(
        "--dataset",
        default="Aviation.csv",
        help="Path to the Kaggle aviation dataset (defaults to Aviation.csv in the repo).",
    )
    parser.add_argument(
        "--algorithm",
        choices=tuple(ALGORITHMS.keys()),
        default="dijkstra",
        help="Select the primary shortest-path algorithm to use.",
    )
    return parser.parse_args(argv)

def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    
    dataframe = load_route_dataframe(args.dataset)
    graph, metadata = build_graph(dataframe)

    origin = args.origin.upper()
    destination = args.destination.upper()
    
    comparison = {}
    for key, (label, solver) in ALGORITHMS.items():
        start_time = time.perf_counter()
        cost, path = solver(graph, origin, destination)
        runtime = time.perf_counter() - start_time
        comparison[key] = {"label": label, "cost": cost, "path": path, "runtime": runtime}

    chosen = comparison[args.algorithm]

    if not chosen["path"]:
        print("No route was found between the selected airports.")
        return 1

    segments = summarise_path(chosen["path"], metadata)

    print(f"Cheapest itinerary from {origin} to {destination} using {ALGORITHMS[args.algorithm][0]}:")
    for segment in segments:
        print("  •", format_segment(segment))
    print(f"Total fare: ${chosen['cost']:,.2f}")

    print("\nAlgorithm comparison:")
    for key, result in comparison.items():
        cost_display = f"${result['cost']:,.2f}" if result["path"] else "No route"
        runtime_ms = result["runtime"] * 1000
        marker = "→" if key == args.algorithm else " "
        print(
            f" {marker} {result['label']:<20} | {cost_display:<15} | {runtime_ms:7.2f} ms"
        )
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
