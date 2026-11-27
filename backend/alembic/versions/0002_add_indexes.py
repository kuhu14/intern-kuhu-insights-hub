"""add indexes on sales(invoice_date), sales(distributor_id), sales(sku_id)

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-27

Postgres indexes primary keys and UNIQUE columns automatically, but not foreign
keys or filter columns. These three back the date-range filter and the joins to
distributors and skus. Evidence: docs/week04-explain.md.
"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_index(op.f("ix_sales_invoice_date"), "sales", ["invoice_date"])
    op.create_index(op.f("ix_sales_distributor_id"), "sales", ["distributor_id"])
    op.create_index(op.f("ix_sales_sku_id"), "sales", ["sku_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_sales_sku_id"), table_name="sales")
    op.drop_index(op.f("ix_sales_distributor_id"), table_name="sales")
    op.drop_index(op.f("ix_sales_invoice_date"), table_name="sales")
