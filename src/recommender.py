from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import csv
import math

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


# Default weights and tempo normalization bounds (tunable)
GENRE_WEIGHT = 2.0
MOOD_WEIGHT = 1.0
NUMERIC_WEIGHTS = {
    "energy": 0.4,
    "valence": 0.25,
    "tempo": 0.15,
    "danceability": 0.15,
    "acousticness": 0.05,
}
BPM_MIN = 40.0
BPM_MAX = 200.0


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return top-k Song objects for the given user profile."""
        # Score each song using the same scoring logic as the functional API
        scored = []
        for song in self.songs:
            # convert Song dataclass to dict for scoring helper
            song_dict = {
                "id": song.id,
                "title": song.title,
                "artist": song.artist,
                "genre": song.genre,
                "mood": song.mood,
                "energy": song.energy,
                "tempo_bpm": song.tempo_bpm,
                "valence": song.valence,
                "danceability": song.danceability,
                "acousticness": song.acousticness,
            }
            score, reasons = score_song({
                "genre": user.favorite_genre,
                "mood": user.favorite_mood,
                "energy": user.target_energy,
                # no tempo/valence/danceability preferences available in this dataclass
            }, song_dict)
            scored.append((song, score, reasons))

        # sort by score descending
        scored.sort(key=lambda x: x[1], reverse=True)
        return [item[0] for item in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a human-readable explanation for why a song was recommended."""
        song_dict = {
            "id": song.id,
            "title": song.title,
            "artist": song.artist,
            "genre": song.genre,
            "mood": song.mood,
            "energy": song.energy,
            "tempo_bpm": song.tempo_bpm,
            "valence": song.valence,
            "danceability": song.danceability,
            "acousticness": song.acousticness,
        }
        score, reasons = score_song({
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
        }, song_dict)
        return "; ".join(reasons) if reasons else f"Score: {score:.2f}"


def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file and converts numeric fields to floats/ints.

    Returns a list of dictionaries, one per song.
    """
    songs: List[Dict] = []
    with open(csv_path, newline='', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            try:
                song = {
                    "id": int(row["id"]),
                    "title": row["title"],
                    "artist": row.get("artist", ""),
                    "genre": row.get("genre", "").strip(),
                    "mood": row.get("mood", "").strip(),
                    "energy": float(row.get("energy", 0.0)),
                    "tempo_bpm": float(row.get("tempo_bpm", 0.0)),
                    "valence": float(row.get("valence", 0.0)),
                    "danceability": float(row.get("danceability", 0.0)),
                    "acousticness": float(row.get("acousticness", 0.0)),
                }
                songs.append(song)
            except Exception:
                # skip malformed rows but continue loading
                continue
    print(f"Loaded songs: {len(songs)}")
    return songs


def _linear_similarity(a: float, b: float) -> float:
    """Return a linear similarity in [0,1] where 1.0 means exact match."""
    return max(0.0, 1.0 - abs(a - b))


def _normalize_tempo(bpm: float) -> float:
    """Normalize tempo_bpm into [0,1] using BPM_MIN/BPM_MAX bounds."""
    if bpm <= BPM_MIN:
        return 0.0
    if bpm >= BPM_MAX:
        return 1.0
    return (bpm - BPM_MIN) / (BPM_MAX - BPM_MIN)


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.

    Returns a tuple (score, reasons) where reasons is a list of strings describing
    individual contributions (e.g., 'genre match (+2.0)').
    """
    reasons: List[str] = []
    score = 0.0

    # Categorical bonuses
    if "genre" in user_prefs and user_prefs["genre"]:
        if song.get("genre", "").lower() == user_prefs["genre"].lower():
            score += GENRE_WEIGHT
            reasons.append(f"genre match (+{GENRE_WEIGHT:.2f})")
    if "mood" in user_prefs and user_prefs["mood"]:
        if song.get("mood", "").lower() == user_prefs["mood"].lower():
            score += MOOD_WEIGHT
            reasons.append(f"mood match (+{MOOD_WEIGHT:.2f})")

    # Prepare numeric preferences and weights
    numeric_prefs = {}
    for key in ["energy", "valence", "danceability", "acousticness"]:
        if key in user_prefs and user_prefs[key] is not None:
            numeric_prefs[key] = user_prefs[key]
    # tempo special key name - accept 'tempo' or 'tempo_bpm'
    if "tempo_bpm" in user_prefs:
        numeric_prefs["tempo"] = _normalize_tempo(float(user_prefs["tempo_bpm"]))
    elif "tempo" in user_prefs:
        numeric_prefs["tempo"] = float(user_prefs["tempo"])

    # Compute which numeric weights are active
    active_weights = {k: v for k, v in NUMERIC_WEIGHTS.items() if k in numeric_prefs}
    total_active = sum(active_weights.values())

    numeric_score = 0.0
    if total_active > 0:
        # normalize active weights to sum to 1 across provided numeric prefs
        normalized_weights = {k: (v / total_active) for k, v in active_weights.items()}
        for k, w in normalized_weights.items():
            if k == "tempo":
                song_val = _normalize_tempo(float(song.get("tempo_bpm", 0.0)))
                pref_val = float(numeric_prefs["tempo"])
            else:
                song_val = float(song.get(k, 0.0))
                pref_val = float(numeric_prefs[k])
            sim = _linear_similarity(song_val, pref_val)
            contrib = sim * w
            numeric_score += contrib
            reasons.append(f"{k} similarity {sim:.2f} * w{w:.2f} = {contrib:.2f}")
        # numeric_score is in [0,1]
        score += numeric_score
    else:
        # No numeric prefs provided — we can optionally add a small default or skip
        pass

    return score, reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation: score all songs and return top-k as tuples
    (song_dict, score, explanation_string).
    """
    scored: List[Tuple[Dict, float, List[str]]] = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        scored.append((song, score, reasons))

    # sort by score descending
    scored.sort(key=lambda x: x[1], reverse=True)

    # convert reasons list to explanation string
    top_k = []
    for song, score, reasons in scored[:k]:
        explanation = "; ".join(reasons) if reasons else "No strong matches"
        top_k.append((song, score, explanation))
    return top_k
