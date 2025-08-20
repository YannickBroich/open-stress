from __future__ import annotations
import numpy as np
import pandas as pd

def summary(pnl: pd.Series, scale_per_year: int = 252) -> dict:
    pnl = pnl.dropna()
    if pnl.empty:
        return {"mean_pa": 0.0, "vol_pa": 0.0, "sharpe": 0.0, "max_drawdown": 0.0}
    ret = pnl  
    mu = float(ret.mean() * scale_per_year)
    sigma = float(ret.std(ddof=1) * np.sqrt(scale_per_year))
    sharpe = float(mu / sigma) if sigma > 0 else 0.0
    cum = ret.cumsum()
    peak = cum.cummax()
    mdd = float((cum - peak).min())
    return {"mean_pa": mu, "vol_pa": sigma, "sharpe": sharpe, "max_drawdown": mdd}