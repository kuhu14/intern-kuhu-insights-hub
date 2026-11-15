--Table: sales (loaded from data_pipeline/output/clean_sales.csv)
--is_return is 1 for credit notes (returns), 0 for normal sales

--Q1. Total net value and total quantity
SELECT
    ROUND(SUM(net_value), 2) AS total_net_value,
    SUM(qty) AS total_qty
FROM sales;

--Q2. Net value by region, with percentage share.
SELECT
    region,
    ROUND(SUM(net_value), 2) AS net_value,
    ROUND(100.0 * SUM(net_value) / (SELECT SUM(net_value) FROM sales), 2) AS pct_share
FROM sales
GROUP BY region
ORDER BY net_value DESC;

--Q3. Top 5 SKUs by net value.
SELECT
    sku_code,
    sku_name,
    ROUND(SUM(net_value), 2) AS net_value
FROM sales
GROUP BY sku_code, sku_name
ORDER BY net_value DESC
LIMIT 5;

--Q4. Monthly net value trend.
SELECT
    strftime('%Y-%m', invoice_date) AS month,
    ROUND(SUM(net_value), 2) AS net_value
FROM sales
GROUP BY month
ORDER BY month;

--Q5. Return value as a percentage of gross sales, by region.
--gross sales = sum of net_value on normal invoices (is_return = 0)
--return value = sum of net_value on credit notes (is_return = 1)
SELECT
    region,
    ROUND(-SUM(CASE WHEN is_return = 1 THEN net_value ELSE 0 END), 2) AS return_value,
    ROUND(SUM(CASE WHEN is_return = 0 THEN net_value ELSE 0 END), 2) AS gross_sales,
    ROUND(100.0 * -SUM(CASE WHEN is_return = 1 THEN net_value ELSE 0 END) /
          SUM(CASE WHEN is_return = 0 THEN net_value ELSE 0 END), 2) AS return_pct
FROM sales
GROUP BY region
ORDER BY return_pct DESC;

--Q6. The 3 distributors with the highest return value.
SELECT
    dist_code,
    distributor_name,
    ROUND(-SUM(net_value), 2) AS return_value,
    COUNT(*) AS credit_notes
FROM sales
WHERE is_return = 1
GROUP BY dist_code, distributor_name
ORDER BY return_value DESC
LIMIT 3;
