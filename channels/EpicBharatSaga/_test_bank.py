import sys
sys.path.insert(0, 'channels/EpicBharatSaga')
from story_bank import ALL_MYTH_STORIES
print(f'Total stories: {len(ALL_MYTH_STORIES)}')
deities = {}
for s in ALL_MYTH_STORIES:
    d = s['deity']
    deities[d] = deities.get(d, 0) + 1
for d, c in deities.items():
    print(f'  {d}: {c} stories')
print()
from story_generator import generate_story_from_bank
for ep in [1, 2, 16, 23, 25]:
    s = generate_story_from_bank(ep)
    print(f'Ep{ep:02d}: Season{s.get("season")} [{s.get("deity")}] {s["title"]}')
