import pandas as pd

FEATURE_SETS = {
    "attack": ["Gls_p90", "npxG_p90", "Sh_p90", "npxG_per_Sh", "xA_p90", "KP_p90", "xGChain_p90", "xGBuildup_p90"],
    "midfield": ["xGChain_p90", "xGBuildup_p90", "KP_p90", "xA_p90", "Gls_p90", "Ast_p90"],
}

RAW_COLS = ["goals", "assists", "time", "games"]

UNDERSTAT_LABELS = {
    "attack": {0: "Lower-Tier Finisher", 1: "Link-Up Forward", 2: "Elite Dual-Threat", 3: "Elite Finisher"},
    "midfield": {0: "High Attacking Involvement", 1: "Low Attacking Involvement", 2: "Elite Attacking Involvement", 3: "Moderate Attacking Involvement"},
}

def label_understat():
    frames = []
    for group in ["attack", "midfield"]:
        df = pd.read_csv(f"data/processed/clustered_understat_{group}.csv")
        df["Style"] = df["Cluster"].map(UNDERSTAT_LABELS[group])
        df["Group"] = group
        cols = ["player_name", "team_title", "Comp", "position", "Group", "Style"] + RAW_COLS + FEATURE_SETS[group]
        cols = [c for c in cols if c in df.columns]
        frames.append(df[cols])

    final = pd.concat(frames, ignore_index=True)
    final = final.rename(columns={
        "player_name": "Player", "team_title": "Squad", "position": "Pos",
        "goals": "Goals", "assists": "Assists", "time": "Minutes", "games": "Games",
    })
    final.to_csv("data/processed/understat_player_styles_2025-26.csv", index=False)
    print(f"saved {len(final)} players")
    return final

if __name__ == "__main__":
    label_understat()