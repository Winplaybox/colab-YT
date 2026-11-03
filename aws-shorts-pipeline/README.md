# AWS Shorts Autopilot Pipeline (EpicBharatSaga & YouTube Shorts)

Dual-engine automated YouTube Shorts generator combining Amazon Web Services (Bedrock & Polly) with an automatic free fallback.

---

## Architecture & Features

```
[AWS Mode (Active Credits)]
├── Script Generation: AWS Bedrock (Model: amazon.nova-micro-v1:0)
└── Voiceover: AWS Polly Generative Engine (Voice: Arjun / Kajal)

[Free Mode (Zero-Cost / Fallback)]
├── Script Generation: Local Story Bank
└── Voiceover: Microsoft Edge-TTS (Voice: hi-IN-MadhurNeural)
```

---

## How to Run

### 1. Default Run (Bedrock AI + Polly Generative Voice):
```bash
python autopilot.py --topic "Kailash Parvat Ka Rahasya" --deity "Lord Shiva"
```

### 2. Force Free Mode (Zero-Cost Local Mode):
```bash
python autopilot.py --free --topic "Kailash Parvat Ka Rahasya"
```

### 3. Generate Script & Voice Only (Skip video render):
```bash
python autopilot.py --no-render --topic "Mahadev Ka Trishul Rahasya"
```

---

## Integration with EpicBharatSaga
* Generated stories are automatically structured and saved into `channels/EpicBharatSaga/stories/*.json`.
* Voiceover audio files are saved into `channels/EpicBharatSaga/stories/assets/<story_id>/voiceover.mp3`.
* Direct compatibility with `EpicBharatSaga/video_producer.py` for 9:16 vertical 1080p rendering and automated YouTube scheduling.
