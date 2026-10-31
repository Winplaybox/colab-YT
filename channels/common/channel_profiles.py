"""One place that describes every channel: niche, language, audience, playlists.
Used by yt_brain (metadata) and channel_insights (analytics)."""
import os

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def _load_dotenv():
    """Local runs: keys can live in <repo>/.env (git-ignored). CI uses GitHub Secrets."""
    path = os.path.join(REPO_ROOT, ".env")
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


_load_dotenv()

PROFILES = {
    "DigitalImmortals": {
        "dir": "DigitalImmortals",
        "handle": "@DigitalImmortals",
        "language": "Hindi (Devanagari)",
        "niche": "Sanatan Dharma: temple mysteries, Puranic stories, festival darshan",
        "audience": "Hindi-speaking devotees and mythology fans, 18-45, India",
        "own_playlists": True,   # long-form uses playlist_manager.py
        "niche_queries": ["hindu mythology shorts hindi", "mandir rahasya shorts"], "region": "IN", "lang": "hi",
        "playlists": ["मंदिरों के रहस्य | Temple Mysteries", "पौराणिक कथाएँ | Puranic Stories",
                      "त्योहार दर्शन | Festival Darshan", "रामायण की कथाएँ | Ramayana Stories",
                      "महाभारत की कथाएँ | Mahabharata Stories"],
    },
    "EpicBharatSaga": {
        "dir": "EpicBharatSaga",
        "handle": "@EpicBharatSaga",
        "language": "Hindi",
        "niche": "Hindu deity stories organised in seasons (Shiva, Vishnu, Hanuman, Durga, Ganesha)",
        "audience": "Hindi mythology fans, India",
        "niche_queries": ["mahabharat story shorts hindi", "shiv katha shorts"], "region": "IN", "lang": "hi",
        "playlists": ["Lord Shiva Stories | महादेव की कथाएँ", "Lord Vishnu & Avatars | विष्णु अवतार",
                      "Hanuman Ji Stories | हनुमान कथाएँ", "Maa Durga Stories | देवी कथाएँ",
                      "Ganesha Stories | गणेश कथाएँ", "Devta & Rishi Stories | देवता और ऋषि"],
    },
    "IndianHorrorTapes": {
        "dir": "IndianHorrorTapes",
        "handle": "@IndianHorrorTapes",
        "language": "Hinglish",
        "niche": "Real Indian haunted places and horror folklore Shorts",
        "audience": "Indian horror fans, 16-35",
        "own_playlists": True,   # playlist_manager.py handles categories
        "niche_queries": ["haunted places india shorts", "horror story hindi shorts"], "region": "IN", "lang": "hi",
        "playlists": [],
    },
    "AllTrainReels": {
        "dir": "AllTrainReels",
        "handle": "@AllTrainReels",
        "language": "Hinglish",
        "niche": "Train and railway facts: records, engineering, Indian Railways, world trains",
        "audience": "Rail fans and curious viewers, India",
        "niche_queries": ["indian railways facts shorts", "train facts hindi"], "region": "IN", "lang": "hi",
        "playlists": ["Indian Railways Facts", "World's Fastest Trains", "Railway Engineering Marvels",
                      "Train vs Train Comparisons", "Railway History"],
    },
    "MindNestTales": {
        "dir": "MindNestTales",
        "handle": "@EnglishMindNestTales (+ Hindi/French/German/... MindNest Tales)",
        "language": "Same language as the original title (11-language network)",
        "niche": "Animal fables and moral stories for families, 2D flat explainer animation",
        "audience": "Parents and kids; must stay family-safe",
        "niche_queries": ["moral stories for kids animation", "histoire pour enfants animaux"], "region": "", "lang": "",
        "playlists": ["Moral Stories", "Animal Fables", "Bedtime Stories"],
    },
    "TigerVlogs": {
        "dir": "TigerVlogs-2026",
        "handle": "@TigerVlogs-2026",
        "language": "English title, Hinglish description",
        "niche": "Pure-vegetarian Indian street food: dishes, history, how it's made",
        "audience": "Indian food lovers, 18-40",
        "niche_queries": ["indian street food shorts", "veg street food india"], "region": "IN", "lang": "hi",
        "playlists": ["Street Food Shorts", "Indian Veg Dishes Explained", "Food History"],
    },
}


def get(channel):
    return PROFILES.get(channel, {"dir": channel, "handle": "", "language": "same as original",
                                  "niche": "", "audience": "", "playlists": []})


def insights_path(channel):
    return os.path.join(REPO_ROOT, "channels", get(channel)["dir"], "insights.json")
