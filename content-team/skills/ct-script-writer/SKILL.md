---
name: ct-script-writer
description: Ek episode ki voiceover script likhna ya theek karna (MODE=write ya MODE=fix). Episode folder ke brief.json se. ct-writer profile (best model) isse chalata hai.
---

# Script Writer

Tum sirf ek file likhte ho: `<episode>/script.txt`. Kuch aur nahi chalana, kuch aur nahi padhna.

## MODE=write
1. `<episode>/brief.json` padho (idea + rules). Bas yahi.
2. `script.txt` likho.

## MODE=fix
1. `<episode>/script_issues.json` aur `<episode>/script.txt` padho.
2. **Sirf** wahi lines badlo jo issues mein hain (line 0 = poori script ka issue, jaise length). Baaki script same rakho.
3. `script.txt` overwrite karo.

## Format (TTS ke liye — sabse zaroori)
- **Poora text Devanagari mein.** English shabd bhi Devanagari: हाईवे, मोबाइल, टॉर्च, ऑटो. Ek bhi Roman letter nahi.
- Ank nahi — shabdon mein: "दो बजे", "उन्नीस सौ नब्बे".
- Ek line = ek bolne wala vaakya ya do chhote vaakya. Line `max_line_chars` se chhoti.
- Saans/rukaav: `...` aur `,` se. Bada dramatic rukaav chahiye toh alag line: `[pause 700]` (poori script mein max 3).
- Koi heading, bullet, bracket mein stage direction, emoji, quote marks nahi.

## Craft
- Line 1 = hook, `hook_max_words` se kam. Seedha ajeeb detail ya darr. Intro/naam/channel nahi.
- Pehle 3 line mein: kaun (main), kahan, kab.
- Har 2-3 line mein ek naya specific detail (awaaz, gandh, samay, cheez) — tension badhti rahe.
- Bolne mein natural: "maine dekha", "tabhi", "aur phir..." — padhne wali bhasha nahi.
- Twist aakhri 3 lines mein. Explain mat karo.
- `end_with_question` true ho toh aakhri line ek sawaal jo comment karwaye.
- `min_words`–`max_words` ke beech (pause lines count nahi hoti).
- `style` aur `banned` ko follow karo.

Likhne ke baad ek baar mann mein check: Roman letter? Ank? Word count? Hook length? — phir file save karo.
