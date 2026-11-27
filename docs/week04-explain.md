# Week 4 – EXPLAIN ANALYZE: sales indexes

Migration `0002_add_indexes` adds three B-tree indexes:

| Index                     | Column                 | Helps                                  |
| ------------------------- | ---------------------- | -------------------------------------- |
| `ix_sales_invoice_date`   | `sales.invoice_date`   | date-range filters (monthly summaries) |
| `ix_sales_distributor_id` | `sales.distributor_id` | joins to distributors, region filters  |
| `ix_sales_sku_id`         | `sales.sku_id`         | joins to skus, brand/SKU filters       |

Postgres creates indexes for primary keys and UNIQUE columns automatically, but not for
foreign keys or ordinary filter columns, so these had to be added.

**How measured:** PostgreSQL 16, `sales` seeded with 5,418 rows, `ANALYZE sales` run first,
queries in [`week04-explain.sql`](week04-explain.sql). "Before" is at migration `0001`,
"after" at `0002`. The "after" plans are from a second run so the index is in memory.

## Query A – monthly summary for one month (December 2025)

```sql
SELECT date_trunc('month', invoice_date)::date AS month,
       SUM(net_value), SUM(quantity), COUNT(*)
FROM sales
WHERE invoice_date >= DATE '2025-12-01' AND invoice_date < DATE '2026-01-01'
GROUP BY 1;
```

### Before (no index)

```text
PASTE QUERY A PLAN FROM STEP 2 HERE
```

### After (with `ix_sales_invoice_date`)

```text
PASTE QUERY A PLAN FROM STEP 6 HERE
```

## Query B – monthly summary over all months

```sql
SELECT date_trunc('month', invoice_date)::date AS month,
       SUM(net_value), SUM(quantity), COUNT(*)
FROM sales
GROUP BY 1
ORDER BY 1;
```

### Before

```text
PASTE QUERY B PLAN FROM STEP 2 HERE
```

### After

```text
PASTE QUERY B PLAN FROM STEP 6 HERE
```

## Summary

| Query         | Before                        | After                                 | Index used?  |
| ------------- | ----------------------------- | ------------------------------------- | ------------ |
| A: one month  | Seq Scan, total cost [157.74] | Bitmap Index Scan, total cost [87.97] | **Yes**      |
| B: all months | Seq Scan, total cost [250.48] | Seq Scan, total cost [250.48]         | No (correct) |

**Query A uses the index.** Before, Postgres read every row and threw away 5,126 of them
(`Rows Removed by Filter`). After, the Bitmap Index Scan on `ix_sales_invoice_date` finds
only the 292 December rows, and the planner's estimated cost falls by about 45%.

**Query B does not use the index, and that is the right choice.** It needs every row in
the table. Reading the whole table straight through (Seq Scan) is cheaper than looking up
each row through an index first, so the planner ignores the index.

**Honest note on timings.** With only 5,418 rows (67 pages of 8 KB) the whole table sits in
memory, so both versions finish in about 1 ms and the timing difference is noise. The
benefit shows in the plan and the cost estimate now, and grows with the table: at
millions of rows a one-month query reads a small slice instead of the whole table.
