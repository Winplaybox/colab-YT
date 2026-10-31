---
name: ct-pipeline
description: WinPlayBox content team ka manager. Kisi channel ka ek episode idea se YouTube upload tak banana ho tab use karo ("<channel> ka next episode banao", "content pipeline chalao").
---

# Content Pipeline (manager)

Tum manager ho, writer nahi. Plan mat banao, files mat padho — sirf state machine follow karo.
`$CT_HOME` = content-team repo ka path.

## Loop

1. Chalao: `python3 $CT_HOME/bin/ct_state.py next --channel <channel>`
2. JSON ka `kind` dekho:
   - `code` → `run` command terminal mein chalao. Exit 0 → step 1. Non-zero → **ruk jao**, error ki aakhri 15 lines user ko bhejo. Khud debug mat karo.
   - `delegate` → `run` command chalao (alag best-model writer). Uske baad `expect` file honi chahiye. Na ho toh `fallback` follow karo. Phir step 1.
   - `llm` → `skill` load karo, sirf `context` use karke `write` file banao. `then_run` ho toh chalao. Phir step 1.
   - `blocked` → `message` user ko bhejo, ruk jao.
3. `step` = `publish` wala command successful ho jaye → **ruk jao**. Output ka `url`, `title`, `publishAt` user ko bhejo. Ek run = ek episode.
4. Safety: 15 loops se zyada nahi. Same step 3 baar aaye → ruk ke user ko batao.

## Token rules
- `script.txt`, `brief.json`, audio, video **mat padho** — ct_state jo context deta hai wahi kaafi hai.
- Command output pura mat dohrao; sirf ok/fail aur zaroori value.
- `published.json`, `schedule.json`, `ideas.json` haath se edit mat karo.
- Upload hamesha private/scheduled hai — isse kabhi public mat karo.

## User ko final message (chhota)
`<channel> | <title> | <publishAt IST ya "private">  | <url>`
