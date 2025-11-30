import pandas as pd
import os

data_dir = "data"
files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]

for file in files:
    print(f"--- {file} ---")
    try:
        df = pd.read_csv(os.path.join(data_dir, file))
        print(df.head())
        print(df.info())
        print("\n")
    except Exception as e:
        print(f"Error reading {file}: {e}")
