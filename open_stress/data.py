from __future__ import annotations
from pathlib import Path
import pandas as pd

# Map: unsere Spaltennamen -> FRED Series IDs
FRED_IDS: dict[str, str] = {
    "DGS2": "DGS2",                 # 2Y UST yield (%)
    "DGS10": "DGS10",               # 10Y UST yield (%)
    "IG_OAS": "BAMLC0A0CM",         # US IG OAS (%)
    "HY_OAS": "BAMLH0A0HYM2",       # US HY OAS (%)
}

def _read_fred_series(symbol: str, colname: str,
                      start: str | None = None, end: str | None = None) -> pd.Series:
    
    from pandas_datareader import data as web  # lazy import
    s = web.DataReader(symbol, "fred", start=start, end=end).squeeze("columns")
    s.name = colname
    # Ensure float and proper datetime index
    s = pd.to_numeric(s, errors="coerce")
    s = s.dropna()
    s.index = pd.to_datetime(s.index)
    return s

def fetch_fred(cache_dir: str | Path = "data",
               series: dict[str, str] | None = None,
               start: str | None = None, end: str | None = None) -> pd.DataFrame:
 
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    series = series or FRED_IDS

    parts: list[pd.Series] = []
    for colname, fred_id in series.items():
        s = _read_fred_series(fred_id, colname, start=start, end=end)
        parts.append(s)

    df = pd.concat(parts, axis=1).sort_index()
    out_path = cache_dir / "fred_timeseries.csv"
    df.to_csv(out_path, index=True)
    return df

def load_cached_fred(cache_dir: str | Path = "data") -> pd.DataFrame:
    p = Path(cache_dir) / "fred_timeseries.csv"
    if not p.exists():
        raise FileNotFoundError(f"Cache not found: {p}. Run fetch_fred() or the CLI 'fetch'.")
    return pd.read_csv(p, parse_dates=[0], index_col=0)
