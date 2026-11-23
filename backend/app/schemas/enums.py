from enum import StrEnum


class Region(StrEnum):
    EAST = "East"
    NORTH = "North"
    SOUTH = "South"
    WEST = "West"


class Channel(StrEnum):
    CHEMIST = "Chemist"
    GENERAL_TRADE = "General Trade"
    MODERN_TRADE = "Modern Trade"


class GroupBy(StrEnum):
    REGION = "region"
    STATE = "state"
    BRAND = "brand"
    SKU = "sku"
    CHANNEL = "channel"
    MONTH = "month"
