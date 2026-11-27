# Week 4 – Database ERD

Postgres schema for the Insights Hub. Five master (dimension) tables, seeded from
`week04_masters.xlsx`, and one fact table, `sales`, loaded from
`data_pipeline/output/clean_sales.csv`.

```mermaid
erDiagram
    regions ||--o{ states : "contains"
    states ||--o{ distributors : "contains"
    brands ||--o{ skus : "owns"
    distributors ||--o{ sales : "bills"
    skus ||--o{ sales : "sold as"

    regions {
        int region_id PK
        varchar region_name UK "NOT NULL"
    }

    states {
        int state_id PK
        varchar state_name UK "NOT NULL"
        int region_id FK "NOT NULL"
    }

    distributors {
        int distributor_id PK "number in the code, D007 -> 7"
        varchar distributor_code UK "NOT NULL, D001 to D024"
        varchar distributor_name "NOT NULL"
        int state_id FK "NOT NULL"
        varchar city "NOT NULL"
    }

    brands {
        int brand_id PK
        varchar brand_name UK "NOT NULL"
    }

    skus {
        int sku_id PK
        varchar sku_code UK "NOT NULL, EM-1001 to EM-1023"
        varchar sku_name "NOT NULL"
        int brand_id FK "NOT NULL"
        varchar category "NOT NULL"
        varchar pack_size "NOT NULL, e.g. 200 ml"
        numeric mrp "NOT NULL, NUMERIC(10,2)"
    }

    sales {
        bigint sale_id PK
        varchar invoice_no UK "NOT NULL"
        date invoice_date "NOT NULL"
        int distributor_id FK "NOT NULL"
        int sku_id FK "NOT NULL"
        varchar channel "NOT NULL"
        int quantity "NOT NULL"
        numeric net_value "NOT NULL, NUMERIC(12,2)"
        boolean is_return "NOT NULL"
    }
```

## How to read it

- `||--o{` means **one to many**: one region has many states, one SKU appears on many sales.
- **PK** = primary key, **FK** = foreign key, **UK** = unique (the natural key the seed
  script upserts on).

## Relationships

| From (many)             | To (one)                      | Meaning                          |
| ----------------------- | ----------------------------- | -------------------------------- |
| `states.region_id`      | `regions.region_id`           | each state belongs to one region |
| `distributors.state_id` | `states.state_id`             | each distributor is in one state |
| `skus.brand_id`         | `brands.brand_id`             | each SKU belongs to one brand    |
| `sales.distributor_id`  | `distributors.distributor_id` | who billed the sale              |
| `sales.sku_id`          | `skus.sku_id`                 | which product was sold           |

## Rules the schema enforces

- **Money is NUMERIC, never float**: `skus.mrp` is `NUMERIC(10,2)`, `sales.net_value` is
  `NUMERIC(12,2)`.
- **Returns check**: `CHECK ((is_return AND quantity < 0) OR (NOT is_return AND quantity > 0))`.
  A return must have a negative quantity; a normal sale must have a positive one.
- **Foreign keys** stop a sale from pointing to a distributor or SKU that does not exist.
- **Load order** (parents before children): regions → states → distributors → brands → skus → sales.

## What is not stored on `sales`

Region, state, distributor name, SKU name and brand are **not** columns on `sales`.
They come back through joins in the view `v_sales_denorm`, which returns the same shape
as the Week 3 API.
