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

**Distinct values:**

Region : 24

Channel : 3

Dist Code : 25

**5 problems found:**

Duplicate `Invoice No` rows : 60

Region distinct values: 24 intead of 4 (N, north, EAST...)

Dates in 3 mixed formats

Test rows for `D999` : 6

Rows with negative `Qty`: 91 (79 are valide credit notes, 12 are errors)

Rows with `Qty` over 1000: 14

Net Value stored as rupee text: 244(₹17,022)

Date range: 2025-04-01 to 2026-09-28

Unparsed dates: 0
