import pandas as pd
from understatapi import UnderstatClient

LEAGUES = ["EPL", "La_Liga", "Bundesliga", "Serie_A", "Ligue_1"]

def fetch_current_season(season="2026"):
    client = UnderstatClient()
    all_players = []

    for league in LEAGUES:
        data = client.league(league=league).get_player_data(season=season)
        df = pd.DataFrame(data)
        df["Comp"] = league
        all_players.append(df)
        print(f"{league}: {len(df)} players")

    combined = pd.concat(all_players, ignore_index=True)
    return combined


if __name__ == "__main__":
    df = fetch_current_season()
    print(f"\nTotal: {df.shape}")
    df.to_csv("data/raw/understat_2026-27_live.csv", index=False)