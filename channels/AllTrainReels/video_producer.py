"""
AllTrainReels Dynamic 9:16 Portrait Rail Video Producer
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

def synthesize_procedural_rail_audio(output_audio_path, duration=25.0):
    """
    Synthesizes an authentic procedural railway soundscape via pure Python wave module:
    - Rhythmic track clatter (ta-dak ta-dak low pulses)
    - Distant resonant locomotive horn blast
    - Low rail hum
    100% robust, zero FFmpeg filter crashes.
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
        # 1. Distant horn (first 2 seconds)
        horn = 0.0
        if t < 2.0:
            env = math.sin((t / 2.0) * math.pi)
            horn = (math.sin(2 * math.pi * 329.63 * t) * 0.3 + math.sin(2 * math.pi * 440.0 * t) * 0.25) * env * 0.25

        # 2. Rhythmic track clatter (two clicks every 0.6 seconds)
        cycle_pos = t % 0.6
        clatter = 0.0
        if cycle_pos < 0.04:
            clatter += math.sin(2 * math.pi * 90 * cycle_pos) * math.exp(-cycle_pos * 70) * 0.25
        elif 0.12 < cycle_pos < 0.16:
            p2 = cycle_pos - 0.12
            clatter += math.sin(2 * math.pi * 110 * p2) * math.exp(-p2 * 70) * 0.18

        # 3. Low rumble
        rumble = math.sin(2 * math.pi * 55 * t) * 0.05

        sample = horn + clatter + rumble
        sample = max(-0.95, min(0.95, sample))
        int_sample = int(sample * 32767)
        frames.extend(struct.pack("<hh", int_sample, int_sample))

    wav_file.writeframes(frames)
    wav_file.close()
    print(f"🎵 [Procedural Rail Sound] Synthesized: {output_audio_path}")
    return True

def build_railway_hud_filter(theme, w, h, font_arg, episode_num):
    """Builds visual HUD overlay filters strictly avoiding the bottom Shorts safe zone."""
    scale = w / 1080.0

    # Persistent brand banner on top (Safe zone: y=0 to 140)
    brand_filters = [
        f"drawbox=x=0:y=0:w={w}:h={int(130*scale)}:color=0x0B1F3A@0.85:t=fill",
        f"drawbox=x=0:y={int(130*scale)}:w={w}:h={int(6*scale)}:color=0xE63946@1.0:t=fill",
        f"drawtext={font_arg}text='ALL TRAIN REELS':x={int(45*scale)}:y={int(35*scale)}:fontsize={int(32*scale)}:fontcolor=0xFFC300:shadowcolor=black:shadowx=2:shadowy=2",
        f"drawtext={font_arg}text='EPISODE #{episode_num:02d}':x={w - int(240*scale)}:y={int(35*scale)}:fontsize={int(28*scale)}:fontcolor=0xF1F5F9:shadowcolor=black:shadowx=2:shadowy=2"
    ]

    # Contextual top badge (y=150 to 220)
    if theme == "SPEEDOMETER_HUD":
        badge = [
            f"drawbox=x={w - int(280*scale)}:y={int(150*scale)}:w={int(240*scale)}:h={int(60*scale)}:color=0x0B1F3A@0.85:t=fill",
            f"drawbox=x={w - int(280*scale)}:y={int(150*scale)}:w={int(6*scale)}:h={int(60*scale)}:color=0xFFC300@1.0:t=fill",
            f"drawtext={font_arg}text='HIGH-SPEED':x={w - int(255*scale)}:y={int(165*scale)}:fontsize={int(24*scale)}:fontcolor=0xFFC300:shadowcolor=black:shadowx=2:shadowy=2"
        ]
        return brand_filters + badge

    elif theme == "SPLIT_VS_ARENA":
        badge = [
            f"drawbox=x={w//2 - int(60*scale)}:y={int(150*scale)}:w={int(120*scale)}:h={int(60*scale)}:color=0xE63946@0.95:t=fill",
            f"drawtext={font_arg}text='VS':x={w//2 - int(22*scale)}:y={int(162*scale)}:fontsize={int(36*scale)}:fontcolor=0xFFFFFF:shadowcolor=black:shadowx=2:shadowy=2"
        ]
        return brand_filters + badge

    elif theme == "VINTAGE_STEAM_GAUGE":
        badge = [
            f"drawbox=x={int(40*scale)}:y={int(150*scale)}:w={int(260*scale)}:h={int(60*scale)}:color=0x2c1a0e@0.85:t=fill",
            f"drawtext={font_arg}text='HERITAGE STEAM':x={int(55*scale)}:y={int(165*scale)}:fontsize={int(24*scale)}:fontcolor=0xE0A96D:shadowcolor=black:shadowx=2:shadowy=2"
        ]
        return brand_filters + badge

    elif theme == "CABIN_POV_RADAR":
        badge = [
            f"drawbox=x={w - int(280*scale)}:y={int(150*scale)}:w={int(240*scale)}:h={int(60*scale)}:color=0x0B1F3A@0.85:t=fill",
            f"drawtext={font_arg}text='CABIN VIEW':x={w - int(255*scale)}:y={int(165*scale)}:fontsize={int(24*scale)}:fontcolor=0x22C55E:shadowcolor=black:shadowx=2:shadowy=2"
        ]
        return brand_filters + badge

    return brand_filters

def produce_train_video(story_json_path, quality="1080p"):
    """
    Renders an end-to-end 9:16 YouTube Short from a story JSON file:
    - Eliminates -loop 1 -t frame explosion bug (uses single frame input + upscale to eliminate zoompan stutter)
    - Subtitles rendered in Shorts safe zone (y=1080-1350) via sanitized textfiles
    - Audio mixed via amix(normalize=0) and loudnorm(-16 LUFS)
    """
    with open(story_json_path, "r", encoding="utf-8") as f:
        story_data = json.load(f)

    story_id = story_data["story_id"]
    title = story_data["title"]
    episode_num = story_data.get("episode_number", 1)
    visual_theme = story_data.get("visual_theme", "SPEEDOMETER_HUD")
    voiceover_text = story_data.get("voiceover_script", "")
    shots = story_data.get("shots", [])

    print(f"\n==================================================")
    print(f"🚂 PRODUCING ALLTRAINREELS SHORT #{episode_num:02d}: {title}")
    print(f"==================================================")

    # Resolution settings (Safe from zoompan OOM)
    res_map = {
        "1080p": (1080, 1920),
        "4k": (2160, 3840),
        "8k": (4320, 7680)
    }
    w, h = res_map.get(quality, (2160, 3840))
    scale = w / 1080.0

    # Ensure shot image assets exist
    from image_generator import generate_story_assets
    episode_assets_dir = os.path.join(assets_base, story_id)
    generate_story_assets(story_json_path)

    # Step 1: Voiceover Audio (pluggable TTS engine — no asyncio.run needed)
    voice_path = os.path.join(output_dir, f"{story_id}_voice.mp3")
    generate_voiceover(voiceover_text, voice_path)
    duration = get_audio_duration(voice_path)
    print(f"⏱️ Audio Duration: {duration:.2f} seconds")

    # Step 2: Procedural Rail Soundscape
    sfx_path = os.path.join(output_dir, f"{story_id}_rail_sfx.wav")
    synthesize_procedural_rail_audio(sfx_path, duration=duration)

    # Step 3: Broadcast-standard Audio Mix (normalize=0, loudnorm)
    mixed_audio_path = os.path.join(output_dir, f"{story_id}_mixed_audio.wav")
    audio_filter = (
        "[0:a]volume=1.0[v];"
        "[1:a]volume=0.10[s];"
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
    num_shots = len(shots)
    shot_duration = duration / num_shots
    frames = int(shot_duration * 30)
    font_file = resolve_font()
    font_arg = f"fontfile='{font_file}':" if font_file else ""

    input_args = []
    filter_chains = []

    def prepare_optimized_shot(img_path, target_w, target_h, cache_dir):
        try:
            from PIL import Image, ImageOps
            out_path = os.path.join(cache_dir, f"opt_{target_w}x{target_h}_" + os.path.basename(img_path))
            if os.path.exists(out_path):
                return out_path
            with Image.open(img_path) as im:
                im = im.convert("RGB")
                fitted = ImageOps.fit(im, (target_w, target_h), method=Image.Resampling.LANCZOS)
                fitted.save(out_path, format="JPEG", quality=95)
            return out_path
        except Exception:
            return img_path

    zoom_w = min(int(w * 1.25), 2160)
    zoom_h = min(int(h * 1.25), 3840)

    for i in range(num_shots):
        shot_img = os.path.join(episode_assets_dir, f"shot_{i+1:02d}.jpg")
        if not os.path.exists(shot_img):
            from image_generator import generate_procedural_fallback
            generate_procedural_fallback(title, shots[i].get("subtitle", ""), shot_img, w, h)

        opt_shot = prepare_optimized_shot(shot_img, zoom_w, zoom_h, output_dir)
        input_args.extend(["-i", opt_shot])

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
        clean_text = clean_sub(shots[i].get("subtitle", ""))
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

        # Hardware-efficient zoompan on pre-scaled image
        filter_chains.append(
            f"[{i}:v]zoompan={zoom_expr}:d={frames}:s={w}x{h}:fps=30,"
            f"{sub_draw}[v{i}]"
        )

    # Concatenate all visual segments
    concat_inputs = "".join(f"[v{i}]" for i in range(num_shots))
    concat_filter = f"{concat_inputs}concat=n={num_shots}:v=1:a=0[vconcat]"

    # HUD & Branding overlay
    hud_filters = build_railway_hud_filter(visual_theme, w, h, font_arg, episode_num)
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
        "-preset", "ultrafast",
        "-crf", "20",
        "-threads", "0",
        "-sws_flags", "fast_bilinear",
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
    ep1_json = os.path.join(stories_dir, "story_01_01_scmaglev_603kmh.json")
    if os.path.exists(ep1_json):
        produce_train_video(ep1_json, quality="1080p")
