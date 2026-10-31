# Oct 2026 fixes — kya badla aur aapko kya karna hai

## Kya badla
| Problem | Fix |
|---|---|
| HF ne 15 Oct 2026 se free inference credits band kiye → sab image calls 402 | Naya `channels/common/ai_images.py` (Gemini → OpenAI). Horror, EpicBharat, Train, MindNest pehle isse try karte hain; purana chain fallback rahta hai. |
| `git push \|\| echo` → state chupchaap lost → episodes repeat/duplicate | Har workflow: `concurrency` group, 5 baar rebase+push retry, fail hone pe run red. |
| Fail run bhi state commit karta tha (`if: always()`) | Commit sirf `if: success()`. |
| MindNest ke 11 parallel jobs ek hi `state.json` edit karte the | `max-parallel: 1` (ek ke baad ek). |
| 4K default → timeouts + Actions minutes khatam | Default 1080p (input se 4k abhi bhi chun sakte ho). |
| TigerVlogs: kisi aur ka YouTube video re-upload + 4 scripts ka loop | Re-upload hataya. Roz 2 original videos, Claude se naya topic, `used_topics.json` se repeat block. |
| DI playlist IDs adhure (13 chars) | Chhote IDs ignore hoke playlist title se dobara resolve hote hain; description mein sirf valid link. |
| Duplicate checker: "ep 1" = "ep 12" | Word-boundary match. |
| DI ka koi daily Shorts pipeline nahi | `channels/DigitalImmortals/shorts/` + workflow + `local_run/digitalimmortals_shorts_run_once.bat`. |

## Update 2: sab channels ke liye "YT brain" + analytics
| Kya | Kaise |
|---|---|
| **Weekly audit** | `channel_insights.yml` har Monday ~09:10 IST: har channel ke recent public videos, channel ke median se kitna guna (yt-analyze/yt-audit method), top vs bottom titles, Claude se patterns → `channels/<channel>/insights.json` |
| **Har upload se pehle** | `channels/common/yt_brain.py`: insights + packaging rules se title (≤60 chars), description (hook + comment question + keywords), 10-15 tags, aur playlist (na ho toh bana deta hai). Episode marker ("Ep 07") aur credits/links kabhi nahi hat-te. API fail = original metadata. Band karna: `YT_BRAIN=off` |
| **DI Shorts script** | Script writer `insights.json` padh ke wahi likhta hai jo audience dekhti hai |
| **Images** | Horror, EpicBharat, Train, Tiger, DI: museum/Wikimedia pehle, phir Gemini. MindNest: 2D flat explainer style. Credits description mein apne aap |
| **TigerVlogs** | 1080p (pehle 4K), Wikipedia photo na mile toh Gemini, text overlays 1080p ke hisaab se |

## Update 3: saari yt-* skills pipeline mein
Skills ke asli tools (hookscore, title lint, swipe, retention + 21 hook formulas) `channels/common/ytskills/` mein vendored hain (MIT), aur `channels/common/skills.py` unpe **Hindi/Hinglish layer** jodta hai (original tools Devanagari ko khaali text samajhte the).

| Skill | Kahan chalta hai |
|---|---|
| /yt-audit | Weekly: median multiples, last 10 titles lint + formula, upload rhythm, ONE fix + "abhi mat karo" |
| /yt-retention | Weekly: YouTube Analytics se avg % viewed + best/worst videos ka hook leak, cliffs, slide (scope ho toh) |
| /yt-viral | Weekly: niche search → 5 competitor channels → unke apne median se ≥2× outliers + formula |
| /yt-comment | Weekly: comments 4 piles mein, reply drafts, kaunsa pin karein → `comments_report.md`. Auto-reply sirf `COMMENT_AUTO_REPLY=true` (repo Variable) pe |
| /yt-plan | Weekly: 7 din ka plan → `content_plan.json`; DI Shorts + Tiger isi se topic lete hain |
| /yt-script | DI Shorts: 5 hooks (21 formulas), hookscore se best = pehli line |
| /yt-package | Har upload: title lint (40/60 char, caps, vague, number) + purane titles se repeat block |
| /yt-seo | Har upload: 3 target searches → title/description/tags |
| /yt-chapters | DI long-form: chapters YouTube rules pe fix + validate (00:00, 3+, ≥10s) |
| /yt-shorts | DI long-form ke baad 3 Shorts apne aap (`longform_to_shorts.py`), ya `local_run\digitalimmortals_longform_to_shorts.bat` |
| /yt-edit | Lagu nahi: videos generate hote hain, recorded footage nahi |

Workflow ka naam ab "Weekly Growth Loop" hai (file wahi `channel_insights.yml`).

## Aapko karna hai (ek baar)
1. **GitHub Secrets** (repo → Settings → Secrets and variables → Actions):
   - `GEMINI_API_KEY` (aistudio.google.com, billing on) — sab channels ki images
   - `ANTHROPIC_API_KEY` — yt_brain (sab channels), DI Shorts scripts, Tiger topics, weekly insights
   - `DIGITALIMMORTALS_TOKEN_JSON` — `channels/DigitalImmortals/token.json` ka content
   - (optional) `OPENAI_API_KEY` — image backup
2. **Google Cloud → OAuth consent screen → Publish app ("In production")**. "Testing" mode mein refresh token 7 din mein expire hota hai aur sab uploads ruk jaate hain. Production karne ke baad har channel ka token ek baar dobara banao aur secrets update karo.
3. **Actions minutes check**: Settings → Billing. MindNest (11 languages × 3/week) sabse zyada minute khata hai.

4. **Pehla insights run**: Actions → "Weekly Growth Loop" → Run workflow. Iske baad har channel ki `insights.json` ban jayegi.
5. **Local .bat ke liye**: repo root mein `.env.example` ko `.env` copy karo aur keys daalo.
6. **channel_profiles.py**: Sabhi confirmed channel handles (`@DigitalImmortals`, `@EpicBharatSaga`, `@IndianHorrorTapes`, `@AllTrainReels`, `@MindNestTales`, `@TigerVlogs-2026`) code mein fill kar diye gaye hain.
7. **Workflows**: Sabhi workflow files apply ho chuki hain. Update 3 ke liye sirf `workflows_update_v3.zip` (channel_insights.yml + buzzstorm push fix) `.github/` mein extract karo.

## Abhi bhi baaki (code se fix nahi hota)
- DI long-form Ramayana: scripts sirf Ep 8 tak likhe hain; Ep 9 se pipeline ruk jayegi.
- Purane story banks static hain; lambe time mein LLM-based scripts pe shift karna behtar (DI Shorts jaisa).
