import pandas as pd

def load_raw_data(path="data/raw/players_2024-25_full.csv"):
    df = pd.read_csv(path)
    return df


def drop_duplicate_identity_columns(df):
    """
    FBref's raw export repeats identity columns (Rk, Nation, Pos, etc.)
    once per stat category, tagged like 'Rk_stats_shooting'. These are
    junk duplicates of the real columns, not new data, so we drop them.
    """
    junk_suffixes = [
        '_stats_shooting', '_stats_passing', '_stats_passing_types',
        '_stats_gca', '_stats_defense', '_stats_possession',
        '_stats_playing_time', '_stats_misc', '_stats_keeper',
        '_stats_keeper_adv'
    ]
    cols_to_drop = [c for c in df.columns if any(c.endswith(suf) for suf in junk_suffixes)]
    return df.drop(columns=cols_to_drop)


def split_by_position(df):
    """
    Goalkeepers get a totally different stat set (save%, PSxG-GA, etc.)
    and aren't comparable to outfield playing styles, so we split them
    out for separate analysis rather than clustering everyone together.
    """
    is_gk = df['Pos'].str.contains('GK', na=False)
    goalkeepers = df[is_gk].copy()
    outfield = df[~is_gk].copy()
    return outfield, goalkeepers

def select_outfield_columns(df):
    identity_cols = ['Player', 'Nation', 'Pos', 'Squad', 'Comp', 'Age', 'Born', 'MP', 'Starts', 'Min', '90s']

    attacking_cols = ['Gls', 'Ast', 'G+A', 'G-PK', 'PK', 'PKatt', 'xG', 'npxG', 'xAG', 'npxG+xAG',
                       'xG+xAG', 'Sh', 'SoT', 'SoT%', 'Sh/90', 'SoT/90', 'G/Sh', 'G/SoT', 'npxG/Sh']

    passing_cols = ['Cmp', 'Att', 'Cmp%', 'TotDist', 'PrgDist', 'xA', 'KP', '1/3', 'PPA', 'CrsPA',
                     'Crs', 'CK', 'TB', 'Sw', 'PrgP']

    creation_cols = ['SCA', 'SCA90', 'GCA', 'GCA90']

    defense_cols = ['Tkl', 'TklW', 'Def 3rd', 'Mid 3rd', 'Att 3rd', 'Tkl%', 'Int', 'Tkl+Int',
                     'Clr', 'Blocks', 'Err']

    possession_cols = ['Touches', 'Def Pen', 'Att Pen', 'Succ', 'Succ%', 'Carries', 'PrgC', 'CPA',
                        'Mis', 'Dis', 'Rec', 'PrgR']

    discipline_cols = ['CrdY', 'CrdR', '2CrdY', 'Fls', 'Fld', 'PKwon', 'PKcon', 'OG', 'Recov',
                        'Won', 'Won%']

    keep = identity_cols + attacking_cols + passing_cols + creation_cols + defense_cols + possession_cols + discipline_cols
    keep = [c for c in keep if c in df.columns]
    return df[keep]


def select_goalkeeper_columns(df):
    identity_cols = ['Player', 'Nation', 'Pos', 'Squad', 'Comp', 'Age', 'Born', 'MP', 'Starts', 'Min', '90s']

    keeper_cols = ['GA', 'GA90', 'SoTA', 'Saves', 'Save%', 'W', 'D', 'L', 'CS', 'CS%',
                    'PKA', 'PKsv', 'PKm', 'PSxG', 'PSxG/SoT', 'PSxG+/-', 'Launch%', 'AvgLen',
                    'Stp', 'Stp%', '#OPA', '#OPA/90', 'AvgDist']

    keep = identity_cols + keeper_cols
    keep = [c for c in keep if c in df.columns]
    return df[keep]


if __name__ == "__main__":
    df = load_raw_data()
    print(f"Raw shape: {df.shape}")

    df = drop_duplicate_identity_columns(df)
    print(f"After dropping junk columns: {df.shape}")

    outfield, goalkeepers = split_by_position(df)

    outfield = select_outfield_columns(outfield)
    goalkeepers = select_goalkeeper_columns(goalkeepers)

    print(f"\nOutfield players: {outfield.shape}")
    print(f"Goalkeepers: {goalkeepers.shape}")

    print(f"\nOutfield columns:\n{list(outfield.columns)}")
    print(f"\nGoalkeeper columns:\n{list(goalkeepers.columns)}")

    outfield.to_csv("data/processed/outfield.csv", index=False)
    goalkeepers.to_csv("data/processed/goalkeepers.csv", index=False)