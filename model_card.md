# 🎧 Model Card: VibeFinder 1.0

## 1. Model Name

VibeFinder 1.0

---

## 2. Goal / Task

VibeFinder recommends songs from a small catalog that match a user's stated taste. It predicts which songs will fit a user's desired "vibe" by combining coarse categorical matches (genre, mood) with how close numeric features (energy, valence, tempo, danceability, acousticness) are to the user's targets.

This is an educational simulator, not a production service.

---

## 3. Data Used

- Catalog size: starter dataset has 10 songs. The README suggests 8 more example rows that can be added to expand to 18.
- Features per song: id, title, artist, genre, mood, energy (0–1), tempo_bpm, valence (0–1), danceability (0–1), acousticness (0–1).
- Notes: The dataset is small and unevenly distributed across genres and moods. It does not include popularity, lyrics, or listening history.

---

## 4. Algorithm Summary (plain language)

- The system awards fixed bonus points if a song matches the user's preferred genre and mood.
- For numeric features (energy, valence, tempo, danceability, acousticness), it measures how close the song's value is to the user's target. Closer values get higher similarity scores.
- Tempo (BPM) is converted to a 0–1 scale before comparison.
- The model combines the categorical bonuses and weighted numeric similarities into one score per song. Songs are sorted by score and the top K are returned.
- Weights are tunable. By default genre is given the largest bonus, mood a smaller bonus, and the numeric features share the remaining mass.

---

## 5. Observed Behavior / Biases

- The model tends to favor songs that exactly match genre labels because of the genre bonus. This can create a filter bubble and reduce cross-genre discovery.
- Small catalog size causes a few songs to dominate recommendations for multiple profiles.
- Exact string matching for genre/mood makes the system brittle to synonyms or slightly different labels.
- Numeric scales are mixed (tempo vs 0–1 features), so tempo normalization matters; mistakes in bpm bounds can skew scores.

---

## 6. Evaluation Process

How the system was tested:
- Created three representative profiles to probe different parts of the space:
  1. High-Energy Pop (pop, happy, energy ~0.9, tempo ~130)
  2. Chill Lofi (lofi, chill, energy ~0.35, tempo ~78, high acousticness)
  3. Deep Intense Rock (rock, intense, energy ~0.92, tempo ~150)
- For each profile the system scores every song, sorts by score, and returns the top-5.
- Planned experiments:
  - Weight Shift: increase energy weight and reduce genre weight to test sensitivity.
  - Feature Removal: disable mood bonus to see how important mood is.
- Observations to check for when running locally:
  - Whether songs match both categorical and numeric prefs.
  - Whether a single song repeatedly tops all lists (indicates weight imbalance or dataset skew).

---

## 7. Intended Use and Non-Intended Use

Intended use:
- Classroom learning and experimentation with simple content-based recommendation ideas.
- Demonstrating how feature engineering and weights affect ranked outputs.

Non-intended use:
- Do not use for real user-facing music recommendations (too small a catalog and too few signals).
- Not suitable for personalization at scale or for making commercial decisions about artists or licensing.

---

## 8. Ideas for Improvement

1. Use fuzzy matching or canonical genre/mood taxonomies to avoid brittle exact-string matches.
2. Learn or tune weights from user interaction data (clicks/plays) rather than hand-setting constants.
3. Add additional signals: popularity, recentness, user listening history, and content-derived features (lyrics, instrumentation embeddings).
4. Add re-ranking for diversity and artist-frequency limits to avoid repeats.

---

## 9. Personal Reflection

I built a simple but interpretable recommender and learned how much impact a single categorical bonus can have. The biggest learning moment was seeing that a modest fixed genre bonus can overpower nuanced numeric similarities, especially in a tiny dataset.

Using AI-assisted coding saved time: I leaned on it to write consistent loading and scoring code and to propose formulas for similarity. I double-checked the generated math and tests because generated code can include small logic or normalization errors (for example tempo bounds or which keys are present in user profiles).

I was surprised that simple linear similarity and a clear weight scheme produce outputs that "feel" reasonable for many profiles. That shows how much structure is already embedded in a few good features. Next, I'd try learning weights from simulated clicks and improving genre normalization.

---

## 10. Quick Run Instructions (reminder)

1. Ensure Python 3 is installed.
2. (Optional) Create and activate a venv.
3. Run: python -m src.main
4. Inspect the printed top-5 recommendations for the three sample profiles.
