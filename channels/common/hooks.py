"""
/yt-script hook step for the pipeline: write FIVE hooks against the 21 formulas, score them with the
vendored hookscore (+ Hindi layer), keep the best. Never ship a single unscored hook.

    from channels.common.hooks import best_hook
    res = best_hook(topic, current_first_line, language="Hindi (Devanagari)", insights=dict)
    res["best"]["hook"], res["candidates"]  (all five with scores)

Falls back to the current first line if Claude is unavailable.
"""
import json
import os
import re

from . import skills

FORMULA_NAMES = [f["name"] for f in skills._hs.FORMULAS]


def _claude(prompt):
    import anthropic

    msg = anthropic.Anthropic().messages.create(
        model=os.environ.get("CLAUDE_MODEL", "claude-sonnet-5-5"), max_tokens=900,
        messages=[{"role": "user", "content": prompt}])
    text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
    return json.loads(re.search(r"\{.*\}", text, re.S).group(0))


def best_hook(topic, current_first_line, language="Hindi", insights=None, is_short=True):
    cands = [current_first_line] if current_first_line else []
    if os.environ.get("ANTHROPIC_API_KEY"):
        ins = {k: (insights or {}).get(k) for k in ("winning_patterns", "avoid", "top_titles") if (insights or {}).get(k)}
        prompt = f"""Write FIVE alternative opening lines (the hook, first 2-3 seconds of a {"YouTube Short" if is_short else "video"}) for this video.
Topic: {topic}
Current opening line: {current_first_line}
Language: {language} (spoken, natural).
Each hook uses a DIFFERENT formula from: {", ".join(FORMULA_NAMES)}.
Rules: confirm what the title promises, open a question the viewer cannot close, be specific (a name, place, number),
9-20 words, no greeting, no channel name, no invented facts or numbers.
What this channel's audience responds to: {json.dumps(ins, ensure_ascii=False)}
Return ONLY JSON: {{"hooks": [{{"formula": "...", "text": "..."}}]}}"""
        try:
            cands += [h["text"] for h in _claude(prompt).get("hooks", []) if h.get("text")]
        except Exception as e:
            print(f"[hooks] generation notice: {e}")
    ranked = skills.rank_hooks(cands)
    if not ranked:
        return {"best": None, "candidates": []}
    return {"best": ranked[0], "candidates": ranked}
