"""SQLAlchemy models for the Week 4 Postgres schema (see docs/erd.md).

A column typed Mapped[X] is NOT NULL; Mapped[X | None] would allow NULL.
Money uses Numeric (exact decimals), never Float.
"""

from datetime import date
from decimal import Decimal

from sqlalchemy import BigInteger, CheckConstraint, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Region(Base):
    __tablename__ = "regions"

    region_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    region_name: Mapped[str] = mapped_column(String(50), unique=True)

    states: Mapped[list["State"]] = relationship(back_populates="region")


class State(Base):
    __tablename__ = "states"

    state_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    state_name: Mapped[str] = mapped_column(String(50), unique=True)
    region_id: Mapped[int] = mapped_column(ForeignKey("regions.region_id"))

    region: Mapped[Region] = relationship(back_populates="states")
    distributors: Mapped[list["Distributor"]] = relationship(back_populates="state")


class Distributor(Base):
    __tablename__ = "distributors"

    # The number in the code: D007 -> 7.
    distributor_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    distributor_code: Mapped[str] = mapped_column(String(10), unique=True)
    distributor_name: Mapped[str] = mapped_column(String(100))
    state_id: Mapped[int] = mapped_column(ForeignKey("states.state_id"))
    city: Mapped[str] = mapped_column(String(50))

    state: Mapped[State] = relationship(back_populates="distributors")
    sales: Mapped[list["Sale"]] = relationship(back_populates="distributor")


class Brand(Base):
    __tablename__ = "brands"

    brand_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    brand_name: Mapped[str] = mapped_column(String(50), unique=True)

    skus: Mapped[list["Sku"]] = relationship(back_populates="brand")


class Sku(Base):
    __tablename__ = "skus"

    sku_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    sku_code: Mapped[str] = mapped_column(String(20), unique=True)
    sku_name: Mapped[str] = mapped_column(String(100))
    brand_id: Mapped[int] = mapped_column(ForeignKey("brands.brand_id"))
    category: Mapped[str] = mapped_column(String(50))
    pack_size: Mapped[str] = mapped_column(String(20))
    mrp: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    brand: Mapped[Brand] = relationship(back_populates="skus")
    sales: Mapped[list["Sale"]] = relationship(back_populates="sku")


class Sale(Base):
    __tablename__ = "sales"
    __table_args__ = (
        # Returns must have a negative quantity, normal sales a positive one.
        CheckConstraint(
            "(is_return AND quantity < 0) OR (NOT is_return AND quantity > 0)",
            name="return_quantity_sign",
        ),
    )

    sale_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    invoice_no: Mapped[str] = mapped_column(String(30), unique=True)
        # index=True: indexes added in migration 0002_add_indexes.
    invoice_date: Mapped[date] = mapped_column(index=True)
    distributor_id: Mapped[int] = mapped_column(
        ForeignKey("distributors.distributor_id"), index=True
    )
    sku_id: Mapped[int] = mapped_column(ForeignKey("skus.sku_id"), index=True)
    channel: Mapped[str] = mapped_column(String(20))
    quantity: Mapped[int]
    net_value: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    is_return: Mapped[bool]

    distributor: Mapped[Distributor] = relationship(back_populates="sales")
    sku: Mapped[Sku] = relationship(back_populates="sales")
