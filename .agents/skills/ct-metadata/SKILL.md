---
name: ct-metadata
description: Content pipeline ka metadata step — episode ka YouTube title, description, tags JSON mein likhna. Sirf ct-pipeline isse bulata hai.
---

# Metadata

Input: ct_state ka `context` (idea, script_file, language, title_max_chars).
`script_file` padh sakte ho (chhoti hai). Output: `write` path pe **sirf JSON**:

```json
{
  "title": "...",
  "description": "...",
  "tags": ["...", "..."]
}
```

## Rules
- Sab `language` mein (default Roman Hinglish — search mein yahi chalta hai).
- **Title** ≤ `title_max_chars`: curiosity + ek search keyword (horror story / bhootiya / sachi ghatna). Twist mat kholo. Clickbait jo video mein na ho — nahi.
- **Description** 2-3 line: kahani ka setup (twist nahi) + ek sawaal comment ke liye. Hashtags mat daalo — code khud jodta hai.
- **Tags** 6-10, search jaise phrases (Hinglish + English), har tag ≤ 30 chars.
- Koi `<` `>` nahi. Real logon ke naam nahi.
