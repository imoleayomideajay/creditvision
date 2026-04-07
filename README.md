# CrediVision Executive Demo

CrediVision Executive Demo is a board-level analytics product demonstration built on **fully synthetic lending data**. It showcases how executive teams can monitor portfolio delivery, branch productivity, risk movement, pipeline quality, scenarios, and forward outlook in one streamlined interface.

## Overview

This repository contains a premium-style Streamlit application designed for leadership presentations and investor briefings. The dataset is generated locally in SQLite and does not connect to any external systems or real institutions.

## Features

- Executive summary KPI cards (value achievement, count achievement, PAR30, PAR90, pending applications, average loans per officer, queue ratio)
- Portfolio overview with a budget-vs-actual waterfall bridge and pipeline composition
- Branch performance ranking for latest month disbursement output
- Risk and arrears view with PAR trend monitoring
- Scenario analysis comparing strategic operating assumptions
- Forecast view with clear separation of historical and projected periods
- Concise board commentary generated from current synthetic portfolio metrics

## Architecture

The demo uses a simple synthetic SQL model:

1. `simulated_schema.sql` defines operational and analytics tables.
2. `generate_simulated_data.py` seeds deterministic synthetic records into `simulated_lending.db`.
3. `app.py` loads SQLite data, computes KPIs, and renders presentation-grade Plotly visuals in Streamlit.

### Simulated SQL Model

Core entities include:
- `branches`, `officers` for operating structure
- `monthly_portfolio` for budget/actual and pipeline metrics
- `monthly_risk` for PAR30, PAR90, and arrears indicators
- `applications` for stage and composition analysis
- `scenario_results` for executive what-if comparisons
- `forecast` for historical + forecast periods

## How to Run

```bash
python generate_simulated_data.py
streamlit run app.py
```

## Screenshots

Launch the app and capture presentation screenshots from:
- Executive Summary
- Portfolio Overview
- Branch Performance
- Risk and Arrears
- Scenario Analysis
- Forecasts

## Use Cases

- Board pack and steering committee dry-runs
- Investor narrative rehearsal using synthetic performance data
- Analytics UI prototyping for lending portfolio governance
- Internal enablement and training for portfolio monitoring workflows

## Notes

- All data is synthetic and generated locally.
- No live API or external core banking connection is used.
- This is a product demo, not a production decisioning platform.
