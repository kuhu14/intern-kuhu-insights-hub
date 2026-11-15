Loaded 5418 rows into sales.db

--Table: sales (loaded from data_pipeline/output/clean_sales.csv)
--is_return is 1 for credit notes (returns), 0 for normal sales

--Q1. Total net value and total quantity
SELECT
ROUND(SUM(net_value), 2) AS total_net_value,
SUM(qty) AS total_qty
FROM sales
total_net_value total_qty
60984552.24 568254

--Q2. Net value by region, with percentage share.
SELECT
region,
ROUND(SUM(net_value), 2) AS net_value,
ROUND(100.0 \* SUM(net_value) / (SELECT SUM(net_value) FROM sales), 2) AS pct_share
FROM sales
GROUP BY region
ORDER BY net_value DESC
region net_value pct_share
West 18726486.86 30.71
South 15657120.63 25.67
North 14621494.11 23.98
East 11979450.64 19.64

--Q3. Top 5 SKUs by net value.
SELECT
sku_code,
sku_name,
ROUND(SUM(net_value), 2) AS net_value
FROM sales
GROUP BY sku_code, sku_name
ORDER BY net_value DESC
LIMIT 5
sku_code sku_name net_value
EM-1007 Kesh King Ayurvedic Oil 200 ml 3956206.23
EM-1018 Dermicool Prickly Heat Powder 300 g 3527485.97
EM-1009 BoroPlus Antiseptic Cream 40 ml 3280513.22
EM-1023 He Deodorant 150 ml 3109241.46
EM-1016 Zandu Chyawanprash 900 g 3014871.09

--Q4. Monthly net value trend.
SELECT
strftime('%Y-%m', invoice_date) AS month,
ROUND(SUM(net_value), 2) AS net_value
FROM sales
GROUP BY month
ORDER BY month
month net_value
2025-04 3158293.16
2025-05 2775995.85
2025-06 3523902.36
2025-07 2630840.05
2025-08 3141961.13
2025-09 3396992.69
2025-10 3080862.22
2025-11 3299606.54
2025-12 3292201.25
2026-01 3480115.84
2026-02 4016439.79
2026-03 3964361.64
2026-04 3873734.62
2026-05 3338807.19
2026-06 4111652.01
2026-07 3042097.84
2026-08 3313326.08
2026-09 3543361.98

--Q5. Return value as a percentage of gross sales, by region.
--gross sales = sum of net_value on normal invoices (is_return = 0)
--return value = sum of net_value on credit notes (is_return = 1)
SELECT
region,
ROUND(-SUM(CASE WHEN is_return = 1 THEN net_value ELSE 0 END), 2) AS return_value,
ROUND(SUM(CASE WHEN is_return = 0 THEN net_value ELSE 0 END), 2) AS gross_sales,
ROUND(100.0 \* -SUM(CASE WHEN is_return = 1 THEN net_value ELSE 0 END) /
SUM(CASE WHEN is_return = 0 THEN net_value ELSE 0 END), 2) AS return_pct
FROM sales
GROUP BY region
ORDER BY return_pct DESC
region return_value gross_sales return_pct
North 69176.65 14690670.76 0.47
South 53330.04 15710450.67 0.34
East 30055.10 12009505.74 0.25
West 35941.07 18762427.93 0.19

--Q6. The 3 distributors with the highest return value.
SELECT
dist_code,
distributor_name,
ROUND(-SUM(net_value), 2) AS return_value,
COUNT(\*) AS credit_notes
FROM sales
WHERE is_return = 1
GROUP BY dist_code, distributor_name
ORDER BY return_value DESC
LIMIT 3
dist_code distributor_name return_value credit_notes
D006 Amritsar Distributors 27752.27 8
D009 Chennai Traders 16601.31 5
D003 Lucknow Enterprises 13941.70 6
