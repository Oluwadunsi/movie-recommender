
# recommender.py
import os
import requests
from dotenv import load_dotenv
from typing import List, Dict

# Load OMDb API key securely
load_dotenv()                                           # reads .env file
OMDB_API_KEY = os.getenv("OMDB_API_KEY")        
if not OMDB_API_KEY:
    raise ValueError("OMDB_API_KEY not set in environment variables")

OMDB_BASE = "http://www.omdbapi.com/"

# Mood - search term mapping (We don’t have genre IDs so we map moods to example search phrases)
MOOD_TO_SEARCH = {
    "funny": "comedy", "hilarious": "comedy", "comedy": "comedy",
    "action": "action", "thrilling": "thriller", "adventure": "adventure",
    "scary": "horror", "horror": "horror",
    "romantic": "romance", "romance": "romance", "love": "romance",
    "christmas": "christmas", "family": "family", "cozy": "family",
    "drama": "drama", "emotional": "drama", "sad": "drama",
    "sci-fi": "sci-fi", "science fiction": "sci-fi",
    "animated": "animation", "animation": "animation",
}

# Detect mood keywords from user prompt
def extract_mood_keywords(prompt: str) -> List[str]:
    prompt = prompt.lower()
    return [word for word in MOOD_TO_SEARCH.keys() if word in prompt]

# Broad search using the strongest mood keyword
def search_movies(prompt: str) -> List[Dict]:
    keywords = extract_mood_keywords(prompt)
    if not keywords:
        return []                                      # no mood detected - nothing

    # Pick the first detected mood as search term
    search_term = MOOD_TO_SEARCH[keywords[0]]
    
    params = {
        "apikey": OMDB_API_KEY,
        "s": search_term,                               # search string
        "type": "movie",
        "page": 1
    }
    response = requests.get(OMDB_BASE, params=params)
    response.raise_for_status()
    data = response.json()

    if data.get("Response") == "True":
        return data["Search"][:12]                      # max 12 candidates (keeps it fast)
    return []

# Fetch full details + rank by how well the plot matches the prompt
def rank_by_plot_similarity(candidates: List[Dict], prompt: str) -> List[Dict]:
    prompt_lower = prompt.lower()
    ranked = []

    for movie in candidates:
        imdb_id = movie["imdbID"]
        detail_params = {
            "apikey": OMDB_API_KEY,
            "i": imdb_id,
            "plot": "short"                             # short plot is enough and faster
        }
        try:
            detail = requests.get(OMDB_BASE, params=detail_params).json()
            if detail.get("Response") != "True":
                continue
        except:
            continue

        plot = detail.get("Plot", "").lower()
        title = movie["Title"].lower()
        score = 0

        # Simple scoring - the more prompt words appear in title/plot, the better
        for word in prompt_lower.split():
            if word in plot or word in title:
                score += 2
        # Bonus for christmas/cozy etc.
        if "christmas" in prompt_lower and "christmas" in plot:
            score += 10

        movie.update({
            "Plot": detail.get("Plot", "No plot available")[:220] + "…",
            "Rating": detail.get("imdbRating", "N/A"),
            "Poster": detail.get("Poster", "N/A"),
            "mood_score": score
        })
        ranked.append(movie)

    # Return top 5
    return sorted(ranked, key=lambda x: x["mood_score"], reverse=True)[:5]

# Recommendation function
def recommend(prompt: str) -> List[Dict]:
    candidates = search_movies(prompt)
    if not candidates:
        return []
    return rank_by_plot_similarity(candidates, prompt)

