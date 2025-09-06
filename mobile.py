import streamlit as st
import random
import time
import pandas as pd

# -------------------------------
# Page Config
# -------------------------------
st.set_page_config(page_title="Safety Points Mobile Demo", layout="centered")

st.markdown("<h2 style='text-align:center'>🚦 Gamified Road Safety (Mobile Demo)</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center'>Avishkar 2025 – Safe Driving + Ambulance Priority + Badges + Profile</p>", unsafe_allow_html=True)

# -------------------------------
# Session State Init
# -------------------------------
if "points" not in st.session_state:
    st.session_state.points = 0
if "leaderboard" not in st.session_state:
    st.session_state.leaderboard = {"Driver A": 120, "Driver B": 95, "Driver C": 80}
if "trip_log" not in st.session_state:
    st.session_state.trip_log = []
if "badges" not in st.session_state:
    st.session_state.badges = []
if "safe_streak" not in st.session_state:
    st.session_state.safe_streak = 0
if "trips_completed" not in st.session_state:
    st.session_state.trips_completed = 0
if "history" not in st.session_state:
    st.session_state.history = []

# -------------------------------
# Driver Profile
# -------------------------------
st.markdown("### 👤 Driver Profile")
col1, col2 = st.columns(2)
with col1:
    driver_name = st.text_input("Name:", "You")
    age = st.number_input("Age:", min_value=18, max_value=100, value=25)
with col2:
    license_no = st.text_input("License No:", "MH-00-0000")
    vehicle_type = st.selectbox("Vehicle Type:", ["Car", "Bike", "Auto"])

st.markdown(f"**Total Trips Completed:** {st.session_state.trips_completed}")
st.markdown(f"**Total Points Earned:** {st.session_state.points}")

# -------------------------------
# Trip Settings
# -------------------------------
st.markdown("### ⚙️ Trip Settings")
col1, col2 = st.columns(2)
with col1:
    urgency_mode = st.checkbox("🚨 Urgency Mode", value=False)
with col2:
    ambulance_mode = st.checkbox("🚑 Ambulance Priority Mode", value=False)

# -------------------------------
# Start Trip Simulation
# -------------------------------
if st.button("▶️ Start Trip"):
    st.markdown("### Trip started... Driving 🚗💨")
    
    st.session_state.trips_completed += 1
    trip_badges = []
    trip_points = 0
    trip_details = []

    for km in range(1, 6):
        time.sleep(0.5)
        violation = random.random() < 0.2
        ambulance_event = ambulance_mode and random.random() < 0.3

        if urgency_mode:
            if violation:
                st.warning(f"⚠️ KM {km}: Violation ignored (Urgency Mode)")
                trip_details.append((km, "Urgent Violation"))
            else:
                st.info(f"ℹ️ KM {km}: Safe driving (Urgency Mode)")
                trip_details.append((km, "Urgent Safe"))
            st.session_state.safe_streak = 0
        else:
            if violation:
                st.session_state.points -= 5
                trip_points -= 5
                st.warning(f"❌ KM {km}: Violation -5 pts")
                trip_details.append((km, "Violation"))
                st.session_state.safe_streak = 0
            else:
                st.session_state.points += 10
                trip_points += 10
                st.success(f"✅ KM {km}: Safe +10 pts")
                trip_details.append((km, "Safe"))
                st.session_state.safe_streak += 1

            if ambulance_event:
                st.balloons()
                st.success(f"🚑 KM {km}: Ambulance nearby — Bonus +5 pts!")
                st.session_state.points += 5
                trip_points += 5
                trip_details.append((km, "Ambulance Bonus"))
                if "Life Saver 🏅" not in trip_badges:
                    trip_badges.append("Life Saver 🏅")

    # Streak & Zero Violation Badges
    if st.session_state.safe_streak >= 3:
        trip_badges.append("Streak Master 🔥")
    if all(status == "Safe" for km, status in trip_details[-5:]):
        trip_badges.append("Zero Violation Hero 🛡️")

    # Update global badges
    for badge in trip_badges:
        if badge not in st.session_state.badges:
            st.session_state.badges.append(badge)

    # Save trip history
    st.session_state.history.append({
        "Trip": st.session_state.trips_completed,
        "Points": trip_points,
        "Badges": ", ".join(trip_badges),
        "Urgency": urgency_mode,
        "Ambulance Mode": ambulance_mode
    })

    st.write("Trip ended ✅")

# -------------------------------
# Scoreboard
# -------------------------------
st.markdown("### 🎯 Score")
st.metric("Points", st.session_state.points)

st.session_state.leaderboard[driver_name] = st.session_state.points

st.markdown("### 🏆 Leaderboard")
for rank, (driver, score) in enumerate(sorted(st.session_state.leaderboard.items(), key=lambda x: x[1], reverse=True), start=1):
    st.markdown(f"{rank}. {driver} — {score} pts")

# -------------------------------
# Rewards
# -------------------------------
st.markdown("### 🎁 Rewards")
if urgency_mode:
    st.info("Urgency Mode: Rewards disabled")
elif st.session_state.points >= 100:
    st.success("🎉 You unlocked a ₹50 Fuel Voucher!")
else:
    st.info("Earn 100+ points to unlock rewards")

# -------------------------------
# Trip Log
# -------------------------------
st.markdown("### 📜 Trip Log")
if st.session_state.trip_log:
    df = pd.DataFrame(st.session_state.trip_log, columns=["KM", "Status"])
    st.dataframe(df, use_container_width=True)
else:
    st.info("No trips yet. Start one above")

# -------------------------------
# Badges
# -------------------------------
st.markdown("### 🏅 Badges Earned")
if st.session_state.badges:
    for badge in st.session_state.badges:
        st.markdown(f"- {badge}")
else:
    st.info("No badges yet — try safe driving or ambulance compliance")

# -------------------------------
# Trip History
# -------------------------------
st.markdown("### 📈 Trip History")
if st.session_state.history:
    history_df = pd.DataFrame(st.session_state.history)
    st.dataframe(history_df, use_container_width=True)
else:
    st.info("No trip history yet")
