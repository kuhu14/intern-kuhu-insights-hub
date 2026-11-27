-- Week 4 Task 6: queries used for the EXPLAIN ANALYZE evidence in week04-explain.md.
-- Run from the repo root:
--   & "C:\Program Files\PostgreSQL\16\bin\psql.exe" -h localhost -U insights -d insights_hub -f docs/week04-explain.sql

-- Refresh the planner's statistics so the plans are realistic.
ANALYZE sales;

-- Query A: monthly summary for one month (what the API runs for date_from/date_to)
EXPLAIN (ANALYZE, BUFFERS)
SELECT date_trunc('month', invoice_date)::date AS month,
       SUM(net_value) AS net_value,
       SUM(quantity)  AS quantity,
       COUNT(*)       AS row_count
FROM sales
WHERE invoice_date >= DATE '2025-12-01'
  AND invoice_date <  DATE '2026-01-01'
GROUP BY 1;

-- Query B: monthly summary over the whole table
EXPLAIN (ANALYZE, BUFFERS)
SELECT date_trunc('month', invoice_date)::date AS month,
       SUM(net_value) AS net_value,
       SUM(quantity)  AS quantity,
       COUNT(*)       AS row_count
FROM sales
GROUP BY 1
ORDER BY 1;
