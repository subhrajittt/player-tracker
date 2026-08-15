import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

FEATURE_SETS = {
    "attack": ["Gls_p90", "npxG_p90", "Sh_p90", "SoT%", "G/Sh", "xAG_p90",
               "SCA90", "PrgC_p90", "Succ%", "Att Pen_p90", "CrsPA_p90", "PrgR_p90"],
    "midfield": ["PrgP_p90", "PrgC_p90", "Cmp%", "KP_p90", "xAG_p90", "SCA90",
                 "Tkl_p90", "Int_p90", "Tkl+Int_p90", "TotDist_p90", "Succ%", "1/3_p90"],
    "defense": ["Tkl_p90", "Int_p90", "Clr_p90", "Blocks_p90", "Cmp%", "PrgP_p90",
                "PrgC_p90", "Att 3rd_p90", "CrsPA_p90", "Tkl%", "Won%"],
    "goalkeepers": ["Save%", "PSxG+/-", "Stp%", "#OPA/90", "AvgDist", "Launch%", "AvgLen", "CS%"],
}

POSITION_TO_GROUP = {"FW": "attack", "MF": "midfield", "DF": "defense"}


def bucket_by_primary_position(df, pos_col="Pos"):
    parts = df[pos_col].fillna("").str.split(",")
    df = df.copy()
    df["PrimaryPos"] = parts.str[0].str.strip()
    df["SecondaryPos"] = parts.apply(lambda p: ",".join(x.strip() for x in p[1:]) if len(p) > 1 else "")
    df["Group"] = df["PrimaryPos"].map(POSITION_TO_GROUP)
    return df


def prepare_group(df, group_name):
    cols = FEATURE_SETS[group_name]
    before = len(df)
    clean = df.dropna(subset=cols).copy()
    print(f"[{group_name}] {before} -> {len(clean)} ({before - len(clean)} dropped)")

    X_scaled = StandardScaler().fit_transform(clean[cols].values)
    return clean, X_scaled


def run_elbow(X_scaled, group_name, k_range=range(2, 11)):
    inertias = [KMeans(n_clusters=k, n_init=10, random_state=42).fit(X_scaled).inertia_ for k in k_range]

    plt.figure(figsize=(7, 5))
    plt.plot(list(k_range), inertias, marker="o")
    plt.xlabel("k")
    plt.ylabel("Inertia")
    plt.title(f"Elbow — {group_name}")
    plt.xticks(list(k_range))
    plt.grid(alpha=0.3)
    plt.savefig(f"data/processed/elbow_{group_name}.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[{group_name}] saved elbow_{group_name}.png")


def phase1_elbow():
    outfield = bucket_by_primary_position(pd.read_csv("data/processed/outfield_normalized.csv"))

    for group in ["attack", "midfield", "defense"]:
        clean, X_scaled = prepare_group(outfield[outfield["Group"] == group], group)
        run_elbow(X_scaled, group)

    gk = pd.read_csv("data/processed/goalkeepers.csv")
    gk = gk[gk["Min"] >= 900]
    clean, X_scaled = prepare_group(gk, "goalkeepers")
    run_elbow(X_scaled, "goalkeepers")


def phase2_fit(k_by_group, players_per_cluster=8):
    outfield = bucket_by_primary_position(pd.read_csv("data/processed/outfield_normalized.csv"))
    results = {}

    for group in ["attack", "midfield", "defense"]:
        clean, X_scaled = prepare_group(outfield[outfield["Group"] == group], group)
        clean["Cluster"] = KMeans(n_clusters=k_by_group[group], n_init=10, random_state=42).fit_predict(X_scaled)

        print(f"\n=== {group.upper()} k={k_by_group[group]} ===")
        for c in sorted(clean["Cluster"].unique()):
            members = clean[clean["Cluster"] == c]
            print(f"\nCluster {c} ({len(members)}):")
            print(members[["Player", "Squad", "PrimaryPos"]].head(players_per_cluster).to_string(index=False))

        results[group] = clean

    gk = pd.read_csv("data/processed/goalkeepers.csv")
    gk = gk[gk["Min"] >= 900].copy()
    clean, X_scaled = prepare_group(gk, "goalkeepers")
    clean["Cluster"] = KMeans(n_clusters=k_by_group["goalkeepers"], n_init=10, random_state=42).fit_predict(X_scaled)

    print(f"\n=== GOALKEEPERS k={k_by_group['goalkeepers']} ===")
    for c in sorted(clean["Cluster"].unique()):
        members = clean[clean["Cluster"] == c]
        print(f"\nCluster {c} ({len(members)}):")
        print(members[["Player", "Squad"]].head(players_per_cluster).to_string(index=False))

    results["goalkeepers"] = clean

    for group, df in results.items():
        df.to_csv(f"data/processed/clustered_{group}.csv", index=False)

    return results


if __name__ == "__main__":
    phase1_elbow()