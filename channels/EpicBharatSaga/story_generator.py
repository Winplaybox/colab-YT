"""
EpicBharatSaga Story Generator
================================
Builds the complete episode payload from the mythology story bank.
Routes to story_bank.py for episodes 1-26, then auto-generates new deity stories.
"""

import os
import sys
import json
import hashlib

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

script_dir  = os.path.dirname(os.path.abspath(__file__))
stories_dir = os.path.join(script_dir, "stories")
os.makedirs(stories_dir, exist_ok=True)


def load_bank():
    """Loads all stories from the mythology story bank."""
    sys.path.insert(0, script_dir)
    from story_bank import ALL_MYTH_STORIES
    return ALL_MYTH_STORIES


def build_full_data(story, episode_number):
    """Constructs the complete episode payload for video production."""
    yt_title = story.get("youtube_title", story.get("title", ""))
    if len(yt_title) > 58:
        yt_title = yt_title[:55] + "..."

    clean_tags = [t.lstrip("#").strip() for t in story.get("tags", []) if t.strip()]
    hashtags_str = " ".join([f"#{t}" for t in clean_tags])
    deity = story.get("deity", "Hindu Mythology")
    season = story.get("season", 1)

    description = (
        f"{yt_title}\n\n"
        f"🔱 {story['tagline']}\n\n"
        f"{story['verified_fact']}\n\n"
        f"👉 {story['debate_question']}\n\n"
        f"Season {season} — {deity}\n\n"
        f"Subscribe to @EpicBharatSaga for daily stories of Sanatan Dharma — "
        f"gods, avatars, myths, and legends from the timeless Hindu epics!\n\n"
        f"{hashtags_str}"
    )

    story_hash = hashlib.sha256(json.dumps(story, sort_keys=True).encode("utf-8")).hexdigest()[:16]

    return {
        "channel": "EpicBharatSaga",
        "handle": "@EpicBharatSaga",
        "episode_number": episode_number,
        "season": season,
        "deity": deity,
        "story_id": story["story_id"],
        "story_hash": story_hash,
        "format": story["format"],
        "title": yt_title,
        "youtube_title": yt_title,
        "tagline": story["tagline"],
        "visual_theme": story.get("visual_theme", "DIVINE_MYTHOLOGY"),
        "target_duration_seconds": story.get("target_duration", 180),
        "review_status": story.get("review_status", "verified"),
        "sources": story.get("sources", []),
        "verified_fact": story["verified_fact"],
        "voiceover_script": story["voiceover_script"],
        "debate_question": story["debate_question"],
        "pinned_comment": story["pinned_comment"],
        "description": description,
        "tags": clean_tags,
        "shots": story["shots"]
    }


def get_or_create_story(episode_number=1, force_refresh=False):
    """Retrieves or generates episode JSON for the given episode number."""
    bank = load_bank()
    matching = [s for s in bank if s.get("episode_number") == episode_number]

    if matching:
        story = matching[0]
    else:
        # Episodes beyond the bank → route to extended generator
        from extended_generator import get_extended_myth_story
        story = get_extended_myth_story(episode_number)

    if story.get("review_status") != "verified" and "--allow-unverified" not in sys.argv:
        raise SystemExit(f"Ep {episode_number} unverified — verify sources first")

    safe_id = story["story_id"].replace("/", "_")
    filename = f"story_{episode_number:03d}_{safe_id}.json"
    filepath = os.path.join(stories_dir, filename)

    expected_hash = hashlib.sha256(json.dumps(story, sort_keys=True).encode("utf-8")).hexdigest()[:16]

    if os.path.exists(filepath) and not force_refresh:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            if data.get("story_hash") == expected_hash and "shots" in data and len(data["shots"]) >= 4:
                return data
        except Exception:
            pass

    full_data = build_full_data(story, episode_number)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(full_data, f, ensure_ascii=False, indent=2)

    print(f"✅ [EpicBharat] Ep #{episode_number:03d} [{story.get('deity', '')}]: '{story['youtube_title']}'")
    return full_data


def peek_story(episode_number=1):
    """Returns story dictionary in-memory without saving any file to disk."""
    bank = load_bank()
    matching = [s for s in bank if s.get("episode_number") == episode_number]
    if matching:
        return matching[0]
    from extended_generator import get_extended_myth_story
    return get_extended_myth_story(episode_number)


def generate_story_from_bank(episode_number):
    """Alias for on-demand generation with force refresh."""
    return get_or_create_story(episode_number=episode_number, force_refresh=True)


if __name__ == "__main__":
    ep = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 1
    force = "--force" in sys.argv
    get_or_create_story(ep, force_refresh=force)
