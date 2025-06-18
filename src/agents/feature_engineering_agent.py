# src/agents/feature_engineering_agent.py

import pandas as pd


class FeatureEngineeringAgent:
    """
    Extracts and prepares features for the recommendation model.
    """

    def __init__(self):
        pass

    def get_features(self, song_data: pd.DataFrame) -> pd.DataFrame:
        """
        Gets the features for the given song data, mapping columns
        from various schemas to a consistent internal format.
        """
        df = song_data.copy()
        cols = df.columns

        mapping = {
            "track_id": "song_id",
            "id": "song_id",
            "track_name": "title",
            "name": "title",
            "track_genre": "genre",
            "artists": "artist",
        }
        for old, new in mapping.items():
            if old in cols and new not in cols:
                df[new] = df[old]

        feature_cols = [
            "song_id", "title", "artist", "genre", "year", "popularity",
            "explicit", "duration_ms", "tempo", "danceability", "energy",
            "valence", "loudness", "acousticness", "instrumentalness",
            "liveness", "speechiness", "mode", "key",
        ]

        existing_features = [col for col in feature_cols if col in df.columns]
        return df[existing_features]

    def run(self, song_data: pd.DataFrame) -> pd.DataFrame:
        """Runs the agent to engineer features."""
        return self.get_features(song_data)