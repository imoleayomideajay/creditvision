import math
import random
import sqlite3
from datetime import date
from pathlib import Path

DB_PATH = Path("simulated_lending.db")
SCHEMA_PATH = Path("simulated_schema.sql")


def month_starts(start_year: int, start_month: int, end_year: int, end_month: int) -> list[date]:
    months = []
    year, month = start_year, start_month
    while (year < end_year) or (year == end_year and month <= end_month):
        months.append(date(year, month, 1))
        month += 1
        if month == 13:
            month = 1
            year += 1
    return months


def add_months(d: date, count: int) -> date:
    year = d.year + (d.month - 1 + count) // 12
    month = (d.month - 1 + count) % 12 + 1
    return date(year, month, 1)


def seed_database() -> None:
    random.seed(42)

    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA_PATH.read_text())

    branches = [
        (1, "Central City", "Metro"),
        (2, "Harbor Point", "Coastal"),
        (3, "Summit North", "Highlands"),
        (4, "River East", "Inland"),
        (5, "Lakeside West", "Regional"),
    ]
    conn.executemany("INSERT INTO branches VALUES (?, ?, ?)", branches)

    officers = []
    oid = 1
    for bid, *_ in branches:
        for i in range(1, 8):
            officers.append((oid, bid, f"Officer {bid}-{i}"))
            oid += 1
    conn.executemany("INSERT INTO officers VALUES (?, ?, ?)", officers)

    months = month_starts(2024, 1, 2026, 3)
    portfolio_rows, risk_rows, app_rows = [], [], []
    rid = risk_id = app_id = 1

    for m in months:
        seasonality = 1 + 0.08 * math.sin(m.month / 12 * 2 * math.pi)
        trend = 1 + ((m.year - 2024) * 0.06)

        for bid, *_ in branches:
            branch_factor = 0.9 + bid * 0.05
            budget = 950_000 * seasonality * trend * branch_factor
            actual = budget * random.uniform(0.88, 1.08)
            budget_count = int(220 * trend * branch_factor)
            actual_count = int(budget_count * random.uniform(0.9, 1.12))
            outstanding = actual * random.uniform(2.2, 3.1)
            pipeline = actual * random.uniform(0.45, 0.85)
            pending = int(actual_count * random.uniform(0.18, 0.32))
            approved = int(actual_count * random.uniform(0.72, 0.89))
            rejected = max(actual_count - approved, 0)

            portfolio_rows.append((rid, m.isoformat(), bid, budget, actual, budget_count, actual_count, outstanding, pipeline, pending, approved, rejected))
            rid += 1

            par30 = max(0.018, min(0.075, random.gauss(0.038 + bid * 0.002, 0.006)))
            par90 = max(0.006, min(par30 * 0.6, random.gauss(0.018 + bid * 0.0015, 0.003)))
            arrears = outstanding * (par30 + random.uniform(0.02, 0.04))
            risk_rows.append((risk_id, m.isoformat(), bid, par30, par90, arrears))
            risk_id += 1

            for _ in range(20):
                stage = random.choices(["Under Review", "Approved", "Rejected", "Pending Documents"], [0.35, 0.42, 0.11, 0.12])[0]
                product = random.choice(["SME", "Consumer", "Agriculture", "Trade Finance"])
                req_amt = random.uniform(2_500, 38_000)
                app_rows.append((app_id, m.isoformat(), bid, product, stage, req_amt))
                app_id += 1

    conn.executemany("INSERT INTO monthly_portfolio VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", portfolio_rows)
    conn.executemany("INSERT INTO monthly_risk VALUES (?, ?, ?, ?, ?, ?)", risk_rows)
    conn.executemany("INSERT INTO applications VALUES (?, ?, ?, ?, ?, ?)", app_rows)

    scenarios = [
        ("Base Case", 0.0, 0, 0.0),
        ("Growth Push", 8.5, 35, -1.2),
        ("Risk Tightening", -4.0, -40, 0.8),
        ("Operational Acceleration", 5.2, -10, -0.6),
    ]
    conn.executemany("INSERT INTO scenario_results VALUES (?, ?, ?, ?)", scenarios)

    recent = months[-9:]
    future = [add_months(months[-1], i) for i in range(1, 7)]
    forecast_rows = []
    base = 6_500_000
    for i, m in enumerate(recent):
        forecast_rows.append((m.isoformat(), "Historical", base + i * 85_000, 0.039 - i * 0.0004))
    for i, m in enumerate(future):
        forecast_rows.append((m.isoformat(), "Forecast", base + (i + len(recent)) * 110_000, 0.034 - i * 0.0003))

    conn.executemany("INSERT INTO forecast VALUES (?, ?, ?, ?)", forecast_rows)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    seed_database()
