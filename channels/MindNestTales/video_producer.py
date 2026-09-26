"""
MindNest Tales 3D Animation Video Producer:
- Generates 11-language native neural narration using Pixar/Disney style storyteller voices
- Renders 9:16 8K/4K Ultra-HD Portrait Video (4320x7680 / 2160x3840) with 3D Pixar imagery,
  smooth cinematic crossfade (xfade) transitions between clips, cinema bars, and high-retention typography.
- Standard 2-minute (120-second) cinematic runtime with synchronized narration & audio padding.
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

import textwrap

# Auto-configure cross-platform FFmpeg
try:
    import static_ffmpeg
    static_ffmpeg.add_paths()
except Exception:
    pass

script_dir = os.path.dirname(os.path.abspath(__file__))

MORAL_LABELS = {
    "en": "MORAL",
    "hi": "सीख",
    "es": "MORALEJA",
    "pt": "LIÇÃO",
    "fr": "MORALE",
    "de": "LEHRE",
    "ar": "الحكمة",
    "ja": "教訓",
    "ko": "교훈",
    "vi": "BÀI HỌC",
    "fil": "ARAL",
}

def resolve_brand_font():
    """Returns font file path for English branding and handles (guaranteed zero tofu boxes)."""
    fonts_dir = os.path.join(script_dir, "fonts")
    poppins = os.path.join(fonts_dir, "Poppins-Bold.ttf")
    if os.path.exists(poppins):
        return poppins.replace("\\", "/").replace(":", "\\:")
    
    is_win = sys.platform.startswith("win")
    if is_win:
        win_fonts = os.environ.get("WINDIR", "C:\\Windows") + "\\Fonts\\"
        for f in [win_fonts + "segoeuib.ttf", win_fonts + "arialbd.ttf", win_fonts + "calibrib.ttf"]:
            if os.path.exists(f):
                return f.replace("\\", "/").replace(":", "\\:")
    else:
        for f in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"]:
            if os.path.exists(f):
                return f.replace("\\", "/").replace(":", "\\:")
    return ""

def resolve_font_for_language(lang_code):
    """
    Returns the appropriate fontfile path for ffmpeg drawtext filter across OS.
    Handles Indic (Devanagari/Hindi), CJK (Japanese/Korean), Arabic, Vietnamese, and Latin scripts.
    Uses bundled repository Google Fonts first for 100% deterministic cross-platform typography.
    """
    fonts_dir = os.path.join(script_dir, "fonts")
    font_map = {
        "hi": "Poppins-Bold.ttf",       # Native Devanagari + Latin (zero boxes on 3D/English words)
        "en": "Poppins-Bold.ttf",       # Latin
        "es": "Poppins-Bold.ttf",       # Latin
        "pt": "Poppins-Bold.ttf",       # Latin
        "fr": "Poppins-Bold.ttf",       # Latin
        "de": "Poppins-Bold.ttf",       # Latin
        "fil": "Poppins-Bold.ttf",      # Latin
        "vi": "BeVietnamPro-Bold.ttf",  # Vietnamese diacritics + Latin
        "ar": "NotoSansArabic.ttf",     # Arabic + Latin
        "ja": "NotoSansJP.ttf",         # Japanese Kanji/Kana + Latin
        "ko": "NotoSansKR.ttf",         # Korean Hangul + Latin
    }
    
    bundled = os.path.join(fonts_dir, font_map.get(lang_code, "Poppins-Bold.ttf"))
    if os.path.exists(bundled):
        return bundled.replace("\\", "/").replace(":", "\\:")

    is_win = sys.platform.startswith("win")
    font_candidates = []
    if is_win:
        win_fonts = os.environ.get("WINDIR", "C:\\Windows") + "\\Fonts\\"
        if lang_code == "hi":
            font_candidates = [win_fonts + "Nirmala.ttc", win_fonts + "NirmalaB.ttf", win_fonts + "arialbd.ttf"]
        elif lang_code == "ja":
            font_candidates = [win_fonts + "msgothic.ttc", win_fonts + "meiryo.ttc", win_fonts + "arialbd.ttf"]
        elif lang_code == "ko":
            font_candidates = [win_fonts + "malgun.ttf", win_fonts + "gulim.ttc", win_fonts + "arialbd.ttf"]
        elif lang_code == "ar":
            font_candidates = [win_fonts + "seguiemj.ttf", win_fonts + "arial.ttf"]
        else:
            font_candidates = [win_fonts + "segoeuib.ttf", win_fonts + "arialbd.ttf", win_fonts + "calibrib.ttf"]
    else:
        # Linux (Colab / GitHub Actions runner)
        if lang_code == "hi":
            font_candidates = [
                "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Bold.ttf",
                "/usr/share/fonts/opentype/noto/NotoSansDevanagari-Bold.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            ]
        elif lang_code in ("ja", "ko"):
            font_candidates = [
                "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
                "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            ]
        elif lang_code == "ar":
            font_candidates = [
                "/usr/share/fonts/truetype/noto/NotoSansArabic-Bold.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            ]
        else:
            font_candidates = [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
            ]
            
    for f in font_candidates:
        if os.path.exists(f):
            return f.replace("\\", "/").replace(":", "\\:")

    if not is_win:
        import glob
        pattern_map = {
            "hi": "*Devanagari*",
            "ja": "*CJK*",
            "ko": "*CJK*",
            "ar": "*Arabic*"
        }
        pat = pattern_map.get(lang_code, "*Noto*")
        found = glob.glob(f"/usr/share/fonts/**/{pat}", recursive=True)
        for cand in found:
            if cand.lower().endswith(('.ttf', '.ttc', '.otf')):
                return cand.replace("\\", "/").replace(":", "\\:")

    return ""

def sanitize_ffmpeg_text(text):
    """Sanitizes text for safe ffmpeg drawtext filter rendering across all languages without tofu boxes."""
    clean = text.replace(":", " -").replace("'", "").replace('"', '').replace("\\", "").replace("%", "")
    def is_emoji_or_symbol(ch):
        code = ord(ch)
        # Strip emoji, pictograph, and miscellaneous symbol planes that lack font glyphs
        if (0x1F000 <= code <= 0x1FFFF) or (0x2600 <= code <= 0x27BF) or (0x2300 <= code <= 0x23FF) or (0x2B50 <= code <= 0x2BFF) or (0x25A0 <= code <= 0x25FF):
            return True
        return False
    clean = "".join(c for c in clean if not is_emoji_or_symbol(c))
    clean = " ".join(clean.split())
    return clean.strip()

def load_network_config():
    config_path = os.path.join(script_dir, "channels_config.json")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_story(story_number=1):
    try:
        from story_generator import get_or_create_story
        return get_or_create_story(story_number)
    except Exception:
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
        return 120.0

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

def produce_story_video(story_data, lang_code, output_video_path, quality="8k", target_duration=120.0):
    """
    Renders the complete 9:16 portrait video for a specific language channel.
    - Synchronizes 3D Pixar-style visual scenes with localized neural voiceover.
    - Applies smooth cinematic xfade crossfade transitions between all clips.
    - Default target runtime: 120.0 seconds (2:00 minutes).
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
    raw_audio_dur = get_audio_duration(audio_file)
    
    # Target duration (default 120 seconds / 2 minutes)
    duration = target_duration if target_duration else max(raw_audio_dur, 60.0)

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

    # Fallback to thumbnail if scene assets are not yet downloaded
    if not scene_images:
        thumb_path = os.path.join(script_dir, "stories", "thumbnails", f"story_{story_no:02d}_thumbnail.jpg")
        if os.path.exists(thumb_path):
            scene_images = [thumb_path]

    # Brand Font (for Latin branding and channel handle - 100% zero tofu boxes)
    brand_font = resolve_brand_font()
    brand_font_arg = f":fontfile='{brand_font}'" if brand_font else ""

    # Language Font (for story titles and morals across 11 languages)
    font_file = resolve_font_for_language(lang_code)
    shaping_arg = ":text_shaping=1" if lang_code == "ar" else ""
    font_arg = f":fontfile='{font_file}'{shaping_arg}" if font_file else ""

    # Clean text for ffmpeg drawtext filter
    clean_title = sanitize_ffmpeg_text(title)
    moral_text = translation.get("moral", story_data.get("moral", ""))
    moral_label = MORAL_LABELS.get(lang_code, "MORAL")
    clean_moral = sanitize_ffmpeg_text(moral_text)
    clean_handle = sanitize_ffmpeg_text(handle)

    # Wrap moral text to prevent truncation at screen edges
    wrap_w = 26 if lang_code in ("hi", "ja", "ko", "ar") else 34
    moral_lines = textwrap.wrap(clean_moral, width=wrap_w)
    if not moral_lines:
        moral_lines = [clean_moral]
    moral_lines = moral_lines[:2]

    # Typography & Box Dimensions scaled to resolution
    box_top_h = int(220 * scale)
    box_bot_h = int(240 * scale)
    box_bot_y = int(h - box_bot_h)

    f_brand = int(44 * scale)
    y_brand = int(60 * scale)
    f_title = int(48 * scale)
    y_title = int(140 * scale)

    f_badge = int(36 * scale)
    f_moral = int(34 * scale)
    f_handle = int(30 * scale)

    if len(moral_lines) > 1:
        y_badge = int(box_bot_y + (38 * scale))
        y_moral_1 = int(box_bot_y + (90 * scale))
        y_moral_2 = int(box_bot_y + (138 * scale))
        y_handle = int(box_bot_y + (192 * scale))
        moral_drawtext = (
            f"drawtext={font_arg}:text='- {moral_label} -':fontsize={f_badge}:fontcolor=0xf59e0b:x=(w-text_w)/2:y={y_badge},"
            f"drawtext={font_arg}:text='{moral_lines[0]}':fontsize={f_moral}:fontcolor=0xffffff:x=(w-text_w)/2:y={y_moral_1},"
            f"drawtext={font_arg}:text='{moral_lines[1]}':fontsize={f_moral}:fontcolor=0xffffff:x=(w-text_w)/2:y={y_moral_2}"
        )
    else:
        y_badge = int(box_bot_y + (50 * scale))
        y_moral_1 = int(box_bot_y + (110 * scale))
        y_handle = int(box_bot_y + (182 * scale))
        moral_drawtext = (
            f"drawtext={font_arg}:text='- {moral_label} -':fontsize={f_badge}:fontcolor=0xf59e0b:x=(w-text_w)/2:y={y_badge},"
            f"drawtext={font_arg}:text='{moral_lines[0]}':fontsize={f_moral}:fontcolor=0xffffff:x=(w-text_w)/2:y={y_moral_1}"
        )

    overlay_filters = (
        f"drawbox=y=0:h={box_top_h}:color=0x0a0f1d@0.65:t=fill,"
        f"drawbox=y={box_bot_y}:h={box_bot_h}:color=0x0a0f1d@0.65:t=fill,"
        f"drawtext={brand_font_arg}:text='MINDNEST TALES':fontsize={f_brand}:fontcolor=0xf59e0b:x=(w-text_w)/2:y={y_brand},"
        f"drawtext={font_arg}:text='{clean_title}':fontsize={f_title}:fontcolor=0xffffff:x=(w-text_w)/2:y={y_title},"
        f"{moral_drawtext},"
        f"drawtext={brand_font_arg}:text='{clean_handle}':fontsize={f_handle}:fontcolor=0x94a3b8:x=(w-text_w)/2:y={y_handle}"
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
        ffmpeg_inputs.extend(["-f", "lavfi", "-i", f"color=c=0x1a1528:s={w}x{h}:r=30:d={duration:.2f}"])
        full_filter = f"[0:v]{overlay_filters}[v]"
        audio_idx = 1

    # Ensure audio is padded smoothly to duration
    audio_filter = f"[{audio_idx}:a]apad=whole_dur={duration:.2f}[a]"
    final_filter = f"{full_filter};{audio_filter}"

    ffmpeg_cmd = [
        "ffmpeg", "-y",
        *ffmpeg_inputs,
        "-i", audio_file,
        "-filter_complex", final_filter,
        "-map", "[v]", "-map", "[a]",
        "-t", f"{duration:.2f}",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        output_video_path
    ]

    print(f"🎬 Rendering [{lang_code.upper()}] at {quality.upper()} ({w}x{h}) for 2:00 runtime ({duration:.1f}s)...")
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
