import pandas as pd

MIN_MINUTES = 900  # roughly 10 full matches, filters out small-sample noise

# raw counting stats that should be converted to per-90 rates for fair comparison
PER90_STATS = [
    'Gls', 'Ast', 'G+A', 'G-PK', 'xG', 'npxG', 'xAG', 'npxG+xAG', 'xG+xAG',
    'Sh', 'SoT', 'Cmp', 'Att', 'TotDist', 'PrgDist', 'xA', 'KP', '1/3', 'PPA',
    'CrsPA', 'Crs', 'CK', 'TB', 'Sw', 'PrgP', 'Tkl', 'TklW', 'Def 3rd', 'Mid 3rd',
    'Att 3rd', 'Int', 'Tkl+Int', 'Clr', 'Blocks', 'Touches', 'Def Pen', 'Att Pen',
    'Succ', 'Carries', 'PrgC', 'CPA', 'Mis', 'Dis', 'Rec', 'PrgR',
    'CrdY', 'CrdR', 'Fls', 'Fld', 'PKwon', 'PKcon', 'OG', 'Recov', 'Won'
]


def filter_by_minutes(df, min_minutes=MIN_MINUTES):
    before = len(df)
    filtered = df[df['Min'] >= min_minutes].copy()
    print(f"Filtered {before} -> {len(filtered)} players (>= {min_minutes} minutes)")
    return filtered


def add_per90_columns(df, stat_cols=PER90_STATS):
    df = df.copy()
    for col in stat_cols:
        if col in df.columns:
            df[f'{col}_p90'] = (df[col] / df['Min']) * 90
    return df


if __name__ == "__main__":
    df = pd.read_csv("data/processed/outfield.csv")
    print(f"Before filtering: {df.shape}")

    df = filter_by_minutes(df)
    df = add_per90_columns(df)

    print(f"After per-90 conversion: {df.shape}")
    print(f"\nSample per-90 columns:\n{df[['Player', 'Squad', 'Min', 'Gls', 'Gls_p90', 'xG', 'xG_p90']].head(10)}")

    print(f"\nMissing values check:\n{df.isnull().sum()[df.isnull().sum() > 0]}")

    df.to_csv("data/processed/outfield_normalized.csv", index=False)