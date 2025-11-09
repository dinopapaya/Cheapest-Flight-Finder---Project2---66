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
