import streamlit as st
import pandas as pd
import os
import sys

# Add project root to path to allow absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agents import FeatureEngineeringAgent, RecommendationAgent, DataAcquisitionAgent
from dotenv import load_dotenv

st.set_page_config(page_title="Music Recommender Demo")

st.title("🎵 Music Recommender Demo")

st.markdown(
    "This application demonstrates a music recommendation engine using an offline dataset. "
    "Select a song from the list below to see the top 5 most similar tracks based on audio features."
)

def load_data():
    """Loads the dataset from the CSV file."""
    try:
        return pd.read_csv("data/mock_songs.csv")
    except FileNotFoundError:
        st.error("Error: The data file 'data/mock_songs.csv' was not found. Please make sure the file is in the correct directory.")
        return pd.DataFrame()

songs = load_data()

# --- UI: Select Data Source --------------------------------------------------
source = st.radio("Select data source", ["Offline dataset", "Spotify API"], index=0)

# --- Helper Functions --------------------------------------------------------

def get_recommendations(song_title, songs_df, num_recs=5):
    """Gets song recommendations based on a seed song title from the offline dataset."""
    if song_title not in songs_df["title"].values:
        return pd.DataFrame()

    seed_df = songs_df[songs_df["title"] == song_title]
    rest_df = songs_df[songs_df["title"] != song_title]
    combined = pd.concat([seed_df, rest_df], ignore_index=True)

    fe_agent = FeatureEngineeringAgent()
    features = fe_agent.run(combined)

    rec_agent = RecommendationAgent()
    recs = rec_agent.recommend_songs(features, num_recommendations=num_recs)
    return recs

# --- OFFLINE DATASET MODE ----------------------------------------------------
if source == "Offline dataset" and not songs.empty:
    st.subheader("Offline Mode: Select a Song")
    title = st.selectbox("Choose a song title", songs["title"].unique().tolist())

    if st.button("Get Recommendations", key="offline_btn"):
        with st.spinner(f"Finding songs similar to '{title}'..."):
            recommendations = get_recommendations(title, songs)
            if not recommendations.empty:
                st.subheader("Recommendations")
                st.table(recommendations[["title", "artist", "genre", "similarity"]])
            else:
                st.warning("Could not generate recommendations for the selected song.")

# --- SPOTIFY API MODE --------------------------------------------------------
if source == "Spotify API":
    st.subheader("Live Spotify Recommendations (may be limited)")
    from dotenv import load_dotenv
    load_dotenv()

    client_id = os.getenv("SPOTIPY_CLIENT_ID")
    client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
    redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI") or "http://localhost:8888/callback"

    if not client_id or not client_secret:
        st.error("Spotify credentials are not configured. Please set SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET in a .env file.")
    else:
        query = st.text_input("Enter a genre or song title")
        if st.button("Fetch Spotify Recommendations", key="spotify_btn") and query:
            with st.spinner("Contacting Spotify API..."):
                agent = DataAcquisitionAgent(
                    "data/mock_songs.csv",
                    client_id,
                    client_secret,
                    redirect_uri
                )
                df = agent.get_spotify_recommendations(user_input=query)
                if df.empty:
                    st.warning("Spotify request failed or returned no results.")
                else:
                    st.success("Top recommendations from Spotify:")
                    st.dataframe(df[["title", "artist", "genre"]])

st.info("Project functionality is based on an offline dataset. Spotify API integration may not work for new developer accounts due to recent endpoint deprecations.") 