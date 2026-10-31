"""Daily run: script -> voice -> images -> render -> upload -> log.

python -m pipeline.main                 # full run (needs API keys)
python -m pipeline.main --script x.json # use a ready script instead of Claude
python -m pipeline.main --no-upload     # render only
"""
import argparse
import datetime as dt
import json
import shutil

from . import config, images, render, script_gen, tts

HISTORY = config.DATA_DIR / "history.json"


def load_history() -> list:
    return json.loads(HISTORY.read_text(encoding="utf-8")) if HISTORY.exists() else []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", help="path to a ready script JSON")
    ap.add_argument("--no-upload", action="store_true")
    args = ap.parse_args()

    today = dt.date.today()
    stamp = today.isoformat()
    work = config.OUT_DIR / stamp
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    history = load_history()

    # 1. script
    if args.script:
        meta = script_gen.validate(json.loads(open(args.script, encoding="utf-8").read()))
    else:
        meta = script_gen.generate(history, today)
    (work / "script.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[script] {meta['title']}  ({len(meta['scenes'])} scenes, mood={meta['mood']})")

    # 2. voice + timings
    vo = tts.build_narration(meta["scenes"], work)
    print(f"[voice] {vo['duration']:.1f}s, {len(vo['words'])} words")

    # 3. images
    imgs, credits = images.make_scene_images(meta["scenes"], work)
    meta["credits"] = credits

    # 4. render
    seed = f"{stamp}-{meta['topic']}"
    music = render.pick_music(meta["mood"], seed)
    print(f"[music] {music.name if music else 'none (add mp3s to music/<mood>/)'}")
    video = work / f"digital_immortals_{stamp}.mp4"
    render.render_video(imgs, vo["scenes"], vo["words"], vo["wav"], music,
                        vo["duration"], meta.get("hook_text", ""), video, work, seed)
    print(f"[render] {video}")

    # 5. upload
    video_id = None
    if config.UPLOAD and not args.no_upload:
        from . import upload
        video_id = upload.upload(video, meta)
        print(f"[upload] https://youtube.com/shorts/{video_id}  (privacy={config.PRIVACY})")

    history.append({"date": stamp, "topic": meta["topic"], "title": meta["title"],
                    "format": meta.get("format"), "video_id": video_id})
    HISTORY.parent.mkdir(parents=True, exist_ok=True)
    HISTORY.write_text(json.dumps(history, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
