Shape: (5564, 12)
**Column types worth noting:**
Invoice No str
Invoice Date object
Region str
State str
Dist Code str
Distributor Name str
SKU Code str
SKU Name str
Brand str
Channel str
Qty float64
Net Value (INR) object
dtype: object
**Nulls per column:**
Invoice No 0
Invoice Date 0
Region 0
State 0
Dist Code 0
Distributor Name 0
SKU Code 0
SKU Name 0
Brand 0
Channel 0
Qty 35
Net Value (INR) 25
dtype: int64
**Distinct values:**
Region : 24
Channel : 3
Dist COde : 25
_Region:_
South 1064
East 1053
West 1031
North 1008
north 86
East 79
WEST 75
East 75
West 75
SOUTH 74
South 74
West 74
W 73
east 71
E 71
S 69
south 69
North 68
N 68
west 64
South 62
NORTH 61
North 60
EAST 60
Name: count, dtype: int64
**Date range:**
0 2026-06-26 00:00:00
1 2026-09-28
2 15/07/2026
3 2026-09-06 00:00:00
4 2026-04-09 00:00:00
5 2025-05-25 00:00:00
6 2026-02-01 00:00:00
7 10-Jul-25
8 2025-10-09
9 16-Sep-26
10 2025-12-31 00:00:00
11 18/07/2026
12 22/01/2026
13 2025-05-26 00:00:00
14 2026-02-16
15 2025-05-22 00:00:00
16 14/07/2025
17 10/11/2025
18 03/12/2025
19 24/05/2026
Name: Invoice Date, dtype: object
Duplicate `Invoice No` rows : 60
Test rows for `D999` : 6
Rows with neagtive `Qty`: 91
Rows with `Qty` over 1000: 14
Net Value stored as rupee text: 244
1 ₹17,022.59
17 ₹16,555.19
24 ₹18,167.31
27 ₹7,693.87
78 ₹15,571.64
108 ₹26,350.19
159 ₹5,011.78
179 ₹4,295.07
231 ₹11,998.75
321 ₹7,784.15
352 ₹16,478.31
377 ₹8,520.26
381 ₹10,478.08
393 ₹4,432.47
418 ₹10,944.31
421 ₹7,768.20
426 ₹12,307.06
432 ₹14,660.35
435 ₹6,065.54
440 ₹10,424.58
Name: Net Value (INR), dtype: object
Date range: 2025-04-01 to 2026-09-28
Unpared dates: 0
