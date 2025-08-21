# OpenStress — Credit & Rates Stress Testing Toolkit

**OpenStress** is a small, practical Python toolkit that stress-tests fixed-income / credit portfolios using **public data** only.  
It fetches FRED time series (UST 2y/10y yields and US IG/HY option-adjusted spreads), builds **synthetic** and **historical** scenarios, and estimates portfolio **P&L** using **duration/convexity** (rates) and **spread duration** (credit).  
Results include **rates-vs-credit P&L attribution**, **DV01/CS01** exposures, and CSV/Markdown reports—**all from a simple CLI**.

> Why this is useful: it’s a clear, reproducible way to show risk intuition (rates vs. credit) with clean code and zero proprietary data.

---

## Features
- **Public data (FRED)** — no API key required; cache saved to `data/`.
- **Scenarios**
  - **Synthetic:** parallel rate shocks + credit widening (per bucket).
  - **Historical presets:** `covid2020`, `gfc2008`, `energy2022` (robust to weekends via business-day resample + forward-fill).
- **Attribution & exposures**
  - P&L split into **rates** vs. **credit** contributions.
  - **DV01 / CS01** reported by bucket and available per asset.
- **Outputs**
  - Console summary, `out/stress_detail.csv`, `out/stress_agg.csv`, and `out/stress_report.md`.
- **Lightweight**
  - Pure Python/pandas, CLI-first, notebook-friendly, minimal dependencies.

---

## Quickstart

```bash
# (optional) create & activate a virtual environment
python -m venv .venv
# Windows: .\.venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate

python -m pip install -r requirements.txt

# 1) Fetch public FRED data (cached under ./data)
python run_cli.py fetch --cache data --start 2005-01-01

# 2) Synthetic stress (preset: UST +150bp, IG +200bp, HY +400bp)
python run_cli.py stress-synth --portfolio examples/portfolio_example.csv --preset --out out

# 3) Historical stress (e.g., covid 2020)
python run_cli.py stress-hist --portfolio examples/portfolio_example.csv --preset covid2020 --out out
