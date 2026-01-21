import pandas as pd

# input parquet file
parquet_file = "train-00000-of-00001-25f40520d4548308.parquet"

# output csv file
csv_file = "lex_fridman_full.csv"

# read parquet
df = pd.read_parquet(parquet_file)

# write csv (no changes, all columns preserved)
df.to_csv(csv_file, index=False)

print("Saved CSV to:", csv_file)
