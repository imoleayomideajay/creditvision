# CreditVision Demo App

A polished, demo-safe frontend designed for GitHub presentation and investor screenshots.

## Detailed app description

CreditVision is a synthetic lending intelligence demo built to communicate product vision clearly in
board, investor, and stakeholder conversations without exposing production data. The app combines a
polished static web layout (`index.html` + `styles.css`) with a richer Streamlit analytics experience
(`app.py`) powered by generated, fully synthetic portfolio data.

At a product-story level, the experience is intentionally structured as an executive narrative:

1. **Context first (landing):** a top-of-page hero introduces the purpose of the demo environment and
   sets expectations that the content is synthetic and presentation-ready.
2. **Signal summary (KPIs):** concise portfolio health indicators show trend direction and relative
   movement to anchor the discussion quickly.
3. **Diagnostic visuals (charts):** utilization, segment allocation, branch performance, risk trends,
   scenario outcomes, and forecast trajectories provide enough depth for strategic questioning.
4. **Guided storytelling (help/empty states):** where live integrations are absent, the UI gives clear
   narration prompts so presenters can continue confidently.

The Streamlit version extends this narrative into a decision-support dashboard with:

- **Automatic data readiness checks** for required tables in `simulated_lending.db`.
- **Self-healing demo setup** that rebuilds synthetic data if the database is missing or incomplete.
- **Filter controls** (region, branch, month window) to tailor analysis for different audiences.
- **Executive commentary generation** that converts KPI outputs into board-ready narrative language.
- **Multi-view analytics** including budget-vs-actual bridge, pipeline composition, delinquency trends,
  branch ranking, scenario comparison, and forward-looking disbursement forecasting.

From a design perspective, the app uses a clean light theme, card-based information architecture, and
consistent accent styling to maximize screenshot quality and deck readability. The repository also
includes explicit screenshot composition guidance and demo-safe wording rules to support repeatable,
compliant presentation workflows.

In short, CreditVision is less a production ops console and more a **high-confidence demo artifact**:
it demonstrates how a lending analytics product could look and feel in executive settings while
remaining safe, anonymized, and easy to showcase.

## What this repo now includes

- A top-of-page **landing section** that introduces the synthetic product story.
- Consistent design language across overview, portfolio, and trends views.
- Polished **empty-state/help text** in every section where data may be missing.
- Synthetic/demo-safe labels and wording in every visible UI label.
- Screenshot composition guidance for investor-ready captures.

## Quick start

Open `index.html` in any modern browser.

## Screenshot generation guidance

Use this checklist to capture investor-friendly screenshots:

1. **Viewport**: 16:9 ratio at 1440×810 or 1920×1080.
2. **Theme**: Keep default light theme for clean deck readability.
3. **Focus area**: Capture the landing + KPI row first, then each dashboard section.
4. **Data framing**: Keep synthetic values visible; avoid cropping chart titles.
5. **Empty states**: Include one screenshot that shows the polished no-data guidance.
6. **Naming**: Save files with sequence numbers, e.g. `01-landing.png`, `02-overview.png`.

Recommended screenshot set:

- `01-landing.png` — Hero and value proposition.
- `02-overview-kpis.png` — KPI cards and synthetic trend chart.
- `03-portfolio.png` — Segment cards and allocation visuals.
- `04-empty-state.png` — Help/empty guidance block.

## Demo-safe wording policy

This app intentionally uses synthetic content for safe demos:

- No real customer names.
- No real account identifiers.
- No regulated-credit decisions.
- Labels use neutral terms (e.g., “Demo Segment A”, “Synthetic Utilization Trend”).
