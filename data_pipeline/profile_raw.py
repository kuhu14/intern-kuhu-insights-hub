import pandas as pd
df = pd.read_excel("datasets/week02/week02_secondary_sales_raw.xlsx", sheet_name="Raw Data")
print(df.shape) #shape
print(df.dtypes) #data types
print(df.isna().sum()) #missing values
print(df["Region"].nunique()) #unique values
print(df["Channel"].nunique()) #unique values
print(df["Dist Code"].nunique()) #unique values
print(df["Region"].value_counts()) #value counts
print(df["Invoice Date"].head(20))
print(df["Invoice No"].duplicated().sum()) #duplicate values
print((df["Dist Code"]=="D999").sum())
print((df["Qty"]<0).sum()) #negative values
print((df["Qty"]>1000).sum()) #outliers
net_text = df["Net Value (INR)"].astype(str).str.contains("₹")
print("Net Value stored as rupee text:",net_text.sum()) #non-numeric values
print(df.loc[net_text, "Net Value (INR)"].head(20)) #non-numeric values
raw=df["Invoice Date"].astype(str).str.strip()
dates = pd.to_datetime(raw, format="%d/%m/%Y", errors="coerce")
dates=dates.fillna(pd.to_datetime(raw, format="%d-%b-%y", errors="coerce"))
dates=dates.fillna(pd.to_datetime(raw, format="ISO8601", errors="coerce"))
print("Date range:",dates.min().date(), "to", dates.max().date())
print("Unparsed dates:",dates.isna().sum())
