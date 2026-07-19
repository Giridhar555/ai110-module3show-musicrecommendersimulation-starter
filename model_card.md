# 🎧 Model Card: VibeFinder 1.0

## 1. Model Name

VibeFinder 1.0

---

## 2. Goal / Task

VibeFinder recommends songs from a small catalog that match a user's stated taste. It predicts which songs will fit a user's desired "vibe" by combining coarse categorical matches (genre, mood) with how close numeric features (energy, valence, tempo, danceability, acousticness) are to the user's targets.

This is an educational simulator, not a production service.

---

## 3. Data Used

- Catalog size: 18 songs (the original 10-song starter set plus 8 additional songs I generated to add genres and moods not already present — classical, hip hop, metal, reggae, country, blues, electronic, and world).
- Features per song: id, title, artist, genre, mood, energy (0–1), tempo_bpm, valence (0–1), danceability (0–1), acousticness (0–1).
- Notes: The dataset is still small and unevenly distributed across genres and moods (some genres, like pop and lofi, have 2-3 songs; others, like classical, have exactly 1). It does not include popularity, lyrics, or listening history.

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
- Executed experiment — Weight Shift: halved GENRE_WEIGHT (2.0 → 1.0) and doubled
  the energy numeric weight (0.4 → 0.8), then re-ran all three profiles. Result:
  the top-3 ranking barely changed for Pop and Lofi (genre+mood combined still
  outweighs numeric closeness), but in Deep Intense Rock, "Night Drive Loop"
  dropped out of the top 5 and was replaced by "Neon Festival" — a song with no
  genre or mood match but very high energy similarity. Conclusion: a single
  weight change wasn't enough to reorder the top of most lists; genre+mood
  together form a floor that's hard for numeric similarity alone to overcome.
  See the "Experiments You Tried" section of README.md for the full before/after
  output.
- Pairwise findings: Pop vs. Lofi have zero song overlap in their top-5s (opposite
  energy/tempo targets). Pop and Rock share "Gym Hero" (both want high energy)
  but differ in the #1 song because Rock's low valence target favors "Storm
  Runner" while Pop's high valence target favors "Sunrise City." Lofi and Rock
  are near-opposite on every numeric axis and also share zero overlap.
- Observations checked for: whether songs match both categorical and numeric
  prefs (they generally do for the top 1-2 results); whether a single song
  repeatedly tops all lists (it doesn't — each profile's #1 differs, which
  confirms the scoring logic responds to the stated preferences).

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