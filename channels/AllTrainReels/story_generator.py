"""
AllTrainReels High-Retention Short Story Generator
=================================================
Generates fast-paced 20-30 second viral train shorts in Hinglish:
- 0-2s explosive psychological hook
- 3-20s fast-fact pacing (cuts every 4-5 seconds)
- 21-25s loop ending or debate question
- Mobile-optimized titles (<= 58 characters)
- Pinned comments and YouTube SEO tags
- Strictly enforces verified fact-gate & eliminates stale cache via story hashing
"""

import os
import sys
import json
import hashlib

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

script_dir = os.path.dirname(os.path.abspath(__file__))
stories_dir = os.path.join(script_dir, "stories")
bank_file = os.path.join(script_dir, "stories_bank.json")

os.makedirs(stories_dir, exist_ok=True)

def load_bank():
    """Loads pre-verified 30-episode story bank directly from story_bank."""
    from story_bank import ALL_TRAIN_STORIES
    return ALL_TRAIN_STORIES

def build_full_data(story, episode_number):
    """
    Constructs the complete, authoritative story payload from verified bank data.
    Enforces title limits, tag cleaning, and clean public descriptions.
    """
    yt_title = story.get("youtube_title", story.get("title", ""))
    assert len(yt_title) <= 58, (
        f"Episode {episode_number} title exceeds 58 characters ({len(yt_title)}): {yt_title}"
    )

    clean_tags = [t.lstrip("#").strip() for t in story.get("tags", []) if t.strip()]
    hashtags_str = " ".join([f"#{t}" for t in clean_tags])

    # Clean description without internal labels like 'Verified Fact:'
    description = (
        f"{yt_title}\n\n"
        f"🚂 {story['tagline']}\n\n"
        f"{story['verified_fact']}\n\n"
        f"👉 {story['debate_question']}\n\n"
        f"Subscribe to @AllTrainReels for daily world records, monster locomotives, high-speed bullet trains, and extreme railway marvels from around the globe!\n\n"
        f"{hashtags_str}"
    )

    story_hash = hashlib.sha256(json.dumps(story, sort_keys=True).encode("utf-8")).hexdigest()[:16]

    return {
        "channel": "AllTrainReels",
        "handle": "@AllTrainReels",
        "episode_number": episode_number,
        "story_id": story["story_id"],
        "story_hash": story_hash,
        "format": story["format"],
        "title": yt_title,
        "youtube_title": yt_title,
        "title_variations": [
            yt_title,
            f"{story['tagline']} 🚂",
            f"{yt_title} #Shorts",
            f"The Real Story: {story['tagline']}"
        ],
        "tagline": story["tagline"],
        "visual_theme": story.get("visual_theme", "SPEEDOMETER_HUD"),
        "target_duration_seconds": story.get("target_duration", 95),
        "review_status": story.get("review_status", "verified"),
        "sources": story.get("sources", []),
        "verified_fact": story["verified_fact"],
        "voiceover_script": story["voiceover_script"],
        "debate_question": story["debate_question"],
        "pinned_comment": story["pinned_comment"],
        "description": description,
        "tags": clean_tags,
        "seo_keywords": [
            "World Railways", "Monster Trains", "Bullet Train", "Locomotive",
            "High Speed Rail", "Shorts", "Viral Trains", "Train Spotting",
            "Fastest Train", "Railway Engineering", "Extreme Railways"
        ],
        "shots": story["shots"]
    }

def get_or_create_story(episode_number=1, force_refresh=False):
    """
    Retrieves existing episode JSON or generates it on-demand for that specific day's run.
    Follows IndianHorrorTapes episodic lifecycle:
    - Enforces fact gate (must be 'verified')
    - Checks story_hash against bank to prevent stale cache bugs
    - Re-generates only when changed or forced
    """
    bank = load_bank()
    matching = [s for s in bank if s.get("episode_number") == episode_number]
    if matching:
        story = matching[0]
    else:
        # Tier 2: Seamlessly route episodes 31+ to Extended Railway Archive
        from extended_generator import get_extended_rail_story
        story = get_extended_rail_story(episode_number)

    # Patch D: Fact Gate Check
    if story.get("review_status") != "verified" and "--allow-unverified" not in sys.argv:
        raise SystemExit(f"Ep {episode_number} unverified — sources check karo")

    filename = f"story_{episode_number:02d}_{story['story_id'].replace('train_', '')}.json"
    filepath = os.path.join(stories_dir, filename)

    expected_hash = hashlib.sha256(json.dumps(story, sort_keys=True).encode("utf-8")).hexdigest()[:16]

    if os.path.exists(filepath) and not force_refresh:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data.get("story_hash") == expected_hash and "shots" in data and len(data["shots"]) >= 5:
                    return data
        except Exception:
            pass

    full_data = build_full_data(story, episode_number)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(full_data, f, ensure_ascii=False, indent=2)

    print(f"✅ [On-Demand Generation] Episode #{episode_number}: '{story['youtube_title']}' -> {filename}")
    return full_data

def peek_story(episode_number=1):
    """Returns story dictionary in-memory without saving any file to disk."""
    bank = load_bank()
    matching = [s for s in bank if s.get("episode_number") == episode_number]
    if matching:
        return matching[0]
    from extended_generator import get_extended_rail_story
    return get_extended_rail_story(episode_number)


def generate_story_from_bank(episode_number):
    """Alias for on-demand generation with force_refresh enabled."""
    return get_or_create_story(episode_number=episode_number, force_refresh=True)

if __name__ == "__main__":
    ep = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 1
    force = "--force" in sys.argv
    get_or_create_story(ep, force_refresh=force)
