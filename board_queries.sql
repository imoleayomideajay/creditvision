-- Executive snapshot (most recent month)
SELECT
  mp.month_date,
  SUM(mp.actual_disbursement) AS total_actual_disbursement,
  SUM(mp.budget_disbursement) AS total_budget_disbursement,
  SUM(mp.actual_loan_count) AS total_actual_loan_count,
  SUM(mp.budget_loan_count) AS total_budget_loan_count,
  SUM(mp.pending_applications) AS pending_applications,
  AVG(mr.par30_ratio) AS avg_par30,
  AVG(mr.par90_ratio) AS avg_par90
FROM monthly_portfolio mp
JOIN monthly_risk mr
  ON mp.month_date = mr.month_date
 AND mp.branch_id = mr.branch_id
WHERE mp.month_date = (SELECT MAX(month_date) FROM monthly_portfolio);

-- Branch ranking by actual disbursement (most recent month)
SELECT
  b.branch_name,
  SUM(mp.actual_disbursement) AS actual_disbursement,
  SUM(mp.budget_disbursement) AS budget_disbursement,
  AVG(mr.par30_ratio) AS par30_ratio
FROM monthly_portfolio mp
JOIN branches b ON b.branch_id = mp.branch_id
JOIN monthly_risk mr
  ON mp.month_date = mr.month_date
 AND mp.branch_id = mr.branch_id
WHERE mp.month_date = (SELECT MAX(month_date) FROM monthly_portfolio)
GROUP BY b.branch_name
ORDER BY actual_disbursement DESC;
