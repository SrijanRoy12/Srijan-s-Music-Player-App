import os
import pandas as pd
import streamlit as st
from pygame import mixer
from datetime import datetime
import base64
from PIL import Image

# ========== INIT MIXER ==========
mixer.init()

# ========== CONFIG ==========
MUSIC_FOLDER = r"C:\Users\Srijan Roy\OneDrive\Desktop\music"
LOGO_PATH = r"C:\Users\Srijan Roy\OneDrive\Documents\musiccc app\logo 1.jpeg"
BG_IMAGE_PATH = "black_wire_headphone_blue_background_hd_music.jpg"

# ========== BACKGROUND IMAGE & THEME ==========
def get_base64_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def set_app_style():
    bg_img = get_base64_image(BG_IMAGE_PATH)
    theme = st.session_state.get("theme", "Dark")
    text_color = "white" if theme == "Dark" else "black"
    bg_color = "rgba(0,0,0,0.6)" if theme == "Dark" else "rgba(255,255,255,0.6)"

    st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{bg_img}");
        background-size: cover;
        background-attachment: fixed;
        background-repeat: no-repeat;
        color: {text_color} !important;
        position: relative;
        min-height: 100vh;
    }}
    .stSidebar {{
        background-color: rgba(0,0,0,0.8);
    }}
    .main .block-container {{
        padding-bottom: 100px;
    }}
    </style>
    """, unsafe_allow_html=True)

# ========== LOAD MUSIC ==========
def load_music(folder):
    data = []
    for root, dirs, files in os.walk(folder):
        for file in sorted(files):
            if file.endswith((".mp3", ".wav", ".ogg")):
                path = os.path.join(root, file)
                name = os.path.splitext(file)[0]
                data.append({'Song-Name': name, 'Audio_Path': path, 'Artist': os.path.basename(root)})
    return pd.DataFrame(data)

# ========== AUDIO CONTROLS ==========
def play_audio(path, name):
    if mixer.music.get_busy():
        mixer.music.stop()
    mixer.music.load(path)
    mixer.music.play()
    st.session_state.current_song = name
    st.session_state.current_audio_path = path
    st.session_state.is_playing = True
    st.session_state.is_paused = False
    st.session_state.start_time = datetime.now()

    if st.session_state.library_df is not None:
        matches = st.session_state.library_df[st.session_state.library_df["Song-Name"] == name]
        if not matches.empty:
            st.session_state.current_index = matches.index[0]

    if name not in [s["Song-Name"] for s in st.session_state.recently_played]:
        st.session_state.recently_played.insert(0, {
            "Song-Name": name, "Audio_Path": path
        })
        if len(st.session_state.recently_played) > 10:
            st.session_state.recently_played.pop()

def pause_audio():
    mixer.music.pause()
    st.session_state.is_playing = False
    st.session_state.is_paused = True

def unpause_audio():
    mixer.music.unpause()
    st.session_state.is_playing = True
    st.session_state.is_paused = False

def play_next_song():
    if st.session_state.library_df is not None and st.session_state.current_index != -1:
        next_index = st.session_state.current_index + 1
        if next_index < len(st.session_state.library_df):
            next_row = st.session_state.library_df.iloc[next_index]
            play_audio(next_row["Audio_Path"], next_row["Song-Name"])

def play_previous_song():
    if st.session_state.library_df is not None and st.session_state.current_index > 0:
        prev_index = st.session_state.current_index - 1
        prev_row = st.session_state.library_df.iloc[prev_index]
        play_audio(prev_row["Audio_Path"], prev_row["Song-Name"])

# ========== SESSION INIT ==========
for key, value in {
    "favorites": [],
    "recently_played": [],
    "current_song": None,
    "current_audio_path": None,
    "is_playing": False,
    "is_paused": False,
    "start_time": None,
    "theme": "Dark",
    "profile_name": "Guest",
    "default_volume": 80,
    "avatar_img": None,
    "library_df": None,
    "current_index": -1
}.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ========== UI SETUP ==========
set_app_style()
df = load_music(MUSIC_FOLDER)
df = df.sort_values("Song-Name").reset_index(drop=True)
st.session_state.library_df = df

# Add Font Awesome and custom styles
st.markdown("""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css">
<style>
    /* Social Icons */
    .social-icons-floating {
        position: fixed;
        bottom: 80px;
        right: 20px;
        display: flex;
        flex-direction: column;
        gap: 15px;
        z-index: 100;
    }

    .social-icons-floating a {
        color: white;
        background: rgba(0,0,0,0.7);
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        text-decoration: none;
        transition: all 0.3s ease;
        box-shadow: 0 2px 5px rgba(0,0,0,0.3);
    }

    .social-icons-floating a:hover {
        background: rgba(30,144,255,0.9);
        transform: translateY(-3px);
    }

    /* Footer */
    .footer {
        position: fixed !important;
        bottom: 20px !important;
        left: 20px !important;
        color: white;
        font-size: 0.8rem;
        background: rgba(0,0,0,0.7);
        padding: 8px 15px;
        border-radius: 20px;
        z-index: 100;
    }

    .footer strong {
        color: #1e90ff;
    }

    /* Song Cards */
    .song-card {
        background-color: rgba(255, 255, 255, 0.08);
        padding: 15px;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
        margin-bottom: 15px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.2);
    }
    .song-card h4 {
        color: white;
        margin-bottom: 5px;
    }
    .song-card p {
        color: #aaa;
        font-size: 0.9rem;
    }
    .stButton>button {
        width: 100%;
        margin-top: 5px;
    }

    /* Player Controls */
    .bottom-bar {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: rgba(0,0,0,0.85);
        padding: 10px 20px;
        z-index: 100;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .control-buttons {
        display: flex;
        gap: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ========== SIDEBAR ==========
if os.path.exists(LOGO_PATH):
    logo = Image.open(LOGO_PATH)
    st.sidebar.image(logo, use_container_width=True)  # Changed from use_column_width to use_container_width
else:
    st.sidebar.title("🎵 Srijan's Music")

if st.session_state["avatar_img"]:
    st.sidebar.image(st.session_state["avatar_img"], width=100)
st.sidebar.markdown(f"### 👤 {st.session_state['profile_name']}")

menu = st.sidebar.radio("Navigate", ["🎵 Library", "▶ Now Playing", "❤️ Favorites", "🕒 Recently Played", "⚙️ Settings"])

# ========== LIBRARY ==========
# ========== LIBRARY ==========
if menu == "🎵 Library":
    st.markdown("<h2 style='color: limegreen;'>🎶 Srijan's Personal Music App</h2>", unsafe_allow_html=True)

    # Add search bar at the top
    search_query = st.text_input("🔍 Search for songs...", "")
    
    if st.session_state.current_song:
        st.success(f"🎧 Now Playing: {st.session_state.current_song}")

    # Filter songs based on search query
    if search_query:
        filtered_df = df[df['Song-Name'].str.contains(search_query, case=False) | 
                      df['Artist'].str.contains(search_query, case=False)]
    else:
        filtered_df = df

    if len(filtered_df) == 0:
        st.warning("No songs found matching your search.")
    else:
        for i in range(0, len(filtered_df), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(filtered_df):
                    row = filtered_df.iloc[i + j]
                    with cols[j]:
                        st.markdown("<div class='song-card'>", unsafe_allow_html=True)
                        st.markdown(f"<h4>{row['Song-Name']}</h4>", unsafe_allow_html=True)
                        st.markdown(f"<p>{row['Artist']}</p>", unsafe_allow_html=True)

                        label = "⏸" if st.session_state.is_playing and st.session_state.current_song == row["Song-Name"] else "▶"
                        if st.button(label, key=f"play_{row['Song-Name']}"):
                            if label == "▶":
                                play_audio(row["Audio_Path"], row["Song-Name"])
                            else:
                                pause_audio()
                            st.rerun()

                        fav = any(f["Song-Name"] == row["Song-Name"] for f in st.session_state.favorites)
                        icon = "💖" if fav else "🤍"
                        if st.button(icon, key=f"fav_{row['Song-Name']}"):
                            if fav:
                                st.session_state.favorites = [f for f in st.session_state.favorites if f["Song-Name"] != row["Song-Name"]]
                            else:
                                st.session_state.favorites.append(row.to_dict())
                            st.rerun()

                        st.markdown("</div>", unsafe_allow_html=True)

# ========== NOW PLAYING ==========
elif menu == "▶ Now Playing":
    st.header("▶ Now Playing")
    if st.session_state.current_song:
        st.subheader(st.session_state.current_song)
        elapsed = (datetime.now() - st.session_state.start_time).seconds if st.session_state.start_time else 0
        st.progress(min(elapsed / 180, 1.0))
        st.caption(f"{elapsed//60}:{elapsed%60:02d} / 3:00")

        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("⏮ Previous"):
                play_previous_song()
                st.rerun()
        with col2:
            if st.session_state.is_playing:
                if st.button("⏸ Pause"):
                    pause_audio()
                    st.rerun()
            else:
                if st.button("▶ Resume"):
                    unpause_audio()
                    st.rerun()
        with col3:
            if st.button("⏭ Next"):
                play_next_song()
                st.rerun()

        volume = st.slider("🔊 Volume", 0, 100, st.session_state.default_volume)
        mixer.music.set_volume(volume / 100)
    else:
        st.info("No song currently playing")

# ========== FAVORITES ==========
elif menu == "❤️ Favorites":
    st.header("💖 Favorite Songs")
    if st.session_state.favorites:
        for song in st.session_state.favorites:
            st.markdown(f"**{song['Song-Name']}**  \n{song['Artist']}")
        df_fav = pd.DataFrame(st.session_state.favorites)
        csv = df_fav.to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Download Playlist as CSV", csv, file_name="favorites.csv", mime='text/csv')
    else:
        st.info("No favorites yet!")

# ========== RECENTLY PLAYED ==========
elif menu == "🕒 Recently Played":
    st.header("🕒 Recently Played")
    if st.session_state.recently_played:
        for song in st.session_state.recently_played:
            st.markdown(f"**{song['Song-Name']}**")
    else:
        st.info("You haven't played any songs yet.")

# ========== SETTINGS ==========
elif menu == "⚙️ Settings":
    st.header("⚙️ Settings & Personalization")

    profile_name = st.text_input("Your Display Name", st.session_state["profile_name"])
    theme = st.radio("Theme", ["Dark", "Light"], index=0 if st.session_state.theme == "Dark" else 1)
    volume = st.slider("Default Volume", 0, 100, st.session_state.default_volume)
    uploaded_avatar = st.file_uploader("Upload Profile Avatar", type=["jpg", "png", "jpeg"])

    if uploaded_avatar:
        st.session_state["avatar_img"] = uploaded_avatar.getvalue()

    if st.button("Save Settings"):
        st.session_state["profile_name"] = profile_name
        st.session_state["theme"] = theme
        st.session_state["default_volume"] = volume
        st.success("✅ Settings updated!")

    st.markdown("---")
    st.markdown("🚧 **Coming Soon:**")
    st.markdown("- Theme switch with transitions (Added)")
    st.markdown("- Custom equalizer and audio preferences")
    st.markdown("- Profile avatar and preferences (Added)")
    st.markdown("- Download and export playlists (Added)")

# ========== MINI MUSIC BAR ==========
if st.session_state.current_song:
    elapsed = (datetime.now() - st.session_state.start_time).seconds if st.session_state.start_time else 0
    progress = min(elapsed / 180, 1.0)

    col1, col2 = st.columns([2, 6])
    with col1:
        st.markdown(f"""
        <div class="bottom-bar">
            <div class="control-buttons">
                <button onclick="document.getElementById('prev').click()">⏮</button>
                <button onclick="document.getElementById('playpause').click()">{'⏸' if st.session_state.is_playing else '▶️'}</button>
                <button onclick="document.getElementById('next').click()">⏭</button>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.progress(progress)
        st.caption(f"{elapsed//60}:{elapsed%60:02d} / 3:00")

    if st.button("⏮ Previous", key="prev"):
        play_previous_song()
        st.rerun()

    if st.button("⏸ Pause" if st.session_state.is_playing else "▶️ Play", key="playpause"):
        if st.session_state.is_playing:
            pause_audio()
        else:
            unpause_audio()
        st.rerun()

    if st.button("⏭ Next", key="next"):
        play_next_song()
        st.rerun()

# ========== FOOTER AND SOCIAL ICONS ==========
st.markdown("""
<div class="social-icons-floating">
    <a href="https://www.linkedin.com/in/srijan-roy-29bb19256" target="_blank" aria-label="LinkedIn"><i class="fab fa-linkedin-in"></i></a>
    <a href="https://github.com/SrijanRoy12" target="_blank" aria-label="GitHub"><i class="fab fa-github"></i></a>
    <a href="mailto:roysrijan53@gmail.com" target="_blank" aria-label="Email"><i class="fas fa-envelope"></i></a>
    <a href="https://www.instagram.com/its_ur_roy123/" target="_blank" aria-label="Instagram"><i class="fab fa-instagram"></i></a>
    <a href="https://x.com/home" target="_blank" aria-label="Twitter"><i class="fab fa-twitter"></i></a>
</div>

<div class="footer">
    <p><strong>Designed & Engineered by</strong> <strong>Srijan Roy</strong><br>IEM Kolkata</p>
</div>
""", unsafe_allow_html=True)