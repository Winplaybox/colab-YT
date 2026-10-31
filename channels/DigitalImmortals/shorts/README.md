# Digital Immortals — Daily Short

Roz ek naya mythology Short: Claude script → Hindi voice (Edge TTS) → Gemini flat-style scenes → narrator "Amar" (lip-flap) → word-by-word captions → mood music (ducking) → `@DigitalImmortals` watermark (har 5 sec corner badalta hai). 1080×1920, 30fps, 40–50 sec. Upload **private** hota hai, aap review karke Public karte ho.

## Local (Windows)
1. `.env.example` ko `.env` naam se copy karo, `ANTHROPIC_API_KEY` aur `GEMINI_API_KEY` bharo.
2. `local_run\digitalimmortals_shorts_run_once.bat` chalao.
   - Sirf render, upload nahi: `digitalimmortals_shorts_run_once.bat --no-upload`
   - YouTube login ke liye `channels\DigitalImmortals\token.json` (long-form wala) apne aap use hota hai.
3. Video `out\<date>\` mein milega.

## GitHub Actions (roz ~04:47 IST)
Workflow: `.github/workflows/digital_immortals_shorts.yml`. Secrets:
- `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`
- `DIGITALIMMORTALS_TOKEN_JSON` = `channels/DigitalImmortals/token.json` ka poora content

## Music
`music/<mood>/` (mystery, epic, devotional, calm) mein YouTube Audio Library ke "attribution not required" tracks daalo. Ye mp3 git mein jaa sakte hain (`.gitignore` mein exception hai) taaki CI ko bhi milein.

## Test bina keys/internet
`python -m tests.offline_preview` — placeholder art + nakli awaaz se poora render.

## Settings
`pipeline/config.py`: voice, speed, art style, privacy. Formats aur script rules: `pipeline/script_gen.py`.
