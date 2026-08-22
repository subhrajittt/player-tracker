import streamlit as st
import pandas as pd

st.set_page_config(page_title="Player Tracker", layout="wide")

STAT_LABELS = {
    "Gls_p90": "Goals per 90", "npxG_p90": "Non-Penalty xG per 90", "xAG_p90": "Assist Contribution per 90",
    "SCA90": "Shot-Creating Actions per 90", "PrgC_p90": "Progressive Carries per 90", "Succ%": "Dribble Success %",
    "PrgP_p90": "Progressive Passes per 90", "Cmp%": "Pass Completion %", "KP_p90": "Key Passes per 90",
    "Tkl_p90": "Tackles per 90", "Int_p90": "Interceptions per 90", "Tkl+Int_p90": "Tackles + Interceptions per 90",
    "TotDist_p90": "Distance Covered per 90", "1/3_p90": "Passes into Final Third per 90",
    "Clr_p90": "Clearances per 90", "Blocks_p90": "Blocks per 90", "Att 3rd_p90": "Final Third Touches per 90",
    "CrsPA_p90": "Crosses into Box per 90", "Tkl%": "Tackle Success %", "Won%": "Aerial Duels Won %",
    "Save%": "Save %", "PSxG+/-": "Shot-Stopping vs Expected", "Launch%": "Long Pass %", "#OPA/90": "Sweeping Actions per 90",
    "AvgDist": "Avg Defensive Action Distance", "AvgLen": "Avg Pass Length", "Stp%": "Crosses Stopped %", "CS%": "Clean Sheet %",
    "SoT%": "Shots on Target %", "G/Sh": "Goals per Shot", "Sh_p90": "Shots per 90", "Att Pen_p90": "Box Touches per 90",
    "PrgR_p90": "Progressive Passes Received per 90",
    "xG_p90": "Expected Goals per 90", "xA_p90": "Expected Assists per 90",
    "xGChain_p90": "Buildup Involvement per 90", "xGBuildup_p90": "Deep Buildup Involvement per 90",
    "Ast_p90": "Assists per 90", "npxG_per_Sh": "Shot Quality (xG per Shot)",
}

RAW_LABELS = {"Gls": "Goals", "Ast": "Assists", "Min": "Minutes", "MP": "Matches",
              "GA": "Goals Conceded", "Saves": "Saves", "CS": "Clean Sheets",
              "Goals": "Goals", "Assists": "Assists", "Minutes": "Minutes", "Games": "Matches"}

ATTACK_STATS = ["Gls_p90", "npxG_p90", "xAG_p90", "SCA90", "PrgC_p90", "Succ%"]
MIDFIELD_STATS = ["PrgP_p90", "PrgC_p90", "Cmp%", "Tkl_p90", "Int_p90", "xAG_p90"]
DEFENSE_STATS = ["Tkl_p90", "Int_p90", "Clr_p90", "Cmp%", "PrgP_p90", "CrsPA_p90"]
GK_STATS = ["Save%", "PSxG+/-", "Launch%", "#OPA/90"]
GROUP_STATS = {"attack": ATTACK_STATS, "midfield": MIDFIELD_STATS, "defense": DEFENSE_STATS, "goalkeepers": GK_STATS}
RAW_COLS_2425 = ["Gls", "Ast", "Min", "MP"]

UNDERSTAT_ATTACK_STATS = ["Gls_p90", "npxG_p90", "xA_p90", "KP_p90", "xGBuildup_p90"]
UNDERSTAT_MID_STATS = ["xGChain_p90", "xGBuildup_p90", "Gls_p90", "Ast_p90"]
UNDERSTAT_GROUP_STATS = {"attack": UNDERSTAT_ATTACK_STATS, "midfield": UNDERSTAT_MID_STATS}
RAW_COLS_2526 = ["Goals", "Assists", "Minutes", "Games"]


@st.cache_data
def load_data():
    df_2425 = pd.read_csv("data/processed/player_styles.csv")
    df_2526 = pd.read_csv("data/processed/understat_player_styles_2025-26.csv")
    return df_2425, df_2526

df_2425, df_2526 = load_data()


def show_player_card(row, stat_cols, raw_cols):
    raw_present = [c for c in raw_cols if c in row and pd.notna(row[c])]
    if raw_present:
        cols = st.columns(len(raw_present))
        for col, stat in zip(cols, raw_present):
            val = row[stat]
            display_val = int(val) if float(val).is_integer() else round(val, 1)
            col.metric(RAW_LABELS.get(stat, stat), display_val)

    stats_present = {STAT_LABELS.get(s, s): round(row[s], 2) for s in stat_cols if s in row and pd.notna(row[s])}
    if stats_present:
        st.table(pd.DataFrame(stats_present.items(), columns=["Stat", "Value"]).set_index("Stat"))


st.title("Player Style Tracker")

tab_browse, tab_search, tab_compare = st.tabs(["Browse", "Search", "Compare Seasons"])

with tab_browse:
    season = st.selectbox("Season", ["2024-25", "2025-26"])
    df = df_2425 if season == "2024-25" else df_2526
    stat_map = GROUP_STATS if season == "2024-25" else UNDERSTAT_GROUP_STATS
    raw_cols = RAW_COLS_2425 if season == "2024-25" else RAW_COLS_2526

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
    show_cols = base_cols + raw_cols
    if group != "All" and group in stat_map:
        show_cols += stat_map[group]
    show_cols = [c for c in show_cols if c in filtered.columns]

    display_df = filtered[show_cols].rename(columns={**RAW_LABELS, **STAT_LABELS})
    st.dataframe(display_df, use_container_width=True, hide_index=True)

with tab_search:
    query = st.text_input("Search player name")
    if query:
        for label, df_s, stat_map, raw_cols in [
            ("2024-25", df_2425, GROUP_STATS, RAW_COLS_2425),
            ("2025-26", df_2526, UNDERSTAT_GROUP_STATS, RAW_COLS_2526),
        ]:
            hits = df_s[df_s["Player"].str.contains(query, case=False, na=False)]
            st.subheader(label)
            if len(hits) == 0:
                st.write("No match")
                continue
            for _, row in hits.iterrows():
                st.markdown(f"**{row['Player']}** — {row['Squad']} ({row['Comp']}) — **{row['Style']}**")
                grp = row["Group"]
                show_player_card(row, stat_map.get(grp, []), raw_cols)

                if grp in stat_map:
                    cluster_avg = df_s[(df_s["Group"] == grp) & (df_s["Style"] == row["Style"])][stat_map[grp]].mean()
                    group_avg = df_s[df_s["Group"] == grp][stat_map[grp]].mean()
                    comp_df = pd.DataFrame({
                        "This Player": [round(row[s], 2) if pd.notna(row.get(s)) else None for s in stat_map[grp]],
                        "This Style Avg": cluster_avg.round(2).values,
                        f"All {grp.title()} Avg": group_avg.round(2).values,
                    }, index=[STAT_LABELS.get(s, s) for s in stat_map[grp]])
                    st.write("Compared to others:")
                    st.table(comp_df)
                st.divider()

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
            st.write(f"{r['Squad']} — {r['Comp']}")
            show_player_card(r, GROUP_STATS.get(r["Group"], []), RAW_COLS_2425)
        else:
            st.write("Not in this season's dataset")
    with col2:
        st.subheader("2025-26")
        if len(row_2526):
            r = row_2526.iloc[0]
            st.metric("Style", r["Style"])
            st.write(f"{r['Squad']} — {r['Comp']}")
            show_player_card(r, UNDERSTAT_GROUP_STATS.get(r["Group"], []), RAW_COLS_2526)
        else:
            st.write("Not in this season's dataset")