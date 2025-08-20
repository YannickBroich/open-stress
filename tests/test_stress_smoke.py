import pandas as pd
from open_stress.stressor import stress_portfolio

def test_synthetic_preset_matches_demo():
    port = pd.read_csv("examples/portfolio_example.csv")
    shock = {
        "UST": {"dy_bp": 150.0, "ds_bp": 0.0},
        "IG":  {"dy_bp": 150.0, "ds_bp": 200.0},
        "HY":  {"dy_bp": 150.0, "ds_bp": 400.0},
    }
    detail, agg = stress_portfolio(port, shock)


    assert round(float(agg.loc["IG", "pnl"]), 1)  == -579000.0
    assert round(float(agg.loc["UST","pnl"]), 1) == -213000.0
    assert round(float(agg.loc["HY", "pnl"]), 1) == -179600.0
    total = float(agg["pnl"].sum())
    assert round(total, 1) == -971600.0


    for col in ["dv01", "cs01"]:
        assert col in agg.columns
