"""Utilities for building a weighted flight graph and computing cheapest routes."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
import heapq
import math
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

import pandas as pd


Graph = Dict[str, Dict[str, float]]
