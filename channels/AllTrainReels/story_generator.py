"""
AllTrainReels High-Retention Short Story Generator
=================================================
Generates fast-paced 20-30 second viral train shorts in Hinglish:
- 0-2s explosive psychological hook
- 3-20s fast-fact pacing (cuts every 4-5 seconds)
- 21-25s loop ending or debate question
- Mobile-optimized titles (<= 58 characters)
- Pinned comments and YouTube SEO tags
- Integrates with pre-verified 30-episode Story Bank or AI synthesis
"""

import os
import sys
import json
import re

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

script_dir = os.path.dirname(os.path.abspath(__file__))
stories_dir = os.path.join(script_dir, "stories")
bank_file = os.path.join(script_dir, "stories_bank.json")

os.makedirs(stories_dir, exist_ok=True)

def load_bank():
    """Loads pre-verified 30-episode story bank."""
    if os.path.exists(bank_file):
        with open(bank_file, "r", encoding="utf-8") as f:
            return json.load(f)
    from story_bank import ALL_TRAIN_STORIES
    return ALL_TRAIN_STORIES

def generate_story_from_bank(episode_number):
    """Retrieves and saves an episode from the pre-verified 30-story bank."""
    bank = load_bank()
    matching = [s for s in bank if s.get("episode_number") == episode_number]
    if not matching:
        raise ValueError(f"Episode {episode_number} not found in story bank (1-30 available).")
    story = matching[0]

    filename = f"story_{episode_number:02d}_{story['story_id'].replace('train_', '')}.json"
    filepath = os.path.join(stories_dir, filename)

    # Format into complete execution schema
    full_data = {
        "channel": "AllTrainReels",
        "handle": "@AllTrainReels",
        "episode_number": episode_number,
        "story_id": story["story_id"],
        "format": story["format"],
        "title": story["youtube_title"],
        "title_variations": [
            story["youtube_title"],
            f"{story['tagline']} 🚂",
            f"{story['title']} #Shorts",
            f"Wait for the End! {story['title'][:40]}"
        ],
        "tagline": story["tagline"],
        "visual_theme": story.get("visual_theme", "SPEEDOMETER_HUD"),
        "target_duration_seconds": story.get("target_duration", 25),
        "verified_fact": story["verified_fact"],
        "voiceover_script": story["voiceover_script"],
        "debate_question": story["debate_question"],
        "pinned_comment": story["pinned_comment"],
        "description": (
            f"{story['youtube_title']}\n\n"
            f"🚂 {story['tagline']}\n"
            f"💡 Verified Fact: {story['verified_fact']}\n\n"
            f"👉 {story['debate_question']}\n\n"
            f"Subscribe to @AllTrainReels for daily high-speed rail facts, monster locomotives, and Indian Railways marvels!\n\n"
            f"{' '.join(story['tags'])}"
        ),
        "tags": story["tags"],
        "seo_keywords": [
            "Indian Railways", "Train Facts", "Bullet Train", "Locomotive",
            "High Speed Rail", "Shorts", "Viral Trains", "Vande Bharat",
            "Train Spotting", "Fastest Train", "Monster Train"
        ],
        "shots": story["shots"]
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(full_data, f, ensure_ascii=False, indent=2)

    print(f"✅ Generated Episode #{episode_number}: '{story['youtube_title']}' -> {filename}")
    return full_data

def get_or_create_story(episode_number=1, force_refresh=False):
    """
    Retrieves existing episode JSON or generates it on-demand for that specific day's run.
    Follows IndianHorrorTapes episodic lifecycle (zero batch pre-generation).
    """
    bank = load_bank()
    matching = [s for s in bank if s.get("episode_number") == episode_number]
    if not matching:
        episode_number = ((episode_number - 1) % len(bank)) + 1
        matching = [s for s in bank if s.get("episode_number") == episode_number]
    story = matching[0]

    filename = f"story_{episode_number:02d}_{story['story_id'].replace('train_', '')}.json"
    filepath = os.path.join(stories_dir, filename)

    if os.path.exists(filepath) and not force_refresh:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "shots" in data and len(data["shots"]) >= 5:
                    return data
        except Exception:
            pass

    full_data = {
        "channel": "AllTrainReels",
        "handle": "@AllTrainReels",
        "episode_number": episode_number,
        "story_id": story["story_id"],
        "format": story["format"],
        "title": story["youtube_title"],
        "title_variations": [
            story["youtube_title"],
            f"{story['tagline']} 🚂",
            f"{story['title']} #Shorts",
            f"Wait for the End! {story['title'][:40]}"
        ],
        "tagline": story["tagline"],
        "visual_theme": story.get("visual_theme", "SPEEDOMETER_HUD"),
        "target_duration_seconds": story.get("target_duration", 25),
        "verified_fact": story["verified_fact"],
        "voiceover_script": story["voiceover_script"],
        "debate_question": story["debate_question"],
        "pinned_comment": story["pinned_comment"],
        "description": (
            f"{story['youtube_title']}\n\n"
            f"🚂 {story['tagline']}\n"
            f"💡 Verified Fact: {story['verified_fact']}\n\n"
            f"👉 {story['debate_question']}\n\n"
            f"Subscribe to @AllTrainReels for daily high-speed rail facts, monster locomotives, and Indian Railways marvels!\n\n"
            f"{' '.join(story['tags'])}"
        ),
        "tags": story["tags"],
        "seo_keywords": [
            "Indian Railways", "Train Facts", "Bullet Train", "Locomotive",
            "High Speed Rail", "Shorts", "Viral Trains", "Vande Bharat",
            "Train Spotting", "Fastest Train", "Monster Train"
        ],
        "shots": story["shots"]
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(full_data, f, ensure_ascii=False, indent=2)

    print(f"✅ [Workflow Generation] Created Episode #{episode_number}: '{story['youtube_title']}' -> {filename}")
    return full_data

if __name__ == "__main__":
    ep = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 1
    force = "--force" in sys.argv
    get_or_create_story(ep, force_refresh=force)
