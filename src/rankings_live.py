import pandas as pd

NUMERIC_COLS = ["games", "time", "goals", "xG", "assists", "xA", "shots",
                 "key_passes", "yellow_cards", "red_cards", "npg", "npxG",
                 "xGChain", "xGBuildup"]

PER90_MIN_MINUTES = 400

def load_live(path="data/raw/understat_2026-27_live.csv"):
    df = pd.read_csv(path)
    if df.empty or "games" not in df.columns:
        print("No data yet — season hasn't started or no matches played.")
        return None
    for c in NUMERIC_COLS:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def add_per90(df):
    df = df.copy()
    df["Gls_p90"] = df["goals"] / df["time"] * 90
    df["Ast_p90"] = df["assists"] / df["time"] * 90
    df["xG_p90"] = df["xG"] / df["time"] * 90
    df["xA_p90"] = df["xA"] / df["time"] * 90
    df["npxG_p90"] = df["npxG"] / df["time"] * 90
    return df


def raw_leaderboard(df, sort_by="goals", league=None, top_n=20):
    filtered = df.copy()
    if league:
        filtered = filtered[filtered["Comp"] == league]
    filtered = filtered.sort_values(sort_by, ascending=False)
    cols = ["player_name", "team_title", "Comp", "position", "games", "time", "goals", "xG", "assists", "xA"]
    return filtered[cols].head(top_n)


def per90_leaderboard(df, sort_by="Gls_p90", league=None, top_n=20, min_minutes=PER90_MIN_MINUTES):
    qualified = df[df["time"] >= min_minutes].copy()
    qualified = add_per90(qualified)
    if league:
        qualified = qualified[qualified["Comp"] == league]
    qualified = qualified.sort_values(sort_by, ascending=False)
    cols = ["player_name", "team_title", "Comp", "time", "Gls_p90", "xG_p90", "Ast_p90", "xA_p90"]
    print(f"({len(df) - len(qualified)} players below {min_minutes}-minute threshold, excluded)")
    return qualified[cols].head(top_n)


if __name__ == "__main__":
    df = load_live()
    if df is not None:
        print(f"Loaded {df.shape[0]} players\n")
        print("=== Top 10 by raw goals ===")
        print(raw_leaderboard(df, sort_by="goals", top_n=10))
        print(f"\n=== Top 10 by Gls_p90 ({PER90_MIN_MINUTES}+ min qualified only) ===")
        print(per90_leaderboard(df, sort_by="Gls_p90", top_n=10))