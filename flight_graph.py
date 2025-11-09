"""Utilities for building a weighted flight graph and computing cheapest routes."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
import heapq
import math
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

import pandas as pd


Graph = Dict[str, Dict[str, float]]

@dataclass(frozen=True)
class RouteMetadata:
    origin_city: str
    destination_city: str
    origin_airport: str
    destination_airport: str
    fare: float
    passengers: Optional[float]
    miles: Optional[float]
    primary_carrier: Optional[str]


def load_route_dataframe(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    required_columns = [
        "city1",
        "city2",
        "airport_1",
        "airport_2",
        "fare",
        "passengers",
        "nsmiles",
        "carrier_low",
        "carrier_lg",
    ]
    missing = set(required_columns) - set(df.columns)
    if missing:
        raise ValueError(f"Dataset is missing required columns: {sorted(missing)}")

    trimmed = df[required_columns].dropna(subset=["fare", "airport_1", "airport_2"])
    trimmed["fare"] = trimmed["fare"].astype(float)
    return trimmed

def _build_metadata_row(row: Mapping[str, object]) -> RouteMetadata:
    origin_city = str(row["city1"]).strip()
    dest_city = str(row["city2"]).strip()
    origin_airport = str(row["airport_1"]).strip()
    dest_airport = str(row["airport_2"]).strip()
    fare = float(row["fare"])
    passengers = None if pd.isna(row["passengers"]) else float(row["passengers"])
    miles = None if pd.isna(row["nsmiles"]) else float(row["nsmiles"])

    carrier = row.get("carrier_low") or row.get("carrier_lg")
    carrier_str = None if pd.isna(carrier) else str(carrier)

    return RouteMetadata(
        origin_city=origin_city,
        destination_city=dest_city,
        origin_airport=origin_airport,
        destination_airport=dest_airport,
        fare=fare,
        passengers=passengers,
        miles=miles,
        primary_carrier=carrier_str,
    )

def build_graph(
    dataframe: pd.DataFrame,
) -> Tuple[Graph, Dict[Tuple[str, str], RouteMetadata]]:
    graph: Graph = defaultdict(dict)
    metadata: Dict[Tuple[str, str], RouteMetadata] = {}

    for row in dataframe.to_dict(orient="records"):
        record = _build_metadata_row(row)

        if not record.origin_airport or not record.destination_airport:
            continue

        current = graph[record.origin_airport].get(record.destination_airport)
        if current is None or record.fare < current:
            graph[record.origin_airport][record.destination_airport] = record.fare
            metadata[(record.origin_airport, record.destination_airport)] = record

        reverse = metadata.get((record.destination_airport, record.origin_airport))
        if reverse is None or record.fare < reverse.fare:
            mirrored = RouteMetadata(
                origin_city=record.destination_city,
                destination_city=record.origin_city,
                origin_airport=record.destination_airport,
                destination_airport=record.origin_airport,
                fare=record.fare,
                passengers=record.passengers,
                miles=record.miles,
                primary_carrier=record.primary_carrier,
            )
            graph[record.destination_airport][record.origin_airport] = record.fare
            metadata[(record.destination_airport, record.origin_airport)] = mirrored

    return graph, metadata

def build_city_airport_lookup(dataframe: pd.DataFrame) -> Dict[str, List[str]]:
    city_to_airports: Dict[str, set] = defaultdict(set)

    for row in dataframe.to_dict(orient="records"):
        city_to_airports[str(row["city1"]).strip()].add(str(row["airport_1"]).strip())
        city_to_airports[str(row["city2"]).strip()].add(str(row["airport_2"]).strip())

    return {city: sorted(airports) for city, airports in city_to_airports.items()}
