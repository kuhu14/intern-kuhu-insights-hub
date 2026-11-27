-- Week 4 Task 7: checks for the view v_sales_denorm.
-- The -f path is relative to the folder you are in.
-- From the repo root:
--   & "C:\Program Files\PostgreSQL\16\bin\psql.exe" -h localhost -U insights -d insights_hub -f docs/week04-view-checks.sql
-- From backend/:
--   & "C:\Program Files\PostgreSQL\16\bin\psql.exe" -h localhost -U insights -d insights_hub -f ../docs/week04-view-checks.sql
-- Do not paste this file into PowerShell; it is SQL, not a PowerShell script.

-- 1. Same number of rows as sales (every sale joins to all five masters): 5418
SELECT COUNT(*) AS view_rows FROM v_sales_denorm;

-- 2. Net value by region:
--    East 11979450.64, North 14621494.11, South 15657120.63, West 18726486.86
SELECT region, SUM(net_value) AS net_value
FROM v_sales_denorm
GROUP BY region
ORDER BY region;

-- 3. Navratna, December 2025: 462440.22
SELECT SUM(net_value) AS navratna_dec_2025
FROM v_sales_denorm
WHERE brand = 'Navratna'
  AND invoice_date >= DATE '2025-12-01'
  AND invoice_date <  DATE '2026-01-01';

-- 4. One row, to see the shape (same columns as the Week 3 API)
SELECT * FROM v_sales_denorm ORDER BY invoice_date, invoice_no LIMIT 1;
