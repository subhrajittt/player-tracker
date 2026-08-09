import pandas as pd

df = pd.read_csv("data/raw/players_2024-25_full.csv")

print(f"Shape: {df.shape}")
print(f"\nColumns:\n{list(df.columns)}")
print(f"\nSample rows:\n{df.head()}")
print(f"\nPositions: {df['Pos'].unique()}")
print(f"\nLeagues (Comp column): {df['Comp'].unique()}")