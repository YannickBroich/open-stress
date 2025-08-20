from __future__ import annotations
__all__ = [
    "fetch_fred", "load_cached_fred", "SYNTH_PARALLEL",
    "synthetic_parallel", "historic_window", "historic_preset",
    "stress_portfolio", "pnl_duration_convexity_spread",
    "summary", "print_report", "export_csv", "export_markdown"
]

from .data import fetch_fred, load_cached_fred
from .scenarios import SYNTH_PARALLEL, synthetic_parallel, historic_window, historic_preset
from .stressor import stress_portfolio, pnl_duration_convexity_spread
from .metrics import summary
from .report import print_report, export_csv, export_markdown