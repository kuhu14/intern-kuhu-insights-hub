"""create view v_sales_denorm

Revision ID: 0003
Revises: 0002
Create Date: 2026-11-27

One row per sale with the names joined back in from the master tables. Its
columns match the Week 3 API's SaleItem (and the Week 2 clean CSV), so the
Postgres repository can read it the same way the file repository read the CSV.

Alembic autogenerate does not track views, so this migration is hand-written.
"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

CREATE_VIEW = """
CREATE VIEW v_sales_denorm AS
SELECT
    s.sale_id,
    s.invoice_no,
    s.invoice_date,
    r.region_name      AS region,
    st.state_name      AS state,
    d.distributor_code AS dist_code,
    d.distributor_name,
    k.sku_code,
    k.sku_name,
    b.brand_name       AS brand,
    s.channel,
    s.quantity         AS qty,
    s.net_value,
    s.is_return
FROM sales s
JOIN distributors d ON d.distributor_id = s.distributor_id
JOIN states st      ON st.state_id      = d.state_id
JOIN regions r      ON r.region_id      = st.region_id
JOIN skus k         ON k.sku_id         = s.sku_id
JOIN brands b       ON b.brand_id       = k.brand_id
"""


def upgrade() -> None:
    op.execute(CREATE_VIEW)


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS v_sales_denorm")
