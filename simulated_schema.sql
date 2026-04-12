PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS monthly_portfolio;
DROP TABLE IF EXISTS monthly_risk;
DROP TABLE IF EXISTS applications;
DROP TABLE IF EXISTS officers;
DROP TABLE IF EXISTS scenario_results;
DROP TABLE IF EXISTS forecast;
DROP TABLE IF EXISTS branches;

CREATE TABLE branches (
  branch_id INTEGER PRIMARY KEY,
  branch_name TEXT NOT NULL,
  region TEXT NOT NULL
);

CREATE TABLE officers (
  officer_id INTEGER PRIMARY KEY,
  branch_id INTEGER NOT NULL,
  officer_name TEXT NOT NULL,
  FOREIGN KEY (branch_id) REFERENCES branches(branch_id)
);

CREATE TABLE monthly_portfolio (
  record_id INTEGER PRIMARY KEY,
  month_date TEXT NOT NULL,
  branch_id INTEGER NOT NULL,
  budget_disbursement REAL NOT NULL,
  actual_disbursement REAL NOT NULL,
  budget_loan_count INTEGER NOT NULL,
  actual_loan_count INTEGER NOT NULL,
  portfolio_outstanding REAL NOT NULL,
  pipeline_amount REAL NOT NULL,
  pending_applications INTEGER NOT NULL,
  approved_applications INTEGER NOT NULL,
  rejected_applications INTEGER NOT NULL,
  FOREIGN KEY (branch_id) REFERENCES branches(branch_id)
);

CREATE TABLE monthly_risk (
  risk_id INTEGER PRIMARY KEY,
  month_date TEXT NOT NULL,
  branch_id INTEGER NOT NULL,
  par30_ratio REAL NOT NULL,
  par90_ratio REAL NOT NULL,
  arrears_amount REAL NOT NULL,
  FOREIGN KEY (branch_id) REFERENCES branches(branch_id)
);

CREATE TABLE applications (
  application_id INTEGER PRIMARY KEY,
  month_date TEXT NOT NULL,
  branch_id INTEGER NOT NULL,
  product_type TEXT NOT NULL,
  stage TEXT NOT NULL,
  requested_amount REAL NOT NULL,
  FOREIGN KEY (branch_id) REFERENCES branches(branch_id)
);

CREATE TABLE scenario_results (
  scenario_name TEXT PRIMARY KEY,
  disbursement_impact_pct REAL NOT NULL,
  risk_impact_bps INTEGER NOT NULL,
  liquidity_impact_pct REAL NOT NULL
);

CREATE TABLE forecast (
  month_date TEXT PRIMARY KEY,
  period_type TEXT NOT NULL,
  projected_disbursement REAL NOT NULL,
  projected_par30 REAL NOT NULL
);
