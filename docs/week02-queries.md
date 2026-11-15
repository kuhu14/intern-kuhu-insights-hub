# Week 2 – SQL queries on clean sales

**Data:** `data_pipeline/output/clean_sales.csv` loaded into SQLite as table `sales` (5,418 rows).
**Queries:** `data_pipeline/queries.sql`
**Run:** `python data_pipeline/run_queries.py` (rebuilds `data_pipeline/output/sales.db` and prints every result)

`is_return` is 1 for credit notes (returns) and 0 for normal sales. Credit notes carry negative `qty` and `net_value`, so a plain `SUM` gives sales **net of returns**.

---

## Q1. Total net value and total quantity

```sql
SELECT ROUND(SUM(net_value), 2) AS total_net_value,
       SUM(qty)                 AS total_qty
FROM sales;
```

| total_net_value | total_qty |
|---:|---:|
| 60,984,552.24 | 568,254 |

**Explanation:** Both numbers match the acceptance targets exactly, which confirms the cleaning kept the right rows. They are net of returns, because the 78 credit notes are included with negative values.

---

## Q2. Net value by region, with percentage share

```sql
SELECT region,
       ROUND(SUM(net_value), 2) AS net_value,
       ROUND(100.0 * SUM(net_value) / (SELECT SUM(net_value) FROM sales), 2) AS pct_share
FROM sales
GROUP BY region
ORDER BY net_value DESC;
```

| region | net_value | pct_share |
|---|---:|---:|
| West | 18,726,486.86 | 30.71 |
| South | 15,657,120.63 | 25.67 |
| North | 14,621,494.11 | 23.98 |
| East | 11,979,450.64 | 19.64 |

**Explanation:** The sub-query gives the grand total, so each region's share is its net value divided by that total. The shares add up to 100%. West is the largest region (about 31%) and East the smallest (about 20%). Only the four standard regions appear, which confirms Rule 3 worked.

---

## Q3. Top 5 SKUs by net value

```sql
SELECT sku_code, sku_name,
       ROUND(SUM(net_value), 2) AS net_value
FROM sales
GROUP BY sku_code, sku_name
ORDER BY net_value DESC
LIMIT 5;
```

| sku_code | sku_name | net_value |
|---|---|---:|
| EM-1007 | Kesh King Ayurvedic Oil 200 ml | 3,956,206.23 |
| EM-1018 | Dermicool Prickly Heat Powder 300 g | 3,527,485.97 |
| EM-1009 | BoroPlus Antiseptic Cream 40 ml | 3,280,513.22 |
| EM-1023 | He Deodorant 150 ml | 3,109,241.46 |
| EM-1016 | Zandu Chyawanprash 900 g | 3,014,871.09 |

**Explanation:** Kesh King oil is the top seller. Together, these 5 SKUs make up about 27.7% of total net value. Grouping by `sku_code` works only because Rule 5 trimmed and upper-cased the codes; otherwise `em-1007` and `EM-1007 ` would be counted as separate SKUs.

---

## Q4. Monthly net value trend

```sql
SELECT strftime('%Y-%m', invoice_date) AS month,
       ROUND(SUM(net_value), 2)        AS net_value
FROM sales
GROUP BY month
ORDER BY month;
```

| month | net_value |
|---|---:|
| 2025-04 | 3,158,293.16 |
| 2025-05 | 2,775,995.85 |
| 2025-06 | 3,523,902.36 |
| 2025-07 | 2,630,840.05 |
| 2025-08 | 3,141,961.13 |
| 2025-09 | 3,396,992.69 |
| 2025-10 | 3,080,862.22 |
| 2025-11 | 3,299,606.54 |
| 2025-12 | 3,292,201.25 |
| 2026-01 | 3,480,115.84 |
| 2026-02 | 4,016,439.79 |
| 2026-03 | 3,964,361.64 |
| 2026-04 | 3,873,734.62 |
| 2026-05 | 3,338,807.19 |
| 2026-06 | 4,111,652.01 |
| 2026-07 | 3,042,097.84 |
| 2026-08 | 3,313,326.08 |
| 2026-09 | 3,543,361.98 |

**Explanation:** All 18 months from April 2025 to September 2026 appear with no gaps, which confirms every date was parsed (Rule 4). The highest month is June 2026 (4.11M) and the lowest is July 2025 (2.63M). Feb–Jun 2026 runs higher than the same months in 2025.

---

## Q5. Return value as a percentage of gross sales, by region

```sql
SELECT region,
       ROUND(-SUM(CASE WHEN is_return = 1 THEN net_value ELSE 0 END), 2) AS return_value,
       ROUND(SUM(CASE WHEN is_return = 0 THEN net_value ELSE 0 END), 2)  AS gross_sales,
       ROUND(100.0 * -SUM(CASE WHEN is_return = 1 THEN net_value ELSE 0 END)
                   / SUM(CASE WHEN is_return = 0 THEN net_value ELSE 0 END), 2) AS return_pct
FROM sales
GROUP BY region
ORDER BY return_pct DESC;
```

| region | return_value | gross_sales | return_pct |
|---|---:|---:|---:|
| North | 69,176.65 | 14,690,670.76 | 0.47 |
| South | 53,330.04 | 15,710,450.67 | 0.34 |
| East | 30,055.10 | 12,009,505.74 | 0.25 |
| West | 35,941.07 | 18,762,427.93 | 0.19 |

**Definition (judgement call):** *gross sales* = total `net_value` of normal invoices (`is_return = 0`); *return value* = total `net_value` of credit notes, made positive. Gross sales minus return value gives back the Q1 total (61,173,055.10 − 188,502.86 = 60,984,552.24).

**Explanation:** Returns are small overall (about 0.31% of gross sales). North has the highest return rate, at 0.47%. West has the lowest rate (0.19%), even though it is the biggest region by sales.

---

## Q6. The 3 distributors with the highest return value

```sql
SELECT dist_code, distributor_name,
       ROUND(-SUM(net_value), 2) AS return_value,
       COUNT(*)                  AS credit_notes
FROM sales
WHERE is_return = 1
GROUP BY dist_code, distributor_name
ORDER BY return_value DESC
LIMIT 3;
```

| dist_code | distributor_name | return_value | credit_notes |
|---|---|---:|---:|
| D006 | Amritsar Distributors | 27,752.27 | 8 |
| D009 | Chennai Traders | 16,601.31 | 5 |
| D003 | Lucknow Enterprises | 13,941.70 | 6 |

**Explanation:** Only credit-note rows are used, and their value is made positive. Amritsar Distributors has the most returns by a wide margin. Amritsar (D006) and Lucknow (D003) are both in North, which helps explain why North has the highest return rate in Q5. These 3 distributors account for about 31% of all return value. Grouping by both code and name works because Rule 5 made each distributor's name consistent.
