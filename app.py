"""
app.py — ORBIT interactive app.

Everything is typed into the app itself — you never open or edit the CSV
by hand. The CSV is just where the app remembers your data between runs.

First run: it asks you to name the habit you're building.
Every run after: log today's numbers, and flip between Week / Month / All
Time to see the black hole and constellation for that window.

Run with: streamlit run app.py
"""

import os
import json
import datetime
import pandas as pd
import streamlit as st
from orbit_core import load_data, draw_black_hole, draw_constellation, filter_period, save_combined

CSV_PATH = "data_log.csv"
CONFIG_PATH = "config.json"

st.set_page_config(page_title="ORBIT", page_icon="🌌", layout="wide")

# ---------- load / create config (remembers your habit name) ----------
if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH) as f:
        config = json.load(f)
else:
    config = {"habit_name": ""}

# ---------- load / create data log ----------
if not os.path.exists(CSV_PATH):
    pd.DataFrame(columns=[
        "date", "total_screentime_minutes", "instagram_minutes",
        "habit_minutes", "habit_done"
    ]).to_csv(CSV_PATH, index=False)

df = load_data(CSV_PATH)

st.markdown(
    "<h1 style='text-align:center;'>🌌 ORBIT</h1>"
    "<p style='text-align:center;color:#999;'>Same data. Two futures. "
    "One black hole, one constellation.</p>",
    unsafe_allow_html=True,
)

# ---------- ask for habit name (only truly required once, but always editable) ----------
st.subheader("Your habit")
habit_name = st.text_input(
    "What habit are you building? (e.g. Reading, Gym, Guitar, Sleep by 11pm)",
    value=config.get("habit_name", ""),
    placeholder="Reading",
)
if habit_name != config.get("habit_name", ""):
    config["habit_name"] = habit_name
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f)

if not habit_name:
    st.warning("Type the habit you're building above to continue.")
    st.stop()

st.divider()

# ---------- typed input for today ----------
st.subheader(f"Log today — {datetime.date.today().strftime('%A, %d %b %Y')}")

already_logged_today = (
    len(df) > 0 and (df["date"].dt.date == datetime.date.today()).any()
)
if already_logged_today:
    st.info("You already logged today. Adding again will add a second entry for today — "
            "use this if you're correcting a mistake, otherwise come back tomorrow.")

col1, col2, col3, col4 = st.columns(4)
with col1:
    total_min = st.number_input("Total screen time (minutes)", min_value=0,
                                 max_value=1440, value=300, step=5)
with col2:
    ig_min = st.number_input("Instagram time (minutes)", min_value=0,
                              max_value=1440, value=90, step=5)
with col3:
    habit_min = st.number_input(f"{habit_name} time today (minutes)", min_value=0,
                                 max_value=600, value=0, step=5)
with col4:
    habit_done = st.selectbox(f"Did you do {habit_name} today?", ["no", "yes"])

if st.button("➕ Add today", use_container_width=True):
    new_row = pd.DataFrame([{
        "date": datetime.date.today().isoformat(),
        "total_screentime_minutes": total_min,
        "instagram_minutes": ig_min,
        "habit_minutes": habit_min if habit_done == "yes" else 0,
        "habit_done": habit_done,
    }])
    df_raw = pd.read_csv(CSV_PATH)
    df_raw = pd.concat([df_raw, new_row], ignore_index=True)
    df_raw.to_csv(CSV_PATH, index=False)
    st.success("Today logged.")
    st.rerun()

st.divider()

# ---------- view toggle: Week / Month / All time ----------
if len(df) == 0:
    st.info("No days logged yet — add today's numbers above to see your galaxy.")
else:
    view = st.radio("View", ["This Week", "This Month", "All Time"],
                     horizontal=True, index=2)
    period_map = {"This Week": "week", "This Month": "month", "All Time": "all"}
    period_label_map = {"This Week": "This Week", "This Month": "This Month",
                         "All Time": "All Time"}
    period_df = filter_period(df, period_map[view])

    if len(period_df) == 0:
        st.info(f"No entries in {view.lower()} yet.")
    else:
        left, right = st.columns(2)
        fig1 = draw_black_hole(period_df, period_label=period_label_map[view])
        fig2 = draw_constellation(period_df, period_label=period_label_map[view],
                                   habit_name=habit_name)

        with left:
            st.pyplot(fig1, use_container_width=True)
        with right:
            st.pyplot(fig2, use_container_width=True)

        fig1.savefig("black_hole.png", dpi=150, facecolor="black")
        fig2.savefig("constellation.png", dpi=150, facecolor="black")
        save_combined("black_hole.png", "constellation.png", "combined.png")

    with st.expander("See raw logged data"):
        st.dataframe(df, use_container_width=True)

    if st.button("🗑️ Reset all data"):
        pd.DataFrame(columns=df.columns).to_csv(CSV_PATH, index=False)
        st.rerun()
