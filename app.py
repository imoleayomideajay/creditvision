import sqlite3
import subprocess
import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

DB_PATH = Path("simulated_lending.db")

st.set_page_config(page_title="CrediVision Executive Demo", layout="wide")


def currency(value: float) -> str:
    return f"${value:,.0f}"


def pct(value: float) -> str:
    return f"{value * 100:.2f}%"


@st.cache_data
def load_data() -> dict[str, pd.DataFrame]:
    expected_tables = {
        "monthly_portfolio",
        "monthly_risk",
        "branches",
        "officers",
        "applications",
        "scenario_results",
        "forecast",
    }
    with sqlite3.connect(DB_PATH) as conn:
        table_df = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type = 'table'", conn)
        available_tables = set(table_df["name"])
        missing_tables = sorted(expected_tables - available_tables)
        if missing_tables:
            missing = ", ".join(missing_tables)
            raise RuntimeError(
                "simulated_lending.db is missing required tables: "
                f"{missing}. Rebuild the database with `python generate_simulated_data.py`."
            )

        frames = {
            "portfolio": pd.read_sql_query("SELECT * FROM monthly_portfolio", conn),
            "risk": pd.read_sql_query("SELECT * FROM monthly_risk", conn),
            "branches": pd.read_sql_query("SELECT * FROM branches", conn),
            "officers": pd.read_sql_query("SELECT * FROM officers", conn),
            "applications": pd.read_sql_query("SELECT * FROM applications", conn),
            "scenarios": pd.read_sql_query("SELECT * FROM scenario_results", conn),
            "forecast": pd.read_sql_query("SELECT * FROM forecast", conn),
        }
    for key in ["portfolio", "risk", "applications", "forecast"]:
        frames[key]["month_date"] = pd.to_datetime(frames[key]["month_date"])
    return frames


def rebuild_database() -> None:
    result = subprocess.run(
        [sys.executable, "generate_simulated_data.py"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        stderr = result.stderr.strip()
        raise RuntimeError(
            "Failed to rebuild simulated_lending.db with `python generate_simulated_data.py`."
            + (f" Details: {stderr}" if stderr else "")
        )


def build_kpis(data: dict[str, pd.DataFrame]) -> dict[str, float]:
    latest = data["portfolio"]["month_date"].max()
    p = data["portfolio"].query("month_date == @latest")
    r = data["risk"].query("month_date == @latest")

    value_achievement = p["actual_disbursement"].sum() / p["budget_disbursement"].sum()
    count_achievement = p["actual_loan_count"].sum() / p["budget_loan_count"].sum()
    pending_apps = p["pending_applications"].sum()
    avg_loans_per_officer = p["actual_loan_count"].sum() / data["officers"]["officer_id"].nunique()
    queue_ratio = p["pending_applications"].sum() / p["approved_applications"].sum()

    return {
        "month": latest,
        "value_achievement": value_achievement,
        "count_achievement": count_achievement,
        "par30": r["par30_ratio"].mean(),
        "par90": r["par90_ratio"].mean(),
        "pending_applications": pending_apps,
        "avg_loans_per_officer": avg_loans_per_officer,
        "queue_ratio": queue_ratio,
    }


def apply_filters(
    data: dict[str, pd.DataFrame],
    selected_regions: list[str],
    selected_branches: list[str],
    month_window: tuple[pd.Timestamp, pd.Timestamp],
) -> dict[str, pd.DataFrame]:
    filtered = {k: v.copy() for k, v in data.items()}

    branches = filtered["branches"].copy()
    if selected_regions:
        branches = branches[branches["region"].isin(selected_regions)]
    if selected_branches:
        branches = branches[branches["branch_name"].isin(selected_branches)]

    branch_ids = set(branches["branch_id"])
    if branch_ids:
        for frame_key in ["portfolio", "risk", "applications", "officers"]:
            filtered[frame_key] = filtered[frame_key][filtered[frame_key]["branch_id"].isin(branch_ids)]
    else:
        for frame_key in ["portfolio", "risk", "applications", "officers"]:
            filtered[frame_key] = filtered[frame_key].iloc[0:0]

    start, end = month_window
    for frame_key in ["portfolio", "risk", "applications", "forecast"]:
        filtered[frame_key] = filtered[frame_key].query("month_date >= @start and month_date <= @end")

    filtered["branches"] = branches
    return filtered


def waterfall_budget_vs_actual(data: pd.DataFrame) -> go.Figure:
    latest = data["month_date"].max()
    current = data.query("month_date == @latest")
    budget = current["budget_disbursement"].sum()
    actual = current["actual_disbursement"].sum()
    delta = actual - budget

    fig = go.Figure(
        go.Waterfall(
            name="Budget vs Actual",
            orientation="v",
            measure=["absolute", "relative", "total"],
            x=["Budget", "Variance", "Actual"],
            textposition="outside",
            y=[budget, delta, 0],
            connector={"line": {"color": "#a6a6a6"}},
            decreasing={"marker": {"color": "#B91C1C"}},
            increasing={"marker": {"color": "#0F766E"}},
            totals={"marker": {"color": "#1E3A8A"}},
        )
    )
    fig.update_layout(title="Budget vs Actual Disbursement Bridge", height=360, margin=dict(l=20, r=20, t=50, b=20))
    return fig


def branch_ranking(portfolio: pd.DataFrame, branches: pd.DataFrame) -> go.Figure:
    latest = portfolio["month_date"].max()
    current = portfolio.query("month_date == @latest").merge(branches, on="branch_id")
    ranked = current.groupby("branch_name", as_index=False)["actual_disbursement"].sum().sort_values("actual_disbursement")

    fig = go.Figure(go.Bar(
        x=ranked["actual_disbursement"],
        y=ranked["branch_name"],
        orientation="h",
        marker=dict(color="#1D4ED8"),
        text=[currency(v) for v in ranked["actual_disbursement"]],
        textposition="outside",
    ))
    fig.update_layout(title="Branch Ranking by Monthly Disbursement", height=360, margin=dict(l=20, r=20, t=50, b=20))
    return fig


def delinquency_trend(risk: pd.DataFrame) -> go.Figure:
    trend = risk.groupby("month_date", as_index=False)[["par30_ratio", "par90_ratio"]].mean()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=trend["month_date"], y=trend["par30_ratio"], mode="lines+markers", name="PAR30", line=dict(color="#DC2626", width=3)))
    fig.add_trace(go.Scatter(x=trend["month_date"], y=trend["par90_ratio"], mode="lines+markers", name="PAR90", line=dict(color="#7C3AED", width=3)))
    fig.update_layout(title="Delinquency Trend", yaxis_tickformat=".1%", height=360, margin=dict(l=20, r=20, t=50, b=20))
    return fig


def pipeline_mix(applications: pd.DataFrame) -> go.Figure:
    latest = applications["month_date"].max()
    mix = applications.query("month_date == @latest").groupby("stage", as_index=False)["application_id"].count()
    fig = go.Figure(go.Pie(labels=mix["stage"], values=mix["application_id"], hole=0.5))
    fig.update_layout(title="Pipeline Composition", height=360, margin=dict(l=20, r=20, t=50, b=20))
    return fig


def scenario_chart(scenarios: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Disbursement Impact %", x=scenarios["scenario_name"], y=scenarios["disbursement_impact_pct"], marker_color="#0891B2"))
    fig.add_trace(go.Bar(name="Risk Impact (bps)", x=scenarios["scenario_name"], y=scenarios["risk_impact_bps"], marker_color="#F59E0B"))
    fig.update_layout(title="Scenario Comparison", barmode="group", height=360, margin=dict(l=20, r=20, t=50, b=20))
    return fig


def forecast_chart(forecast: pd.DataFrame) -> go.Figure:
    hist = forecast.query("period_type == 'Historical'")
    fwd = forecast.query("period_type == 'Forecast'")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hist["month_date"], y=hist["projected_disbursement"], mode="lines+markers", name="Historical", line=dict(color="#1E3A8A", width=3)))
    fig.add_trace(go.Scatter(x=fwd["month_date"], y=fwd["projected_disbursement"], mode="lines+markers", name="Forecast", line=dict(color="#0D9488", width=3, dash="dash")))
    fig.update_layout(title="Disbursement Forecast", height=360, margin=dict(l=20, r=20, t=50, b=20))
    return fig


def board_commentary(kpis: dict[str, float]) -> str:
    return (
        f"In {kpis['month'].strftime('%B %Y')}, portfolio value delivery reached {pct(kpis['value_achievement'])} of budget, "
        f"while volume delivery closed at {pct(kpis['count_achievement'])}. Risk remains within tolerance bands with "
        f"PAR30 at {pct(kpis['par30'])} and PAR90 at {pct(kpis['par90'])}. The operating queue stands at "
        f"{kpis['pending_applications']:,} pending applications, translating to a queue ratio of {kpis['queue_ratio']:.2f}."
    )


def main() -> None:
    st.markdown("""
        <style>
        .block-container {padding-top: 1.8rem; padding-bottom: 2rem;}
        [data-testid="stMetricValue"] {font-size: 1.65rem;}
        </style>
    """, unsafe_allow_html=True)

    st.title("CrediVision Executive Demo")
    st.caption("Synthetic lending analytics showcase for board and investor discussions.")

    if not DB_PATH.exists():
        with st.spinner("simulated_lending.db not found. Rebuilding synthetic data..."):
            try:
                rebuild_database()
            except RuntimeError as exc:
                st.error(str(exc))
                st.stop()

    try:
        data = load_data()
    except RuntimeError as exc:
        if "missing required tables" in str(exc):
            with st.spinner("Database schema is incomplete. Rebuilding synthetic data..."):
                try:
                    rebuild_database()
                    load_data.clear()
                    data = load_data()
                except RuntimeError as rebuild_exc:
                    st.error(str(rebuild_exc))
                    st.stop()
        else:
            st.error(str(exc))
            st.stop()

    filtered = data
    try:
        min_month = data["portfolio"]["month_date"].min()
        max_month = data["portfolio"]["month_date"].max()

        st.sidebar.header("Filters")
        regions = sorted(data["branches"]["region"].unique())
        selected_regions = st.sidebar.multiselect("Region", options=regions, default=regions)

        branch_source = data["branches"].copy()
        if selected_regions:
            branch_source = branch_source[branch_source["region"].isin(selected_regions)]
        branch_options = sorted(branch_source["branch_name"].unique())
        selected_branches = st.sidebar.multiselect("Branch", options=branch_options, default=branch_options)

        start_month, end_month = st.sidebar.slider(
            "Month range",
            min_value=min_month.to_pydatetime(),
            max_value=max_month.to_pydatetime(),
            value=(min_month.to_pydatetime(), max_month.to_pydatetime()),
            format="MMM YYYY",
        )

        filtered = apply_filters(
            data,
            selected_regions=selected_regions,
            selected_branches=selected_branches,
            month_window=(pd.Timestamp(start_month), pd.Timestamp(end_month)),
        )
    except Exception as exc:
        st.warning(f"Filter controls are temporarily unavailable; showing full dataset. Details: {exc}")

    if filtered["portfolio"].empty or filtered["risk"].empty:
        st.warning("No data matches the current filter selection. Try broadening filters.")
        st.stop()

    kpis = build_kpis(filtered)

    st.info("This product demo uses fully synthetic data generated for showcase purposes only.")

    st.subheader("Executive Summary")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Value Achievement", pct(kpis["value_achievement"]))
    c2.metric("Count Achievement", pct(kpis["count_achievement"]))
    c3.metric("PAR30", pct(kpis["par30"]))
    c4.metric("PAR90", pct(kpis["par90"]))

    c5, c6, c7 = st.columns(3)
    c5.metric("Pending Applications", f"{kpis['pending_applications']:,}")
    c6.metric("Avg Loans per Officer", f"{kpis['avg_loans_per_officer']:.1f}")
    c7.metric("Queue Ratio", f"{kpis['queue_ratio']:.2f}")

    st.markdown(f"**Board Commentary:** {board_commentary(kpis)}")

    st.subheader("Portfolio Overview")
    p1, p2 = st.columns(2)
    p1.plotly_chart(waterfall_budget_vs_actual(filtered["portfolio"]), use_container_width=True)
    p2.plotly_chart(pipeline_mix(filtered["applications"]), use_container_width=True)

    st.subheader("Branch Performance")
    st.plotly_chart(branch_ranking(filtered["portfolio"], filtered["branches"]), use_container_width=True)

    st.subheader("Risk and Arrears")
    st.plotly_chart(delinquency_trend(filtered["risk"]), use_container_width=True)

    st.subheader("Scenario Analysis")
    st.plotly_chart(scenario_chart(filtered["scenarios"]), use_container_width=True)

    st.subheader("Forecasts")
    st.plotly_chart(forecast_chart(filtered["forecast"]), use_container_width=True)


if __name__ == "__main__":
    main()
