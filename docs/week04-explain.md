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
 HashAggregate  (cost=153.28..157.74 rows=223 width=52) (actual time=0.773..0.775 rows=1 loops=1)
   Group Key: (date_trunc('month'::text, (invoice_date)::timestamp with time zone))::date
   Batches: 1  Memory Usage: 40kB
   Buffers: shared hit=67
   ->  Seq Scan on sales  (cost=0.00..150.41 rows=286 width=15) (actual time=0.043..0.669 rows=292 loops=1)
         Filter: ((invoice_date >= '2025-12-01'::date) AND (invoice_date < '2026-01-01'::date))
         Rows Removed by Filter: 5126
         Buffers: shared hit=67
 Planning:
   Buffers: shared hit=58
 Planning Time: 0.780 ms
 Execution Time: 0.917 ms
```

### After (with `ix_sales_invoice_date`)

```text
 HashAggregate  (cost=83.51..87.97 rows=223 width=52) (actual time=0.544..0.546 rows=1 loops=1)
   Group Key: (date_trunc('month'::text, (invoice_date)::timestamp with time zone))::date
   Batches: 1  Memory Usage: 40kB
   Buffers: shared hit=69
   ->  Bitmap Heap Scan on sales  (cost=7.21..80.65 rows=286 width=15) (actual time=0.121..0.410 rows=292 loops=1)
         Recheck Cond: ((invoice_date >= '2025-12-01'::date) AND (invoice_date < '2026-01-01'::date))
         Heap Blocks: exact=66
         Buffers: shared hit=69
         ->  Bitmap Index Scan on ix_sales_invoice_date  (cost=0.00..7.14 rows=286 width=0) (actual time=0.064..0.064 rows=292 loops=1)
               Index Cond: ((invoice_date >= '2025-12-01'::date) AND (invoice_date < '2026-01-01'::date))
               Buffers: shared hit=3
 Planning:
   Buffers: shared hit=62
 Planning Time: 1.007 ms
 Execution Time: 0.746 ms
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
 Sort  (cost=249.20..250.48 rows=511 width=52) (actual time=3.415..3.417 rows=18 loops=1)
   Sort Key: ((date_trunc('month'::text, (invoice_date)::timestamp with time zone))::date)
   Sort Method: quicksort  Memory: 25kB
   Buffers: shared hit=67
   ->  HashAggregate  (cost=215.99..226.22 rows=511 width=52) (actual time=3.378..3.387 rows=18 loops=1)
         Group Key: (date_trunc('month'::text, (invoice_date)::timestamp with time zone))::date
         Batches: 1  Memory Usage: 49kB
         Buffers: shared hit=67
         ->  Seq Scan on sales  (cost=0.00..161.81 rows=5418 width=15) (actual time=0.010..2.259 rows=5418 loops=1)
               Buffers: shared hit=67
 Planning Time: 0.076 ms
 Execution Time: 3.463 ms
```

### After

```text
 Sort  (cost=249.20..250.48 rows=511 width=52) (actual time=4.795..4.798 rows=18 loops=1)
   Sort Key: ((date_trunc('month'::text, (invoice_date)::timestamp with time zone))::date)
   Sort Method: quicksort  Memory: 25kB
   Buffers: shared hit=67
   ->  HashAggregate  (cost=215.99..226.22 rows=511 width=52) (actual time=4.741..4.753 rows=18 loops=1)
         Group Key: (date_trunc('month'::text, (invoice_date)::timestamp with time zone))::date
         Batches: 1  Memory Usage: 49kB
         Buffers: shared hit=67
         ->  Seq Scan on sales  (cost=0.00..161.81 rows=5418 width=15) (actual time=0.024..3.155 rows=5418 loops=1)
               Buffers: shared hit=67
 Planning Time: 0.363 ms
 Execution Time: 4.892 ms
```

## Summary

| Query         | Before                                 | After                                            | Index used?  |
| ------------- | -------------------------------------- | ------------------------------------------------ | ------------ |
| A: one month  | Seq Scan, cost 157.74, 0.917 ms        | Bitmap Index Scan, cost 87.97, 0.746 ms          | **Yes**      |
| B: all months | Seq Scan, cost 250.48, 3.463 ms        | Seq Scan, cost 250.48, 4.892 ms                  | No (correct) |

**Query A uses the index.** Before, Postgres read every row and threw away 5,126 of them
(`Rows Removed by Filter`). After, the Bitmap Index Scan on `ix_sales_invoice_date` finds
only the 292 December rows (3 index pages), and the planner's estimated cost falls from
157.74 to 87.97, about 45% lower.

**Query B does not use the index, and that is the right choice.** It needs every row in
the table. Reading the whole table straight through (Seq Scan) is cheaper than looking up
each row through an index first, so the planner ignores the index.

**Honest note on timings.** With only 5,418 rows (67 pages of 8 KB) the whole table sits in
memory, so both versions finish in about 1 ms and the timing difference is noise. The
benefit shows in the plan and the cost estimate now, and grows with the table: at
millions of rows a one-month query reads a small slice instead of the whole table.
