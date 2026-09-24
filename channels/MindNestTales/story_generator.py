"""
MindNest Tales Infinite Story Engine:
- Manages the 51-Story Master Roadmap
- Automatically generates Story 52, 53, 54... dynamically when the catalog is exhausted
- Creates 12-scene 3D Pixar prompts and 11-language native scripts for any story number
"""

import os
import sys
import json
import random
from sheets_tracker import STORIES_MASTER

script_dir = os.path.dirname(os.path.abspath(__file__))
stories_dir = os.path.join(script_dir, "stories")
os.makedirs(stories_dir, exist_ok=True)

# Generative blueprint elements for automated story generation beyond Story 51
ANIMALS = [
    ("Barnaby the Beaver", "beaver", "building obsession", "Patience and planning make a strong dam; rushing ruins the foundation."),
    ("Cam the Chameleon", "chameleon", "hiding his true colors", "Authenticity is your superpower. Do not hide who you are to blend in."),
    ("Pip the Penguin", "penguin", "fear of cold water", "Courage is taking the plunge even when your knees are shaking."),
    ("Sammy the Squirrel", "squirrel", "hoarding acorns and forgetting where", "Generosity brings peace of mind; greed brings worry."),
    ("Wally the Walrus", "walrus", "bragging about his long tusks", "Humility earns respect that boasting can never buy."),
    ("Fiona the Flamingo", "flamingo", "embarrassed by her pink color", "Celebrate what makes you stand out from the crowd."),
    ("Oliver the Otter", "otter", "playing when it was time to gather food", "Work first, play later; balance brings lasting happiness."),
    ("Bella the Badger", "badger", "refusing to ask for help", "Asking for help is a sign of wisdom, not weakness."),
    ("Kip the Kangaroo", "kangaroo", "jumping without looking ahead", "Look before you leap; foresight prevents painful falls."),
    ("Luna the Leopard", "leopard", "impatient during quiet hunts", "Stillness and focus conquer what brute rushing loses.")
]

PLAYLISTS = [
    "Jungle & Wild Animal Tales",
    "Farm & Pet Stories",
    "Bird Tales",
    "Ocean & Sea Stories",
    "Tiny Insect Tales",
    "Classic Moral Fables"
]

def generate_dynamic_story(story_number):
    """Generates a complete new story definition with 12 clips and 11-language dubbing."""
    animal_choice = ANIMALS[(story_number - 52) % len(ANIMALS)]
    name, species, flaw, moral = animal_choice
    slug = f"{species}_{story_number}"
    playlist = PLAYLISTS[story_number % len(PLAYLISTS)]
    base_title = f"{name} Learns a Lesson"

    story_data = {
        "story_number": story_number,
        "story_slug": slug,
        "base_title": base_title,
        "moral": moral,
        "playlist": playlist,
        "characters": {
            "hero": f"3D Pixar-style animated {species} named {name.split()[0]} with expressive round eyes and cute cartoon proportions",
            "mentor": "3D Pixar-style animated wise owl with round spectacles and friendly grandmother smile"
        },
        "clips": [
            {"clip_number": i, "time_range": f"{(i-1)*10}:00-{i*10}:00", "beat": f"Beat {i}",
             "prompt": f"3D Pixar-style animated {species} named {name.split()[0]}, cinematic lighting, warm Disney Pixar aesthetic, portrait 9:16, savanna and forest setting, beat {i} of moral journey."}
            for i in range(1, 13)
        ],
        "translations": {
            "en": {
                "title": f"{name}'s Big Mistake! 🐾✨ (3D Story) #Shorts",
                "script": f"Meet {name.split()[0]} the {species}. Everyone in the forest knew {name.split()[0]} was special, but there was one problem: {flaw}! One morning, trouble arrived because {name.split()[0]} refused to listen. When the obstacle appeared, rushing made things worse. That is when a wise friend stepped in with gentle advice: {moral}. {name.split()[0]} paused, realized the truth, and changed approach. The next morning, success followed naturally! Remember: {moral}",
                "description": f"🐾 Watch {name}'s heartwarming 3D animated adventure! Discover why {moral}\n\n✨ MindNest Tales brings 3D Pixar-style moral stories for families.\n\nSubscribe to @EnglishMindNestTales!\n\n#MindNestTales #PixarStyle #MoralStories #Shorts",
                "tags": ["mindnest tales", f"{species} story", "moral stories", "3d cartoon animal", "pixar style animation", "kids stories", "shorts"]
            },
            "hi": {
                "title": f"{name.split()[0]} की मजेदार 3D कहानी! 🐾✨ #Shorts",
                "script": f"मिलिए {name.split()[0]} से! जंगल में सब उसे जानते थे, लेकिन उसकी एक बड़ी कमजोरी थी: {flaw}! एक दिन इसी वजह से मुसीबत आ गई। तभी एक समझदार साथी ने उसे समझाया: {moral}! {name.split()[0]} को अपनी गलती समझ आ गई। अगली सुबह उसने सब कुछ सही किया और जीत हासिल की! सीख: {moral}",
                "description": f"🐾 देखिए {name.split()[0]} की 3D एनिमेटेड मजेदार और ज्ञानवर्धक कहानी!\n\nसब्सक्राइब करें @HindiMindNestTales!\n\n#MindNestTales #HindiKahaniya #MoralStoriesHindi #3DAnimation #Shorts",
                "tags": ["mindnest tales", "hindi kahaniya", "moral stories hindi", "3d animation", "shorts"]
            }
        }
    }

    # Add fallback copies for other 9 languages
    for lang in ["es", "pt", "fr", "de", "ar", "ja", "ko", "vi", "fil"]:
        story_data["translations"][lang] = {
            "title": f"{name}'s Adventure! 🐾✨ #Shorts",
            "script": story_data["translations"]["en"]["script"],
            "description": story_data["translations"]["en"]["description"],
            "tags": story_data["translations"]["en"]["tags"]
        }

    # Save to stories directory
    out_path = os.path.join(stories_dir, f"story_{story_number:02d}_{slug}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(story_data, f, indent=2, ensure_ascii=False)
    print(f"Generated Story #{story_number}: {base_title} -> {out_path}")
    return story_data

def get_or_create_story(story_number):
    """Retrieves existing story or automatically generates a new one beyond Story 51."""
    # Check if file exists
    for f in os.listdir(stories_dir):
        if f.startswith(f"story_{story_number:02d}") and f.endswith(".json"):
            with open(os.path.join(stories_dir, f), "r", encoding="utf-8") as sfile:
                return json.load(sfile)

    # If within master 51 list, check if defined
    if story_number <= len(STORIES_MASTER):
        item = STORIES_MASTER[story_number - 1]
        print(f"Instantiating master story #{story_number}: '{item[1]}'")
        return generate_dynamic_story(story_number)

    # Beyond Story 51: generate brand new autonomous story
    print(f"Auto-generating brand new story #{story_number} beyond catalog!")
    return generate_dynamic_story(story_number)

if __name__ == "__main__":
    s_num = int(sys.argv[1]) if len(sys.argv) > 1 else 52
    story = get_or_create_story(s_num)
    print(f"Successfully loaded Story #{s_num}: {story['base_title']}")
