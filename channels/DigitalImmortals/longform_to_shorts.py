"""
/yt-shorts for Digital Immortals: the Shorts already inside a long Ramayana episode.

Reads the episode's timed SRT (one cue per scene, written by video_producer.py), asks Claude for the
3 strongest self-contained moments (20-58 s), writes 3 opening lines per clip and keeps the one the
hookscore (+Hindi layer) ranks highest, then cuts each moment into a 1080x1920 Short: blurred
background, the 16:9 picture centred, the new first line on screen, "full episode" footer and the
@DigitalImmortals watermark. Uploads PRIVATE (review, then publish) with a link to the full episode.

    python channels/DigitalImmortals/longform_to_shorts.py 7              # episode 7, upload private
    python channels/DigitalImmortals/longform_to_shorts.py 7 --no-upload  # render only

Done clips are tracked in longform_shorts.json so an episode is never cut twice.
"""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, ROOT)
OUT = os.path.join(HERE, "output")
DONE = os.path.join(HERE, "longform_shorts.json")
FONTS = os.path.join(HERE, "shorts", "assets", "fonts")
W, H = 1080, 1920


def parse_srt(path):
    txt = open(path, encoding="utf-8").read().replace("\r\n", "\n")
    cues = []
    for block in re.split(r"\n\s*\n", txt.strip()):
        lines = block.strip().split("\n")
        if len(lines) < 3:
            continue
        m = re.match(r"(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)", lines[1])
        if not m:
            continue
        g = [int(x) for x in m.groups()]
        start = g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000
        end = g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000
        cues.append({"id": int(lines[0]) if lines[0].strip().isdigit() else len(cues) + 1,
                     "start": start, "end": end, "text": " ".join(lines[2:])})
    return cues


def candidate_windows(cues, lo=20, hi=58):
    """Consecutive scene windows that fit a Short."""
    out = []
    for i in range(len(cues)):
        for j in range(i, min(i + 3, len(cues))):
            d = cues[j]["end"] - cues[i]["start"]
            if lo <= d <= hi:
                out.append((i, j, round(d, 1)))
    return out


def pick_moments(cues, ep_title, n=3):
    wins = candidate_windows(cues)
    if not wins:
        return []
    if os.environ.get("ANTHROPIC_API_KEY"):
        try:
            import anthropic
            menu = [{"w": k, "scenes": f"{cues[i]['id']}-{cues[j]['id']}", "sec": d,
                     "text": " ".join(c["text"] for c in cues[i:j + 1])[:600]} for k, (i, j, d) in enumerate(wins)]
            prompt = f"""Episode: {ep_title} (Hindi Valmiki Ramayana series, channel Digital Immortals).
Pick the {n} windows that work best as standalone YouTube Shorts: a complete mini-story or revelation, strong emotion,
understandable without the rest of the episode. Avoid overlapping windows.
For each, write 3 different opening lines in Hindi (Devanagari, 6-12 words, on-screen hook; no invented facts)
and a Shorts title (Hindi, <=60 chars, curiosity, no "का सच").
Windows: {json.dumps(menu, ensure_ascii=False)}
Return ONLY JSON: {{"picks": [{{"w": 0, "hooks": ["...", "...", "..."], "title": "..."}}]}}"""
            msg = anthropic.Anthropic().messages.create(
                model=os.environ.get("CLAUDE_MODEL", "claude-sonnet-5-5"), max_tokens=1500,
                messages=[{"role": "user", "content": prompt}])
            text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
            picks = json.loads(re.search(r"\{.*\}", text, re.S).group(0))["picks"]
            from channels.common.skills import rank_hooks
            out, used = [], set()
            for p in picks:
                i, j, d = wins[int(p["w"])]
                if used & set(range(i, j + 1)):
                    continue
                used |= set(range(i, j + 1))
                best = rank_hooks(p.get("hooks") or [cues[i]["text"][:60]])[0]
                out.append({"i": i, "j": j, "sec": d, "hook": best["hook"], "hook_score": best["verdict"],
                            "title": p.get("title") or best["hook"]})
            if out:
                return out[:n]
        except Exception as e:
            print(f"[shorts] Claude pick notice: {e}")
    # fallback: evenly spaced single-scene windows
    singles = [w for w in wins if w[0] == w[1]]
    step = max(1, len(singles) // n)
    return [{"i": w[0], "j": w[1], "sec": w[2], "hook": cues[w[0]]["text"][:60], "hook_score": None,
             "title": cues[w[0]]["text"][:55]} for w in singles[::step][:n]]


def _ass(path, hook, dur):
    esc = lambda s: s.replace("{", "(").replace("}", ")").replace("\\", "")
    body = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Hook,Baloo 2 ExtraBold,84,&H0028D7FF,&H0028D7FF,&H00101010,&H90000000,-1,0,0,0,100,100,0,0,1,8,4,8,70,70,260,1
Style: Foot,Baloo 2 ExtraBold,58,&H00FFFFFF,&H00FFFFFF,&H00101010,&H90000000,-1,0,0,0,100,100,0,0,1,6,3,2,60,60,300,1
Style: WM,Baloo 2 Bold,42,&H70FFFFFF,&H70FFFFFF,&H90000000,&H00000000,-1,0,0,0,100,100,0,0,1,2,0,9,0,50,120,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 1,0:00:00.00,0:00:03.50,Hook,,0,0,0,,{{\\fad(100,250)}}{esc(hook)}
Dialogue: 1,0:00:{max(dur - 4, 0):05.2f},0:00:{dur:05.2f},Foot,,0,0,0,,{{\\fad(200,0)}}पूरा एपिसोड चैनल पर देखें 🔱
Dialogue: 0,0:00:00.00,0:00:{dur:05.2f},WM,,0,0,0,,@DigitalImmortals
"""
    open(path, "w", encoding="utf-8").write(body)


def _ffp(p):
    return "'" + str(p).replace("\\", "/").replace(":", "\\:").replace("'", "\\'") + "'"


def cut_short(video, start, end, hook, out):
    dur = round(end - start, 2)
    ass = out.replace(".mp4", ".ass")
    _ass(ass, hook, dur)
    vf = (f"[0:v]split[a][b];[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=30:2,"
          f"eq=brightness=-0.18[bg];[b]scale={W}:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2-80,"
          f"ass={_ffp(ass)}:fontsdir={_ffp(FONTS)}[v]")
    tmp = out.replace(".mp4", ".part.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{start:.2f}", "-t", f"{dur:.2f}", "-i", video,
                    "-filter_complex", vf, "-map", "[v]", "-map", "0:a?", "-c:v", "libx264", "-preset", "veryfast",
                    "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
                    "-af", "afade=t=out:st=" + f"{max(dur - 0.6, 0):.2f}" + ":d=0.6", "-movflags", "+faststart", tmp],
                   check=True)
    os.replace(tmp, out)
    os.remove(ass)
    return out


def _episode_link(ep):
    try:
        st = json.load(open(os.path.join(HERE, "state.json"), encoding="utf-8"))
        for h in st.get("history", []):
            if h.get("episode_number") == ep and h.get("video_id"):
                return f"https://youtu.be/{h['video_id']}", h.get("title", "")
    except Exception:
        pass
    return "", ""


def upload(path, title, hook, ep, link):
    import scheduler   # same folder: reuses the long-form token refresh
    from googleapiclient.http import MediaFileUpload
    yt = scheduler.get_youtube_client()
    desc = (f"{hook}\n\nरामायण एपिसोड {ep:02d} का एक हिस्सा।"
            + (f"\n▶️ पूरा एपिसोड देखें: {link}" if link else "")
            + "\n\n🔔 Subscribe करें — @DigitalImmortals\n\n#Shorts #Ramayana #DigitalImmortals #ValmikiRamayan")
    body = {"snippet": {"title": (title[:88] + " #Shorts"), "description": desc,
                        "tags": ["valmiki ramayan", "ramayan shorts", "रामायण", "digital immortals"],
                        "categoryId": "27", "defaultLanguage": "hi", "defaultAudioLanguage": "hi"},
            "status": {"privacyStatus": "private", "selfDeclaredMadeForKids": False}}
    try:
        from channels.common import yt_brain
        body = yt_brain.before_insert("DigitalImmortals", yt, body, is_short=True)
    except Exception:
        yt_brain = None
    r = yt.videos().insert(part="snippet,status", body=body,
                           media_body=MediaFileUpload(path, mimetype="video/mp4", resumable=True)).execute()
    if yt_brain:
        yt_brain.after_insert("DigitalImmortals", yt, r["id"])
    return r["id"]


def run(ep, do_upload=True):
    srt = os.path.join(OUT, f"DigitalImmortals_Ep{ep:02d}.srt")
    vids = [f for f in os.listdir(OUT) if f.startswith(f"DigitalImmortals_Ep{ep:02d}_") and f.endswith(".mp4")] if os.path.isdir(OUT) else []
    if not (os.path.exists(srt) and vids):
        print(f"[shorts] Ep {ep:02d}: need {srt} and the rendered episode mp4 in output/")
        return []
    done = json.load(open(DONE, encoding="utf-8")) if os.path.exists(DONE) else {}
    if str(ep) in done:
        print(f"[shorts] Ep {ep:02d} already cut: {done[str(ep)]}")
        return done[str(ep)]
    video = os.path.join(OUT, sorted(vids)[0])
    cues = parse_srt(srt)
    link, ep_title = _episode_link(ep)
    results = []
    for k, m in enumerate(pick_moments(cues, ep_title or f"Episode {ep}")):
        s, e = cues[m["i"]]["start"], cues[m["j"]]["end"]
        out = os.path.join(OUT, f"DI_Ep{ep:02d}_short{k + 1}.mp4")
        cut_short(video, s, e, m["hook"], out)
        print(f"[shorts] {out}  ({m['sec']}s, hook score {m['hook_score']}): {m['hook']}")
        vid = upload(out, m["title"], m["hook"], ep, link) if do_upload else None
        results.append({"file": os.path.basename(out), "start": s, "end": e, "hook": m["hook"], "video_id": vid})
    if results and do_upload:
        done[str(ep)] = results
        json.dump(done, open(DONE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return results


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        sys.exit(1)
    run(int(args[0]), do_upload="--no-upload" not in sys.argv)
