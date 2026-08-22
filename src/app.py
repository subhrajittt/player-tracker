import streamlit as st
import pandas as pd

st.set_page_config(page_title="Player Tracker", layout="wide")

ATTACK_STATS = ["Gls_p90", "npxG_p90", "xAG_p90", "SCA90", "PrgC_p90", "Succ%"]
MIDFIELD_STATS = ["PrgP_p90", "PrgC_p90", "Cmp%", "Tkl_p90", "Int_p90", "xAG_p90"]
DEFENSE_STATS = ["Tkl_p90", "Int_p90", "Clr_p90", "Cmp%", "PrgP_p90", "CrsPA_p90"]
GK_STATS = ["Save%", "PSxG+/-", "Launch%", "#OPA/90"]

GROUP_STATS = {"attack": ATTACK_STATS, "midfield": MIDFIELD_STATS, "defense": DEFENSE_STATS, "goalkeepers": GK_STATS}

UNDERSTAT_ATTACK_STATS = ["Gls_p90", "npxG_p90", "xA_p90", "KP_p90", "xGBuildup_p90"]
UNDERSTAT_MID_STATS = ["xGChain_p90", "xGBuildup_p90", "Gls_p90", "Ast_p90"]
UNDERSTAT_GROUP_STATS = {"attack": UNDERSTAT_ATTACK_STATS, "midfield": UNDERSTAT_MID_STATS}


@st.cache_data
def load_data():
    df_2425 = pd.read_csv("data/processed/player_styles.csv")
    df_2526 = pd.read_csv("data/processed/understat_player_styles_2025-26.csv")
    return df_2425, df_2526

df_2425, df_2526 = load_data()

st.title("Player Style Tracker")

tab_browse, tab_search, tab_compare = st.tabs(["Browse", "Search", "Compare Seasons"])

with tab_browse:
    season = st.selectbox("Season", ["2024-25", "2025-26"])
    df = df_2425 if season == "2024-25" else df_2526
    stat_map = GROUP_STATS if season == "2024-25" else UNDERSTAT_GROUP_STATS

    col1, col2, col3 = st.columns(3)
    with col1:
        league = st.selectbox("League", ["All"] + sorted(df["Comp"].dropna().unique().tolist()))
    with col2:
        group = st.selectbox("Position Group", ["All"] + sorted(df["Group"].dropna().unique().tolist()))
    with col3:
        style_options = df["Style"].dropna().unique().tolist() if group == "All" else df[df["Group"] == group]["Style"].dropna().unique().tolist()
        style = st.selectbox("Style", ["All"] + sorted(style_options))

    filtered = df.copy()
    if league != "All":
        filtered = filtered[filtered["Comp"] == league]
    if group != "All":
        filtered = filtered[filtered["Group"] == group]
    if style != "All":
        filtered = filtered[filtered["Style"] == style]

    st.write(f"{len(filtered)} players")

    base_cols = ["Player", "Squad", "Comp", "Group", "Style"]
    if group != "All" and group in stat_map:
        show_cols = base_cols + stat_map[group]
    else:
        show_cols = base_cols
    show_cols = [c for c in show_cols if c in filtered.columns]
    st.dataframe(filtered[show_cols], use_container_width=True, hide_index=True)

with tab_search:
    query = st.text_input("Search player name")
    if query:
        for label, df_s, stat_map in [("2024-25", df_2425, GROUP_STATS), ("2025-26", df_2526, UNDERSTAT_GROUP_STATS)]:
            hits = df_s[df_s["Player"].str.contains(query, case=False, na=False)]
            st.subheader(label)
            if len(hits) == 0:
                st.write("No match")
                continue
            for _, row in hits.iterrows():
                st.markdown(f"**{row['Player']}** — {row['Squad']} ({row['Comp']}) — **{row['Style']}**")
                grp = row["Group"]
                if grp in stat_map:
                    stats = {s: row[s] for s in stat_map[grp] if s in row and pd.notna(row[s])}
                    st.write(stats)

                    grp_avg = df_s[df_s["Group"] == grp][stat_map[grp]].mean()
                    cluster_avg = df_s[(df_s["Group"] == grp) & (df_s["Style"] == row["Style"])][stat_map[grp]].mean()
                    comp = pd.DataFrame({"Player": stats, "This Style Avg": cluster_avg, f"All {grp.title()} Avg": grp_avg})
                    st.dataframe(comp.round(2), use_container_width=True)

with tab_compare:
    all_names = sorted(set(df_2425["Player"]).union(set(df_2526["Player"])))
    player = st.selectbox("Player", all_names)

    row_2425 = df_2425[df_2425["Player"] == player]
    row_2526 = df_2526[df_2526["Player"] == player]

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("2024-25")
        if len(row_2425):
            r = row_2425.iloc[0]
            st.metric("Style", r["Style"])
            st.write(r[["Squad", "Comp"]])
            grp = r["Group"]
            if grp in GROUP_STATS:
                st.write({s: r[s] for s in GROUP_STATS[grp] if s in r and pd.notna(r[s])})
        else:
            st.write("Not in this season's dataset")
    with col2:
        st.subheader("2025-26")
        if len(row_2526):
            r = row_2526.iloc[0]
            st.metric("Style", r["Style"])
            st.write(r[["Squad", "Comp"]])
            grp = r["Group"]
            if grp in UNDERSTAT_GROUP_STATS:
                st.write({s: r[s] for s in UNDERSTAT_GROUP_STATS[grp] if s in r and pd.notna(r[s])})
        else:
            st.write("Not in this season's dataset")