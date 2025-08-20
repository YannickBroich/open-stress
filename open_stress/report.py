from __future__ import annotations
from pathlib import Path
import pandas as pd


def print_report(detail: pd.DataFrame, agg: pd.DataFrame) -> None:
    total_mv = agg["mv"].sum()
    total_pnl = agg["pnl"].sum()
    print("STRESS RESULT")
    print(agg.round(2))
    print("\nTotal MV:", f"{total_mv:,.0f}")
    print("Total PnL:", f"{total_pnl:,.0f}")
    if total_mv:
        print("Total PnL %:", f"{100.0 * total_pnl / total_mv:,.2f}%")

    print("Top5 Greatest Losses")
    print(detail.sort_values("pnl").head(5).round(2))


def export_csv(detail: pd.DataFrame, agg: pd.DataFrame, out_dir: str | Path = "out") -> tuple[Path, Path]:
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    p1 = out / "stress_detail.csv"
    p2 = out / "stress_agg.csv"
    detail.to_csv(p1, index=False)
    agg.to_csv(p2)
    return p1, p2


def export_markdown(detail: pd.DataFrame, agg: pd.DataFrame, out_path: str | Path = "out/stress_report.md") -> Path:
    out = Path(out_path); out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write("# Stress Report\n\n")
        f.write("#Aggregation\n\n")
        f.write(agg.round(3).to_markdown())
        f.write("\n\n## Top 10 Losers\n\n")
        f.write(detail.sort_values("pnl").head(10).round(2).to_markdown(index=False))
    return out