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
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

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

BRAND_LABELS = {
    "en": "MINDNEST TALES",
    "hi": "माइंडनेस्ट टेल्स",
    "es": "MINDNEST TALES",
    "pt": "MINDNEST TALES",
    "fr": "MINDNEST TALES",
    "de": "MINDNEST TALES",
    "ar": "حكايات مايند نست",
    "ja": "マインドネスト・テイルズ",
    "ko": "마인드네스트 테일즈",
    "vi": "MINDNEST TALES",
    "fil": "MINDNEST TALES",
}

BOTTOM_LABELS = {
    "en": "Subscribe 💛 New stories every day",
    "hi": "सब्सक्राइब करें 💛 नई कहानियाँ हर दिन",
    "es": "Suscríbete 💛 Nuevas historias cada día",
    "pt": "Inscreva-se 💛 Novas histórias todos os dias",
    "fr": "Abonnez-vous 💛 De nouvelles histoires chaque jour",
    "de": "Abonnieren 💛 Jeden Tag neue Geschichten",
    "ar": "اشترك للمزيد 💛 حكايات جديدة كل يوم",
    "ja": "チャンネル登録してね 💛 毎日新しい物語",
    "ko": "구독하기 💛 매일 새로운 이야기",
    "vi": "Đăng ký kênh 💛 Câu chuyện mới mỗi ngày",
    "fil": "Mag-subscribe 💛 Mga bagong kwento araw-araw",
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
        "hi": "NotoSansDevanagari-Bold.ttf", # 100% Native Devanagari script support
        "en": "Poppins-Bold.ttf",            # Latin
        "es": "Poppins-Bold.ttf",            # Latin
        "pt": "Poppins-Bold.ttf",            # Latin
        "fr": "Poppins-Bold.ttf",            # Latin
        "de": "Poppins-Bold.ttf",            # Latin
        "fil": "Poppins-Bold.ttf",           # Latin
        "vi": "BeVietnamPro-Bold.ttf",       # Vietnamese diacritics + Latin
        "ar": "NotoSansArabic.ttf",          # Arabic + Latin
        "ja": "NotoSansJP.ttf",              # Japanese Kanji/Kana + Latin
        "ko": "NotoSansKR.ttf",              # Korean Hangul + Latin
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
        return 180.0

def generate_voiceover(script_text, voice, output_audio_path, rate="+2%", pitch="+0Hz"):
    """Generates expressive, human-like animated storyteller speech via edge-tts."""
    os.makedirs(os.path.dirname(output_audio_path) if os.path.dirname(output_audio_path) else ".", exist_ok=True)
    cmd = [
        sys.executable,
        "-m",
        "edge_tts",
        "--voice", voice,
        f"--rate={rate}",
        f"--pitch={pitch}",
        "--text", script_text,
        "--write-media", output_audio_path
    ]
    subprocess.run(cmd, check=True)
    print(f"Generated Voiceover: {output_audio_path} ({os.path.getsize(output_audio_path)} bytes)")
    return output_audio_path

def produce_story_video(story_data, lang_code, output_video_path, quality="1080p", target_duration=75.0):
    """
    Renders the complete 9:16 portrait video for a specific language channel.
    - Synchronizes 3D Pixar-style visual scenes with localized neural voiceover.
    - Applies smooth cinematic xfade crossfade transitions between all clips.
    - Strict Shorts safety runtime: 60-90 seconds (default 75.0s) for high-retention trailer funnel.
    - Guarantees 100% pure native typography with ZERO mixed English overlays on foreign language channels.
    - Supports '8k' (4320x7680), '4k' (2160x3840), or '1080p' (1080x1920).
    """
    os.makedirs(os.path.dirname(output_video_path) if os.path.dirname(output_video_path) else ".", exist_ok=True)
    config = load_network_config()
    
    ch_config = next((c for c in config["channels"] if c["lang_code"] == lang_code), config["channels"][0])
    translation = story_data["translations"].get(lang_code, story_data["translations"]["en"])
    
    voice = ch_config["voice"]
    rate = ch_config.get("voice_rate", "+2%")
    pitch = ch_config.get("voice_pitch", "+0Hz")
    # Script selection: For Shorts, prioritize the 60-90s Hook/Trailer short_script
    script = translation.get("short_script") or translation.get("script")
    title = translation.get("short_title") or translation.get("title")
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

    # 1. Generate Voiceover in native language (60-90s trailer pacing)
    audio_file = os.path.splitext(output_video_path)[0] + f"_{lang_code}_voice.mp3"
    generate_voiceover(script, voice, audio_file, rate=rate, pitch=pitch)
    raw_audio_dur = get_audio_duration(audio_file)
    
    # Target duration for Shorts: Strictly 60-90 seconds (default 75.0s) for high-retention trailer funnel
    if target_duration and 50.0 <= target_duration <= 90.0:
        duration = target_duration
    else:
        # Dynamically fit narration comfortably inside 60-88s window
        duration = min(max(raw_audio_dur + 1.5, 65.0), 88.0)

    # 2. Check for 3D Pixar Scene Assets (Auto-generates via Free Tier if missing)
    story_no = story_data.get("story_number", 1)
    assets_dir = os.path.join(script_dir, "stories", "assets", f"story_{story_no:02d}")
    try:
        from image_generator import build_narrative_shots, ensure_story_assets
        narrative_shots = build_narrative_shots(story_data)
        existing = [
            os.path.join(assets_dir, fn)
            for fn, _ in narrative_shots
            if os.path.exists(os.path.join(assets_dir, fn)) and os.path.getsize(os.path.join(assets_dir, fn)) > 10000
        ]
        if len(existing) >= 8:
            scene_images = existing
        else:
            scene_images = ensure_story_assets(story_no)
    except Exception as e:
        print(f"Notice: Asset manager note: {e}")

    if not scene_images and os.path.exists(assets_dir):
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
    display_title = clean_title.replace("#Shorts", "").replace("#shorts", "").strip()
    moral_text = translation.get("moral", "")
    if not moral_text:
        if lang_code == "en":
            moral_text = story_data.get("moral", "")
        else:
            fallback_morals = {
                "hi": "समय की पाबंदी ही असली रफ्तार है। हमेशा समय पर रहें और धैर्य से काम लें!",
                "es": "La mayor velocidad no significa nada sin el momento adecuado. ¡Sé puntual y reflexivo!",
                "pt": "A velocidade não significa nada sem o horário certo. Seja pontual e paciente!",
                "fr": "La plus grande vitesse ne signifie rien sans le bon timing. Sois ponctuel et réfléchi !",
                "de": "Die größte Geschwindigkeit bedeutet nichts ohne die richtige Zeit. Sei pünktlich und besonnen!",
                "ar": "السرعة بلا توقيت لا معنى لها. كن في الوقت المناسب دائماً!",
                "ja": "速さだけでは意味がない。時間を守ることが大切です。",
                "ko": "가장 빠른 속도도 적절한 타이밍 없이는 아무 소용이 없다.",
                "vi": "Tốc độ nhanh nhất cũng không có ý nghĩa gì nếu không đúng lúc.",
                "fil": "Ang bilis na hindi may tamang panahon ay walang halaga.",
            }
            moral_text = fallback_morals.get(lang_code, "")
    moral_label = MORAL_LABELS.get(lang_code, "MORAL")
    clean_moral = sanitize_ffmpeg_text(moral_text)

    # Localized brand header and bottom action text
    brand_title = BRAND_LABELS.get(lang_code, "MINDNEST TALES")
    bottom_text = BOTTOM_LABELS.get(lang_code, handle)
    clean_brand = sanitize_ffmpeg_text(brand_title)
    clean_bottom = sanitize_ffmpeg_text(bottom_text)

    # End-Card CTA (Last 4.5 seconds): Funnel viewer to the 10-Minute Full Episode
    cta_start_t = max(0.0, duration - 4.5)
    default_ctas = {
        "en": ("What happens next? 👉", "Full story link in description"),
        "hi": ("आगे क्या हुआ? 👉", "पूरी कहानी देखें लिंक नीचे है"),
        "es": ("¿Qué pasó después? 👉", "Historia completa en descripción"),
        "pt": ("O que acontece a seguir? 👉", "História completa no link"),
        "fr": ("Que se passe-t-il ensuite ? 👉", "Histoire complète en description"),
        "de": ("Wie geht es weiter? 👉", "Ganze Geschichte im Link"),
        "ar": ("ماذا حدث بعد ذلك؟ 👉", "القصة الكاملة في الرابط بالأسفل"),
        "ja": ("続きはどうなる？ 👉", "完全版は概要欄のリンクから！"),
        "ko": ("다음 이야기는? 👉", "설명란 링크에서 전체 감상!"),
        "vi": ("Chuyện gì xảy ra tiếp theo? 👉", "Xem trọn vẹn tại mô tả nhé!"),
        "fil": ("Ano ang susunod na mangyayari? 👉", "Panoorin ang buong kwento sa description!"),
    }
    cta_l1, cta_l2 = default_ctas.get(lang_code, default_ctas["en"])
    if translation.get("short_cta_text"):
        cta_l2 = translation["short_cta_text"]

    clean_cta_l1 = sanitize_ffmpeg_text(cta_l1)
    clean_cta_l2 = sanitize_ffmpeg_text(cta_l2)

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

    f_cta_h = int(40 * scale)
    f_cta_sub = int(28 * scale)
    y_cta_1 = int(box_bot_y + (48 * scale))
    y_cta_2 = int(box_bot_y + (125 * scale))

    # Font assignment: Ensure non-Latin scripts use native font for brand & bottom text
    is_non_latin = lang_code in ("hi", "ar", "ja", "ko", "vi")
    header_font_arg = font_arg if is_non_latin else (brand_font_arg or font_arg)
    bottom_font_arg = font_arg if is_non_latin else (brand_font_arg or font_arg)

    normal_enable = f":enable='between(t,0,{cta_start_t:.2f})'"
    cta_enable = f":enable='between(t,{cta_start_t:.2f},{duration:.2f})'"

    if len(moral_lines) > 1:
        y_badge = int(box_bot_y + (38 * scale))
        y_moral_1 = int(box_bot_y + (90 * scale))
        y_moral_2 = int(box_bot_y + (138 * scale))
        y_handle = int(box_bot_y + (192 * scale))
        moral_drawtext = (
            f"drawtext={font_arg}:text='- {moral_label} -':fontsize={f_badge}:fontcolor=0xf59e0b:x=(w-text_w)/2:y={y_badge}{normal_enable},"
            f"drawtext={font_arg}:text='{moral_lines[0]}':fontsize={f_moral}:fontcolor=0xffffff:x=(w-text_w)/2:y={y_moral_1}{normal_enable},"
            f"drawtext={font_arg}:text='{moral_lines[1]}':fontsize={f_moral}:fontcolor=0xffffff:x=(w-text_w)/2:y={y_moral_2}{normal_enable}"
        )
    else:
        y_badge = int(box_bot_y + (50 * scale))
        y_moral_1 = int(box_bot_y + (110 * scale))
        y_handle = int(box_bot_y + (182 * scale))
        moral_drawtext = (
            f"drawtext={font_arg}:text='- {moral_label} -':fontsize={f_badge}:fontcolor=0xf59e0b:x=(w-text_w)/2:y={y_badge}{normal_enable},"
            f"drawtext={font_arg}:text='{moral_lines[0]}':fontsize={f_moral}:fontcolor=0xffffff:x=(w-text_w)/2:y={y_moral_1}{normal_enable}"
        )

    endcard_drawtext = (
        f"drawbox=y={box_bot_y}:h={box_bot_h}:color=0xb45309@0.92:t=fill{cta_enable},"
        f"drawtext={header_font_arg}:text='{clean_cta_l1}':fontsize={f_cta_h}:fontcolor=0xffffff:x=(w-text_w)/2:y={y_cta_1}{cta_enable},"
        f"drawtext={bottom_font_arg}:text='{clean_cta_l2}':fontsize={f_cta_sub}:fontcolor=0xfef08a:x=(w-text_w)/2:y={y_cta_2}{cta_enable}"
    )

    overlay_filters = (
        f"drawbox=y=0:h={box_top_h}:color=0x0a0f1d@0.65:t=fill,"
        f"drawbox=y={box_bot_y}:h={box_bot_h}:color=0x0a0f1d@0.65:t=fill{normal_enable},"
        f"drawtext={header_font_arg}:text='{clean_brand}':fontsize={f_brand}:fontcolor=0xf59e0b:x=(w-text_w)/2:y={y_brand},"
        f"drawtext={font_arg}:text='{display_title}':fontsize={f_title}:fontcolor=0xffffff:x=(w-text_w)/2:y={y_title},"
        f"{moral_drawtext},"
        f"drawtext={bottom_font_arg}:text='{clean_bottom}':fontsize={f_handle}:fontcolor=0x94a3b8:x=(w-text_w)/2:y={y_handle}{normal_enable},"
        f"{endcard_drawtext}"
    )

    def prepare_optimized_scene_images(scenes, target_w, target_h, cache_dir):
        try:
            from PIL import Image, ImageOps
            opt_dir = os.path.join(cache_dir, "optimized_scenes")
            os.makedirs(opt_dir, exist_ok=True)
            optimized = []
            for idx, img in enumerate(scenes):
                if not os.path.exists(img):
                    continue
                out_path = os.path.join(opt_dir, f"opt_{idx:02d}_{target_w}x{target_h}_" + os.path.basename(img))
                if os.path.exists(out_path):
                    optimized.append(out_path)
                    continue
                with Image.open(img) as im:
                    im = im.convert("RGB")
                    fitted = ImageOps.fit(im, (target_w, target_h), method=Image.Resampling.LANCZOS)
                    fitted.save(out_path, format="PNG", optimize=False)
                optimized.append(out_path)
            if len(optimized) == len(scenes):
                return optimized, True
        except Exception:
            pass
        return scenes, False

    ffmpeg_inputs = []
    temp_render_dir = os.path.dirname(output_video_path)
    if len(scene_images) > 1:
        # Multi-Scene with Smooth Cinematic Crossfade Transitions (Paced for 60-90s)
        max_scenes = 8
        if len(scene_images) > max_scenes:
            step = len(scene_images) / max_scenes
            selected_scenes = [scene_images[int(i * step)] for i in range(max_scenes)]
        else:
            selected_scenes = scene_images

        optimized_scenes, is_opt = prepare_optimized_scene_images(selected_scenes, w, h, temp_render_dir)
        scale_op = "" if is_opt else f"scale={w}:{h}:force_original_aspect_ratio=increase:flags=lanczos,crop={w}:{h},"
        num_scenes = len(optimized_scenes)
        fade_dur = 0.5
        L = (duration + (num_scenes - 1) * fade_dur) / num_scenes

        scale_parts = []
        for i, img in enumerate(optimized_scenes):
            clean_img = os.path.abspath(img).replace("\\", "/")
            ffmpeg_inputs.extend(["-loop", "1", "-t", f"{L:.3f}", "-i", clean_img])
            scale_parts.append(
                f"[{i}:v]{scale_op}setsar=1,fps=30[s{i}];"
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
        optimized_scenes, is_opt = prepare_optimized_scene_images(scene_images, w, h, temp_render_dir)
        scale_op = "" if is_opt else f"scale={w}:{h}:force_original_aspect_ratio=increase:flags=lanczos,crop={w}:{h},"
        clean_img = os.path.abspath(optimized_scenes[0]).replace("\\", "/")
        ffmpeg_inputs.extend(["-loop", "1", "-t", f"{duration:.3f}", "-i", clean_img])
        full_filter = f"[0:v]{scale_op}setsar=1,fps=30[vbase];[vbase]{overlay_filters}[v]"
        audio_idx = 1
    else:
        # Fallback Dynamic Cinematic Gradient
        ffmpeg_inputs.extend(["-f", "lavfi", "-i", f"color=c=0x1a1528:s={w}x{h}:r=30:d={duration:.2f}"])
        full_filter = f"[0:v]{overlay_filters}[v]"
        audio_idx = 1

    # Ensure audio fits smoothly and finishes before video ends without clipping words
    target_speech_dur = duration - 3.0
    if raw_audio_dur > target_speech_dur:
        speed_factor = raw_audio_dur / target_speech_dur
        print(f"⏱️ Audio sync: Auto-adjusting narration tempo by {speed_factor:.2f}x to fit full story into {duration:.1f}s perfectly without clipping words.")
        audio_filter = f"[{audio_idx}:a]atempo={speed_factor:.4f},atrim=0:{duration:.2f},apad=whole_dur={duration:.2f}[a]"
    else:
        audio_filter = f"[{audio_idx}:a]atrim=0:{duration:.2f},apad=whole_dur={duration:.2f}[a]"
    final_filter = f"{full_filter};{audio_filter}"

    ffmpeg_cmd = [
        "ffmpeg", "-y",
        *ffmpeg_inputs,
        "-i", audio_file,
        "-filter_complex", final_filter,
        "-map", "[v]", "-map", "[a]",
        "-t", f"{duration:.2f}",
        "-shortest",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "20",
        "-threads", "0",
        "-sws_flags", "fast_bilinear",
        "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        output_video_path
    ]

    print(f"🎬 Rendering [{lang_code.upper()}] at {quality.upper()} ({w}x{h}) for 3:00 runtime ({duration:.1f}s)...")
    subprocess.run(ffmpeg_cmd, check=True)

    if os.path.exists(audio_file):
        os.remove(audio_file)

    print(f"SUCCESS [{lang_code.upper()}]: Rendered {output_video_path} ({os.path.getsize(output_video_path)} bytes)")
    return output_video_path

def produce_all_languages(story_number=1, output_dir="/tmp/mindnest_batch", quality="1080p"):
    """Produces the story video dubbed across all 11 languages at 1080p/4K."""
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
    quality = sys.argv[3] if len(sys.argv) > 3 else "1080p"
    story = load_story(story_no)
    produce_story_video(story, lang, f"story_{story_no}_{lang}_{quality}.mp4", quality=quality)
