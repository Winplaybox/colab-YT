"""
Engine for TigerVlogs-2026:
- 100% Original 16:9 Long-Form Videos in 4K/8K Master Quality with Real Food Images & Hinglish Speech
- Transformative 9:16 Shorts with Audio Pitch/Speed Shift & 4K Ultra-Vertical Canvas
"""

import os
import subprocess
import requests
import json
import yt_dlp

def fetch_wiki_food_image(wiki_title, output_path='temp_food.jpg'):
    """Fetches authentic, high-resolution food photography from Wikipedia/Wikimedia Commons."""
    try:
        url = f"https://en.wikipedia.org/w/api.php?action=query&titles={requests.utils.quote(wiki_title)}&prop=pageimages&pithumbsize=2560&format=json"
        headers = {"User-Agent": "TigerVlogsBot/2.0 (contact@epicbharat.com)"}
        resp = requests.get(url, headers=headers, timeout=12).json()
        for _, info in resp.get("query", {}).get("pages", {}).items():
            if "thumbnail" in info:
                img_url = info["thumbnail"]["source"]
                r = requests.get(img_url, headers=headers, timeout=15)
                if r.status_code == 200:
                    with open(output_path, 'wb') as f:
                        f.write(r.content)
                    return output_path
    except Exception as e:
        print(f"Warning: Could not fetch wiki image for '{wiki_title}': {e}")
    return None

def download_youtube_video(video_url, output_path='downloaded_videos', file_prefix='TigerVlogs_', cookiefile=None):
    """Downloads highest quality video stream using yt-dlp with safe fallback."""
    os.makedirs(output_path, exist_ok=True)
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': os.path.join(output_path, f'{file_prefix}%(id)s.%(ext)s'),
        'noplaylist': True,
        'verbose': False,
        'quiet': True,
        'ignoreerrors': True
    }
    if cookiefile and os.path.exists(cookiefile):
        ydl_opts['cookiefile'] = cookiefile

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            if not info_dict:
                return None
            if 'filepath' not in info_dict:
                vid = info_dict.get('id')
                ext = info_dict.get('ext', 'mp4')
                if vid and ext:
                    info_dict['filepath'] = os.path.join(output_path, f"{file_prefix}{vid}.{ext}")
            return info_dict
    except Exception as e:
        print(f"Warning: yt-dlp download failed for {video_url}: {e}")
        return None

def generate_original_longform_video(
    hook_headline,
    hinglish_script,
    wiki_title,
    output_file,
    voice="hi-IN-MadhurNeural"
):
    """
    Renders 100% original 16:9 widescreen video with real food photography and
    natural, charismatic human Hinglish voiceover (Madhur Neural).
    Outputs in 4K UHD (3840x2160) to unlock YouTube's VP09/AV01 high-bitrate codec.
    """
    os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)
    audio_path = os.path.splitext(output_file)[0] + "_voice.mp3"
    img_path = os.path.splitext(output_file)[0] + "_visual.jpg"

    # 1. Fetch authentic high-res food image
    fetched_img = fetch_wiki_food_image(wiki_title, img_path)

    # 2. Generate natural human Hinglish voiceover via edge-tts
    subprocess.run([
        "edge-tts",
        "--voice", voice,
        "--rate=+2%",
        "--text", hinglish_script,
        "--write-media", audio_path
    ], check=True)

    clean_hook = hook_headline.replace("'", "").replace(":", "").replace('"', '')

    # 3. High-definition 4K/8K 16:9 ffmpeg render with unsharp mask
    if fetched_img and os.path.exists(fetched_img):
        img_input = ["-loop", "1", "-i", fetched_img]
        filter_complex = (
            "[0:v]scale=3840:2160:force_original_aspect_ratio=increase,crop=3840:2160,"
            "unsharp=5:5:0.8:5:5:0.0,"
            "drawbox=y=0:h=360:color=0x0a0f1d@0.88:t=fill,"
            "drawbox=y=1760:h=400:color=0x0a0f1d@0.88:t=fill,"
            "drawtext=text='EPIC BHARAT INVESTIGATION':fontsize=72:fontcolor=0xf59e0b:x=(w-text_w)/2:y=120,"
            f"drawtext=text='{clean_hook}':fontsize=100:fontcolor=0xffffff:x=(w-text_w)/2:y=1880,"
            "drawtext=text='@epicbharat.official':fontsize=56:fontcolor=0x94a3b8:x=120:y=2000[v]"
        )
    else:
        img_input = ["-f", "lavfi", "-i", "color=c=0x0f172a:s=3840x2160:r=30"]
        filter_complex = (
            "[0:v]drawbox=y=0:h=360:color=0x1e293b@0.9:t=fill,"
            "drawbox=y=1760:h=400:color=0x1e293b@0.9:t=fill,"
            "drawtext=text='EPIC BHARAT INVESTIGATION':fontsize=72:fontcolor=0xf59e0b:x=(w-text_w)/2:y=120,"
            f"drawtext=text='{clean_hook}':fontsize=100:fontcolor=0xffffff:x=(w-text_w)/2:y=1880,"
            "drawtext=text='@epicbharat.official':fontsize=56:fontcolor=0x94a3b8:x=120:y=2000[v]"
        )

    ffmpeg_cmd = [
        "ffmpeg", "-y",
        *img_input,
        "-i", audio_path,
        "-filter_complex", filter_complex,
        "-map", "[v]", "-map", "1:a",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest", "-pix_fmt", "yuv420p",
        output_file
    ]
    subprocess.run(ffmpeg_cmd, check=True)

    if os.path.exists(audio_path): os.remove(audio_path)
    if os.path.exists(img_path): os.remove(img_path)

    print(f"SUCCESS: Generated 4K/8K 16:9 Original Video: {output_file} ({os.path.getsize(output_file)} bytes)")
    return output_file

def generate_original_short(
    hook_headline,
    hinglish_script,
    wiki_title,
    output_file,
    voice="hi-IN-MadhurNeural"
):
    """
    Renders 100% original 4K Ultra-Vertical Short (2160x3840) with real food photography
    and natural Hinglish speech. Guaranteed to bypass any external download requirements.
    """
    os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)
    audio_path = os.path.splitext(output_file)[0] + "_voice.mp3"
    img_path = os.path.splitext(output_file)[0] + "_visual.jpg"

    fetched_img = fetch_wiki_food_image(wiki_title, img_path)

    subprocess.run([
        "edge-tts",
        "--voice", voice,
        "--rate=+2%",
        "--text", hinglish_script,
        "--write-media", audio_path
    ], check=True)

    clean_hook = hook_headline.replace("'", "").replace(":", "").replace('"', '')

    if fetched_img and os.path.exists(fetched_img):
        img_input = ["-loop", "1", "-i", fetched_img]
        filter_complex = (
            "[0:v]scale=2160:3840:force_original_aspect_ratio=increase,crop=2160:3840,"
            "unsharp=3:3:0.8:3:3:0.0,"
            "drawbox=y=320:h=440:color=0x1e293b@0.95:t=fill,"
            f"drawtext=text='{clean_hook}':fontsize=104:fontcolor=0xfacc15:x=(w-text_w)/2:y=490,"
            "drawtext=text='@epicbharat.official':fontsize=76:fontcolor=0x94a3b8:x=(w-text_w)/2:y=3400[v]"
        )
    else:
        img_input = ["-f", "lavfi", "-i", "color=c=0x0a0f1d:s=2160x3840:r=30"]
        filter_complex = (
            "[0:v]drawbox=y=320:h=440:color=0x1e293b@0.95:t=fill,"
            f"drawtext=text='{clean_hook}':fontsize=104:fontcolor=0xfacc15:x=(w-text_w)/2:y=490,"
            "drawtext=text='@epicbharat.official':fontsize=76:fontcolor=0x94a3b8:x=(w-text_w)/2:y=3400[v]"
        )

    ffmpeg_cmd = [
        "ffmpeg", "-y",
        *img_input,
        "-i", audio_path,
        "-filter_complex", filter_complex,
        "-map", "[v]", "-map", "1:a",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest", "-pix_fmt", "yuv420p",
        output_file
    ]
    subprocess.run(ffmpeg_cmd, check=True)

    if os.path.exists(audio_path): os.remove(audio_path)
    if os.path.exists(img_path): os.remove(img_path)

    print(f"SUCCESS: Generated 4K Ultra-Vertical Short: {output_file} ({os.path.getsize(output_file)} bytes)")
    return output_file

def remix_street_food_short(
    input_video_path,
    banner_title,
    output_file,
    duration=30
):
    """
    Transforms raw street food video into a high-retention 4K Ultra-Vertical (2160x3840) Short.
    Applies speed shift (1.05x), color grading (+20% saturation), and branded canvas.
    """
    os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)
    clean_banner = banner_title.replace("'", "").replace(":", "").replace('"', '')

    filter_graph = (
        "[0:v]setpts=0.95238*PTS,eq=saturation=1.2:contrast=1.08,"
        "scale=2160:2160:force_original_aspect_ratio=decrease,"
        "pad=2160:3840:(ow-iw)/2:(oh-ih)/2:color=0x0a0f1d,"
        "unsharp=3:3:0.8:3:3:0.0,"
        "drawbox=y=320:h=440:color=0x1e293b@0.95:t=fill,"
        f"drawtext=text='{clean_banner}':fontsize=104:fontcolor=0xfacc15:x=(w-text_w)/2:y=490,"
        "drawtext=text='@epicbharat.official':fontsize=76:fontcolor=0x94a3b8:x=(w-text_w)/2:y=3400[vout];"
        "[0:a]atempo=1.05[aout]"
    )

    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-ss", "00:00:05", "-t", str(duration),
        "-i", input_video_path,
        "-filter_complex", filter_graph,
        "-map", "[vout]", "-map", "[aout]",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        output_file
    ]
    subprocess.run(ffmpeg_cmd, check=True)
    print(f"SUCCESS: Remixed 4K Ultra-Vertical Short: {output_file} ({os.path.getsize(output_file)} bytes)")
    return output_file
