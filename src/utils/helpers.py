# utils/helpers.py
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def calculate_similarity(song1_features, song2_features):
    # Explicitly select numerical features
    numerical_features = ['tempo', 'danceability', 'energy', 'valence',
                         'acousticness', 'instrumentalness', 'liveness', 'speechiness']

    # Get the values for numerical features, handling missing keys
    features1 = np.array([song1_features.get(feature, np.nan) for feature in numerical_features])
    features2 = np.array([song2_features.get(feature, np.nan) for feature in numerical_features])

    # Check if there are any NaN values (missing features)
    if np.isnan(features1).any() or np.isnan(features2).any():
      return 0.0 #Return 0 if there is nan

    distance = np.linalg.norm(features1 - features2)
    similarity = 1 / (1 + distance)
    return similarity

def calculate_embedding_similarity(embedding1, embedding2): # Will be used in later stages
    embedding1 = np.array(embedding1).reshape(1, -1)
    embedding2 = np.array(embedding2).reshape(1, -1)
    return cosine_similarity(embedding1, embedding2)[0][0]