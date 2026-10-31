---
name: ct-idea-bank
description: Content pipeline ka idea step — ct_state ke diye context se ek batch mein naye story ideas JSON file mein likhna. Sirf ct-pipeline isse bulata hai.
---

# Idea Bank

Input: ct_state ka `context` (channel, count, themes, style, avoid_titles).
Output: `write` path pe **sirf JSON** — koi aur text nahi.

```json
[
  {"title": "Highway ka aakhri dhaba", "premise": "2-3 line: kaun, kahan, kya ajeeb hua", "theme": "highway", "twist": "1 line ending twist"}
]
```

## Rules
- Exactly `count` ideas. Themes mein barabar baanto.
- `title` Roman Hinglish, max 8 words. `avoid_titles` se milta-julta kuch nahi.
- `premise` mein ek specific, visual, ajeeb detail ho (sirf "bhoot dikha" nahi).
- Har twist alag type ka: pehchaan, samay, jagah, narrator khud, object.
- Real logon / real hadson / real jagah ke naam nahi. Gore nahi.
- Ek hi baar mein likho, research mat karo, tools mat chalao (sirf file write).
