import streamlit as st
import pandas as pd
import glob
import os

# 1. Setup Page
st.set_page_config(page_title="Wrestling Points Leaderboard", layout="wide")
st.title("🤼 Season Points Leaderboard")
st.markdown("### Combined Rankings from All Divisions")

# 2. Smart Data Loader
@st.cache_data
def load_all_data():
    # This line looks for ALL files in your folder that start with "Wrestler List"
    all_files = glob.glob("Wrestler List*.csv")
    
    data_frames = []
    
    for filename in all_files:
        # Skip the "master" and "tot" files to avoid double-counting 
        # (since the other sheets have the individual data)
        if "master" in filename.lower() or "tot" in filename.lower():
            continue
            
        df = pd.read_csv(filename)
        
        # Standardize columns (some of your sheets use 'Full Name', others might differ)
        # We only keep what we need for the leaderboard
        cols_to_keep = ['Full Name', 'Team Name', 'points', 'Division', 'Weight']
        
        # Filter to only the columns that exist in this specific file
        existing_cols = [c for c in cols_to_keep if c in df.columns]
        df = df[existing_cols]
        
        data_frames.append(df)
    
    # Combine all sheets (D1, D2, G1, G2, etc.) into one master list
    combined_df = pd.concat(data_frames, ignore_index=True)
    
    # Clean data
    combined_df['points'] = pd.to_numeric(combined_df['points'], errors='coerce').fillna(0)
    combined_df['Full Name'] = combined_df['Full Name'].str.strip()
    combined_df['Team Name'] = combined_df['Team Name'].fillna("Unattached")
    
    return combined_df

# Load the data
try:
    df = load_all_data()
except Exception as e:
    st.error("Make sure your CSV files are in the same folder as this script!")
    st.stop()

# 3. Process Leaderboard
leaderboard = df.groupby(['Full Name', 'Division', 'Team Name'])['points'].sum().reset_index()
leaderboard = leaderboard.sort_values(by='points', ascending=False)

# 4. Sidebar Filters
st.sidebar.header("Filters")
div_list = ["All Divisions"] + sorted(leaderboard['Division'].unique().tolist())
selected_div = st.sidebar.selectbox("Select Division", div_list)

search_query = st.text_input("🔍 Search for a Wrestler Name:", "")

# 5. Filter Data
display_df = leaderboard.copy()
if selected_div != "All Divisions":
    display_df = display_df[display_df['Division'] == selected_div]

if search_query:
    display_df = display_df[display_df['Full Name'].str.contains(search_query, case=False)]

# Assign Ranks
display_df['Rank'] = display_df['points'].rank(ascending=False, method='min').astype(int)

# 6. Display Rankings
if not display_df.empty:
    # Top 3 Podium
    if not search_query and len(display_df) >= 3:
        st.subheader("🏆 Division Leaders")
        c1, c2, c3 = st.columns(3)
        top = display_df.head(3).values
        c2.metric("🥇 1st Place", f"{top[0][0]}", f"{int(top[0][3])} pts")
        c1.metric("🥈 2nd Place", f"{top[1][0]}", f"{int(top[1][3])} pts")
        c3.metric("🥉 3rd Place", f"{top[2][0]}", f"{int(top[2][3])} pts")
        st.divider()

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
    st.warning("No data found for the selected criteria.")