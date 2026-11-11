from pandas import pd
df = pd.read_excel("datasets/week02/week02_secondary_sales_raw.xlsx", sheet_name="Raw Data")
df.shape #shape
df.dtypes #data types
df.isna().sum() #missing values
df.nunique() #unique values
df.value_counts() #value counts
