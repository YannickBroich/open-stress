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

# Scenarios

## Synthetic

**Preset shock:**
- **UST:** rates **+150 bp**
- **IG:**  rates **+150 bp**, spread **+200 bp**
- **HY:**  rates **+150 bp**, spread **+400 bp**

Customize with CLI flags: `--rates-bp`, `--ig-bp`, `--hy-bp`.

## Historical presets

Presets: `covid2020`, `gfc2008`, `energy2022`

We compute deltas over the chosen date window using the cached series:
- **Rates:** Δ(UST 10y yield)
- **Credit:** Δ(US IG OAS) and Δ(US HY OAS)

The loader resamples to **business days** and **forward-fills** to avoid weekend gaps.  
Make sure your cache covers the window; if not, fetch with an earlier `--start`.

---

# Outputs

- **Console summary** with bucket aggregation and top losers
- **CSV files**
  - `out/stress_detail.csv` — per asset (incl. `pnl_rates`, `pnl_spread`, `dv01`, `cs01`)
  - `out/stress_agg.csv` — per bucket (sum P&L, attribution, exposures)
- **Markdown report** — `out/stress_report.md` (uses `tabulate`; falls back to text if not installed)

---

# Method (brief)

Per asset with market value \(MV\):
\[
\Delta P \approx -MV \cdot \big(D \cdot \Delta y + \tfrac{1}{2}\, C \cdot (\Delta y)^2\big)\;-\; MV \cdot (SD \cdot \Delta s)
\]

Where:
- \(D\) = modified duration (years)  
- \(C\) = convexity (years²)  
- \(SD\) = spread duration (years)  
- \(\Delta y, \Delta s\) are **decimal** changes (bp ÷ 10,000)

**Attribution**
- `pnl_rates` = duration + ½·convexity term  
- `pnl_spread` = spread-duration term

**Exposures**
- **DV01** ≈ \(MV \cdot D / 10{,}000\)  
- **CS01** ≈ \(MV \cdot SD / 10{,}000\)

> FRED series are in **percent** (e.g., 4.25). We convert to **bp** where needed; shocks are specified in **bp**.

---

# Project layout

