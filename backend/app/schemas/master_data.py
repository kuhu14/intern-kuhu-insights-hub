from typing import Literal

from pydantic import BaseModel

from app.schemas.enums import Region


class HealthResponse(BaseModel):
    status: Literal["ok"]


class Sku(BaseModel):
    sku_code: str
    sku_name: str
    brand: str


class Distributor(BaseModel):
    dist_code: str
    distributor_name: str
    region: Region
    state: str
