import pandas as pd

FEATURE_SETS = {
    "attack": ["Gls_p90", "npxG_p90", "Sh_p90", "SoT%", "G/Sh", "xAG_p90", "SCA90", "PrgC_p90", "Succ%", "Att Pen_p90", "CrsPA_p90", "PrgR_p90"],
    "midfield": ["PrgP_p90", "PrgC_p90", "Cmp%", "KP_p90", "xAG_p90", "SCA90", "Tkl_p90", "Int_p90", "Tkl+Int_p90", "TotDist_p90", "Succ%", "1/3_p90"],
    "defense": ["Tkl_p90", "Int_p90", "Clr_p90", "Blocks_p90", "Cmp%", "PrgP_p90", "PrgC_p90", "Att 3rd_p90", "CrsPA_p90", "Tkl%", "Won%"],
    "goalkeepers": ["Save%", "PSxG+/-", "Stp%", "#OPA/90", "AvgDist", "Launch%", "AvgLen", "CS%"],
}

CLUSTER_LABELS = {
    "attack": {0: "All-Around Forward", 1: "Target Forward", 2: "Elite Dual-Threat Forward", 3: "Squad Forward", 4: "Poacher"},
    "midfield": {0: "Advanced Creator", 1: "Destroyer CDM", 2: "Deep Holding Mid", 3: "Box-to-Box", 4: "Rotation Wide-Mid"},
    "defense": {0: "Stopper CB", 1: "Crossing Fullback", 2: "Ball-Playing CB", 3: "Overlapping Fullback"},
    "goalkeepers": {0: "Traditional Keeper", 1: "Mixed/Inconsistent Keeper", 2: "Sweeper-Keeper"},
}

def label_and_merge():
    all_groups = []

    for group in ["attack", "midfield", "defense"]:
        df = pd.read_csv(f"data/processed/clustered_{group}.csv")
        df["Style"] = df["Cluster"].map(CLUSTER_LABELS[group])
        cols = ["Player", "Squad", "Comp", "PrimaryPos", "SecondaryPos", "Group", "Style"] + FEATURE_SETS[group]
        all_groups.append(df[cols])

    gk = pd.read_csv("data/processed/clustered_goalkeepers.csv")
    gk["Style"] = gk["Cluster"].map(CLUSTER_LABELS["goalkeepers"])
    gk["Group"] = "goalkeepers"
    gk["PrimaryPos"] = "GK"
    gk["SecondaryPos"] = ""
    cols = ["Player", "Squad", "Comp", "PrimaryPos", "SecondaryPos", "Group", "Style"] + FEATURE_SETS["goalkeepers"]
    all_groups.append(gk[cols])

    final = pd.concat(all_groups, ignore_index=True)
    final.to_csv("data/processed/player_styles.csv", index=False)
    print(f"saved {len(final)} players")
    return final

if __name__ == "__main__":
    label_and_merge()