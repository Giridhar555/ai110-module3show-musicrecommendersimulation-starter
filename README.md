# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Real-world recommendation systems combine user signals (explicit preferences and implicit behavior) with item attributes to estimate how well each item matches a user's current tastes. They often blend content-based signals (song features like genre, mood, tempo) with collaborative signals (what similar users liked) and business rules (diversity, freshness). This simplified simulator focuses on the content-based side: it prioritizes matching the user's declared genre and mood, and then scores numerical attributes (energy, valence, tempo, danceability, acousticness) by how close they are to the user's preferred values. The goal is to produce a short ranked list that feels right for the user’s described "vibe" while remaining interpretable and easy to tune.

Specific features used:

- Song
  - id, title, artist
  - genre (categorical)
  - mood (categorical)
  - energy (numeric 0–1)
  - valence (numeric 0–1)
  - tempo_bpm (numeric)
  - danceability (numeric 0–1)
  - acousticness (numeric 0–1)

- UserProfile
  - preferred_genre (categorical)
  - preferred_mood (categorical)
  - preferred_energy (numeric 0–1)
  - preferred_valence (numeric 0–1)
  - preferred_tempo_bpm (numeric)
  - weights (per-feature weights, e.g., genre_weight, mood_weight, energy_weight)

How the Recommender computes scores (brief):

- For categorical features (genre, mood): award a fixed bonus when a song matches the user's preference.
- For numeric features (energy, valence, tempo, etc.): compute a closeness score that rewards songs nearer the user's preferred value (see scoring rule in the project doc).
- Combine the categorical bonuses and weighted numeric closeness scores into a single scalar score per song, then sort songs descending to create the ranked recommendations.

You can tune the weights to emphasize genre/mood more heavily than small differences in numeric features, or vice versa, depending on the desired behavior.

You can include a simple diagram or bullet list if helpful.

---

Algorithm Recipe (detailed)

1) Per-song scoring components

- Categorical bonuses
  - genre_bonus = genre_weight if song.genre == user.preferred_genre else 0
  - mood_bonus = mood_weight if song.mood == user.preferred_mood else 0

- Numeric similarity (example formulas)
  - Linear closeness (for features already scaled 0–1):
    similarity = max(0.0, 1.0 - abs(song_value - user_value))
  - Gaussian kernel (smooth, tunable):
    similarity = exp(- (song_value - user_value)^2 / (2 * sigma^2))
    (choose sigma based on how strict you want matching to be; e.g., sigma=0.12)

- Tempo handling
  - Normalize tempo to [0,1] before applying similarity:
    tempo_norm = (tempo_bpm - bpm_min) / (bpm_max - bpm_min)
    (choose bpm_min=40 and bpm_max=200 or compute dataset min/max)

2) Combining components into a single score

- total_score = genre_bonus + mood_bonus + sum(weight_i * similarity_i for each numeric feature)
- Example starting weights (tunable):
  - genre_weight = 2.0
  - mood_weight = 1.0
  - numeric weights (sum to 1 or any convenient mass): energy=0.4, valence=0.25, tempo=0.15, danceability=0.15, acousticness=0.05
- Tie-breaking and post-processing:
  - Remove duplicates by artist if needed
  - Enforce diversity: if top-K contains >N songs from one artist, demote extras
  - Threshold: only recommend songs with score >= min_score (optional)

3) Ranking vs Scoring

- Scoring rule computes a per-item compatibility scalar used to compare songs independently.
- Ranking rule sorts scored items and can apply list-level logic (diversity, business rules, freshness) that cannot be expressed in a per-item score alone.

Biases and limitations to note

- Over-prioritizing genre (high genre_weight) will hide songs from other genres that match mood and numeric features well.
- The system ignores lyrics, cultural or contextual cues, artist popularity, and temporal listening patterns.
- Small catalog amplifies weight choices — testing across multiple user profiles is necessary to tune weights.

Suggested new numeric features to enrich the dataset

- instrumentalness (0–1): higher means likely instrumental — useful for study/ambient profiles
- liveness (0–1): captures crowd presence vs studio sound
- speechiness (0–1): proportion of spoken words (podcast-like)
- energy and valence are already present; keep danceability and acousticness

Step 1: Expanding the catalog (prompt + generated CSV)

- Prompt to an AI collaborator to generate 8 new songs (CSV-ready):

"Attached is data/songs.csv. Please generate 8 additional song rows in valid CSV format that use the same headers (id,title,artist,genre,mood,energy,tempo_bpm,valence,danceability,acousticness). Make sure the new songs add genres and moods not already in the file (e.g., classical, hip hop, metal, reggae, country, blues, world) and include plausible numeric values. Keep numeric features in the same ranges (energy/valence/danceability/acousticness in 0.0–1.0, tempo_bpm realistic). Return only the CSV lines (no explanatory text)."

- Example generated rows (CSV) you can append to data/songs.csv:

id,title,artist,genre,mood,energy,tempo_bpm,valence,danceability,acousticness
11,Moonlight Sonata,Quiet Strings,classical,melancholic,0.12,60,0.20,0.10,0.95
12,Broken Beat,Urban Flow,hip hop,energetic,0.85,100,0.65,0.80,0.10
13,Iron Heart,Black Anvil,metal,triumphant,0.95,170,0.30,0.45,0.02
14,Sunshine Reggae,Island Drift,reggae,relaxed,0.55,90,0.78,0.70,0.30
15,Country Roads Home,Blue Ridge,country,nostalgic,0.48,98,0.52,0.40,0.88
16,Delta Nights,Slow Harbor,blues,reflective,0.38,74,0.45,0.30,0.85
17,Neon Festival,ElectroPulse,electronic,party,0.90,128,0.86,0.92,0.05
18,Sahara Dawn,Desert Choir,world,meditative,0.22,62,0.48,0.15,0.90

(If you want, I can append these rows to data/songs.csv now or create a new augmented file.)

Step 2: Example UserProfile and critique

- Example user profile (dictionary):

user_profile = {
    "preferred_genre": "lofi",
    "preferred_mood": "chill",
    "preferred_energy": 0.35,
    "preferred_valence": 0.60,
    "preferred_tempo_bpm": 78,
    "weights": {
        "genre_weight": 2.0,
        "mood_weight": 1.0,
        "energy_weight": 0.4,
        "valence_weight": 0.25,
        "tempo_weight": 0.15,
        "danceability_weight": 0.15,
        "acousticness_weight": 0.05
    }
}

- Critique:
  - This profile will strongly prefer songs labeled 'lofi' even if a 'chill' song in another genre has very similar numeric attributes. That is OK if the user truly expects genre to be primary. Lower genre_weight if you want more cross-genre discovery.
  - The numeric targets (energy=0.35, tempo=78) are good to separate 'chill lofi' from 'intense rock' (rock songs typically have energy >0.7 and tempo >120). With the given weights, energetic rock tracks will be penalized by low energy similarity and likely outranked by lofi tracks.
  - To avoid being too narrow, consider allowing preferred_genre to be a list (e.g., ['lofi','ambient']) or set a softer genre bonus (e.g., 0.5 instead of 2.0).

Step 3: Scoring Logic Design — prompt for a new chat session

- Use this prompt in a new chat titled "Scoring Logic Design" and attach data/songs.csv:

"I have an attached songs.csv with song attributes (id,title,artist,genre,mood,energy,tempo_bpm,valence,danceability,acousticness). Help me design point-weighting strategies and concrete scoring code. Specifically:

1) Propose 3 sensible sets of weights (Conservative genre-driven, Balanced, Discovery-focused) and justify them.
2) Provide Python implementations for linear similarity and Gaussian similarity functions, tempo normalization, and a function `score_song(song, user_profile)` that returns a scalar.
3) Show a worked example scoring three songs from the CSV for the example user_profile above using the Balanced weights.
4) Add pytest unit tests for the similarity functions and for `score_song` on the example cases.

Return code blocks and brief explanations only."

Step 4: Data flow visualization (text)

- Input: user_profile + data/songs.csv
- Process: For each song in catalog -> compute genre_bonus & mood_bonus -> normalize tempo -> compute numeric similarities -> weighted sum -> produce total_score
- Output: sort songs by total_score desc -> return Top K (e.g., K=5)

Step 5: Document plan in README.md

- The Algorithm Recipe (above), example UserProfile, the CSV expansion prompt and sample rows, scoring prompts for the new chat, biases/limitations, and the data flow text are all included here so you can start implementing.

---

Next actions available (choose one):
- Append the 8 example rows to data/songs.csv now.
- Create a new augmented file data/songs_augmented.csv with the extra rows (safer).
- Implement the scoring functions and unit tests in src/ and run pytest.
- Start the new chat "Scoring Logic Design" and send the prompt with songs.csv attached (I can prepare the exact message for you).

Which should I do next?
---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Paste a sample of your recommender's output here as a text block so a reader can see what it produces:

```
# e.g.:
# User profile: genre=indie, mood=chill, energy=low
# Recommendations:
#   1. ...
#   2. ...
#   3. ...
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



