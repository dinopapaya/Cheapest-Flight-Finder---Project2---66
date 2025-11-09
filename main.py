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
