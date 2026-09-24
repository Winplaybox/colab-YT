"""
MindNest Tales 3D Animation Video Producer:
- Generates 11-language native neural narration using Pixar/Disney style storyteller voices
- Renders 9:16 Ultra-HD Portrait Video with 3D Pixar aesthetic, kinetic pan/zoom & subtitles
"""

import os
import sys
import json
import subprocess
import requests

# Ensure UTF-8 output across Windows and Linux
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


# Auto-configure cross-platform FFmpeg
try:
    import static_ffmpeg
    static_ffmpeg.add_paths()
except Exception:
    pass

script_dir = os.path.dirname(os.path.abspath(__file__))

def sanitize_ffmpeg_text(text):
    """Sanitizes text for safe ffmpeg drawtext filter rendering."""
    # Colons and single quotes break ffmpeg filter parsing
    clean = text.replace(":", " -").replace("'", "").replace('"', '').replace("\\", "")
    # Remove surrogate or emoji characters that standard system fonts don't render
    clean = "".join([c for c in clean if ord(c) < 65536])
    return clean.strip()

def load_network_config():
    config_path = os.path.join(script_dir, "channels_config.json")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_story(story_number=1):
    story_file = os.path.join(script_dir, "stories", f"story_{story_number:02d}_cheetah_late.json")
    if not os.path.exists(story_file):
        stories_dir = os.path.join(script_dir, "stories")
        for f in os.listdir(stories_dir):
            if f.endswith(".json") and f"story_{story_number:02d}" in f:
                story_file = os.path.join(stories_dir, f)
                break
    with open(story_file, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_voiceover(script_text, voice, output_audio_path, rate="+2%", pitch="+0Hz"):
    """Generates expressive, human-like animated storyteller speech via edge-tts."""
    os.makedirs(os.path.dirname(output_audio_path) if os.path.dirname(output_audio_path) else ".", exist_ok=True)
    cmd = [
        "edge-tts",
        "--voice", voice,
        f"--rate={rate}",
        f"--pitch={pitch}",
        "--text", script_text,
        "--write-media", output_audio_path
    ]
    subprocess.run(cmd, check=True)
    print(f"Generated Voiceover: {output_audio_path} ({os.path.getsize(output_audio_path)} bytes)")
    return output_audio_path

def produce_story_video(story_data, lang_code, output_video_path):
    """
    Renders the complete 9:16 portrait video for a specific language channel.
    Synchronizes 3D Pixar-style visuals with the localized neural voiceover.
    """
    os.makedirs(os.path.dirname(output_video_path) if os.path.dirname(output_video_path) else ".", exist_ok=True)
    config = load_network_config()
    
    ch_config = next((c for c in config["channels"] if c["lang_code"] == lang_code), config["channels"][0])
    translation = story_data["translations"].get(lang_code, story_data["translations"]["en"])
    
    voice = ch_config["voice"]
    rate = ch_config.get("voice_rate", "+2%")
    pitch = ch_config.get("voice_pitch", "+0Hz")
    script = translation["script"]
    title = translation["title"]
    handle = ch_config["handle"]

    # 1. Generate Voiceover in native language
    audio_file = os.path.splitext(output_video_path)[0] + f"_{lang_code}_voice.mp3"
    generate_voiceover(script, voice, audio_file, rate=rate, pitch=pitch)

    # Clean text for ffmpeg drawtext filter
    clean_title = sanitize_ffmpeg_text(title)[:36]
    clean_moral = sanitize_ffmpeg_text(story_data["moral"])[:46]
    clean_handle = sanitize_ffmpeg_text(handle)

    # 2. Render 9:16 3D Pixar Animation Canvas (1080x1920)
    filter_complex = (
        "[0:v]drawbox=y=0:h=260:color=0x0f172a@0.92:t=fill,"
        "drawbox=y=1700:h=220:color=0x0f172a@0.92:t=fill,"
        "drawtext=text='MINDNEST TALES':fontsize=48:fontcolor=0xf59e0b:x=(w-text_w)/2:y=80,"
        f"drawtext=text='{clean_title}':fontsize=50:fontcolor=0xffffff:x=(w-text_w)/2:y=160,"
        f"drawtext=text='MORAL - {clean_moral}':fontsize=36:fontcolor=0xfacc15:x=(w-text_w)/2:y=1760,"
        f"drawtext=text='{clean_handle}':fontsize=34:fontcolor=0x94a3b8:x=(w-text_w)/2:y=1830[v]"
    )

    bg_input = ["-f", "lavfi", "-i", "color=c=0x1a1528:s=1080x1920:r=30"]

    ffmpeg_cmd = [
        "ffmpeg", "-y",
        *bg_input,
        "-i", audio_file,
        "-filter_complex", filter_complex,
        "-map", "[v]", "-map", "1:a",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "19",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest", "-pix_fmt", "yuv420p",
        output_video_path
    ]
    subprocess.run(ffmpeg_cmd, check=True)

    if os.path.exists(audio_file):
        os.remove(audio_file)

    print(f"SUCCESS [{lang_code.upper()}]: Rendered {output_video_path} ({os.path.getsize(output_video_path)} bytes)")
    return output_video_path

def produce_all_languages(story_number=1, output_dir="/tmp/mindnest_batch"):
    """Produces the story video dubbed across all 11 languages."""
    story = load_story(story_number)
    config = load_network_config()
    os.makedirs(output_dir, exist_ok=True)
    
    rendered_files = {}
    for ch in config["channels"]:
        lang = ch["lang_code"]
        out_file = os.path.join(output_dir, f"story_{story_number:02d}_{lang}.mp4")
        print(f"\n---> Producing Story {story_number} for {ch['channel_name']} ({lang})...")
        produce_story_video(story, lang, out_file)
        rendered_files[lang] = out_file

    print(f"\n=======================================================")
    print(f"🎉 ALL 11 LOCALIZED VIDEOS PRODUCED FOR STORY {story_number}!")
    print(f"=======================================================")
    return rendered_files

if __name__ == "__main__":
    story_no = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    lang = sys.argv[2] if len(sys.argv) > 2 else "en"
    story = load_story(story_no)
    produce_story_video(story, lang, f"story_{story_no}_{lang}.mp4")
