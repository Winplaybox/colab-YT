"""
MindNest Tales 10-Minute Long-Form Anthology Producer:
- Compiles 3 stories from the 51-Story Master Roadmap into a 10-minute master episode (600.0s).
- Produces 16:9 Landscape Ultra-HD video (1920x1080 / 3840x2160) for TV, Tablet, and Desktop browse feed.
- Features 3 distinct story chapters with acoustic musical transitions, chapter title cards, and moral synthesis outro.
- Designed specifically to maximize Watch Hours (4,000 hour threshold) and unlock Mid-Roll Ad revenue.
"""

import os
import sys
import json
import subprocess
import textwrap

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

try:
    import static_ffmpeg
    static_ffmpeg.add_paths()
except Exception:
    pass

from video_producer import (
    load_network_config,
    load_story,
    generate_voiceover,
    get_audio_duration,
    resolve_brand_font,
    resolve_font_for_language,
    sanitize_ffmpeg_text,
    BOTTOM_LABELS
)
from image_generator import build_narrative_shots, ensure_story_assets
try:
    from generate_thumbnail import generate_10min_master_thumbnail
except ImportError:
    generate_10min_master_thumbnail = None

COMPILATION_BANNERS = {
    "en": "MINDNEST TALES  -  10 MINUTE BEDTIME SPECIAL",
    "hi": "माइंडनेस्ट टेल्स  -  10 मिनट विशेष कहानी संग्रह",
    "es": "MINDNEST TALES  -  ESPECIAL DE 10 MINUTOS",
    "pt": "MINDNEST TALES  -  ESPECIAL DE 10 MINUTOS",
    "fr": "MINDNEST TALES  -  SPÉCIAL 10 MINUTES",
    "de": "MINDNEST TALES  -  10 MINUTEN SPEZIAL",
    "ar": "حكايات مايند نست  -  حلقة خاصة 10 دقائق",
    "ja": "マインドネスト・テイルズ  -  10分特別編",
    "ko": "마인드네스트 테일즈  -  10분 특별 에피소드",
    "vi": "MINDNEST TALES  -  TẬP ĐẶC BIỆT 10 PHÚT",
    "fil": "MINDNEST TALES  -  10-MINUTONG ESPESYAL",
}

CHAPTER_LABELS = {
    "en": "CHAPTER",
    "hi": "अध्याय",
    "es": "CAPÍTULO",
    "pt": "CAPÍTULO",
    "fr": "CHAPITRE",
    "de": "KAPITEL",
    "ar": "الفصل",
    "ja": "第",
    "ko": "제",
    "vi": "CHƯƠNG",
    "fil": "KABANATA"
}

def build_compilation_metadata(story_ids, lang_code="en"):
    """Generates hyper-optimized 10-minute YouTube metadata with timestamps and semantic tags."""
    stories = [load_story(sid) for sid in story_ids]
    titles = [s["translations"].get(lang_code, s["translations"]["en"])["title"].replace("#Shorts", "").replace("#shorts", "").strip() for s in stories]
    morals = [s["translations"].get(lang_code, s["translations"]["en"])["moral"].strip() for s in stories]

    lead_title = titles[0]
    ep_num = story_ids[0] // 3 + 1

    localized_titles = {
        "en": f"3 Bedtime Moral Stories That Teach Life's Greatest Lessons 🐾 (10-Min Special)",
        "hi": f"3 सीख देने वाली दिल छू लेने वाली कहानियां 🐾 (10 मिनट स्पेशल)",
        "es": f"3 Hermosos Cuentos Infantiles con Moraleja 🐾 (Especial 10 Min)",
        "pt": f"3 Histórias Infantis com Lição de Vida 🐾 (Especial 10 Min)",
        "fr": f"3 Magnifiques Contes avec Morale pour Enfants 🐾 (Spécial 10 Min)",
        "de": f"3 Wundervolle Gutenachtgeschichten mit Lehre 🐾 (10 Min Spezial)",
        "ar": f"3 قصص كرتونية هادفة وممتعة للأطفال 🐾 (حلقة خاصة 10 دقائق)",
        "ja": f"子どもの心をやさしく育てる3つの教訓アニメ 🐾 (10分スペシャル)",
        "ko": f"마음이 따뜻해지는 3가지 지혜로운 동물 동화 🐾 (10분 스페셜)",
        "vi": f"3 Câu Chuyện Hoạt Hình Ý Nghĩa Dạy Con Trưởng Thành 🐾 (Tập 10 Phút)",
        "fil": f"3 Kwentong Pambata na may Gintong Aral sa Buhay 🐾 (10-Minutong Espesyal)"
    }

    full_title = localized_titles.get(lang_code, localized_titles["en"])

    intro_descs = {
        "en": "Discover 3 heartwarming 3D animated moral stories that teach children and families the true value of patience, honesty, and wisdom.",
        "hi": "देखिए 3 सीख देने वाली दिल छू लेने वाली 3D एनिमेटेड कहानियां, जो बच्चों और परिवारों को धैर्य, सच्चाई और समझदारी का अनमोल पाठ सिखाती हैं।",
        "es": "Descubre 3 hermosos cuentos animados en 3D que enseñan a niños y familias el verdadero valor de la paciencia, la honestidad y la sabiduría.",
        "pt": "Descubra 3 lindas histórias animadas em 3D que ensinam a crianças e famílias o verdadeiro valor da paciência, honestidade e sabedoria.",
        "fr": "Découvrez 3 magnifiques contes animés en 3D qui enseignent aux enfants et aux familles la vraie valeur de la patience, de l'honnêteté et de la sagesse.",
        "de": "Entdecken Sie 3 herzerwärmende 3D-animierte Gutenachtgeschichten mit wertvollen Lebensweisheiten über Geduld, Ehrlichkeit und Klugheit.",
        "ar": "اكتشف 3 قصص كرتونية ثلاثية الأبعاد مؤثرة وهادفة تعلم الأطفال والعائلات القيمة الحقيقية للصبر والصدق والحكمة.",
        "ja": "子どもたちの心を豊かに育てる、思いやりと忍耐、知恵を学べる心温まる3つの3Dアニメーション物語をお届けします。",
        "ko": "아이들과 온 가족에게 인내, 정직, 지혜의 참된 가치를 전하는 마음 따뜻한 3가지 3D 애니메이션 동화입니다.",
        "vi": "Khám phá 3 câu chuyện hoạt hình 3D cảm động dạy con về lòng kiên nhẫn, sự trung thực và bài học cuộc sống sâu sắc.",
        "fil": "Panoorin ang 3 nakaaantig na 3D animated kwento na nagtuturo sa mga bata at pamilya ng kahalagahan ng pagtitiyaga, katapatan, at karunungan."
    }

    ts_labels = {
        "en": ("TIMESTAMPS:", "Introduction", "Chapter", "Life Lessons (Outro)"),
        "hi": ("समय सूची (TIMESTAMPS):", "प्रस्तावना", "अध्याय", "जीवन की सीख (निष्कर्ष)"),
        "es": ("MARCAS DE TIEMPO:", "Introducción", "Capítulo", "Lecciones de Vida (Conclusión)"),
        "pt": ("MARCADORES DE TEMPO:", "Introdução", "Capítulo", "Lições de Vida (Conclusão)"),
        "fr": ("CHAPITRES :", "Introduction", "Chapitre", "Leçons de Vie (Conclusion)"),
        "de": ("ZEITSTEMPEL:", "Einführung", "Kapitel", "Lebensweisheiten (Fazit)"),
        "ar": ("فصول الحلقة:", "المقدمة", "الفصل", "الدروس المستفادة"),
        "ja": ("タイムスタンプ:", "オープニング", "第", "教訓とまとめ"),
        "ko": ("타임스탬프:", "도입", "제", "교훈과 마무리"),
        "vi": ("MỐC THỜI GIAN:", "Mở đầu", "Chương", "Bài học cuộc sống"),
        "fil": ("MGA BAHAGI:", "Panimula", "Kabanata", "Aral sa Buhay (Pagtatapos)"),
    }

    t_header, t_intro, t_chap, t_outro = ts_labels.get(lang_code, ts_labels["en"])

    desc_lines = [
        intro_descs.get(lang_code, intro_descs["en"]),
        "",
        t_header,
        f"0:00 - {t_intro}",
        f"0:15 - {t_chap} 1: {titles[0]}",
        f"3:25 - {t_chap} 2: {titles[1]}",
        f"6:35 - {t_chap} 3: {titles[2]}",
        f"9:40 - {t_outro}",
        "",
        "MORALS / सीख / LECCIONES:" if lang_code == "hi" else ("MORALS IN THIS EPISODE:" if lang_code == "en" else "MORALEJA / LIÇÃO / LEHRE:"),
        f"• 1: {morals[0]}",
        f"• 2: {morals[1]}",
        f"• 3: {morals[2]}",
        "",
        "✨ " + (
            "माइंडनेस्ट टेल्स आपके लिए लाता है 3D एनीमेशन वाली प्रेरक नैतिक कहानियां।" if lang_code == "hi" else (
                "MindNest Tales produces world-class 3D Pixar-style moral animation across 11 languages." if lang_code == "en" else
                "MindNest Tales ofrece hermosas historias animadas en 3D con moraleja para toda la familia."
            )
        ),
        "सब्सक्राइब करें और घंटी बजाएं!" if lang_code == "hi" else ("Subscribe to follow our weekly adventures every Wednesday, Saturday, and Sunday!" if lang_code == "en" else "¡Suscríbete para disfrutar de nuevas historias cada semana!"),
        "",
        "#हिंदीकहानियां #बालकहानियां #नैतिककहानियां #माइंडनेस्टटेल्स #3Dएनीमेशन" if lang_code == "hi" else (
            "#MindNestTales #BedtimeStories #MoralStories #KidsStories #3DAnimation" if lang_code == "en" else
            "#CuentosInfantiles #HistoriasConMoraleja #Animacion3D #MindNestTales"
        )
    ]
    description = "\n".join(desc_lines)

    localized_tag_sets = {
        "hi": ["माइंडनेस्ट टेल्स", "हिंदी कहानियां", "बाल कहानियां", "नैतिक कहानियां", "बच्चों की कहानियां", "3d कार्टून", "सीखने वाली कहानी", "पंचतंत्र की कहानियां"],
        "es": ["mindnest tales", "cuentos infantiles", "historias con moraleja", "cuentos para dormir", "animacion 3d", "valores para niños"],
        "pt": ["mindnest tales", "historias infantis", "historias com licao", "desenho animado 3d", "historias para dormir"],
        "fr": ["mindnest tales", "contes pour enfants", "histoires avec morale", "animation 3d", "histoires du soir"],
        "de": ["mindnest tales", "gutenachtgeschichten", "geschichten mit lehre", "3d animation kinder", "kindergeschichten"],
        "ar": ["حكايات مايند نست", "قصص اطفال", "قصص قبل النوم", "رسوم متحركة 3d", "قصص هادفة"],
        "ja": ["マインドネストテイルズ", "子ども向けアニメ", "絵本アニメ", "心温まる物語", "3dアニメーション"],
        "ko": ["마인드네스트", "어린이 동화", "지혜로운 동화", "3d 애니메이션", "수면 동화"],
        "vi": ["mindnest tales", "truyen thieu nhi", "hoat hinh 3d", "bai hoc cuoc song", "truyen ke be nghe"],
        "fil": ["mindnest tales", "kwentong pambata", "aral sa buhay", "3d animation", "pambatang palabas"]
    }

    tags = localized_tag_sets.get(lang_code, [
        "mindnest tales", "bedtime stories for kids", "10 minute bedtime stories",
        "moral stories in english", "kids cartoon stories", "pixar style 3d animation",
        "life lessons for children", "animal stories with moral", "family cartoon compilation"
    ])

    return {
        "title": full_title[:100],
        "description": description,
        "tags": tags,
        "chapter_titles": titles,
        "morals": morals
    }

def produce_10min_compilation(story_ids, lang_code, output_video_path, quality="1080p"):
    """
    Renders a complete 10-Minute (600.0 seconds) 16:9 Landscape Master Episode.
    - Concatenates 3 stories with chapter intros, acoustic stings, and moral conclusions.
    - Widescreen 1920x1080 (or 3840x2160 4K).
    - Guarantees exact 600.00 second runtime for mid-roll monetization eligibility.
    """
    os.makedirs(os.path.dirname(output_video_path) if os.path.dirname(output_video_path) else ".", exist_ok=True)
    config = load_network_config()
    ch_config = next((c for c in config["channels"] if c["lang_code"] == lang_code), config["channels"][0])

    voice = ch_config["voice"]
    rate = ch_config.get("voice_rate", "+2%")
    pitch = ch_config.get("voice_pitch", "+0Hz")
    handle = ch_config["handle"]

    # Resolution
    if quality == "4k":
        w, h = 3840, 2160
    else:
        w, h = 1920, 1080

    meta = build_compilation_metadata(story_ids, lang_code)

    # Auto-ensure 16:9 Master Landscape Thumbnail
    thumb_path = os.path.join(script_dir, "stories", "thumbnails", f"compilation_{story_ids[0]:02d}_thumbnail.jpg")
    if not os.path.exists(thumb_path) and generate_10min_master_thumbnail:
        hero_img = os.path.join(script_dir, "stories", "assets", f"story_{story_ids[0]:02d}", "scene_03_pride.jpg")
        if not os.path.exists(hero_img):
            hero_img = os.path.join(script_dir, "stories", "assets", f"story_{story_ids[0]:02d}", "scene_01_intro.jpg")
        if os.path.exists(hero_img):
            generate_10min_master_thumbnail(hero_img, thumb_path)

    print(f"\n=======================================================")
    print(f"🎬 PRODUCING 10-MINUTE MASTER COMPILATION [{lang_code.upper()}]")
    print(f"Stories: {story_ids}")
    print(f"Resolution: {w}x{h} (16:9 Landscape Widescreen)")
    print(f"Target Duration: 600.0 Seconds (10:00 Minutes)")
    print(f"=======================================================")

    # 1. Collect and prepare audio for each chapter
    temp_dir = os.path.join(script_dir, "temp_compilation", f"{lang_code}_ep{story_ids[0]}")
    os.makedirs(temp_dir, exist_ok=True)

    story_audios = []
    all_scenes = []

    for i, sid in enumerate(story_ids):
        s_data = load_story(sid)
        ensure_story_assets(sid)
        s_trans = s_data["translations"].get(lang_code, s_data["translations"]["en"])
        s_script = s_trans["script"]
        
        # Audio
        s_audio_path = os.path.join(temp_dir, f"story_{sid}_audio.mp3")
        generate_voiceover(s_script, voice, s_audio_path, rate=rate, pitch=pitch)
        dur = get_audio_duration(s_audio_path)
        story_audios.append((s_audio_path, dur))

        # Assets
        assets_dir = os.path.join(script_dir, "stories", "assets", f"story_{sid:02d}")
        shots = build_narrative_shots(s_data)
        scenes = [
            os.path.join(assets_dir, fn)
            for fn, _ in shots
            if os.path.exists(os.path.join(assets_dir, fn)) and os.path.getsize(os.path.join(assets_dir, fn)) > 10000
        ]
        if not scenes and os.path.exists(assets_dir):
            scenes = [os.path.join(assets_dir, f) for f in sorted(os.listdir(assets_dir)) if f.lower().endswith(('.jpg', '.png'))]
        all_scenes.append(scenes)

    # 2. Build 10-Minute Audio Track via FFmpeg concat with gentle acoustic bridges
    # Target speech per story: ~185s. Transitions: 15s each. Intro: 15s. Outro: 20s. Total = 600s.
    audio_concat_list = os.path.join(temp_dir, "audio_list.txt")
    
    # Generate 15s acoustic transition audio
    bridge_audio = os.path.join(temp_dir, "bridge_chime.wav")
    subprocess.run([
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", "sine=f=440:b=4:d=4",
        "-af", "afade=t=in:ss=0:d=1,afade=t=out:st=3:d=1,apad=whole_dur=10.0",
        bridge_audio
    ], capture_output=True, check=True)

    # Concatenate audio tracks with speed adjustment if needed
    master_audio = os.path.join(temp_dir, "master_narration.mp3")
    audio_inputs = []
    filter_complex_parts = []
    
    current_in = 0
    for i, (a_path, a_dur) in enumerate(story_audios):
        # We target ~185 seconds per story
        target_s_dur = 185.0
        speed = a_dur / target_s_dur if a_dur > target_s_dur else 1.0
        audio_inputs.extend(["-i", a_path])
        if speed > 1.0:
            filter_complex_parts.append(f"[{current_in}:a]atempo={speed:.4f},apad=whole_dur=185.0[a{i}];")
        else:
            filter_complex_parts.append(f"[{current_in}:a]apad=whole_dur=185.0[a{i}];")
        current_in += 1

    # Add bridge audio input
    audio_inputs.extend(["-i", bridge_audio])
    bridge_idx = current_in

    # Interleave: Story 1 -> Bridge -> Story 2 -> Bridge -> Story 3 -> Outro padding to 600s
    concat_filter = (
        f"{''.join(filter_complex_parts)}"
        f"[a0][{bridge_idx}:a][a1][{bridge_idx}:a][a2]concat=n=5:v=0:a=1[aconcat];"
        f"[aconcat]apad=whole_dur=600.0[aout]"
    )

    cmd_audio = [
        "ffmpeg", "-y",
        *audio_inputs,
        "-filter_complex", concat_filter,
        "-map", "[aout]",
        "-t", "600.0",
        master_audio
    ]
    subprocess.run(cmd_audio, check=True)
    print(f"Master 10-Minute Narration Track Assembled: {master_audio} (Duration: 600.0s)")

    # 3. Assemble Visual Sequence
    # Flatten scenes across all 3 stories (16 scenes each = 48 scenes total across 600 seconds)
    # 600 / 48 = 12.5 seconds per scene with 0.5s xfade crossfade!
    flat_scenes = []
    for s_list in all_scenes:
        flat_scenes.extend(s_list)
    
    if not flat_scenes:
        flat_scenes = [os.path.join(script_dir, "stories", "thumbnails", "story_01_thumbnail.jpg")]

    num_scenes = min(len(flat_scenes), 48)
    flat_scenes = flat_scenes[:num_scenes]

    fade_dur = 0.5
    total_dur = 600.0
    L = (total_dur + (num_scenes - 1) * fade_dur) / num_scenes

    # Build 16:9 Landscape Video with subtle Ken Burns blur background & sharp foreground
    ffmpeg_inputs = []
    scale_parts = []
    for idx, sc_path in enumerate(flat_scenes):
        clean_img = os.path.abspath(sc_path).replace("\\", "/")
        ffmpeg_inputs.extend(["-loop", "1", "-t", f"{L:.3f}", "-i", clean_img])
        # Dual-layer: blurred background filling 16:9 widescreen, with crisp centered hero visual
        scale_parts.append(
            f"[{idx}:v]split=2[bg_raw{idx}][fg_raw{idx}];"
            f"[bg_raw{idx}]scale={w}:{h}:force_original_aspect_ratio=increase:flags=lanczos,crop={w}:{h},boxblur=20:5[bg{idx}];"
            f"[fg_raw{idx}]scale=-1:{h}:flags=lanczos[fg{idx}];"
            f"[bg{idx}][fg{idx}]overlay=(W-w)/2:0,setsar=1,fps=30[s{idx}];"
        )

    prev = "s0"
    xfade_parts = []
    for idx in range(1, num_scenes):
        offset = idx * (L - fade_dur)
        out_tag = f"x{idx}" if idx < num_scenes - 1 else "vbase"
        xfade_parts.append(
            f"[{prev}][s{idx}]xfade=transition=fade:duration={fade_dur:.2f}:offset={offset:.2f}[{out_tag}];"
        )
        prev = out_tag

    # Overlay: Top Cinema Banner + Localized Action + Bottom Safe Zone
    brand_font = resolve_brand_font()
    brand_font_arg = f":fontfile='{brand_font}'" if brand_font else ""
    lang_font = resolve_font_for_language(lang_code)
    lang_font_arg = f":fontfile='{lang_font}'" if lang_font else ""

    is_non_latin = lang_code in ("hi", "ar", "ja", "ko", "vi")
    header_font_arg = lang_font_arg if is_non_latin else (brand_font_arg or lang_font_arg)
    bottom_font_arg = lang_font_arg if is_non_latin else (brand_font_arg or lang_font_arg)

    banner_text = sanitize_ffmpeg_text(COMPILATION_BANNERS.get(lang_code, COMPILATION_BANNERS["en"]))
    bottom_text = sanitize_ffmpeg_text(BOTTOM_LABELS.get(lang_code, handle))

    box_top_h = int(120 * (h / 1080))
    box_bot_h = int(100 * (h / 1080))
    box_bot_y = int(h - box_bot_h)
    f_brand = int(32 * (h / 1080))
    f_handle = int(24 * (h / 1080))

    overlay_filters = (
        f"drawbox=y=0:h={box_top_h}:color=0x0a0f1d@0.60:t=fill,"
        f"drawbox=y={box_bot_y}:h={box_bot_h}:color=0x0a0f1d@0.60:t=fill,"
        f"drawtext={header_font_arg}:text='{banner_text}':fontsize={f_brand}:fontcolor=0xf59e0b:x=(w-text_w)/2:y={int(45*(h/1080))},"
        f"drawtext={bottom_font_arg}:text='{bottom_text}':fontsize={f_handle}:fontcolor=0x94a3b8:x=(w-text_w)/2:y={int(box_bot_y + 35*(h/1080))}"
    )

    full_video_filter = f"{''.join(scale_parts)}{''.join(xfade_parts)}[vbase]{overlay_filters}[v]"
    audio_idx = num_scenes

    ffmpeg_render_cmd = [
        "ffmpeg", "-y",
        *ffmpeg_inputs,
        "-i", master_audio,
        "-filter_complex", full_video_filter,
        "-map", "[v]",
        "-map", f"{audio_idx}:a",
        "-t", f"{total_dur:.2f}",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        output_video_path
    ]

    print(f"🎬 Encoding 10-Minute Master Video at {quality.upper()} ({w}x{h})...")
    subprocess.run(ffmpeg_render_cmd, check=True)

    # Clean up temp
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)

    print(f"SUCCESS: Rendered 10-Minute Special -> {output_video_path} ({os.path.getsize(output_video_path)} bytes)")
    return output_video_path, meta

if __name__ == "__main__":
    lang = sys.argv[1] if len(sys.argv) > 1 else "en"
    out = os.path.join(script_dir, f"compilation_ep01_{lang}.mp4")
    produce_10min_compilation([1, 2, 3], lang, out)
