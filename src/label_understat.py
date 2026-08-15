import pandas as pd

UNDERSTAT_LABELS = {
    "attack": {
        0: "Lower-Tier Finisher",
        1: "Link-Up Forward",
        2: "Elite Dual-Threat",
        3: "Elite Finisher",
    },
    "midfield": {
        0: "High Attacking Involvement",
        1: "Low Attacking Involvement",
        2: "Elite Attacking Involvement",
        3: "Moderate Attacking Involvement",
    },
}

def label_understat():
    frames = []
    for group in ["attack", "midfield"]:
        df = pd.read_csv(f"data/processed/clustered_understat_{group}.csv")
        df["Style"] = df["Cluster"].map(UNDERSTAT_LABELS[group])
        df["Group"] = group
        cols = ["player_name", "team_title", "Comp", "position", "Group", "Style"]
        frames.append(df[cols])

    final = pd.concat(frames, ignore_index=True)
    final.to_csv("data/processed/understat_player_styles_2025-26.csv", index=False)
    print(f"saved {len(final)} players")
    return final

if __name__ == "__main__":
    label_understat()