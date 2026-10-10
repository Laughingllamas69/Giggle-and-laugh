"""
Giggle and Laugh 😂 — Your Daily Dose of Happiness
A fun, lighthearted wellness & entertainment portal for everyone.
"""

import os
import json
import sqlite3
import hashlib
from datetime import datetime
import pandas as pd
import streamlit as st
import random

# Try to import custom UI helpers if they exist, otherwise use fallbacks
try:
    from app_ui import inject_css, hero_header
except ImportError:
    # Fallback dummy functions if app_ui.py is missing
    def inject_css():
        pass
    def hero_header(title, subtitle, chips=None):
        st.title(title)
        st.subheader(subtitle)
        if chips:
            cols = st.columns(len(chips))
            for col, chip in zip(cols, chips):
                col.info(chip)

DB_PATH = "giggle_laugh.db"
APP_TITLE = "Giggle and Laugh 😂"
APP_SUBTITLE = "Your Personal Hub for Fun, Games, and Good Vibes"

# --- Database Setup ---

def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    # Simplified table for mood tracking only
    cur.execute("""
        CREATE TABLE IF NOT EXISTS mood_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            mood_score INTEGER NOT NULL,
            recommended_content TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_mood_log(user_id, mood_score, recommendation):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO mood_logs (user_id, timestamp, mood_score, recommended_content)
        VALUES (?, ?, ?, ?)
        """,
        (
            user_id,
            datetime.now().isoformat(timespec="seconds"),
            mood_score,
            recommendation,
        ),
    )
    conn.commit()
    conn.close()

def get_user_history(user_id):
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM mood_logs WHERE user_id = ? ORDER BY timestamp ASC",
        conn,
        params=(user_id,),
    )
    conn.close()
    return df

def hash_pseudonym(raw_id: str) -> str:
    raw_id = raw_id.strip().lower()
    return "FUN-" + hashlib.sha256(raw_id.encode("utf-8")).hexdigest()[:8].upper()

# --- Content Data ---

JOKES_LIST = [
    {"category": "Puns", "text": "I used to be addicted to soap, but I'm clean now."},
    {"category": "Tech", "text": "Why do programmers prefer dark mode? Because light attracts bugs."},
    {"category": "Animals", "text": "What do you call a fake noodle? An Impasta."},
    {"category": "Work", "text": "I told my boss three companies were after me and I needed a raise to stay. He asked which companies. I said: Electricity, Water, and Gas."},
    {"category": "Science", "text": "Why can't you trust an atom? They make up everything."},
    {"category": "Food", "text": "Why did the coffee file a police report? It got mugged."},
    {"category": "General", "text": "Parallel lines have so much in common. It’s a shame they’ll never meet."},
    {"category": "Animals", "text": "What do you call a bear with no teeth? A gummy bear."},
    {"category": "Tech", "text": "There are 10 types of people in the world: those who understand binary, and those who don't."},
    {"category": "General", "text": "I'm reading a book about anti-gravity. It's impossible to put down!"},
]

MEME_TEMPLATES = [
    {"title": "Distracted Boyfriend", "desc": "Me looking at dessert when I said I'm on a diet.", "img_placeholder": "👀🍰"},
    {"title": "Drake Hotline Bling", "desc": "Working Hard: ❌ | Taking a Nap: ✅", "img_placeholder": "🙅‍♂️😴"},
    {"title": "Two Buttons", "desc": "Sleep Early vs. Watch One More Episode", "img_placeholder": "😵💤📺"},
    {"title": "Expanding Brain", "desc": "Coffee → Espresso → Caffeine IV Drip", "img_placeholder": "🧠☕⚡"},
    {"title": "This is Fine", "desc": "Me when the deadline is tomorrow but today is fine.", "img_placeholder": "🔥🐶☕"},
]

GAMES_HTML = """
<div style="text-align:center; font-family: sans-serif;">
    <h3>Click the Button!</h3>
    <p>How many times can you click it?</p>
    <button onclick="increment()" style="font-size: 24px; padding: 20px 40px; background-color: #FFD700; border: none; border-radius: 50%; cursor: pointer; box-shadow: 0 4px #999;">
        CLICK ME
    </button>
    <h2 id="count">0</h2>
    <script>
        let count = 0;
        function increment() {
            count++;
            document.getElementById('count').innerText = count;
            // Random color change
            const colors = ['#FF5733', '#33FF57', '#3357FF', '#F333FF'];
            document.querySelector('button').style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
        }
    </script>
</div>
"""

# --- Page Config ---

st.set_page_config(
    page_title="Giggle and Laugh",
    page_icon="😂",
    layout="wide",
    initial_sidebar_state="collapsed",
)

init_db()
inject_css()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = ""

# --- Sidebar Login ---

with st.sidebar:
    st.markdown("## 😂 Giggle and Laugh")
    st.caption(APP_SUBTITLE)
    st.divider()

    if not st.session_state.logged_in:
        st.markdown("### 👋 Welcome!")
        st.caption("Enter a nickname to start your fun session.")
        
        raw_id = st.text_input("Nickname", placeholder="e.g. Chuckles")
        
        if st.button("Start Laughing 🎈", use_container_width=True, type="primary"):
            if raw_id.strip():
                st.session_state.user_id = hash_pseudonym(raw_id)
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.warning("Please enter a nickname to continue.")
    else:
        st.success(f"Hi there, **{st.session_state.user_id}**")
        if st.button("End Session", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_id = ""
            st.rerun()

# --- Main Header ---

st.title("😂 Giggle and Laugh")
st.caption("Because life is too short to be serious all the time.")

if not st.session_state.logged_in:
    hero_header(
        "Welcome to Giggle and Laugh",
        "Play games, read jokes, view memes, and track your vibe.",
        chips=[
            "🎮 Mini Games",
            "😂 Hilarious Jokes",
            "🖼️ Meme Gallery",
            "🧘 Mood Tracker"
        ],
    )
    st.stop()

# --- Tabs ---

tab_vibe, tab_games, tab_memes, tab_jokes = st.tabs(
    [
        "🧘 Vibe Check",
        "🎮 Games Zone",
        "🖼️ Meme Gallery",
        "😂 Joke Factory",
    ]
)

# 1. VIBE CHECK (Formerly Assessment)
with tab_vibe:
    st.markdown("### How's your vibe today?")
    st.caption("Quickly tell us how you're feeling so we can recommend some content.")
    
    vibe_options = ["😢 Low Energy", "😐 Neutral", "🙂 Good", "🤩 Great"]
    vibe_scores = [1, 2, 3, 4]
    
    selected_vibe_idx = st.radio("Select your current mood:", range(len(vibe_options)), format_func=lambda x: vibe_options[x], horizontal=True)
    
    if st.button("Get Recommendation"):
        score = vibe_scores[selected_vibe_idx]
        rec_text = ""
        
        if score <= 2:
            rec_text = "You need a pick-me-up! Check out the 'Joke Factory' for puns, or play a game to distract yourself."
            st.info(rec_text)
        elif score == 3:
            rec_text = "Looking good! Maybe some funny memes will boost your mood even higher."
            st.success(rec_text)
        else:
            rec_text = "Wow, great energy! Share a joke with someone else to spread the love."
            st.balloons()
            st.success(rec_text)
            
        # Save to DB
        save_mood_log(st.session_state.user_id, score, rec_text)
        st.toast("Vibe logged successfully!")

    st.divider()
    st.markdown("#### Your Recent Vibes")
    history_df = get_user_history(st.session_state.user_id)
    if not history_df.empty:
        chart_df = history_df.copy()
        chart_df["timestamp"] = pd.to_datetime(chart_df["timestamp"])
        st.line_chart(chart_df.set_index("timestamp")[["mood_score"]])
    else:
        st.write("No vibes logged yet. Click above to log one!")

# 2. GAMES ZONE
with tab_games:
    st.markdown("### 🎮 Arcade Mode")
    st.write("Take a break and play a quick mini-game.")
    
    import streamlit.components.v1 as components
    
    # Simple Clicker Game
    components.html(GAMES_HTML, height=300)
    
    st.divider()
    
    # Simple Rock Paper Scissors using Streamlit buttons
    st.markdown("#### ✊✋✌️ Rock, Paper, Scissors")
    
    if "rps_result" not in st.session_state:
        st.session_state.rps_result = "Make your move!"
        
    choices = ["Rock", "Paper", "Scissors"]
    col1, col2, col3 = st.columns(3)
    
    def play_rps(choice):
        computer = random.choice(choices)
        msg = f"You chose {choice}. Computer chose {computer}. "
        
        if choice == computer:
            msg += "It's a tie! 🤝"
        elif (choice == "Rock" and computer == "Scissors") or \
             (choice == "Paper" and computer == "Rock") or \
             (choice == "Scissors" and computer == "Paper"):
            msg += "You win! 🏆"
        else:
            msg += "You lose! 😅"
            
        st.session_state.rps_result = msg
        
    with col1:
        if st.button("Rock", use_container_width=True):
            play_rps("Rock")
    with col2:
        if st.button("Paper", use_container_width=True):
            play_rps("Paper")
    with col3:
        if st.button("Scissors", use_container_width=True):
            play_rps("Scissors")
            
    st.info(st.session_state.rps_result)

# 3. MEME GALLERY
with tab_memes:
    st.markdown("### 🖼️ Meme Gallery")
    st.caption("Fresh memes to brighten your day.")
    
    # Display memes in columns
    cols = st.columns(2)
    
    for i, meme in enumerate(MEME_TEMPLATES):
        col = cols[i % 2]
        with col:
            st.markdown(f"**{meme['title']}**")
            # Using emoji placeholders since we don't have image URLs/API keys here
            st.markdown(f"<div style='background-color:#f0f2f6; padding:20px; text-align:center; font-size:50px; border-radius:10px;'>{meme['img_placeholder']}</div>", unsafe_allow_html=True)
            st.caption(meme['desc'])
            st.divider()

# 4. JOKE FACTORY
with tab_jokes:
    st.markdown("### 😂 Joke Factory")
    
    category_filter = st.selectbox("Filter by Category", ["All"] + list(set([j['category'] for j in JOKES_LIST])))
    
    filtered_jokes = JOKES_LIST if category_filter == "All" else [j for j in JOKES_LIST if j['category'] == category_filter]
    
    if filtered_jokes:
        # Show random joke first
        st.markdown("#### 🔥 Hot Joke of the Moment")
        random_joke = random.choice(filtered_jokes)
        st.markdown(f"> **{random_joke['text']}**")
        st.caption(f"— Category: {random_joke['category']}")
        
        if st.button("Give me another one! 🔄"):
            st.rerun()
            
        st.divider()
        st.markdown("#### All Jokes")
        for joke in filtered_jokes:
            with st.expander(f"{joke['category']}: {joke['text'][:30]}..."):
                st.markdown(joke['text'])
    else:
        st.warning("No jokes found in this category.")```python
        st.warning("No jokes found in this category.")
