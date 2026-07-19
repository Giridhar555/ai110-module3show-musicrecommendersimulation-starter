"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from src.recommender import load_songs, recommend_songs


def print_recs_for_profile(name: str, user_prefs: dict, songs: list, k: int = 5) -> None:
    """Helper to print top-k recommendations for a named profile."""
    print(f"\n=== Profile: {name} ===")
    print(f"Preferences: {user_prefs}\n")
    recs = recommend_songs(user_prefs, songs, k=k)
    for idx, (song, score, explanation) in enumerate(recs, start=1):
        print(f"{idx}. {song['title']} - {song['artist']} (Score: {score:.2f})")
        print(f"   Because: {explanation}\n")


def print_recs_for_profile(name: str, user_prefs: dict, songs: list, k: int = 5) -> None:
    """Helper to print top-k recommendations for a named profile."""
    print(f"\n=== Profile: {name} ===")
    print(f"Preferences: {user_prefs}\n")
    recs = recommend_songs(user_prefs, songs, k=k)
    for idx, (song, score, explanation) in enumerate(recs, start=1):
        print(f"{idx}. {song['title']} - {song['artist']} (Score: {score:.2f})")
        print(f"   Because: {explanation}\n")


def main() -> None:
    songs = load_songs("data/songs.csv")

    # Define three distinct user profiles
    high_energy_pop = {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.9,
        "valence": 0.8,
        "tempo_bpm": 130,
        "danceability": 0.8,
    }

    chill_lofi = {
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.35,
        "valence": 0.6,
        "tempo_bpm": 78,
        "danceability": 0.5,
        "acousticness": 0.8,
    }

    deep_intense_rock = {
        "genre": "rock",
        "mood": "intense",
        "energy": 0.92,
        "valence": 0.4,
        "tempo_bpm": 150,
        "danceability": 0.5,
    }

    # Print recommendations for each profile
    print_recs_for_profile("High-Energy Pop", high_energy_pop, songs, k=5)
    print_recs_for_profile("Chill Lofi", chill_lofi, songs, k=5)
    print_recs_for_profile("Deep Intense Rock", deep_intense_rock, songs, k=5)


if __name__ == "__main__":
    main()