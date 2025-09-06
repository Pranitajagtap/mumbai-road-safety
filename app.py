import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
import random

st.set_page_config(page_title="🚦 Mumbai Road Safety Points", layout="wide")
st.title("🚦 Gamified Safety Points – Mumbai Prototype")
st.write("**Avishkar 2025 – AI-Powered Road Safety System**")

# -------------------------
# Initialize Session State
# -------------------------
for var in ["points", "violations", "safe_points", "trip_data", "risk_level", "longest_safe_streak"]:
    if var not in st.session_state:
        st.session_state[var] = 0 if var=="points" else []

# -------------------------
# Train Risk Model (Simulated)
# -------------------------
def train_risk_model():
    X, y = [], []
    for _ in range(300):
        speed = random.randint(20, 100)
        violations = random.randint(0, 5)
        trip_len = random.randint(5, 20)
        risk = 2 if speed>70 or violations>=3 else 1 if speed>55 or violations==2 else 0
        X.append([speed, violations, trip_len])
        y.append(risk)
    model = LogisticRegression(max_iter=2000)
    model.fit(X, y)
    return model

model = train_risk_model()

# -------------------------
# Sidebar: Trip Scenario
# -------------------------
st.sidebar.header("📂 Select Trip Scenario")
trip_scenario = st.sidebar.radio(
    "Choose Trip Type:",
    ["Mixed Mumbai Trip (realistic violations)", "Perfect Safe Mumbai Trip (all green)"]
)
dataset_map = {
    "Mixed Mumbai Trip (realistic violations)": "mumbai_trip.csv",
    "Perfect Safe Mumbai Trip (all green)": "mumbai_safe_trip.csv"
}

# -------------------------
# Start Simulation
# -------------------------
if st.sidebar.button("▶️ Start Simulation"):
    # Reset session variables
    st.session_state.points = 0
    st.session_state.violations = []
    st.session_state.safe_points = []
    st.session_state.trip_data = []
    st.session_state.risk_level = None
    st.session_state.longest_safe_streak = 0

    df = pd.read_csv(dataset_map[trip_scenario])
    st.success(f"Trip loaded: {trip_scenario}")
    st.write("Trip started... 🚗💨")

    current_streak = 0
    max_streak = 0

    # Process each KM
    for _, row in df.iterrows():
        km, speed, lat, lon = row["km"], row["speed"], row["lat"], row["lon"]
        
        if speed > 60:
            st.session_state.points -= 5
            st.session_state.violations.append({
                "km": km,
                "type": "Speeding",
                "speed": speed,
                "lat": lat,
                "lon": lon
            })
            status = "❌ Violation (-5)"
            current_streak = 0
        else:
            st.session_state.points += 10
            st.session_state.safe_points.append({
                "km": km,
                "speed": speed,
                "lat": lat,
                "lon": lon
            })
            status = "✅ Safe (+10)"
            current_streak += 1
            max_streak = max(max_streak, current_streak)

        st.session_state.trip_data.append({
            "KM": km,
            "Speed": speed,
            "Status": status,
            "Total Points": st.session_state.points,
            "lat": lat,
            "lon": lon
        })

    st.session_state.longest_safe_streak = max_streak
    st.info("Trip ended ✅")

    # Risk prediction
    avg_speed = df["speed"].mean()
    violations_count = len(st.session_state.violations)
    trip_len = len(df)
    pred = model.predict([[avg_speed, violations_count, trip_len]])[0]
    risk_map = {0:"🟢 Low Risk",1:"🟡 Medium Risk",2:"🔴 High Risk"}
    st.session_state.risk_level = (risk_map[pred], avg_speed, violations_count, trip_len)

# -------------------------
# Trip Summary
# -------------------------
if st.session_state.trip_data:
    st.subheader("📋 Trip Summary")
    st.dataframe(pd.DataFrame(st.session_state.trip_data))

# -------------------------
# Map Visualization
# -------------------------
st.subheader("🗺️ Trip Map")
m = folium.Map(location=[19.085,72.885], zoom_start=13)
if st.session_state.trip_data:
    coords = [(row["lat"], row["lon"]) for row in st.session_state.trip_data]
    folium.PolyLine(coords, color="blue", weight=3, opacity=0.7).add_to(m)

for v in st.session_state.violations:
    folium.Marker([v["lat"],v["lon"]],
                  popup=f"❌ {v['type']} {v['speed']} km/h (KM {v['km']})",
                  icon=folium.Icon(color="red",icon="exclamation")).add_to(m)
for s in st.session_state.safe_points:
    folium.Marker([s["lat"],s["lon"]],
                  popup=f"✅ Safe {s['speed']} km/h (KM {s['km']})",
                  icon=folium.Icon(color="green",icon="ok-sign")).add_to(m)
st_data = st_folium(m, width=700, height=400)

# -------------------------
# Score & Leaderboard
# -------------------------
st.subheader("🎯 Current Score")
st.metric("Points", st.session_state.points)

leaderboard = {"You": st.session_state.points,"Driver A":120,"Driver B":95,"Driver C":80}
sorted_lb = dict(sorted(leaderboard.items(), key=lambda x:x[1], reverse=True))
st.subheader("🏆 Leaderboard")
for rank,(driver,score) in enumerate(sorted_lb.items(),start=1):
    st.write(f"{rank}. {driver} — {score} pts")

# -------------------------
# Rewards + Progress
# -------------------------
st.subheader("🎁 Rewards & Progress")
reward_levels = [
    {"points":70,"reward":"Bronze Badge 🥉"},
    {"points":100,"reward":"₹50 Fuel Voucher ⛽"},
    {"points":150,"reward":"Silver Badge 🥈"},
    {"points":200,"reward":"Gold Badge 🥇 + Extra Rewards 🎉"},
]
current_points = st.session_state.points
next_reward = None
for rl in reward_levels:
    if current_points < rl["points"]:
        next_reward = rl
        break
if next_reward:
    progress = current_points / next_reward["points"]
    st.progress(min(progress,1.0))
    st.write(f"⭐ {current_points}/{next_reward['points']} → Next: {next_reward['reward']}")
else:
    st.success("🏆 All rewards unlocked! 🚗💨")

unlocked = [rl["reward"] for rl in reward_levels if current_points >= rl["points"]]
if unlocked:
    st.success("✅ Rewards Unlocked: "+", ".join(unlocked))

st.subheader("🏅 Rewards Gallery")
cols = st.columns(len(reward_levels))
for idx, rl in enumerate(reward_levels):
    with cols[idx]:
        if current_points >= rl["points"]:
            st.success(f"✅ {rl['reward']}")
        else:
            st.info(f"🔒 {rl['reward']}")

# -------------------------
# Analytics Charts
# -------------------------
st.subheader("📊 Driving Analytics")
if st.session_state.trip_data:
    df_plot = pd.DataFrame(st.session_state.trip_data)
    # Speed per KM
    fig, ax = plt.subplots()
    ax.plot(df_plot["KM"], df_plot["Speed"], marker="o", label="Speed")
    ax.axhline(60,color="red",linestyle="--",label="Speed Limit")
    ax.set_xlabel("KM"); ax.set_ylabel("Speed (km/h)"); ax.set_title("Speed per KM"); ax.legend()
    st.pyplot(fig)
    # Points accumulation
    fig2, ax2 = plt.subplots()
    ax2.plot(df_plot["KM"], df_plot["Total Points"], marker="s", color="green", label="Points")
    ax2.set_xlabel("KM"); ax2.set_ylabel("Points"); ax2.set_title("Points Accumulated"); ax2.legend()
    st.pyplot(fig2)
    # Safe vs Violations Pie
    fig3, ax3 = plt.subplots()
    safe_count = len(st.session_state.safe_points)
    violation_count = len(st.session_state.violations)
    ax3.pie([safe_count,violation_count],labels=["Safe","Violations"],autopct="%1.1f%%",colors=["green","red"])
    ax3.set_title("Safe vs Violations")
    st.pyplot(fig3)

# -------------------------
# Risk Prediction
# -------------------------
if st.session_state.risk_level:
    risk_label, avg_speed, violations_count, trip_len = st.session_state.risk_level
    st.subheader("🤖 AI-Powered Risk Prediction")
    st.success(f"Predicted Driving Risk Level: {risk_label}")
    st.write(f"• Average Speed = {avg_speed:.1f} km/h")
    st.write(f"• Violations = {violations_count}")
    st.write(f"• Trip Length = {trip_len} km")
    st.write(f"• Longest Safe Streak = {st.session_state.longest_safe_streak} KM")
