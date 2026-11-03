"""
Render Video using EpicBharatSaga Video Producer with Full Hindi Devanagari Caption Support
"""
import os
import sys
import shutil
import json
import re

eb_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "channels", "EpicBharatSaga"))
sys.path.insert(0, eb_dir)

import video_producer

# 1. Fix Hindi Font Resolution: Use Nirmala.ttc (Windows Official Devanagari Font)
def resolve_hindi_font():
    nirmala = "C:/Windows/Fonts/Nirmala.ttc"
    if os.path.exists(nirmala):
        return nirmala.replace("\\", "/").replace(":", "\\:")
    return video_producer.resolve_font()

# 2. Fix Subtitle Sanitization: KEEP Devanagari Hindi intact (Do NOT strip \u0900-\u097F)
def clean_hindi_sub(t):
    t = t.replace("₹", "Rs ")
    # Remove control characters and quotes, but PRESERVE Hindi Devanagari
    t = t.replace("'", "").replace('"', '').replace(":", " -").replace("\\", "").replace("%", "")
    # Remove emojis that crash drawtext, keep all Hindi and English
    t = re.sub(r'[\U0001F000-\U0001FAFF\u2600-\u27BF]', '', t)
    return " ".join(t.split()).strip()

# Apply runtime patches to video_producer
video_producer.resolve_font = resolve_hindi_font
video_producer.clean_sub = clean_hindi_sub

def render_story_video(story_json_path, quality="1080p"):
    print(f"\n[RENDER] Initiating video render with Hindi captions for: {story_json_path}")
    
    with open(story_json_path, "r", encoding="utf-8") as f:
        story_data = json.load(f)
        
    story_id = story_data["story_id"]
    output_dir = os.path.join(eb_dir, "output")
    os.makedirs(output_dir, exist_ok=True)
    
    # If AWS Polly voiceover was pre-generated, copy to target voice_path so it is used
    polly_voice = story_data.get("voiceover_path")
    voice_target = os.path.join(output_dir, f"{story_id}_voice.mp3")
    if polly_voice and os.path.exists(polly_voice):
        shutil.copy2(polly_voice, voice_target)
        print(f"[RENDER] Injected AWS Polly Generative voiceover: {voice_target}")
        
        # Preserve AWS Polly audio
        orig_gen_voice = video_producer.generate_voiceover
        def preserve_aws_voice(text, path, *args, **kwargs):
            if os.path.exists(path) and os.path.getsize(path) > 1000:
                print(f"[RENDER] Retaining AWS Polly audio: {path}")
                return
            return orig_gen_voice(text, path, *args, **kwargs)
        video_producer.generate_voiceover = preserve_aws_voice

    output_mp4 = video_producer.produce_train_video(story_data, quality=quality)
    print(f"\n[RENDER SUCCESS] 1080p Video with Pure Hindi Captions Generated: {output_mp4}")
    return output_mp4

if __name__ == "__main__":
    test_json = os.path.join(eb_dir, "stories", "shiva_hindi_a63d2e02.json")
    render_story_video(test_json)
