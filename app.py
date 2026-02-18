import streamlit as st
import pandas as pd

# 1. Setup Page Config
st.set_page_config(page_title="Wrestling Points Leaderboard", layout="wide")
st.title("🤼 Season Points Leaderboard")

# 2. Load Data
# Note: Ensure "Wrestler List.xlsx - master.csv" is in the same folder as this script.
@st.cache_data
def load_data():
    # Use the master file which contains all entries
    df = pd.read_csv("Wrestler List - master.csv")
    
    # Ensure points are treated as numbers
    df['points'] = pd.to_numeric(df['points'], errors='coerce').fillna(0)
    
    # Clean up column names and strings
    df['Full Name'] = df['Full Name'].str.strip()
    df['Division'] = df['Division'].str.strip()
    df['Team Name'] = df['Team Name'].fillna("Unattached")
    
    return df

df = load_data()

# 3. Process Leaderboard (Summing Points)
# We group by Name and Division to get the total season score
leaderboard = df.groupby(['Full Name', 'Division', 'Team Name'])['points'].sum().reset_index()
leaderboard = leaderboard.sort_values(by='points', ascending=False)

# Add a Rank column based on points
leaderboard['Rank'] = leaderboard['points'].rank(ascending=False, method='min').astype(int)

# 4. Sidebar Controls
st.sidebar.header("Filter Rankings")

# Division Filter
division_list = ["All Divisions"] + sorted(leaderboard['Division'].unique().tolist())
selected_division = st.sidebar.selectbox("Choose a Division:", division_list)

# Search Bar
search_query = st.text_input("🔍 Search for a Wrestler Name:", "")

# 5. Apply Filters
display_df = leaderboard.copy()

if selected_division != "All Divisions":
    display_df = display_df[display_df['Division'] == selected_division]
    # Recalculate rank within the specific division
    display_df['Rank'] = display_df['points'].rank(ascending=False, method='min').astype(int)

if search_query:
    display_df = display_df[display_df['Full Name'].str.contains(search_query, case=False)]

# 6. UI Display
if not display_df.empty:
    st.subheader(f"Rankings for {selected_division}")
    
    # Top 3 Highlight (Podium)
    if not search_query and len(display_df) >= 3:
        cols = st.columns(3)
        top3 = display_df.head(3).values
        with cols[1]: # 1st Place
            st.metric("🥇 1st Place", f"{top3[0][0]}", f"{int(top3[0][3])} pts")
        with cols[0]: # 2nd Place
            st.metric("🥈 2nd Place", f"{top3[1][0]}", f"{int(top3[1][3])} pts")
        with cols[2]: # 3rd Place
            st.metric("🥉 3rd Place", f"{top3[2][0]}", f"{int(top3[2][3])} pts")
        st.divider()

    # Full Table
    st.dataframe(
        display_df[['Rank', 'Full Name', 'points', 'Division', 'Team Name']],
        column_config={
            "points": st.column_config.NumberColumn("Total Points", format="%d pts"),
            "Rank": st.column_config.NumberColumn("Rank", format="#%d"),
        },
        hide_index=True,
        use_container_width=True
    )
else:
    st.warning("No wrestlers found for the selected filters.")

# 7. Division Stats
st.sidebar.info(f"Total Wrestlers: {len(display_df)}")
