# database/pgvector_setup.py
import psycopg2

def setup_pgvector(db_url):
    """Sets up the PgVector database."""
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()

        # Enable the vector extension
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

        # Create the songs table (adjust columns as needed)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS songs (
                song_id TEXT PRIMARY KEY,
                title TEXT,
                artist TEXT,
                genre TEXT,
                tempo REAL,
                danceability REAL,
                energy REAL,
                valence REAL,
                acousticness REAL,
                instrumentalness REAL,
                liveness REAL,
                speechiness REAL,
                gemini_embedding vector(768)  -- Adjust dimension if needed
            );
        """)

        conn.commit()
        cur.close()
        conn.close()
        print("PgVector setup complete.")

    except psycopg2.Error as e:
        print(f"Error setting up PgVector: {e}")

# Example usage (you might call this from main.py or a separate setup script):
# setup_pgvector("postgresql://user:password@host:port/database")