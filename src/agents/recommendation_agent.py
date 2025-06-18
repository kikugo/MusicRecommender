# src/agents/recommendation_agent.py

import pandas as pd
import random
from sklearn.preprocessing import StandardScaler  # Feature scaling
from sklearn.metrics.pairwise import cosine_similarity  # Cosine similarity

# Note: calculate_similarity still exists for legacy use, but we now use cosine similarity here.
from src.utils.helpers import calculate_similarity


class RecommendationAgent:
    """
    Recommends songs using cosine similarity on scaled audio features.
    """

    def __init__(self):
        pass

    def recommend_songs(
        self,
        song_features: pd.DataFrame,
        num_recommendations: int = 5,
        similarity_threshold: float = 0.0,
    ) -> pd.DataFrame:
        """
        Recommends songs based on feature similarity.
        """
        if song_features.empty:
            return pd.DataFrame()

        all_songs = song_features.copy()

        numerical_features = [
            "tempo", "danceability", "energy", "valence", "loudness",
            "acousticness", "instrumentalness", "liveness", "speechiness",
        ]
        
        existing_numerical_features = [
            f for f in numerical_features if f in all_songs.columns
        ]

        if not existing_numerical_features:
            return pd.DataFrame()

        all_songs[existing_numerical_features] = StandardScaler().fit_transform(
            all_songs[existing_numerical_features]
        )

        feature_matrix = all_songs[existing_numerical_features].values
        reference_vector = feature_matrix[0].reshape(1, -1)
        similarities = cosine_similarity(reference_vector, feature_matrix).flatten()
        all_songs["similarity"] = similarities

        recommended_songs = all_songs.sort_values(
            by="similarity", ascending=False
        ).iloc[1:]
        
        recommended_songs = recommended_songs[
            recommended_songs["similarity"] >= similarity_threshold
        ]

        return recommended_songs.head(num_recommendations)

    def run(self, song_features: pd.DataFrame) -> pd.DataFrame:
        """Runs the agent to generate recommendations."""
        return self.recommend_songs(song_features)