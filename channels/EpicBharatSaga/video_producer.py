"""
EpicBharatSaga Dynamic 9:16 Portrait Rail Video Producer
======================================================
- Produces ultra-high-retention YouTube Shorts (1080x1920 / 4K) documentary-style.
- Pacing: 12–18 distinct visual shots with 4-style alternating stutter-free zoompan.
- Audio: Pluggable TTS (Kokoro/IndicVoice → Edge-TTS fallback) + procedural rail SFX
  mixed via amix(normalize=0) and loudnorm(I=-16:TP=-1.5:LRA=11) for broadcast standards.
- Kinetic Subtitles: Placed in Shorts safe zone (y=1080-1350) rendered via external textfile
  with sanitization (₹ -> Rs, emoji/Devanagari stripped to prevent tofu glyphs).
- Visual HUDs: Context-aware overlay without fake speedometer spam.
"""

import os
import sys
import json
import re
import subprocess
import textwrap
import asyncio

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

try:
    import static_ffmpeg
    static_ffmpeg.add_paths()
except Exception:
    pass

script_dir = os.path.dirname(os.path.abspath(__file__))
stories_dir = os.path.join(script_dir, "stories")
assets_base = os.path.join(stories_dir, "assets")
output_dir = os.path.join(script_dir, "output")
fonts_dir = os.path.join(script_dir, "fonts")

os.makedirs(output_dir, exist_ok=True)

def resolve_font():
    """Finds best bold font for FFmpeg drawtext."""
    poppins = os.path.join(fonts_dir, "Poppins-Bold.ttf")
    if os.path.exists(poppins):
        return poppins.replace("\\", "/").replace(":", "\\:")
    parent_fonts = os.path.join(script_dir, "..", "MindNestTales", "fonts", "Poppins-Bold.ttf")
    if os.path.exists(parent_fonts):
        return parent_fonts.replace("\\", "/").replace(":", "\\:")
    if sys.platform.startswith("win"):
        win_fonts = os.environ.get("WINDIR", "C:\\Windows") + "\\Fonts\\"
        for f in [win_fonts + "segoeuib.ttf", win_fonts + "arialbd.ttf"]:
            if os.path.exists(f):
                return f.replace("\\", "/").replace(":", "\\:")
    return ""

def ff_path(p):
    """Escapes path for FFmpeg filter arguments."""
    return p.replace("\\", "/").replace(":", "\\:")

def clean_sub(t):
    """Sanitizes subtitle text to prevent drawtext crashes or tofu glyphs in Poppins font."""
    t = t.replace("₹", "Rs ")
    t = re.sub(r'[\u0900-\u097F\U0001F000-\U0001FAFF\u2600-\u27BF]', '', t)
    t = t.replace("'", "").replace('"', '').replace(":", " -").replace("\\", "").replace("%", "")
    return " ".join(t.split()).strip()

def get_audio_duration(audio_path):
    """Returns audio duration in seconds using ffprobe."""
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
        return 25.0

def generate_voiceover(text, output_audio_path, voice="hi-IN-MadhurNeural", rate="+6%"):
    """
    Generates voiceover via the pluggable TTS engine:
    Priority: Kokoro/IndicVoice (local, free) → Edge-TTS (free neural fallback).
    """
    try:
        # Import from the local tts/ package
        from tts.engine import synthesize_narration
        result = synthesize_narration(text, output_audio_path)
        print(f"🎙️ [TTS Engine] Generated via: {result.get('engine', 'unknown')}")
    except Exception as e:
        # Hard fallback: pure Edge-TTS async
        print(f"TTS engine notice ({e}), falling back to direct Edge-TTS...")
        import asyncio
        import edge_tts
        async def _synth():
            communicate = edge_tts.Communicate(text, voice=voice, rate=rate)
            await communicate.save(output_audio_path)
        asyncio.run(_synth())
        print(f"🎙️ [Edge-TTS Fallback] Generated: {output_audio_path}")

def synthesize_procedural_divine_audio(output_audio_path, duration=30.0):
    """
    Synthesizes an authentic divine soundscape via pure Python wave module:
    - Resonant sacred Om fundamental frequency (136.1 Hz + harmonics)
    - Gentle temple bell chime reverberating in the opening seconds
    - Warm atmospheric meditative undertone
    100% robust, zero external audio dependency.
    """
    import wave
    import struct
    import math

    sample_rate = 44100
    total_samples = int(sample_rate * duration)
    wav_file = wave.open(output_audio_path, "w")
    wav_file.setnchannels(2)  # Stereo
    wav_file.setsampwidth(2) # 16-bit
    wav_file.setframerate(sample_rate)

    frames = bytearray()
    for n in range(total_samples):
        t = n / sample_rate
        # 1. Gentle temple bell chime at start
        bell = 0.0
        if t < 4.0:
            decay = math.exp(-t * 1.8)
            bell = (math.sin(2 * math.pi * 587.33 * t) * 0.4 +
                    math.sin(2 * math.pi * 880.0 * t) * 0.25 +
                    math.sin(2 * math.pi * 1174.66 * t) * 0.15) * decay * 0.30

        # 2. Sacred Om drone (136.1 Hz fundamental + warm harmonics)
        f0 = 136.1
        drone = (math.sin(2 * math.pi * f0 * t) * 0.10 +
                 math.sin(2 * math.pi * (f0 * 2) * t) * 0.05 +
                 math.sin(2 * math.pi * (f0 * 3) * t) * 0.025 +
                 math.sin(2 * math.pi * (f0 * 4) * t) * 0.012)
        # Slow breathing amplitude modulation (0.15 Hz)
        mod = 0.85 + 0.15 * math.sin(2 * math.pi * 0.15 * t)
        drone *= mod

        sample = bell + drone
        sample = max(-0.95, min(0.95, sample))
        int_sample = int(sample * 32767)
        frames.extend(struct.pack("<hh", int_sample, int_sample))

    wav_file.writeframes(frames)
    wav_file.close()
    print(f"🔱 [Divine Ambient Soundscape] Synthesized: {output_audio_path}")
    return True

def build_mythology_hud_filter(deity, season, w, h, font_arg, episode_num):
    """Builds visual HUD overlay with divine saffron/gold branding in Shorts safe zone."""
    scale = w / 1080.0

    deity_title = f"{deity.upper()} • S{season}" if deity else "SANATAN DHARMA"

    # Persistent brand banner on top (Safe zone: y=0 to 140)
    brand_filters = [
        f"drawbox=x=0:y=0:w={w}:h={int(130*scale)}:color=0x1A0A00@0.90:t=fill",
        f"drawbox=x=0:y={int(130*scale)}:w={w}:h={int(6*scale)}:color=0xFF9933@1.0:t=fill",
        f"drawtext={font_arg}text='EPIC BHARAT SAGA':x={int(45*scale)}:y={int(35*scale)}:fontsize={int(32*scale)}:fontcolor=0xFFD700:shadowcolor=black:shadowx=2:shadowy=2",
        f"drawtext={font_arg}text='EPISODE #{episode_num:02d}':x={w - int(240*scale)}:y={int(35*scale)}:fontsize={int(28*scale)}:fontcolor=0xF1F5F9:shadowcolor=black:shadowx=2:shadowy=2"
    ]

    # Contextual deity badge (y=150 to 220)
    badge = [
        f"drawbox=x={w - int(320*scale)}:y={int(150*scale)}:w={int(280*scale)}:h={int(60*scale)}:color=0x1A0A00@0.85:t=fill",
        f"drawbox=x={w - int(320*scale)}:y={int(150*scale)}:w={int(6*scale)}:h={int(60*scale)}:color=0xFF9933@1.0:t=fill",
        f"drawtext={font_arg}text='{deity_title}':x={w - int(300*scale)}:y={int(165*scale)}:fontsize={int(22*scale)}:fontcolor=0xFFD700:shadowcolor=black:shadowx=2:shadowy=2"
    ]
    return brand_filters + badge

def split_script_into_subtitles(voiceover_text, target_count, fallback_shots=None):
    """
    Dynamically splits voiceover script into punchy, synchronized subtitles for each shot.
    If shots already have rich granular subtitles matching target_count, uses them.
    """
    if fallback_shots and len(fallback_shots) >= target_count:
        return [s.get("subtitle", "") for s in fallback_shots[:target_count]]

    words = voiceover_text.replace("—", " ").replace("-", " ").split()
    total_words = len(words)
    if total_words == 0:
        return ["Om Namah Shivaya"] * target_count

    chunk_size = max(2, total_words // target_count)
    beats = []
    i = 0
    while i < total_words:
        chunk = " ".join(words[i:i + chunk_size])
        beats.append(chunk)
        i += chunk_size

    # Pad or trim to target_count
    if len(beats) < target_count:
        while len(beats) < target_count:
            beats.append(beats[-1] if beats else "Sanatan Dharma")
    return beats[:target_count]

def produce_train_video(story_input, quality="1080p"):
    """
    Renders an end-to-end 9:16 YouTube Short from a story dictionary or JSON filepath:
    - Eliminates -loop 1 -t frame explosion bug (uses single frame input + upscale to eliminate zoompan stutter)
    - Subtitles rendered in Shorts safe zone (y=1080-1350) via sanitized textfiles
    - Audio mixed via amix(normalize=0) and loudnorm(-16 LUFS)
    """
    if isinstance(story_input, dict):
        story_data = story_input
    else:
        with open(story_input, "r", encoding="utf-8") as f:
            story_data = json.load(f)

    story_id = story_data["story_id"]
    title = story_data["title"]
    episode_num = story_data.get("episode_number", 1)
    deity = story_data.get("deity", "Lord Shiva")
    season = story_data.get("season", 1)
    voiceover_text = story_data.get("voiceover_script", "")
    shots = story_data.get("shots", [])

    print(f"\n==================================================")
    print(f"🔱 PRODUCING EPICBHARATSAGA SHORT #{episode_num:02d}: {title}")
    print(f"==================================================")

    # Resolution settings (Safe from zoompan OOM)
    # GitHub Actions runners have 7GB RAM limit. With 25 inputs, 8K exceeds memory limits (exit code 143).
    is_ci = os.environ.get("GITHUB_ACTIONS") == "true" or os.environ.get("CI") == "true"
    if is_ci and quality in ["8k", "4k"]:
        print(f"⚠️ [Resource Guard] {quality.upper()} with 25 shots exceeds GitHub Actions 7GB RAM limit. Safe-scaling to 1080p (native Shorts resolution).")
        quality = "1080p"

    res_map = {
        "1080p": (1080, 1920),
        "4k": (2160, 3840),
        "8k": (4320, 7680)
    }
    w, h = res_map.get(quality, (1080, 1920))
    scale = w / 1080.0

    # Ensure shot image assets exist (targets 25 shots for high-retention 3-4s visual cuts)
    from image_generator import generate_story_assets
    episode_assets_dir = os.path.join(assets_base, story_id)
    generate_story_assets(story_data, target_shots=25)

    # Discover all available shot images
    shot_imgs = sorted([
        os.path.join(episode_assets_dir, f)
        for f in os.listdir(episode_assets_dir)
        if f.startswith("shot_") and f.endswith(".jpg")
    ])
    num_shots = len(shot_imgs) if shot_imgs else max(24, len(shots))

    # Step 1: Voiceover Audio (pluggable TTS engine — no asyncio.run needed)
    voice_path = os.path.join(output_dir, f"{story_id}_voice.mp3")
    generate_voiceover(voiceover_text, voice_path)
    duration = get_audio_duration(voice_path)
    print(f"⏱️ Audio Duration: {duration:.2f} seconds | Shots: {num_shots} ({duration / num_shots:.2f}s per cut)")

    # Step 2: Divine Ambient Soundscape (Om drone + temple bell)
    sfx_path = os.path.join(output_dir, f"{story_id}_divine_sfx.wav")
    synthesize_procedural_divine_audio(sfx_path, duration=duration)

    # Step 3: Broadcast-standard Audio Mix (normalize=0, loudnorm)
    mixed_audio_path = os.path.join(output_dir, f"{story_id}_mixed_audio.wav")
    audio_filter = (
        "[0:a]volume=1.0[v];"
        "[1:a]volume=0.15[s];"
        "[v][s]amix=inputs=2:duration=first:normalize=0,"
        "loudnorm=I=-16:TP=-1.5:LRA=11[out]"
    )
    cmd_audio = [
        "ffmpeg", "-y",
        "-i", voice_path,
        "-i", sfx_path,
        "-filter_complex", audio_filter,
        "-map", "[out]",
        mixed_audio_path
    ]
    subprocess.run(cmd_audio, check=True)

    # Step 4: Single-Frame Visual Assembly & Stutter-Free Zoompan
    shot_duration = duration / num_shots
    frames = int(shot_duration * 30)
    font_file = resolve_font()
    font_arg = f"fontfile='{font_file}':" if font_file else ""

    subtitles = split_script_into_subtitles(voiceover_text, num_shots, shots)

    input_args = []
    filter_chains = []

    for i in range(num_shots):
        if i < len(shot_imgs):
            shot_img = shot_imgs[i]
        else:
            shot_img = os.path.join(episode_assets_dir, f"shot_{i+1:02d}.jpg")
            if not os.path.exists(shot_img):
                from image_generator import generate_procedural_fallback
                generate_procedural_fallback(title, subtitles[i], shot_img, w, h)

        # Single-frame input (no -loop 1 -t)
        input_args.extend(["-i", shot_img])

        # 4-style alternating zoom/pan for visual variety
        style = i % 4
        if style == 0:
            # Slow zoom-in from center
            zoom_expr = f"zoom='min(zoom+0.0015,1.18)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
        elif style == 1:
            # Slow pan right with mild zoom
            zoom_expr = f"zoom='min(zoom+0.0010,1.12)':x='(iw-iw/zoom)*(on/{frames})':y='ih/2-(ih/zoom/2)'"
        elif style == 2:
            # Slow pan left with mild zoom
            zoom_expr = f"zoom='min(zoom+0.0010,1.12)':x='(iw-iw/zoom)*(1-on/{frames})':y='ih/2-(ih/zoom/2)'"
        else:
            # Slow tilt up (pan vertically)
            zoom_expr = f"zoom='min(zoom+0.0012,1.15)':x='iw/2-(iw/zoom/2)':y='(ih-ih/zoom)*(on/{frames})'"

        # Sanitize subtitle text and write to external textfile
        sub_file = os.path.join(output_dir, f"{story_id}_sub{i}.txt")
        clean_text = clean_sub(subtitles[i])
        wrapped_sub = textwrap.fill(clean_text, width=28)
        with open(sub_file, "w", encoding="utf-8") as sf:
            sf.write(wrapped_sub)

        # Subtitles in Shorts safe zone (y=1080 to 1340)
        box_y = int(1080 * scale)
        box_h = int(240 * scale)
        text_y = int(1110 * scale)

        sub_draw = (
            f"drawbox=x=0:y={box_y}:w={w}:h={box_h}:color=0x000000@0.70:t=fill,"
            f"drawtext={font_arg}textfile='{ff_path(sub_file)}':x=(w-text_w)/2:y={text_y}:"
            f"fontsize={int(48*scale)}:fontcolor=0xFFC300:shadowcolor=black:shadowx=3:shadowy=3:line_spacing=14,"
            f"setsar=1"
        )

        # Scale before zoompan to eliminate jitter/stutter (clamped to 2160x3840 max to prevent OOM)
        zoom_w = min(w * 2, 2160)
        zoom_h = min(h * 2, 3840)
        filter_chains.append(
            f"[{i}:v]scale={zoom_w}:{zoom_h}:force_original_aspect_ratio=increase,crop={zoom_w}:{zoom_h},"
            f"zoompan={zoom_expr}:d={frames}:s={w}x{h}:fps=30,"
            f"{sub_draw}[v{i}]"
        )

    # Concatenate all visual segments
    concat_inputs = "".join(f"[v{i}]" for i in range(num_shots))
    concat_filter = f"{concat_inputs}concat=n={num_shots}:v=1:a=0[vconcat]"

    # HUD & Branding overlay
    hud_filters = build_mythology_hud_filter(deity, season, w, h, font_arg, episode_num)
    hud_chain = ",".join(hud_filters)
    final_v_filter = f"[vconcat]{hud_chain}[vfinal]"

    full_filter = ";".join(filter_chains + [concat_filter, final_v_filter])

    output_video_path = os.path.join(output_dir, f"{story_id}_{quality}.mp4")

    cmd_render = [
        "ffmpeg", "-y",
        *input_args,
        "-i", mixed_audio_path,
        "-filter_complex", full_filter,
        "-map", "[vfinal]",
        "-map", f"{num_shots}:a",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        output_video_path
    ]

    print(f"🎬 Rendering Short ({quality})...")
    subprocess.run(cmd_render, check=True)

    size_mb = os.path.getsize(output_video_path) / (1024 * 1024)
    print(f"✅ VIDEO READY: {output_video_path} ({size_mb:.2f} MB)")

    # Automatically purge intermediate scratch audio and text files
    intermediate_files = [voice_path, sfx_path, mixed_audio_path] + [
        os.path.join(output_dir, f"{story_id}_sub{i}.txt") for i in range(num_shots)
    ]
    for temp_f in intermediate_files:
        try:
            if os.path.exists(temp_f):
                os.remove(temp_f)
        except Exception:
            pass

    return output_video_path

if __name__ == "__main__":
    story_files = [f for f in os.listdir(stories_dir) if f.startswith("story_") and f.endswith(".json")]
    if story_files:
        ep1_json = os.path.join(stories_dir, sorted(story_files)[0])
        produce_train_video(ep1_json, quality="1080p")
