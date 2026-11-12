"""Reads the sales data from an Excel file, cleans it, and saves the cleaned data to a new Excel file."""
from datetime import datetime
from pathlib import Path
import pandas as pd

HERE = Path(__file__).resolve().parent
RAW_PATH = HERE.parent / "datasets" / "week02" / "week02_secondary_sales_raw.xlsx"
OUTPUT_DIR = HERE / "output"

REGION_MAP ={
    "n" : "North",
    "north" : "North",
    "s" : "South",
    "south" : "South",
    "e" : "East",
    "east" : "East",
    "w" : "West",
    "west" : "West"
}

COLUMNS_NAMES = {
    "Invoice No" : "invoice_no",
    "Invoice Date" : "invoice_date",
    "Region" : "region",
    "State" : "state",
    "Dist Code" : "dist_code",
    "Distributor Name" : "distributor_name",
    "SKU Code" : "sku_code",
    "SKU Name" : "sku_name",
    "Brand" : "brand",
    "Channel" : "channel",
    "Qty" : "qty",
    "Net Value (INR)" : "net_value",
}

def load_raw(path):
    """Read the 'Raw Data' sheet from the Excel file and return it as a DataFrame."""
    return pd.read_excel(path, sheet_name="Raw Data")

def remove_duplicates(df):
    """Rule 1:
Rows with the same Invoice No are duplicates. Keep one."""
    return df.drop_duplicates(subset="Invoice No", keep="first")

def remove_test_rows(df):
    """Rule 2: Rows for distributor code D999 (TEST DIST) are test records. Remove them."""
    return df[df["Dist Code"].str.strip() != "D999"]

def normalise_region(value):
    """Rule 3: Normalise Region to exactly: North, South, East, West (fix case, spaces, one-letter codes)."""
    return REGION_MAP[str(value).strip().lower()]

def parse_date(value):
    """Rule 4: Parse all dates to a real date. Text dates containing '/' are dd/mm/yyyy (day first). Other formats: yyyy-mm-dd and dd-Mon-yy."""
    if isinstance(value, datetime):
        return value.date()
    text = str(value).strip()
    if "/" in text:
        return datetime.strptime(text, "%d/%m/%Y").date()
    if any(ch.isalpha() for ch in text):
        return datetime.strptime(text, "%d-%b-%y").date()
    return datetime.strptime(text, "%Y-%m-%d").date()

def parse_amount(value):
    """Rule 5: Net Value may be text such as '₹12,345.60'. Convert to a number. Trim and upper-case SKU Code. Trim Distributor Name and use title-style as in the other rows of the same Dist Code."""
    if pd.isna(value):
        return float("nan")
    text = str(value).strip().replace("₹", "").replace(",", "")
    if text == "":
        return float("nan")
    return float(text)

def clean_text_columns(df):
    """Trim whitespace from all text columns."""
    df = df.copy()
    df["SKU Code"] = df["SKU Code"].str.strip().str.upper()
    df["Distributor Name"] = df["Distributor Name"].str.strip().str.title()
    return df

def clean_Columns(df):
    """Rename columns to standard names."""
    df = df.copy()
    df["Region"] = df["Region"].apply(normalise_region)
    df["Invoice Date"] = df["Invoice Date"].apply(parse_date)
    df["Net Value (INR)"] = df["Net Value (INR)"].apply(parse_amount)
    return clean_text_columns(df)

def add_is_return(df):
    """Rule 6: Invoice No starting with CN are credit notes (returns). Keep them. Negative Qty and Net Value are correct for CN rows. Add a boolean column is_return."""
    df = df.copy()
    df["is_return"] = df["Invoice No"].str.startswith("CN")
    return df

def reject_reason(row):
    """Rule 7: Move to a separate 'rejects' table (with a reason column) every row where: Qty or Net Value is blank; Qty is negative but Invoice No does not start with CN; Qty is greater than 1000."""
    qty = row["Qty"]
    if pd.isna(qty):
        return "blank_qty"
    if pd.isna(row["Net Value (INR)"]):
        return "blank_net_value"
    if qty < 0 and not row["is_return"]:
        return "negative_qty_not_credit_note"
    if qty > 1000:
        return "qty_over_1000"
    return None

def split_rejects(df):
    """Split the DataFrame into valid rows and rejected rows with reasons."""
    reasons = df.apply(reject_reason, axis=1)
    is_reject = reasons.notna()
    clean = df[~is_reject].copy()
    rejects = df[is_reject].copy()
    rejects["reason"] = reasons[is_reject]
    return clean, rejects

def main():
    raw = load_raw(RAW_PATH)
    df = remove_duplicates(raw)
    df = remove_test_rows(df)
    df = clean_Columns(df)
    df = add_is_return(df)
    clean, rejects = split_rejects(df)

    clean["Qty"] = clean["Qty"].astype(int)
    clean = clean.rename(columns=COLUMNS_NAMES)
    rejects = rejects.rename(columns=COLUMNS_NAMES)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    clean.to_csv(OUTPUT_DIR / "clean_sales.csv", index=False, lineterminator="\n")
    rejects.to_csv(OUTPUT_DIR / "rejects.csv", index=False, lineterminator="\n")

    print(f"Raw rows: {len(raw)}")
    print(f"Clean rows: {len(clean)}")
    print(f"Rejected rows: {len(rejects)}")
    print(rejects["reason"].value_counts().to_string())
    print(f"Total net value: {clean['net_value'].sum():,.2f}")
    print(f"Total quantity: {clean['qty'].sum():,}")
    print(f"Credit notes: {clean['is_return'].sum()}")

if __name__ == "__main__":
    main()
