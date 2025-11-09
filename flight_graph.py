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
