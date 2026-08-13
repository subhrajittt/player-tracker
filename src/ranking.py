import pandas as pd

DISPLAY_STATS = {
    'Gls_p90': 'Goals per 90',
    'Ast_p90': 'Assists per 90',
    'G+A_p90': 'G+A per 90',
    'xG_p90': 'xG per 90',
    'xAG_p90': 'xAG per 90',
    'SCA90': 'Shot-Creating Actions per 90',
    'GCA90': 'Goal-Creating Actions per 90',
    'Tkl_p90': 'Tackles per 90',
    'Int_p90': 'Interceptions per 90',
    'PrgC_p90': 'Progressive Carries per 90',
    'PrgP_p90': 'Progressive Passes per 90',
}


def load_normalized_data(path="data/processed/outfield_normalized.csv"):
    return pd.read_csv(path)


def get_rankings(df, sort_by='Gls_p90', league=None, position=None, top_n=20):
    filtered = df.copy()

    if league:
        filtered = filtered[filtered['Comp'] == league]
    if position:
        filtered = filtered[filtered['Pos'].str.contains(position, na=False)]

    filtered = filtered.sort_values(sort_by, ascending=False)

    display_cols = ['Player', 'Squad', 'Comp', 'Pos', 'Min'] + list(DISPLAY_STATS.keys())
    display_cols = [c for c in display_cols if c in filtered.columns]

    return filtered[display_cols].head(top_n)


if __name__ == "__main__":
    df = load_normalized_data()
    print(f"Loaded {df.shape[0]} players\n")

    print("=== Top 10 by Goals per 90 (all leagues, all positions) ===")
    print(get_rankings(df, sort_by='Gls_p90', top_n=10)[['Player', 'Squad', 'Gls_p90']])

    print("\n=== Top 10 by Assists per 90, Premier League only ===")
    print(get_rankings(df, sort_by='Ast_p90', league='eng Premier League', top_n=10)[['Player', 'Squad', 'Ast_p90']])

    print("\n=== Top 10 by xG per 90, Forwards only ===")
    print(get_rankings(df, sort_by='xG_p90', position='FW', top_n=10)[['Player', 'Squad', 'Pos', 'xG_p90']])

    print("\n=== Top 10 by Tackles per 90, Defenders only ===") 
    print(get_rankings(df, sort_by='Tkl_p90', position='DF', top_n=10)[['Player', 'Squad', 'Pos', 'Tkl_p90']])