import streamlit as st
import pandas as pd

st.set_page_config(page_title="Player Tracker", layout="wide")

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

    col1, col2, col3 = st.columns(3)
    with col1:
        league = st.selectbox("League", ["All"] + sorted(df["Comp"].dropna().unique().tolist()))
    with col2:
        group = st.selectbox("Position Group", ["All"] + sorted(df["Group"].dropna().unique().tolist()))
    with col3:
        style = st.selectbox("Style", ["All"] + sorted(df["Style"].dropna().unique().tolist()))

    filtered = df.copy()
    if league != "All":
        filtered = filtered[filtered["Comp"] == league]
    if group != "All":
        filtered = filtered[filtered["Group"] == group]
    if style != "All":
        filtered = filtered[filtered["Style"] == style]

    st.write(f"{len(filtered)} players")
    cols = [c for c in ["Player", "Squad", "Comp", "PrimaryPos", "Pos", "Group", "Style"] if c in filtered.columns]
    st.dataframe(filtered[cols], use_container_width=True, hide_index=True)

with tab_search:
    query = st.text_input("Search player name")
    if query:
        for label, df_s in [("2024-25", df_2425), ("2025-26", df_2526)]:
            hits = df_s[df_s["Player"].str.contains(query, case=False, na=False)]
            st.subheader(label)
            if len(hits):
                cols = [c for c in ["Player", "Squad", "Comp", "PrimaryPos", "Pos", "Group", "Style"] if c in hits.columns]
                st.dataframe(hits[cols], use_container_width=True, hide_index=True)
            else:
                st.write("No match")

with tab_compare:
    all_names = sorted(set(df_2425["Player"]).union(set(df_2526["Player"])))
    player = st.selectbox("Player", all_names)

    row_2425 = df_2425[df_2425["Player"] == player]
    row_2526 = df_2526[df_2526["Player"] == player]

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("2024-25")
        if len(row_2425):
            st.metric("Style", row_2425.iloc[0]["Style"])
            st.write(row_2425.iloc[0][["Squad", "Comp", "PrimaryPos"]])
        else:
            st.write("Not in this season's dataset")
    with col2:
        st.subheader("2025-26")
        if len(row_2526):
            st.metric("Style", row_2526.iloc[0]["Style"])
            st.write(row_2526.iloc[0][["Squad", "Comp", "Pos"]])
        else:
            st.write("Not in this season's dataset")