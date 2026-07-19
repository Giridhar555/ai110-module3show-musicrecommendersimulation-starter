# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

VibeFinder is a small content-based song recommender. Given a user's stated taste
(preferred genre, mood, and target values for energy, valence, tempo, danceability,
and acousticness), it scores every song in the catalog, explains each score with a
list of reasons (e.g., "genre match (+2.00)"), and returns the top-K ranked matches.
Genre and mood are exact-match categorical bonuses; the remaining numeric features
use a linear closeness score so songs land higher the nearer they are to the user's
target, not just for having "more" or "less" of a given feature.

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

Output of `python -m src.main`, run against the three profiles defined in `src/main.py`:

```
Loaded songs: 10

=== Profile: High-Energy Pop ===
Preferences: {'genre': 'pop', 'mood': 'happy', 'energy': 0.9, 'valence': 0.8, 'tempo_bpm': 130, 'danceability': 0.8}

1. Sunrise City - Neon Echo (Score: 3.94)
   Because: genre match (+2.00); mood match (+1.00); energy similarity 0.92 * w0.42 = 0.39; valence similarity 0.96 * w0.26 = 0.25; tempo similarity 0.93 * w0.16 = 0.15; danceability similarity 0.99 * w0.16 = 0.16

2. Gym Hero - Max Pulse (Score: 2.96)
   Because: genre match (+2.00); energy similarity 0.97 * w0.42 = 0.41; valence similarity 0.97 * w0.26 = 0.26; tempo similarity 0.99 * w0.16 = 0.16; danceability similarity 0.92 * w0.16 = 0.15

3. Rooftop Lights - Indigo Parade (Score: 1.93)
   Because: mood match (+1.00); energy similarity 0.86 * w0.42 = 0.36; valence similarity 0.99 * w0.26 = 0.26; tempo similarity 0.96 * w0.16 = 0.15; danceability similarity 0.98 * w0.16 = 0.15

4. Storm Runner - Voltline (Score: 0.87)
   Because: energy similarity 0.99 * w0.42 = 0.42; valence similarity 0.68 * w0.26 = 0.18; tempo similarity 0.86 * w0.16 = 0.14; danceability similarity 0.86 * w0.16 = 0.14

5. Night Drive Loop - Neon Echo (Score: 0.82)
   Because: energy similarity 0.85 * w0.42 = 0.36; valence similarity 0.69 * w0.26 = 0.18; tempo similarity 0.88 * w0.16 = 0.14; danceability similarity 0.93 * w0.16 = 0.15


=== Profile: Chill Lofi ===
Preferences: {'genre': 'lofi', 'mood': 'chill', 'energy': 0.35, 'valence': 0.6, 'tempo_bpm': 78, 'danceability': 0.5, 'acousticness': 0.8}

1. Library Rain - Paper Lanterns (Score: 3.98)
   Because: genre match (+2.00); mood match (+1.00); energy similarity 1.00 * w0.40 = 0.40; valence similarity 1.00 * w0.25 = 0.25; tempo similarity 0.96 * w0.15 = 0.14; danceability similarity 0.92 * w0.15 = 0.14; acousticness similarity 0.94 * w0.05 = 0.05

2. Midnight Coding - LoRoom (Score: 3.94)
   Because: genre match (+2.00); mood match (+1.00); energy similarity 0.93 * w0.40 = 0.37; valence similarity 0.96 * w0.25 = 0.24; tempo similarity 1.00 * w0.15 = 0.15; danceability similarity 0.88 * w0.15 = 0.13; acousticness similarity 0.91 * w0.05 = 0.05

3. Focus Flow - LoRoom (Score: 2.96)
   Because: genre match (+2.00); energy similarity 0.95 * w0.40 = 0.38; valence similarity 0.99 * w0.25 = 0.25; tempo similarity 0.99 * w0.15 = 0.15; danceability similarity 0.90 * w0.15 = 0.14; acousticness similarity 0.98 * w0.05 = 0.05

4. Spacewalk Thoughts - Orbit Bloom (Score: 1.92)
   Because: mood match (+1.00); energy similarity 0.93 * w0.40 = 0.37; valence similarity 0.95 * w0.25 = 0.24; tempo similarity 0.89 * w0.15 = 0.13; danceability similarity 0.91 * w0.15 = 0.14; acousticness similarity 0.88 * w0.05 = 0.04

5. Coffee Shop Stories - Slow Stereo (Score: 0.94)
   Because: energy similarity 0.98 * w0.40 = 0.39; valence similarity 0.89 * w0.25 = 0.22; tempo similarity 0.93 * w0.15 = 0.14; danceability similarity 0.96 * w0.15 = 0.14; acousticness similarity 0.91 * w0.05 = 0.05


=== Profile: Deep Intense Rock ===
Preferences: {'genre': 'rock', 'mood': 'intense', 'energy': 0.92, 'valence': 0.4, 'tempo_bpm': 150, 'danceability': 0.5}

1. Storm Runner - Voltline (Score: 3.95)
   Because: genre match (+2.00); mood match (+1.00); energy similarity 0.99 * w0.42 = 0.42; valence similarity 0.92 * w0.26 = 0.24; tempo similarity 0.99 * w0.16 = 0.16; danceability similarity 0.84 * w0.16 = 0.13

2. Gym Hero - Max Pulse (Score: 1.82)
   Because: mood match (+1.00); energy similarity 0.99 * w0.42 = 0.42; valence similarity 0.63 * w0.26 = 0.17; tempo similarity 0.89 * w0.16 = 0.14; danceability similarity 0.62 * w0.16 = 0.10

3. Night Drive Loop - Neon Echo (Score: 0.83)
   Because: energy similarity 0.83 * w0.42 = 0.35; valence similarity 0.91 * w0.26 = 0.24; tempo similarity 0.75 * w0.16 = 0.12; danceability similarity 0.77 * w0.16 = 0.12

4. Sunrise City - Neon Echo (Score: 0.76)
   Because: energy similarity 0.90 * w0.42 = 0.38; valence similarity 0.56 * w0.26 = 0.15; tempo similarity 0.80 * w0.16 = 0.13; danceability similarity 0.71 * w0.16 = 0.11

5. Rooftop Lights - Indigo Parade (Score: 0.75)
   Because: energy similarity 0.84 * w0.42 = 0.35; valence similarity 0.59 * w0.26 = 0.16; tempo similarity 0.84 * w0.16 = 0.13; danceability similarity 0.68 * w0.16 = 0.11
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

**Genre weight dominance:** Across all three profiles, songs with a genre bonus
consistently start at the top. In the High-Energy Pop run, "Sunrise City"
(score 3.94, includes both genre and mood match) beat "Gym Hero" (2.96, genre
match only) even though Gym Hero's numeric similarities (energy 0.97, valence
0.97) were actually slightly higher across the board. The +2.0 genre bonus and
+1.0 mood bonus create a gap that a handful of numeric points can't close.

**Songs repeating across profiles:** "Gym Hero" and "Sunrise City" both appear
in the top 5 for two different profiles (High-Energy Pop and Deep Intense Rock
for Gym Hero; Pop and Rock for Sunrise City). This is a symptom of the small
10-song catalog — there just aren't enough songs to fill five *good* matches
per profile, so decent-but-imperfect songs get reused.

**What I'd test next:** halving genre_weight (2.0 → 1.0) and doubling energy's
share of the numeric weight to see whether numeric closeness starts to compete
with categorical matches, or whether genre still wins outright.

---

## Limitations and Risks

- **Tiny catalog:** With only 10 songs, the system can't offer real variety —
  the same handful of tracks reappear across very different user profiles
  (e.g., "Gym Hero" shows up for both "High-Energy Pop" and "Deep Intense Rock"
  despite those being different vibes).
- **Genre/mood matching is brittle:** Matching is exact string comparison
  (`song.genre.lower() == user_prefs["genre"].lower()`). A song tagged "hip hop"
  won't match a user who typed "hip-hop" or "rap" — there's no fuzzy matching or
  synonym handling.
- **No understanding of content:** The system never looks at lyrics, instrumentation,
  or actual audio — it only compares numbers a human assigned to each song.
- **Genre bonus can overpower better numeric fits:** Because genre_weight (2.0)
  is larger than the entire numeric similarity contribution typically adds up
  to, a genre match will usually outrank a song that's numerically closer to the
  user's taste but in a different genre.

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Building this recommender showed me how much a single hardcoded weight can
shape a system's behavior. I expected the numeric similarity scores (energy,
valence, tempo) to matter more, but the genre_weight of 2.0 turned out to be
strong enough that a genre match almost always wins, even against a song that's
numerically closer to what the user asked for. That's a small, concrete example
of how a real recommender's "personality" is really just a set of weight choices
someone made — and how those choices quietly decide what gets seen and what
doesn't.

Where bias or unfairness could show up: in this simulator, songs from genres or
moods missing from the catalog can never surface, no matter how well their
numeric features would otherwise match. A real streaming platform has the same
risk at scale — genres, artists, or regions underrepresented in the training
data or catalog get systematically under-recommended, even if listeners would
actually enjoy them.