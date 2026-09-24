"""
MindNest Tales 3D Animation Video Producer:
- Generates 11-language native neural narration using Pixar/Disney style storyteller voices
- Renders 9:16 8K/4K Ultra-HD Portrait Video (4320x7680 / 2160x3840) with 3D Pixar imagery,
  smooth cinematic crossfade (xfade) transitions between clips, cinema bars, and high-retention typography.
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
    clean = text.replace(":", " -").replace("'", "").replace('"', '').replace("\\", "")
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

def get_audio_duration(audio_path):
    """Retrieves audio file duration in seconds using ffprobe."""
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        audio_path
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(res.stdout.strip())
    except Exception:
        return 58.0

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

def produce_story_video(story_data, lang_code, output_video_path, quality="8k"):
    """
    Renders the complete 9:16 portrait video for a specific language channel.
    - Synchronizes 3D Pixar-style visual scenes with localized neural voiceover.
    - Applies smooth cinematic xfade crossfade transitions between all clips.
    - Supports '8k' (4320x7680), '4k' (2160x3840), or '1080p' (1080x1920).
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

    # Resolution Configuration
    if quality == "8k":
        w, h = 4320, 7680
        scale = 4.0
    elif quality == "4k":
        w, h = 2160, 3840
        scale = 2.0
    else:
        w, h = 1080, 1920
        scale = 1.0

    # 1. Generate Voiceover in native language
    audio_file = os.path.splitext(output_video_path)[0] + f"_{lang_code}_voice.mp3"
    generate_voiceover(script, voice, audio_file, rate=rate, pitch=pitch)
    duration = get_audio_duration(audio_file)

    # 2. Check for 3D Pixar Scene Assets
    story_no = story_data.get("story_number", 1)
    assets_dir = os.path.join(script_dir, "stories", "assets", f"story_{story_no:02d}")
    scene_images = []
    if os.path.exists(assets_dir):
        scene_images = [
            os.path.join(assets_dir, f)
            for f in sorted(os.listdir(assets_dir))
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))
        ]

    # Clean text for ffmpeg drawtext filter
    clean_title = sanitize_ffmpeg_text(title)[:36]
    clean_moral = sanitize_ffmpeg_text(story_data["moral"])[:46]
    clean_handle = sanitize_ffmpeg_text(handle)

    # Typography & Box Dimensions scaled to resolution
    box_top_h = int(260 * scale)
    box_bot_y = int(h - (220 * scale))
    box_bot_h = int(220 * scale)

    f_brand = int(48 * scale)
    y_brand = int(80 * scale)

    f_title = int(50 * scale)
    y_title = int(160 * scale)

    f_moral = int(36 * scale)
    y_moral = int(box_bot_y + (60 * scale))

    f_handle = int(34 * scale)
    y_handle = int(box_bot_y + (130 * scale))

    overlay_filters = (
        f"drawbox=y=0:h={box_top_h}:color=0x0a0f1d@0.88:t=fill,"
        f"drawbox=y={box_bot_y}:h={box_bot_h}:color=0x0a0f1d@0.88:t=fill,"
        f"drawtext=text='MINDNEST TALES':fontsize={f_brand}:fontcolor=0xf59e0b:x=(w-text_w)/2:y={y_brand},"
        f"drawtext=text='{clean_title}':fontsize={f_title}:fontcolor=0xffffff:x=(w-text_w)/2:y={y_title},"
        f"drawtext=text='MORAL - {clean_moral}':fontsize={f_moral}:fontcolor=0xfacc15:x=(w-text_w)/2:y={y_moral},"
        f"drawtext=text='{clean_handle}':fontsize={f_handle}:fontcolor=0x94a3b8:x=(w-text_w)/2:y={y_handle}"
    )

    ffmpeg_inputs = []
    if len(scene_images) > 1:
        # Multi-Scene with Smooth Cinematic Crossfade Transitions
        num_scenes = len(scene_images)
        fade_dur = 0.5
        L = (duration + (num_scenes - 1) * fade_dur) / num_scenes

        scale_parts = []
        for i, img in enumerate(scene_images):
            clean_img = os.path.abspath(img).replace("\\", "/")
            ffmpeg_inputs.extend(["-loop", "1", "-t", f"{L:.3f}", "-i", clean_img])
            scale_parts.append(
                f"[{i}:v]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},setsar=1,fps=30[s{i}];"
            )

        prev = "s0"
        xfade_parts = []
        for i in range(1, num_scenes):
            offset = i * (L - fade_dur)
            out_tag = f"x{i}" if i < num_scenes - 1 else "vbase"
            xfade_parts.append(
                f"[{prev}][s{i}]xfade=transition=fade:duration={fade_dur:.2f}:offset={offset:.2f}[{out_tag}];"
            )
            prev = out_tag

        full_filter = f"{''.join(scale_parts)}{''.join(xfade_parts)}[vbase]{overlay_filters}[v]"
        audio_idx = num_scenes
    elif len(scene_images) == 1:
        # Single Scene
        clean_img = os.path.abspath(scene_images[0]).replace("\\", "/")
        ffmpeg_inputs.extend(["-loop", "1", "-t", f"{duration:.3f}", "-i", clean_img])
        full_filter = f"[0:v]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},setsar=1,fps=30[vbase];[vbase]{overlay_filters}[v]"
        audio_idx = 1
    else:
        # Fallback Dynamic Cinematic Gradient
        ffmpeg_inputs.extend(["-f", "lavfi", "-i", f"color=c=0x1a1528:s={w}x{h}:r=30"])
        full_filter = f"[0:v]{overlay_filters}[v]"
        audio_idx = 1

    ffmpeg_cmd = [
        "ffmpeg", "-y",
        *ffmpeg_inputs,
        "-i", audio_file,
        "-filter_complex", full_filter,
        "-map", "[v]", "-map", f"{audio_idx}:a",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest", "-pix_fmt", "yuv420p",
        output_video_path
    ]

    print(f"🎬 Rendering [{lang_code.upper()}] with smooth cinematic transitions at {quality.upper()} ({w}x{h})...")
    subprocess.run(ffmpeg_cmd, check=True)

    if os.path.exists(audio_file):
        os.remove(audio_file)

    print(f"SUCCESS [{lang_code.upper()}]: Rendered {output_video_path} ({os.path.getsize(output_video_path)} bytes)")
    return output_video_path

def produce_all_languages(story_number=1, output_dir="/tmp/mindnest_batch", quality="8k"):
    """Produces the story video dubbed across all 11 languages at 8K/4K."""
    story = load_story(story_number)
    config = load_network_config()
    os.makedirs(output_dir, exist_ok=True)
    
    rendered_files = {}
    for ch in config["channels"]:
        lang = ch["lang_code"]
        out_file = os.path.join(output_dir, f"story_{story_number:02d}_{lang}_{quality}.mp4")
        print(f"\n---> Producing Story {story_number} for {ch['channel_name']} ({lang})...")
        produce_story_video(story, lang, out_file, quality=quality)
        rendered_files[lang] = out_file

    print(f"\n=======================================================")
    print(f"🎉 ALL 11 LOCALIZED VIDEOS PRODUCED AT {quality.upper()} FOR STORY {story_number}!")
    print(f"=======================================================")
    return rendered_files

if __name__ == "__main__":
    story_no = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    lang = sys.argv[2] if len(sys.argv) > 2 else "en"
    quality = sys.argv[3] if len(sys.argv) > 3 else "8k"
    story = load_story(story_no)
    produce_story_video(story, lang, f"story_{story_no}_{lang}_{quality}.mp4", quality=quality)
