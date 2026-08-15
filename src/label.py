import pandas as pd

CLUSTER_LABELS = {
    "attack": {
        0: "All-Around Forward",
        1: "Target Forward",
        2: "Elite Dual-Threat Forward",
        3: "Squad Forward",
        4: "Poacher",
    },
    "midfield": {
        0: "Advanced Creator",
        1: "Destroyer CDM",
        2: "Deep Holding Mid",
        3: "Box-to-Box",
        4: "Rotation Wide-Mid",
    },
    "defense": {
        0: "Stopper CB",
        1: "Crossing Fullback",
        2: "Ball-Playing CB",
        3: "Overlapping Fullback",
    },
    "goalkeepers": {
        0: "Traditional Keeper",
        1: "Mixed/Inconsistent Keeper",
        2: "Sweeper-Keeper",
    },
}


def label_and_merge():
    all_groups = []

    for group in ["attack", "midfield", "defense"]:
        df = pd.read_csv(f"data/processed/clustered_{group}.csv").copy()
        df["Style"] = df["Cluster"].map(CLUSTER_LABELS[group])
        cols = ["Player", "Squad", "Comp", "PrimaryPos", "SecondaryPos", "Group", "Style"]
        all_groups.append(df[cols])

    gk = pd.read_csv("data/processed/clustered_goalkeepers.csv").copy()
    gk["Style"] = gk["Cluster"].map(CLUSTER_LABELS["goalkeepers"])
    gk["Group"] = "goalkeepers"
    gk["PrimaryPos"] = "GK"
    gk["SecondaryPos"] = ""
    cols = ["Player", "Squad", "Comp", "PrimaryPos", "SecondaryPos", "Group", "Style"]
    all_groups.append(gk[cols])

    final = pd.concat(all_groups, ignore_index=True)
    final.to_csv("data/processed/player_styles.csv", index=False)
    print(f"saved {len(final)} players -> data/processed/player_styles.csv")
    return final


if __name__ == "__main__":
    label_and_merge()