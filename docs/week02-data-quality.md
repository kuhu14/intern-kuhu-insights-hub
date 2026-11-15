# Week 2 – Data-quality report

**Input:** `datasets/week02/week02_secondary_sales_raw.xlsx`, sheet `Raw Data`: 5,564 rows, 12 columns (Apr 2025 – Sep 2026).
**Output:** `data_pipeline/output/clean_sales.csv` (5,418 rows) and `data_pipeline/output/rejects.csv` (80 rows).
**Script:** `python data_pipeline/clean_sales.py`. The raw file was never edited by hand.

## Row flow

| Step                                   | Rows left | Change |
| -------------------------------------- | --------: | -----: |
| Raw file                               |     5,564 |        |
| Rule 1 – remove duplicate invoices     |     5,504 |    −60 |
| Rule 2 – remove test distributor D999  |     5,498 |     −6 |
| Rule 7 – move rejects to `rejects.csv` |     5,418 |    −80 |

## What was wrong, and how many rows each rule affected

| Rule                 | Problem found                                      |                                                                             Rows affected | Fix                                                     |
| -------------------- | -------------------------------------------------- | ----------------------------------------------------------------------------------------: | ------------------------------------------------------- |
| 1 – Duplicates       | Same `Invoice No` appeared twice                   |                                                                                60 removed | Kept the first copy                                     |
| 2 – Test rows        | Distributor `D999` (TEST DIST)                     |                                                                                 6 removed | Dropped                                                 |
| 3 – Region           | 24 spellings instead of 4 (`N`, ` north`, `EAST`…) |                                                                               1,387 fixed | Trimmed, lower-cased, mapped to North/South/East/West   |
| 4 – Dates            | 3 text formats mixed with real Excel dates         | 5,498 parsed (2,238 Excel dates, 1,643 `dd/mm/yyyy`, 1,051 `yyyy-mm-dd`, 566 `dd-Mon-yy`) | Parsed each format separately; `/` dates read day-first |
| 5 – Numbers and text | Net Value stored as text like `₹12,345.60`         |                                                                             240 converted | Removed `₹` and `,`, converted to number                |
| 5 – Numbers and text | SKU Code with spaces or lower case                 |                                                                                 204 fixed | Trimmed and upper-cased                                 |
| 5 – Numbers and text | Distributor Name with spaces or ALL CAPS           |                                                                                 267 fixed | Trimmed and title-cased; now one name per Dist Code     |
| 6 – Credit notes     | `CN` invoices have negative Qty and Net Value      |                                                                                   78 kept | Kept as valid returns; added `is_return = true`         |
| 7 – Rejects          | Rows that can't be trusted                         |                                                                                  80 moved | See below                                               |

**Rejects (80):** `blank_qty` 35 · `blank_net_value` 25 · `negative_qty_not_credit_note` 12 · `qty_over_1000` 8

The counts for Rules 3–7 are taken after duplicates and test rows were removed, so they differ slightly from the raw profile (e.g. 244 rupee-text values in the raw file, 240 after de-duplication).

## Checks on the output

- `invoice_no` is unique; no `D999` rows remain.
- Region has only North, South, East, West; every date is a real date; Qty and Net Value are numbers.
- Total net value = **60,984,552.24**; total quantity = **568,254**.
- Running the script twice produces byte-for-byte identical files.
- 14 pytest tests pass (`python -m pytest data_pipeline -v`).

## Judgement calls

1. **Order of steps.** Duplicates and test rows are removed _before_ rejects are split. Doing it the other way round would push duplicate copies and test records into `rejects.csv` and inflate the counts (e.g. 14 rows have Qty over 1000 in the raw file, but 6 of them are D999 test rows, so only 8 are real rejects).
2. **Which duplicate to keep.** Kept the first. Every duplicate pair was an exact copy in all 12 columns, so no information was lost.
3. **One reason per reject.** A row is given the first reason it matches, in this order: `blank_qty` → `blank_net_value` → `negative_qty_not_credit_note` → `qty_over_1000`. This keeps the counts adding up to 80.
4. **Rejects are not fixed.** For example, Qty over 1000 might be a typo, but I didn't guess the correct value. These rows are kept in `rejects.csv` so someone can follow them up with the distributor.
5. **Distributor names.** Used title case (`JODHPUR AGENCIES` → `Jodhpur Agencies`), which matches how the other rows are written. Checked afterwards that every Dist Code has exactly one name.
6. **Unknown regions fail loudly.** A region not in the 4-value map stops the script with an error instead of passing through silently.
7. **Two-digit years.** `dd-Mon-yy` dates are read as 20xx (e.g. `10-Jul-25` → 2025-07-10). All dates fall within Apr 2025 – Sep 2026, matching the README.
8. **Column names.** Renamed to snake_case (`Invoice No` → `invoice_no`, `Net Value (INR)` → `net_value`) so they are easier to use in SQL.
9. **Gross sales for the return % query (Q5).** Gross sales = normal invoices only; return value = credit notes made positive.
10. **Large-file limit.** Raised the pre-commit file-size limit from 500 KB to 1 MB so `clean_sales.csv` (764 KB) could be committed, as the assignment requires.
