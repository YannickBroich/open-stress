from __future__ import annotations
import argparse
import pandas as pd
from pathlib import Path

from open_stress import (
    fetch_fred, load_cached_fred,
    SYNTH_PARALLEL, synthetic_parallel, historic_preset,
    stress_portfolio, print_report, export_csv, export_markdown
)


def cmd_fetch(args: argparse.Namespace) -> None:
    df = fetch_fred(cache_dir=args.cache, start=args.start, end=args.end)
    print("Saved:", Path(args.cache) / "fred_timeseries.csv", "rows:", len(df))


def _load_portfolio(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    # expected columns at minimum
    need = {"asset", "mv"}
    miss = need - set(df.columns)
    if miss:
        raise SystemExit(f"Portfolio missing columns: {miss}")
    return df


def cmd_stress_synth(args: argparse.Namespace) -> None:
    port = _load_portfolio(args.portfolio)
    if args.preset:
        shock = SYNTH_PARALLEL
    else:
        shock = synthetic_parallel(args.ust_bp, args.ig_bp, args.hy_bp, args.rates_bp)
    detail, agg = stress_portfolio(port, shock)
    print_report(detail, agg)
    export_csv(detail, agg, args.out)
    export_markdown(detail, agg, Path(args.out) / "stress_report.md")


def cmd_stress_hist(args: argparse.Namespace) -> None:
    df = load_cached_fred(cache_dir=args.cache)
    shock = historic_preset(df, args.preset)
    port = _load_portfolio(args.portfolio)
    detail, agg = stress_portfolio(port, shock)
    print_report(detail, agg)
    export_csv(detail, agg, args.out)
    export_markdown(detail, agg, Path(args.out) / f"stress_report_{args.preset}.md")


def main() -> None:
    p = argparse.ArgumentParser(description="Open Stress — Credit & Rates Stress Testing Toolkit")
    sub = p.add_subparsers(dest="cmd", required=True)

    pf = sub.add_parser("fetch", help="Fetch public FRED data and cache it under ./data/")
    pf.add_argument("--cache", default="data")
    pf.add_argument("--start", default=None, help="YYYY-MM-DD (optional)")
    pf.add_argument("--end", default=None, help="YYYY-MM-DD (optional)")
    pf.set_defaults(func=cmd_fetch)


    ps = sub.add_parser("stress-synth", help="Synthetic stress (parallel rates + credit widening)")
    ps.add_argument("--portfolio", required=True)
    ps.add_argument("--out", default="out")
    ps.add_argument("--preset", action="store_true", help="use default: UST +150bp, IG +200bp, HY +400bp")
    ps.add_argument("--rates-bp", type=float, default=None)
    ps.add_argument("--ust-bp", type=float, default=150.0)
    ps.add_argument("--ig-bp", type=float, default=200.0)
    ps.add_argument("--hy-bp", type=float, default=400.0)
    ps.set_defaults(func=cmd_stress_synth)

    ph = sub.add_parser("stress-hist", help="Historical stress (predefined window)")
    ph.add_argument("--cache", default="data")
    ph.add_argument("--portfolio", required=True)
    ph.add_argument("--out", default="out")
    ph.add_argument("--preset", choices=["covid2020", "gfc2008", "energy2022"], default="covid2020")
    ph.set_defaults(func=cmd_stress_hist)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
