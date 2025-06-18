# src/agents/data_acquisition_agent.py
import pandas as pd
import logging
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from spotipy import SpotifyException
from src.utils import cache

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DataAcquisitionAgent:
    """
    Acquires data (from mock_songs.csv and Spotify).  Handles both
    Client Credentials (for public data) and User Authorization (for user data).
    """

    def __init__(self, data_filepath: str, spotify_client_id: str = None, spotify_client_secret: str = None, redirect_uri: str = "http://localhost:8888/callback", username:str = None):
        self.data_filepath = data_filepath
        self.song_data = None
        self.sp = None  # Spotify client object
        self.username = username #Needed for user authorization
        self.redirect_uri = redirect_uri #Needed for user authorization

        # Warn early if Spotify credentials are missing
        if not (spotify_client_id and spotify_client_secret):
            logging.warning("Spotify credentials not supplied. Falling back to mock CSV data only.")

        # Prioritize user authorization if username is provided
        if self.username:
            self.setup_user_authorization(spotify_client_id, spotify_client_secret, redirect_uri)
        elif spotify_client_id and spotify_client_secret:
            self.setup_client_credentials(spotify_client_id, spotify_client_secret)



    def setup_client_credentials(self, client_id: str, client_secret: str):
        """Sets up Spotify client with Client Credentials flow."""
        try:
            client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
            self.sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        except Exception as e:
            logging.error(f"Failed to authenticate with Spotify (Client Credentials): {e}")
            print("Failed to authenticate with Spotify (Client Credentials). Check your Client ID and Secret.")

    def setup_user_authorization(self, client_id:str, client_secret:str, redirect_uri:str):
        """Set up Spotify client with User Authorization flow"""
        try:
            # Define the scope: what permissions do we want
            scope = "user-library-read user-read-recently-played user-top-read" #Add other scopes if needed.
            self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                               client_secret=client_secret,
                                               redirect_uri=redirect_uri,
                                               scope=scope,
                                               open_browser=False, # Set to False for running inside non graphical terminals
                                               username=self.username))
        except Exception as e:
            logging.error(f"Failed to authenticate user with Spotify (User Authorization): {e}")
            print("Failed to authenticate user with Spotify (User Authorization). Check your Client ID and Secret.")

    def load_data(self) -> None:
        """Loads song data from the CSV file (same as before, with logging)."""
        try:
            self.song_data = pd.read_csv(self.data_filepath)
            required_columns = ['song_id', 'title', 'artist', 'genre', 'tempo', 'danceability', 'energy', 'valence', 'acousticness', 'instrumentalness', 'liveness', 'speechiness']  # Include audio features
            if not all(col in self.song_data.columns for col in required_columns):
                missing_cols = set(required_columns) - set(self.song_data.columns)
                logging.error(f"Error: Missing required columns in CSV: {missing_cols}")
                raise ValueError(f"Missing required columns: {missing_cols}")
            if self.song_data['song_id'].duplicated().any():
                logging.error("Error: Duplicate song IDs found in CSV.")
                raise ValueError("Duplicate song IDs found.")

        except FileNotFoundError:
            logging.error(f"Error: Could not find data file at {self.data_filepath}")
            print(f"Error: Could not find data file at {self.data_filepath}")
            exit(1)
        except pd.errors.EmptyDataError:
            logging.error(f"Error: Data file at {self.data_filepath} is empty.")
            print(f"Error: Data file at {self.data_filepath} is empty.")
            exit(1)
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            print(f"An unexpected error occurred: {e}")
            exit(1)

    def get_songs_by_genre(self, genre: str) -> pd.DataFrame:
        """Gets songs of a specific genre (using mock data or Spotify)."""
        if self.song_data is None:
          self.load_data()
        return self.song_data[self.song_data["genre"].str.lower() == genre.lower()]


    def get_song_by_title(self, title: str) -> pd.DataFrame:
        """Gets a song by its title (using mock data OR Spotify)."""
        if self.sp:  # Try Spotify first if authenticated
            try:
                results = self.sp.search(q=f"track:{title}", type='track', limit=1)
                tracks = results['tracks']['items']
                if tracks:
                    track = tracks[0]
                    track_info = {
                        'song_id': track['id'],
                        'title': track['name'],
                        'artist': track['artists'][0]['name'],
                        'genre': ""
                    }
                    # Attempt to get first genre of artist (optional)
                    try:
                        artist_info = self.sp.artist(track['artists'][0]['id'])
                        if artist_info.get('genres'):
                            track_info['genre'] = artist_info['genres'][0]
                    except Exception:
                        pass
                    return pd.DataFrame([track_info])
                 
            except Exception as e:
                logging.error(f"Error searching Spotify by title: {e}")
                print("An error occured while searching spotify by title")
                return pd.DataFrame()

        # Fallback to mock data
        if self.song_data is None:
            self.load_data()
        return self.song_data[self.song_data["title"].str.lower() == title.lower()]

    def get_spotify_recommendations(self, user_input: str = None, seed_track_id: str = None) -> pd.DataFrame:
        """Fetch recommendations from Spotify.

        Args:
            user_input: Raw user string (title or genre). Can be None if seed_track_id supplied.
            seed_track_id: Explicit Spotify track ID to seed recommendations.
        Returns: DataFrame of recommended tracks (id, title, artist, genre placeholder).
        """
        # Only attempt if we have a Spotify client
        if not self.sp:
            return pd.DataFrame()

        try:
            if seed_track_id:
                cache_key=f"recs_track_{seed_track_id}"
                recs=cache.get(cache_key)
                if not recs:
                    try:
                        recs = self.sp.recommendations(seed_tracks=[seed_track_id], limit=10, market='US')
                    except SpotifyException:
                        # Maybe the track isn't available; try artist instead
                        try:
                            artist_id=self.sp.track(seed_track_id)['artists'][0]['id']
                            recs=self.sp.recommendations(seed_artists=[artist_id], limit=10, market='US')
                        except SpotifyException:
                            recs=None
                    if recs:
                        cache.set(cache_key, recs)
            else:
                # Try track title search first
                results = self.sp.search(q=f"track:{user_input}", type='track', limit=1)
                tracks = results['tracks']['items']
                if tracks:
                    seed_track_id = tracks[0]['id']
                    cache_key=f"recs_track_{seed_track_id}"
                    cached=cache.get(cache_key)
                    if cached:
                        recs=cached
                    else:
                        recs = self.sp.recommendations(seed_tracks=[seed_track_id], limit=10, market='US')
                        cache.set(cache_key, recs)
                else:
                    # Fallback: treat as genre
                    cache_key=f"recs_genre_{user_input.lower()}"
                    recs=cache.get(cache_key)
                    if not recs:
                        recs = self.sp.recommendations(seed_genres=[user_input.lower()], limit=10, market='US')
                        cache.set(cache_key, recs)

            rows = []
            for track in recs['tracks']:
                genre_guess = ""
                try:
                    artist_info = self.sp.artist(track['artists'][0]['id'])
                    if artist_info.get('genres'):
                        genre_guess = artist_info['genres'][0]
                except Exception:
                    pass
                rows.append({
                    'song_id': track['id'],
                    'title': track['name'],
                    'artist': track['artists'][0]['name'],
                    'genre': genre_guess,
                })
            return pd.DataFrame(rows)
        except Exception as e:
            logging.error(f"Error fetching recommendations via Spotify: {e}")
            return pd.DataFrame()

    def run(self, user_input: str) -> pd.DataFrame:
        """Runs the agent, trying Spotify first, then falling back to mock data."""
        if self.song_data is None:
            self.load_data()

        # Sanitize user input (remove leading/trailing whitespace)
        user_input = user_input.strip()

        # Check if the input is empty after sanitization
        if not user_input:
            logging.warning("User input is empty.")  # Log the warning
            print("Please provide a valid genre or song title.") # User-friendly message
            return pd.DataFrame()

        title_df = self.get_song_by_title(user_input)
        if not title_df.empty:
            # Fetch recommendations based on this track's ID
            track_id = title_df.iloc[0]['song_id']
            rec_df = self.get_spotify_recommendations(seed_track_id=track_id)
            if not rec_df.empty:
                return rec_df
            return title_df

        genre_df = self.get_songs_by_genre(user_input)
        if not genre_df.empty:
          return genre_df

        logging.info(f"No songs found for input: '{user_input}'")
        print(f"No songs found for input: '{user_input}'")
        # As a last resort, try Spotify recommendations
        rec_df = self.get_spotify_recommendations(user_input)
        if not rec_df.empty:
            return rec_df

        return pd.DataFrame()