import streamlit as st
import random
import time
import os
import json
import hashlib
import pandas as pd
import plotly.express as px

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

st.set_page_config(page_title="Multiplayer Stone Paper Scissor", page_icon="✂️")

# ===== Constants =====
YOU_DICT = {"Stone": 0, "Paper": 1, "Scissor": 2}
REVERSE_DICT = {0: "Stone", 1: "Paper", 2: "Scissor"}
USERS_FILE = "users.json"
TIMER_LIMIT = 10  # seconds

# ===== Load/Create User Database =====
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump([], f)

with open(USERS_FILE, "r") as f:
    USERS = json.load(f)

# ===== Login System =====
with st.sidebar:
    st.title("🔐 Login")
    st.subheader("Player 1 Login")
    username1 = st.text_input("Username (P1)")
    password1 = st.text_input("Password (P1)", type="password")

    st.subheader("Player 2 Login")
    username2 = st.text_input("Username (P2)")
    password2 = st.text_input("Password (P2)", type="password")

    login_btn = st.button("Login Both")

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if login_btn:
        user1 = next((u for u in USERS if u["username"] == username1 and u["password"] == hash_password(password1)), None)
        user2 = next((u for u in USERS if u["username"] == username2 and u["password"] == hash_password(password2)), None)
        if user1 and user2:
            st.session_state.logged_in = True
            st.session_state.username1 = username1
            st.session_state.username2 = username2
            st.success(f"Welcome {username1} and {username2}!")
        else:
            st.error("Invalid credentials for one or both players")

    with st.expander("📝 Register New Players"):
        new_user = st.text_input("New Username")
        new_pass = st.text_input("New Password", type="password")
        if st.button("Register"):
            if any(u["username"] == new_user for u in USERS):
                st.warning("Username already exists")
            else:
                USERS.append({"username": new_user, "password": hash_password(new_pass)})
                with open(USERS_FILE, "w") as f:
                    json.dump(USERS, f, indent=4)
                st.success("Registered successfully!")

# ===== Stop if not logged in =====
if not st.session_state.logged_in:
    st.warning("Please log in with both players to access the game.")
    st.stop()

# ===== Game UI =====
st.title("🪨📄✂️ Stone - Paper - Scissor Game")
mode = st.radio("Choose Mode:", ["Player vs Computer", "Player vs Player"])
if mode == "Player vs Computer":
    difficulty = st.radio("Select Difficulty:", ["Easy", "Hard"])
else:
    difficulty = None

if "score1" not in st.session_state:
    st.session_state.score1 = 0
    st.session_state.score2 = 0
    st.session_state.history = []
    st.session_state.round = 0
    st.session_state.locked_choice1 = None
    st.session_state.game_completed = False

start_time = time.time()

if st.session_state.round >= 5:
    st.session_state.game_completed = True

if st.session_state.game_completed:
    st.success("🎉 **GAME COMPLETED!** All 5 rounds finished!")
    if st.session_state.score1 > st.session_state.score2:
        st.balloons()
        st.success(f"🏆 **{st.session_state.username1} WINS THE MATCH!**")
    elif st.session_state.score2 > st.session_state.score1:
        st.balloons()
        winner_name = st.session_state.username2 if mode == "Player vs Player" else "Computer"
        st.success(f"🏆 **{winner_name} WINS THE MATCH!**")
    else:
        st.info("🤝 **IT'S A TIE!** Great match!")

    st.write(f"Final Score: {st.session_state.username1}: {st.session_state.score1} | {st.session_state.username2 if mode == 'Player vs Player' else 'Computer'}: {st.session_state.score2}")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 **REMATCH**", type="primary"):
            st.session_state.score1 = 0
            st.session_state.score2 = 0
            st.session_state.history = []
            st.session_state.round = 0
            st.session_state.locked_choice1 = None
            st.session_state.game_completed = False
            st.success("New match started! Good luck!")
            st.rerun()
    st.divider()

if not st.session_state.game_completed:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(f"🧑 {st.session_state.username1} (Player 1)")
        if st.session_state.locked_choice1 is None:
            choice1 = st.radio("Choose:", ["Stone", "Paper", "Scissor"], key="p1")
            if st.button("🔒 Lock Choice"):
                st.session_state.locked_choice1 = choice1
        else:
            st.success(f"Choice locked: {st.session_state.locked_choice1}")

    with col2:
        if mode == "Player vs Player":
            st.subheader(f"👳️ {st.session_state.username2} (Player 2)")
            choice2 = st.radio("Choose:", ["Stone", "Paper", "Scissor"], key="p2")
        else:
            st.subheader("🤖 Computer will choose automatically")
            if difficulty == "Easy":
                choice2 = random.choice(["Stone", "Paper", "Scissor"])
            else:
                last_choice = st.session_state.locked_choice1
                if last_choice == "Stone":
                    choice2 = "Paper"
                elif last_choice == "Paper":
                    choice2 = "Scissor"
                elif last_choice == "Scissor":
                    choice2 = "Stone"
                else:
                    choice2 = random.choice(["Stone", "Paper", "Scissor"])

    if st.button("🎯 Play Round"):
        if st.session_state.locked_choice1 is None:
            st.warning("Player 1 must lock their choice first")
        else:
            if time.time() - start_time > TIMER_LIMIT:
                st.warning("⏱️ Time's up! You took too long.")
                st.session_state.score2 += 1
            else:
                you = YOU_DICT[st.session_state.locked_choice1]
                opponent = YOU_DICT[choice2]

                st.write(f"🧑 {st.session_state.username1} chose: **{st.session_state.locked_choice1}**")
                st.write(f"👳️ {st.session_state.username2 if mode == 'Player vs Player' else 'Computer'} chose: **{choice2}**")

                if you == opponent:
                    result = "Draw"
                    st.info("It's a draw!")
                elif (you - opponent) % 3 == 1:
                    result = st.session_state.username1
                    st.success("✅ Player 1 Wins This Round!")
                    st.session_state.score1 += 1
                else:
                    result = st.session_state.username2 if mode == "Player vs Player" else "Computer"
                    st.success(f"✅ {result} Wins This Round!")
                    st.session_state.score2 += 1

                st.session_state.round += 1
                st.session_state.history.append({"Round": st.session_state.round, "P1": st.session_state.locked_choice1, "P2": choice2, "Winner": result})

                st.balloons()
                st.success(f"🎯 **ROUND {st.session_state.round} COMPLETED!**")

                st.progress(st.session_state.round / 5)
                st.write(f"Progress: {st.session_state.round}/5 rounds completed")

                st.session_state.locked_choice1 = None

st.divider()
st.subheader("🏆 Scoreboard")
st.write(f"👉 {st.session_state.username1}: {st.session_state.score1}")
st.write(f"💻 {st.session_state.username2 if mode == 'Player vs Player' else 'Computer'}: {st.session_state.score2}")

if st.session_state.history:
    st.subheader("📜 Match History")
    df = pd.DataFrame(st.session_state.history)
    st.table(df)

    st.subheader("📊 Win/Loss Trends")
    chart_df = df.copy()
    chart_df = chart_df[chart_df['Winner'] != 'Draw']
    if not chart_df.empty:
        fig = px.histogram(chart_df, x="Winner", color="Winner", title="Round-wise Win Distribution", nbins=5)
        st.plotly_chart(fig, use_container_width=True)

if not st.session_state.game_completed:
    if st.button("🔁 Reset Game"):
        st.session_state.score1 = 0
        st.session_state.score2 = 0
        st.session_state.history = []
        st.session_state.round = 0
        st.session_state.locked_choice1 = None
        st.session_state.game_completed = False
        st.success("Game reset successfully!")

with st.expander("🍗 Want Theme Support?"):
    st.markdown(
        """
        Streamlit uses your system/browser theme.  
        To switch manually:
        1. Click top-right ☰ menu
        2. Choose **Settings**
        3. Select light/dark theme
        """
    )
