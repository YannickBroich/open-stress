# open_stress/stressor.py
from __future__ import annotations
import pandas as pd

# Rates: Duration/Convexity
# Credit: Spread-Duration

def pnl_duration_convexity_spread(row: pd.Series, dy_bp: float, ds_bp: float) -> float:
    """
    Legacy single-value PnL (kept for compatibility).
    Returns total PnL from rates (duration+convexity) and credit (spread duration).
    """
    dy = float(dy_bp) / 1e4  # bp -> decimal
    ds = float(ds_bp) / 1e4
    mv = float(row.get("mv", 0.0) or 0.0)
    D  = float(row.get("duration", 0.0) or 0.0)
    C  = float(row.get("convexity", 0.0) or 0.0)
    SD = float(row.get("spread_dur", 0.0) or 0.0)
    dP_rates  = - mv * (D * dy + 0.5 * C * dy * dy)
    dP_spread = - mv * (SD * ds)
    return dP_rates + dP_spread


def pnl_components(row: pd.Series, dy_bp: float, ds_bp: float) -> tuple[float, float]:
    """
    Returns (pnl_rates, pnl_spread) separately.
    """
    dy = float(dy_bp) / 1e4  # bp -> decimal
    ds = float(ds_bp) / 1e4
    mv = float(row.get("mv", 0.0) or 0.0)
    D  = float(row.get("duration", 0.0) or 0.0)
    C  = float(row.get("convexity", 0.0) or 0.0)
    SD = float(row.get("spread_dur", 0.0) or 0.0)
    pnl_rates  = - mv * (D * dy + 0.5 * C * dy * dy)
    pnl_spread = - mv * (SD * ds)
    return pnl_rates, pnl_spread


def stress_portfolio(
    df_port: pd.DataFrame,
    shock: dict[str, dict[str, float]]
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Apply a bucketed shock to the portfolio.
    Expected df_port columns (min): asset, mv, duration, convexity, spread_dur, bucket
    shock example:
        {
          "UST": {"dy_bp": +150, "ds_bp": 0},
          "IG":  {"dy_bp": +150, "ds_bp": +200},
          "HY":  {"dy_bp": +150, "ds_bp": +400},
        }
    Returns:
        detail DataFrame (per asset) and agg DataFrame (per bucket)
        with pnl_rates, pnl_spread, total pnl, and exposures dv01/cs01.
    """
    rows: list[dict] = []
    for _, r in df_port.iterrows():
        b = str(r.get("bucket", "")).strip() or "GEN"
        s = shock.get(b, {"dy_bp": 0.0, "ds_bp": 0.0})
        dy = float(s.get("dy_bp", 0.0))
        ds = float(s.get("ds_bp", 0.0))

        # components
        pnl_r, pnl_s = pnl_components(r, dy, ds)

        # exposures (per 1 bp)
        mv = float(r.get("mv", 0.0) or 0.0)
        D  = float(r.get("duration", 0.0) or 0.0)
        SD = float(r.get("spread_dur", 0.0) or 0.0)
        dv01_i = mv * D / 1e4     # ΔP per 1 bp in rates
        cs01_i = mv * SD / 1e4    # ΔP per 1 bp in spread

        rows.append({
            "asset": r.get("asset"),
            "bucket": b,
            "mv": mv,
            "pnl_rates": pnl_r,
            "pnl_spread": pnl_s,
            "pnl": pnl_r + pnl_s,
            "dv01": dv01_i,
            "cs01": cs01_i,
            "dy_bp": dy,
            "ds_bp": ds,
        })

    out = pd.DataFrame(rows)

    agg = (
        out.groupby("bucket", dropna=False)
           .agg(
               mv=("mv", "sum"),
               pnl=("pnl", "sum"),
               pnl_rates=("pnl_rates", "sum"),
               pnl_spread=("pnl_spread", "sum"),
               dv01=("dv01", "sum"),
               cs01=("cs01", "sum"),
           )
           .sort_values("pnl")
    )
    agg["pnl_pct"] = agg["pnl"] / agg["mv"].where(agg["mv"] != 0, other=float("nan"))

    return out, agg
