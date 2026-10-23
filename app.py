import streamlit as st
import pandas as pd
import gspread
import plotly.express as px

# Page Config
st.set_page_config(page_title="CP Tournament Tracker", page_icon="🏆", layout="wide")

# Dashboard Title
st.title("🏆 Competitive Programming Dashboard")
st.markdown("Track your upcoming tournaments and monitor your past progress across Codeforces, LeetCode, AtCoder, and CodeChef.")

# Connect to Google Sheets
@st.cache_resource
def get_sheets_client():
    # Modern gspread service account auth using credentials.json in the same folder
    return gspread.service_account(filename="credentials.json")

try:
    client = get_sheets_client()
    sheet = client.open("Competitive Programming Tournament Tracker")
    
    upcoming_worksheet = sheet.worksheet("Upcoming Contests")
    progress_worksheet = sheet.worksheet("My Progress Log")
    
    upcoming_df = pd.DataFrame(upcoming_worksheet.get_all_records())
    progress_df = pd.DataFrame(progress_worksheet.get_all_records())
    
except Exception as e:
    st.error("⚠️ Connection Error")
    st.write(f"Failed to load Google Sheet data. Error details:\n\n`{e}`")
    st.info("Checklist:\n1. Is `credentials.json` placed in the exact same folder as `app.py`?\n2. Did you share your Google Sheet with the service account email (`client_email`) with Editor permissions?")
    st.stop()

# Tabs for Navigation
tab1, tab2, tab3 = st.tabs(["📅 Upcoming Contests", "📈 My Progress Log", "➕ Log Past Contest"])

with tab1:
    st.header("Upcoming Contests (IST)")
    if not upcoming_df.empty:
        platforms = upcoming_df["Platform"].unique().tolist() if "Platform" in upcoming_df.columns else []
        selected_platforms = st.multiselect("Filter by Platform", platforms, default=platforms)
        
        if selected_platforms:
            filtered_upcoming = upcoming_df[upcoming_df["Platform"].isin(selected_platforms)]
            st.dataframe(filtered_upcoming, use_container_width=True)
        else:
            st.dataframe(upcoming_df, use_container_width=True)
    else:
        st.info("No upcoming contests found. Run your Apps Script to populate!")

with tab2:
    st.header("My Performance History")
    if not progress_df.empty:
        st.metric("Total Contests Taken", len(progress_df))
        
        if "Rating After" in progress_df.columns and not progress_df["Rating After"].eq("").all():
            fig = px.line(progress_df, x="Contest Name", y="Rating After", color="Platform", markers=True, title="Rating Progression Over Time")
            st.plotly_chart(fig, use_container_width=True)
            
        st.dataframe(progress_df, use_container_width=True)
    else:
        st.info("No progress logs recorded yet.")

with tab3:
    st.header("Log a Completed Contest")
    with st.form("progress_form"):
        col1, col2 = st.columns(2)
        with col1:
            plat = st.selectbox("Platform", ["codeforces.com", "leetcode.com", "atcoder.jp", "codechef.com"])
            c_name = st.text_input("Contest Name")
            c_date = st.date_input("Date")
            rank = st.number_input("Rank", min_value=1, step=1)
            solved = st.text_input("Problems Solved (e.g., 3/4)")
        with col2:
            r_before = st.number_input("Rating Before", value=1500)
            r_after = st.number_input("Rating After", value=1520)
            upsolved = st.number_input("Upsolved Count", min_value=0, step=1)
            notes = st.text_area("Notes / Learnings")
            
        submit = st.form_submit_button("Add to Log")
        if submit:
            delta = r_after - r_before
            new_row = [plat, c_name, str(c_date), rank, solved, r_before, r_after, delta, upsolved, notes]
            progress_worksheet.append_row(new_row)
            st.success("Successfully logged your contest and synced to Google Sheets!")
            st.rerun()