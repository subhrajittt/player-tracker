import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

NUMERIC_COLS = ["games", "time", "goals", "xG", "assists", "xA", "shots",
                 "key_passes", "yellow_cards", "red_cards", "npg", "npxG",
                 "xGChain", "xGBuildup"]

FEATURE_SETS = {
    "attack": ["Gls_p90", "npxG_p90", "Sh_p90", "npxG_per_Sh", "xA_p90",
               "KP_p90", "xGChain_p90", "xGBuildup_p90"],
    "midfield": ["xGChain_p90", "xGBuildup_p90", "KP_p90", "xA_p90", "Gls_p90", "Ast_p90"],
}


def bucket_by_position(df):
    df = df.copy()
    df["Group"] = None
    df.loc[df["position"].str.contains("F", na=False), "Group"] = "attack"
    df.loc[(df["Group"].isna()) & (df["position"].str.contains("M", na=False)), "Group"] = "midfield"
    return df


def prepare(df, min_minutes=900):
    df = df.copy()
    for c in NUMERIC_COLS:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    df = df[df["time"] >= min_minutes].copy()
    df = bucket_by_position(df)

    df["Gls_p90"] = df["goals"] / df["time"] * 90
    df["Ast_p90"] = df["assists"] / df["time"] * 90
    df["npxG_p90"] = df["npxG"] / df["time"] * 90
    df["Sh_p90"] = df["shots"] / df["time"] * 90
    df["xA_p90"] = df["xA"] / df["time"] * 90
    df["KP_p90"] = df["key_passes"] / df["time"] * 90
    df["xGChain_p90"] = df["xGChain"] / df["time"] * 90
    df["xGBuildup_p90"] = df["xGBuildup"] / df["time"] * 90
    df["npxG_per_Sh"] = df["npxG"] / df["shots"]

    return df


def prepare_group(df, group_name):
    cols = FEATURE_SETS[group_name]
    sub = df[df["Group"] == group_name]
    before = len(sub)
    clean = sub.dropna(subset=cols).copy()
    print(f"[{group_name}] {before} -> {len(clean)} ({before - len(clean)} dropped)")
    X_scaled = StandardScaler().fit_transform(clean[cols].values)
    return clean, X_scaled


def run_elbow(X_scaled, group_name, k_range=range(2, 11)):
    inertias = [KMeans(n_clusters=k, n_init=10, random_state=42).fit(X_scaled).inertia_ for k in k_range]

    plt.figure(figsize=(7, 5))
    plt.plot(list(k_range), inertias, marker="o")
    plt.xlabel("k")
    plt.ylabel("Inertia")
    plt.title(f"Elbow — understat {group_name}")
    plt.xticks(list(k_range))
    plt.grid(alpha=0.3)
    plt.savefig(f"data/processed/elbow_understat_{group_name}.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[{group_name}] saved elbow_understat_{group_name}.png")

def phase2_fit(k_by_group):
    df = pd.read_csv("data/processed/understat_2025-26_normalized.csv")
    for group in ["attack", "midfield"]:
        clean, X_scaled = prepare_group(df, group)
        clean["Cluster"] = KMeans(n_clusters=k_by_group[group], n_init=10, random_state=42).fit_predict(X_scaled)
        clean.to_csv(f"data/processed/clustered_understat_{group}.csv", index=False)
        print(f"[{group}] saved clustered_understat_{group}.csv")

if __name__ == "__main__":
    phase2_fit({"attack": 4, "midfield": 4})

