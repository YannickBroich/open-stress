from __future__ import annotations
import pandas as pd


SYNTH_PARALLEL = {
    "UST": {"dy_bp": +150.0, "ds_bp": 0.0},
    "IG":  {"dy_bp": +150.0, "ds_bp": +200.0},
    "HY":  {"dy_bp": +150.0, "ds_bp": +400.0},
}


def synthetic_parallel(ust_bp: float, ig_bp: float, hy_bp: float, rates_bp: float | None = None) -> dict:
    dy = float(rates_bp if rates_bp is not None else ust_bp)
    return {
        "UST": {"dy_bp": dy, "ds_bp": 0.0},
        "IG":  {"dy_bp": dy, "ds_bp": float(ig_bp)},
        "HY":  {"dy_bp": dy, "ds_bp": float(hy_bp)},
    }


def historic_window(df: pd.DataFrame, start: str, end: str) -> dict:

    s0, s1 = pd.Timestamp(start), pd.Timestamp(end)
    cols = ["DGS10", "IG_OAS", "HY_OAS"]
    for c in cols:
        if c not in df.columns:
            raise KeyError(f"Missing column in FRED cache: {c}")

    dfw = df[cols].sort_index()

    dfw = dfw.resample("B").ffill()

    # clamp window to data coverage
    s0 = max(s0, dfw.index.min())
    s1 = min(s1, dfw.index.max())
    if s0 >= s1:
        raise ValueError("Requested window is outside data coverage.")

    cut = dfw.loc[s0:s1]
    if cut.empty:
        raise ValueError("No data in the selected window after resampling.")

    first, last = cut.iloc[0], cut.iloc[-1]
    dy_bp  = float((last["DGS10"] - first["DGS10"]) * 100.0)
    dig_bp = float((last["IG_OAS"] - first["IG_OAS"]) * 100.0)
    dhy_bp = float((last["HY_OAS"] - first["HY_OAS"]) * 100.0)
    return synthetic_parallel(ust_bp=dy_bp, ig_bp=dig_bp, hy_bp=dhy_bp, rates_bp=dy_bp)


HIST_PRESETS = {
    # Covid-Crash
    "covid2020": ("2020-02-20", "2020-03-20"),
    # GFC-Segment - "Lehman week"
    "gfc2008": ("2008-09-08", "2008-10-10"),
    # Energy/Inflation Shock
    "energy2022": ("2022-06-01", "2022-10-01"),
}


def historic_preset(df: pd.DataFrame, name: str) -> dict:
    if name not in HIST_PRESETS:
        raise KeyError(f"Unknown preset: {name}")
    s, e = HIST_PRESETS[name]
    return historic_window(df, s, e)