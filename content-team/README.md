# WinPlayBox Content Team — Hermes Agent skill pack

Ek Hermes Agent = poori faceless content team. Idea andar → YouTube pe scheduled video bahar.
Design rule: **code manager hai, LLM sirf writer hai.** Isliye tokens kam, result consistent.

## Flow (har episode)

```
ideas.json ─► brief.json ─► script.txt ─► script.ok ─► voice.mp3 + voice_segments.json
 (LLM sasta,    (code)       (LLM BEST,     (code        (IndicF5, 0 tokens)
  20 ek saath)               alag call)     validator)            │
                                                                   ▼
published.json ◄── meta.json ◄── video.mp4 ◄── subs.srt
 (code, YT API,   (LLM sasta)   (ffmpeg,      (TTS timing se,
  private+schedule)              0 tokens)      0 tokens)
```

Agent kabhi khud plan nahi karta — `bin/ct_state.py next` har baar ek JSON deta hai: agla step kya hai.
Script fail ho toh validator line-wise batata hai, writer **sirf wahi lines** theek karta hai (max 2 baar, phir aapko ping).

| Kaam | Kaun | Tokens |
|---|---|---|
| Ideas (jab 5 se kam bachein) | `ct-idea-bank` skill, sasta model | Kam, batch |
| Script likhna/fix | `ct-script-writer` skill, **best model, alag stateless call** | Yahin kharch |
| Script check | `bin/validate_script.py` | 0 |
| Voice | `bin/indicf5_voice.py` (IndicF5) | 0 |
| Subtitles | `bin/make_subs.py` | 0 |
| Video | `bin/assemble_video.py` (ffmpeg) | 0 |
| Title/desc/tags | `ct-metadata` skill, sasta model | Kam |
| Upload | `bin/publish_youtube.py` | 0 |
| Manager | `ct-pipeline` skill, sasta model | Bahut kam (sirf JSON padhta hai) |

## ⚠️ Zaroori: script Devanagari mein
IndicF5 Devanagari text padhta hai. Roman Hinglish ("raat ke do baje") dene pe uchcharan bigadta hai.
Isliye writer poori voiceover script Devanagari mein likhta hai — English shabd bhi (हाईवे, मोबाइल), ank shabdon mein.
Validator Roman letters / digits pakad leta hai. Title/description Roman Hinglish mein hi rehte hain (search ke liye).

## Setup (ek baar)

```bash
# 1. Hermes
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
hermes setup

# 2. Ye repo
git clone https://github.com/Winplaybox/content-team ~/content-team   # ya jahan rakho
echo 'export CT_HOME=~/content-team' >> ~/.bashrc && source ~/.bashrc
pip install pyyaml soundfile numpy google-api-python-client google-auth-oauthlib
sudo apt install -y ffmpeg fonts-noto-core     # fonts-noto-core = Devanagari subtitles

# 3. Skills Hermes ko do
cp -r $CT_HOME/skills/* ~/.hermes/skills/
#    (ya repo push karke: hermes skills tap add Winplaybox/content-team)

# 4. Do profiles — token bachane ka main trick
hermes profile create ct-ops      # SASTA model: manager, ideas, metadata
hermes profile create ct-writer   # BEST model: sirf script
#    dono ka model set karo: hermes setup -p ct-ops / hermes setup -p ct-writer
```

`config.yaml` ka `writer_cmd` ct-writer profile ko alag call karta hai. Aapke Hermes version ke flags alag hon toh sirf wahi line badlo.
Test: `hermes chat -p ct-writer -s ct-script-writer -q "hello"` chal jaye toh theek hai.

### Voice (GPU)
- **GPU wali machine:** `config.yaml` → `voice_mode: local`. IndicF5 ke liye: `pip install git+https://github.com/AI4Bharat/IndicF5.git`, huggingface.co/ai4bharat/IndicF5 pe terms accept karo, `export HF_TOKEN=hf_...`
- **GPU nahi:** `voice_mode: external`. Pipeline script ke baad ruk ke batayegi; Colab pe `indicf5_voice.py --out voice` chalao, `voice.mp3` + `voice_segments.json` episode folder mein daalo, pipeline dobara chalao.

### YouTube
1. Google Cloud → project → **YouTube Data API v3** enable → OAuth client (Desktop app) → JSON download → `credentials/client_secret.json`
2. Har channel ke liye ek baar login: `python3 $CT_HOME/bin/publish_youtube.py --channel indian-horror-tapes --auth`
3. Pehle `--dry-run` se check karo.

Quota: ek upload ~1600 units, free 10,000/day → ~6 uploads/day per Google project.

## Channel assets
`channels/indian-horror-tapes/`
- `ref.wav` — 5-10 sec saaf clip, **apni ya permission wali awaaz**, emotion wahi jo chahiye
- `ref.txt` — us clip mein exactly kya bola (Devanagari)
- `bg/` — background clips/images (har episode ko alag milta hai)
- `music.mp3` — optional

Naya channel: `channels/indian-horror-tapes.yaml` copy karo, naam + style + themes + hashtags badlo, assets folder banao. Bas.

## Chalana

```bash
# Ek episode, manually
hermes chat -p ct-ops -s ct-pipeline -q "indian-horror-tapes ka next episode banao"

# Roz subah 9 baje auto (video shaam 7:30 pe publish hoti hai — beech mein dekh lo)
hermes -p ct-ops cron create '0 9 * * *' "ct-pipeline skill: indian-horror-tapes ka ek episode banao"

# Haal
python3 $CT_HOME/bin/ct_state.py status --channel indian-horror-tapes
# Ek episode chhodna ho
python3 $CT_HOME/bin/ct_state.py abandon --channel indian-horror-tapes
```

Upload hamesha **private + scheduled** (`publish.mode: schedule`). Phone pe YouTube Studio mein dekh lo; galat ho toh schedule hata do. Bilkul manual chahiye toh `mode: private_only`.

## Token rules (skills mein bhi hain)
1. Manager sirf `ct_state.py next` ka JSON padhta hai — script, audio, video kabhi nahi.
2. Script = best model, **alag stateless call** (manager ki history usmein nahi jaati).
3. Check code karta hai. LLM sirf flagged lines dobara likhta hai.
4. Ideas 20 ek saath; metadata chhota JSON. Dono sasta model.
5. Code step fail → manager ruk ke aapko error bhejta hai, khud debug karke tokens nahi jalata.

## Files
```
config.yaml                 voice_mode, writer_cmd, retries
channels/<ch>.yaml          channel ka style, length, voice, video, publish
bin/ct_state.py             state machine (next / ideas-add / status / abandon)
bin/validate_script.py      script checker
bin/indicf5_voice.py        IndicF5 TTS (cache ke saath)
bin/make_subs.py            SRT from TTS timing
bin/assemble_video.py       ffmpeg render
bin/publish_youtube.py      upload + schedule
skills/ct-*/SKILL.md        4 Hermes skills
data/<ch>/                  ideas.json, schedule.json   (auto)
episodes/<ch>/<id>/         har episode ki files        (auto)
```
