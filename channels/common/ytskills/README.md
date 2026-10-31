# ytskills (vendored)

Unmodified copies of the tools that ship with the yt-* skills
(github.com/Jakeschincariol/youtube-agent-skill, MIT License, see LICENSE):
hooks.json, hookscore.py, title.py, swipe.py, retention.py.

`channels/common/skills.py` wraps them for the pipeline and adds a Hindi / Hinglish layer
(Devanagari tokens, Hindi address/stakes/curiosity words, Hindi formula patterns), because the
originals only tokenise Latin script and would score every Devanagari hook as empty.
