# Music Recommender (archived)

This repository contains a music recommendation engine that demonstrates a powerful offline similarity model using a rich dataset derived from Kaggle's "Spotify Tracks 1921-2020" collection.

- **Originally**: The engine queried Spotify's `/audio-features`, `/audio-analysis`, and `/recommendations` endpoints to build live, personalised playlists.
- **Now**: Since those endpoints were deprecated (see timeline below), the app has pivoted to an _offline-first_ design that ships with a local CSV (`data/mock_songs.csv`). All similarity calculations are performed on that dataset.

The project is presented as a Streamlit web application. A **Spotify** option still exists in the UI for developers with grandfathered credentials, but most users will interact solely with the offline mode.

## Core Logic

The recommendation engine computes similarity between songs using the following process:
1.  **Feature Extraction**: It uses a vector of 9 numerical audio features: `tempo`, `danceability`, `energy`, `valence`, `loudness`, `acousticness`, `instrumentalness`, `liveness`, and `speechiness`.
2.  **Normalization**: The features are scaled using `StandardScaler` to ensure no single feature dominates the calculation.
3.  **Similarity**: It calculates the cosine similarity between the seed song's feature vector and all other songs in the dataset.

## Quick Start

```bash
# 1. Clone this repository
git clone <this-repo-url>
cd MusicRecommender

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch the Streamlit UI
streamlit run streamlit_app/app.py
```
This will launch a web app where you can select a seed song and see the top 5 most similar tracks from the offline dataset.

## Dataset

The `data/mock_songs.csv` file contains a rich, diverse sample of songs from the "Spotify Tracks 1921-2020" dataset available on Kaggle, including a wide array of genres and audio features.

## Spotify Integration (Legacy → Optional)

The Streamlit UI still exposes a **Spotify** mode, but it is considered _best-effort only_. Due to the deprecation of key endpoints (`/audio-features`, `/recommendations`, etc.), this path works **only** if you have an older (grandfathered) client ID with extended access. For everyone else, selecting Spotify will likely return no results, and the app will prompt you to use the offline dataset instead.

If you do have working credentials, place them in a `.env` file (see `env.example`) and launch the app as normal.

---

**PROJECT ARCHIVED – June 2025**

Spotify has deprecated the `audio-features`, `audio-analysis`, **and** `recommendations` endpoints for all *new* or development-mode apps (see [Spotify blog post — 27 Nov 2024](https://developer.spotify.com/blog/2024-11-27-changes-to-the-web-api) and the follow-up [Extended Access update — 15 Apr 2025](https://developer.spotify.com/blog/2025-04-15-updating-the-criteria-for-web-api-extended-access)).

Because this project relied on those endpoints to calculate or retrieve song similarity, its core functionality is no longer possible for newly-created client IDs. The repository is therefore **no longer maintained** and kept here for reference only.
