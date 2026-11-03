"""
Generate and Save an EpicBharatSaga Story using AWS Bedrock & Polly
"""
import os
import sys
import json
import hashlib

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from engine_adapter import smart_generate_story, smart_synthesize_voice

def create_epic_bharat_story(topic="Kailash Parvat Ka Rahasya", deity="Lord Shiva", prefer_aws=True):
    print(f"\n[PIPELINE] Starting Automated Story Generation for {deity}: '{topic}'...")
    
    # 1. AI Script Generation
    story = smart_generate_story(topic=topic, deity=deity, prefer_aws=prefer_aws)
    
    story_id = f"shiva_aws_{hashlib.md5(topic.encode()).hexdigest()[:8]}"
    story["channel"] = "EpicBharatSaga"
    story["handle"] = "@EpicBharatSaga"
    story["deity"] = deity
    story["story_id"] = story_id
    story["format"] = "Mythological Mystery"
    story["target_duration_seconds"] = 58
    story["visual_theme"] = "DIVINE_MYTHOLOGY"
    
    # 2. Output directories
    eb_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "channels", "EpicBharatSaga"))
    stories_dir = os.path.join(eb_dir, "stories")
    assets_dir = os.path.join(stories_dir, "assets", story_id)
    os.makedirs(stories_dir, exist_ok=True)
    os.makedirs(assets_dir, exist_ok=True)
    
    story_json_path = os.path.join(stories_dir, f"{story_id}.json")
    audio_path = os.path.join(assets_dir, "voiceover.mp3")
    
    # 3. Voiceover Synthesis
    print(f"[PIPELINE] Synthesizing Voiceover...")
    smart_synthesize_voice(story["voiceover_script"], audio_path, prefer_aws=prefer_aws, voice="Arjun")
    story["voiceover_path"] = audio_path
    
    # 4. Save Story JSON
    with open(story_json_path, "w", encoding="utf-8") as f:
        json.dump(story, f, ensure_ascii=False, indent=2)
    
    print(f"\n[SUCCESS] Story Created!")
    print(f"  • JSON: {story_json_path}")
    print(f"  • Title: {story.get('title')}")
    print(f"  • Audio: {audio_path}")
    return story, story_json_path

if __name__ == "__main__":
    create_epic_bharat_story()
