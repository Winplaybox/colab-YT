"""
IndianHorrorTapes Story Generator:
- Implements the 100+ Real Indian Horror Stories Universe.
- Adheres strictly to the Universal Template format (6 Beats: Intro, Setup, Build-up, Incident, Aftermath, Outro).
- Generates 120-second immersive Hinglish audio scripts, on-screen captions, and 8K image prompts.
"""

import os
import sys
import json

# Ensure UTF-8 output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

script_dir = os.path.dirname(os.path.abspath(__file__))
stories_dir = os.path.join(script_dir, "stories")
os.makedirs(stories_dir, exist_ok=True)

# Curated episodes from prompt
CURATED_EPISODES = {
    1: {
        "story_number": 1,
        "title": "Bhangarh Fort — Sabse Paapi Kila",
        "location": "Bhangarh Fort, Alwar, Rajasthan",
        "tagline": "ASI-banned after sunset; tantrik's curse on a princess",
        "beats": [
            {
                "beat": "INTRO",
                "time_range": "0:00–0:08",
                "target_dur": 8.0,
                "visual_prompt": "Drone shot of ancient Bhangarh Fort crumbling ruins at dusk, dense fog, eerie dark sky, volumetric red moonlight, hyper-realistic, photorealistic horror, 8k resolution, portrait 9:16",
                "text_overlay": "BHANGARH FORT",
                "vo_text": "Ye Rajasthan ka ek kila hai... jahan Archaeological Survey of India ne khud likha hai — sunset ke baad andar jaana mana hai.",
                "sound_cue": "Wind howling, low drone"
            },
            {
                "beat": "SETUP",
                "time_range": "0:08–0:30",
                "target_dur": 22.0,
                "visual_prompt": "Walking POV shot through broken stone gates of Bhangarh Fort, golden hour sunlight fading into cold twilight, ancient desolate courtyards, photorealistic horror, 8k resolution, portrait 9:16",
                "text_overlay": "16th Century — Rajasthan",
                "vo_text": "Kehte hain, saalon pehle ek tantrik ne rani se pyaar kiya tha. Rani ne mana kar diya, aur gusse mein tantrik ne pura kila hi shraap de diya.",
                "sound_cue": "Deep eerie ambient drone"
            },
            {
                "beat": "BUILD-UP",
                "time_range": "0:30–1:00",
                "target_dur": 30.0,
                "visual_prompt": "Deep shadows moving in empty ruined palace rooms, dust motes in flashlight beam, slow zoom on broken arched windows, sinister darkness, photorealistic horror, 8k resolution, portrait 9:16",
                "text_overlay": "Unexplained Sounds After Sunset",
                "vo_text": "Aaj bhi log kehte hain — raat ko yahan awaazein aati hain. Chudiyon ki jhankaar, kisi ke rone ki awaaz... lekin koi dikhta nahi.",
                "sound_cue": "Distant bangles jingling, faint whisper"
            },
            {
                "beat": "THE INCIDENT",
                "time_range": "1:00–1:35",
                "target_dur": 35.0,
                "visual_prompt": "Tense flashlight beam illuminating a fast-moving dark shadow crossing behind an ancient stone pillar, camera shake, chilling mystery, photorealistic horror, 8k resolution, portrait 9:16",
                "text_overlay": "The 2010 Incident",
                "vo_text": "2010 mein kuch trekkers raat rukne ki koshish kar rahe the fort ke bahar. Subah unme se ek ka phone mila — andar, us jagah jahan koi jaa hi nahi sakta tha.",
                "sound_cue": "Sudden silence, then a loud branch snap and heartbeat"
            },
            {
                "beat": "AFTERMATH",
                "time_range": "1:35–1:50",
                "target_dur": 15.0,
                "visual_prompt": "Single flashlight beam piercing darkness on the rusted ASI iron warning board at Bhangarh fort gate, cold mist, slow pan, photorealistic horror, 8k resolution, portrait 9:16",
                "text_overlay": "Fact: ASI officially bans entry after 6 PM",
                "vo_text": "Aaj bhi ASI ka board wahin khada hai. Sunset ke baad, wahan sirf sannata hai... ya shayad kuch aur bhi.",
                "sound_cue": "Slow atmospheric drone"
            },
            {
                "beat": "OUTRO",
                "time_range": "1:50–2:00",
                "target_dur": 10.0,
                "visual_prompt": "Total darkness with faint red glowing mist and silhouettes of abandoned palace arches fading to black, photorealistic horror, 8k resolution, portrait 9:16",
                "text_overlay": "PART 2 → DUMAS BEACH",
                "vo_text": "Agli kahani ek beach ki hai... jahan log raat ko akele jaana bhool jaate hain. Agla episode zaroor dekhein.",
                "sound_cue": "Heartbeat fades into silence"
            }
        ],
        "tags": ["bhangarh", "bhangarhfort", "indianhorror", "rajasthan", "horrorstories", "shorts", "hauntedfort", "asi", "tantrik"]
    },
    2: {
        "story_number": 2,
        "title": "Dumas Beach — Kaali Reti Ka Raaz",
        "location": "Dumas Beach, Surat, Gujarat",
        "tagline": "Black sand beach, former cremation ground, whispered voices",
        "beats": [
            {
                "beat": "INTRO",
                "time_range": "0:00–0:08",
                "target_dur": 8.0,
                "visual_prompt": "Black sand beach at dark night, slow eerie waves crashing under gloomy moon, cold ocean mist, photorealistic horror, 8k resolution, portrait 9:16",
                "text_overlay": "DUMAS BEACH",
                "vo_text": "Gujarat ka ye beach dikhne mein normal hai... lekin iski reti kaali hai, aur iski kahani aur bhi kaali.",
                "sound_cue": "Ocean waves with dark drone"
            },
            {
                "beat": "SETUP",
                "time_range": "0:08–0:30",
                "target_dur": 22.0,
                "visual_prompt": "Wide shot of eerie black sand beach of Dumas in Surat, blood-orange sunset fading into dark purple, deserted shoreline, photorealistic horror, 8k resolution, portrait 9:16",
                "text_overlay": "Once a Hindu cremation ground",
                "vo_text": "Ye jagah pehle Hindu shamshaan ghat thi — jahan logon ka antim sanskar hota tha. Aaj bhi locals sunset ke baad yahan nahi rukte.",
                "sound_cue": "Wind howling across black dunes"
            },
            {
                "beat": "BUILD-UP",
                "time_range": "0:30–1:00",
                "target_dur": 30.0,
                "visual_prompt": "POV walking alone on black sand beach at night, mysterious wet footprints appearing in sand ahead, fog rolling in, photorealistic horror, 8k resolution, portrait 9:16",
                "text_overlay": "Footsteps Behind You",
                "vo_text": "Tourists kehte hain — akele chalte waqt unhe apne peeche kadmon ki awaaz sunayi deti hai. Palat kar dekho toh koi nahi hota.",
                "sound_cue": "Footsteps crunching in sand, stopping abruptly"
            },
            {
                "beat": "THE INCIDENT",
                "time_range": "1:00–1:35",
                "target_dur": 35.0,
                "visual_prompt": "Shaky flashlight pointing across pitch-black beach, smartphone screen displaying 'No Service', shadowy figure watching from distance, photorealistic horror, 8k resolution, portrait 9:16",
                "text_overlay": "Voices Calling Your Name",
                "vo_text": "Kai logon ne bataya hai — yahan phone ka network achanak chala jaata hai. Kuch logon ko apna naam pukarte hue sunayi diya, jab wahan koi tha hi nahi.",
                "sound_cue": "Radio static, eerie whisper calling in Hindi"
            },
            {
                "beat": "AFTERMATH",
                "time_range": "1:35–1:50",
                "target_dur": 15.0,
                "visual_prompt": "Slow pan of desolate black sand beach under full moon, dark waves whispering, photorealistic horror, 8k resolution, portrait 9:16",
                "text_overlay": "Still avoided by locals after dark",
                "vo_text": "Local fishermen aaj bhi kehte hain — Dumas mein raat ko akele mat jaana. Reti tumhe wapas nahi jaane degi.",
                "sound_cue": "Low haunting drone"
            },
            {
                "beat": "OUTRO",
                "time_range": "1:50–2:00",
                "target_dur": 10.0,
                "visual_prompt": "Pitch black screen with glowing red text and silhouette of an old Indian streetlamp, photorealistic horror, 8k resolution, portrait 9:16",
                "text_overlay": "PART 3 → NALE BA",
                "vo_text": "Agli kahani Bangalore ki ek awaaz ki hai... jo aaj bhi raat ko sunayi deti hai. Part 3 zaroor dekhein.",
                "sound_cue": "Distant metal clang, heartbeat fades"
            }
        ],
        "tags": ["dumasbeach", "surat", "gujarat", "blackbeach", "indianhorror", "horrorstories", "shorts", "hauntedbeach", "cremation"]
    },
    3: {
        "story_number": 3,
        "title": "Nale Ba — Bangalore Ki Awaaz",
        "location": "Bangalore, Karnataka",
        "tagline": "1980s come tomorrow chalk-writing panic",
        "beats": [
            {
                "beat": "INTRO",
                "time_range": "0:00–0:08",
                "target_dur": 8.0,
                "visual_prompt": "Dark foggy 1980s Bangalore street at midnight, flickering yellow streetlight, ominous shadows, photorealistic horror, 8k resolution, portrait 9:16",
                "text_overlay": "NALE BA",
                "vo_text": "1980s mein Bangalore ke logon ne apne ghar ke bahar ek cheez likhna shuru kar diya — 'Nale Ba'.",
                "sound_cue": "Distant flickering bulb buzzing, eerie silence"
            },
            {
                "beat": "SETUP",
                "time_range": "0:08–0:30",
                "target_dur": 22.0,
                "visual_prompt": "Extreme close-up of rough wooden village door with chalk writing in Kannada and English reading 'Nale Ba', photorealistic horror, 8k resolution, portrait 9:16",
                "text_overlay": "Nale Ba = 'Come Tomorrow'",
                "vo_text": "Kannada mein iska matlab hai — 'Kal aana.' Log kehte the ek aurat raat ko darwaza khatkhatati thi, aur agle din wo ghar khaali mil jaata tha.",
                "sound_cue": "Heavy wood knock echoes twice"
            },
            {
                "beat": "BUILD-UP",
                "time_range": "0:30–1:00",
                "target_dur": 30.0,
                "visual_prompt": "Empty deserted Bangalore residential street at 2 AM, shadow of a woman in saree cast against house wall, slow camera zoom, photorealistic horror, 8k resolution, portrait 9:16",
                "text_overlay": "The City-Wide Panic",
                "vo_text": "Logon ne socha agar wo darwaza khatkhataye toh bol do 'Nale Ba' — aur wo agle din tak wapas nahi aayegi. Poore shehar mein log apne ghar ke bahar ye likhne lage.",
                "sound_cue": "Slow rhythmic footsteps approaching gate"
            },
            {
                "beat": "THE INCIDENT",
                "time_range": "1:00–1:35",
                "target_dur": 35.0,
                "visual_prompt": "POV through door peephole, sudden flash of a terrifying pale silhouette outside the porch, red markings across wall, photorealistic horror, 8k resolution, portrait 9:16",
                "text_overlay": "The Night They Kept Shut",
                "vo_text": "Ek raat ek family ne darwaza nahi khola. Subah unhone dekha — poore ghar ke bahar khoon se likha tha... 'Nale Ba'.",
                "sound_cue": "Loud violent knocks, glass rattle, then dead silence"
            },
            {
                "beat": "AFTERMATH",
                "time_range": "1:35–1:50",
                "target_dur": 15.0,
                "visual_prompt": "Wide shot of old heritage Bangalore colonial house, dusty veranda under moon, silence, photorealistic horror, 8k resolution, portrait 9:16",
                "text_overlay": "Urban legend still alive today",
                "vo_text": "Aaj bhi kuch purane gharon par inhi shabdon ke nishaan milte hain. Kahani sach thi ya afwaah — koi nahi jaanta.",
                "sound_cue": "Subtle wind and metallic drone"
            },
            {
                "beat": "OUTRO",
                "time_range": "1:50–2:00",
                "target_dur": 10.0,
                "visual_prompt": "Black background with fading red mist, cinematic horror aesthetic, 8k resolution, portrait 9:16",
                "text_overlay": "PART 4 → KULDHARA",
                "vo_text": "Agli kahani Rajasthan ke us gaon ki hai jahan se 1500 log ek hi raat mein gayab ho gaye. Follow for Part 4.",
                "sound_cue": "Heartbeat fading out"
            }
        ],
        "tags": ["naleba", "bangalore", "karnataka", "urbanlegend", "indianhorror", "horrorstories", "shorts", "stree", "witchcraft"]
    }
}

def load_master_bank():
    """Loads all 103 real Indian horror stories from bank."""
    bank_path = os.path.join(script_dir, "stories_bank.json")
    with open(bank_path, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_procedural_script(story_info, next_story_info=None):
    """
    Generates a full 2-minute Universal Template horror script for any story from the 103 story bank.
    Uses 'kaha jaata hai' (it is said) phrasing for maximum dread and authentic Indian folklore atmosphere.
    """
    num = story_info["story_number"]
    name = story_info["name"]
    loc = story_info["location"]
    hook = story_info["hook"]
    cat = story_info["category"]
    sub = story_info.get("subtitle", "Khaufnaak Raaz")

    next_num = (num % 103) + 1
    next_name = next_story_info["name"] if next_story_info else f"Episode #{next_num}"

    # Visual prompt generator with deep cinematic horror tags
    prompt_base = f"Cinematic dark horror photography of {name} in {loc}, nighttime, eerie atmospheric fog, volumetric moonlight, realistic textures, chilling shadows, 8k resolution, Unreal Engine 5 aesthetic, photorealistic horror, portrait 9:16"

    beats = [
        {
            "beat": "INTRO",
            "time_range": "0:00–0:08",
            "target_dur": 8.0,
            "visual_prompt": f"Establishing dark shot of {name}, {loc}, cold mist, blood red flicker lighting, photorealistic horror, 8k resolution, portrait 9:16",
            "text_overlay": name.upper(),
            "vo_text": f"Ye kahani sach hai... {loc} ki is jagah ko log aaj bhi yaad karke darte hain.",
            "sound_cue": "Low eerie drone + heartbeat"
        },
        {
            "beat": "SETUP",
            "time_range": "0:08–0:30",
            "target_dur": 22.0,
            "visual_prompt": f"Wide establishing cinematic shot of {name} in {loc}, ancient weathered architecture, fading dusk into twilight, photorealistic horror, 8k resolution, portrait 9:16",
            "text_overlay": f"{loc} — {cat}",
            "vo_text": f"Kaha jaata hai, {loc} ke is ilaqe mein saalon se ek ajeeb sa sannata rehta hai. {hook.capitalize()}.",
            "sound_cue": "Ambient wind and eerie drone"
        },
        {
            "beat": "BUILD-UP",
            "time_range": "0:30–1:00",
            "target_dur": 30.0,
            "visual_prompt": f"Slow POV walking shot entering {name}, dim flickering lantern, deep terrifying shadows behind pillars, dust motes in beam, photorealistic horror, 8k resolution, portrait 9:16",
            "text_overlay": "First Warning Signs",
            "vo_text": f"Wahan se guzarne wale log kehte hain — jaise hi andhera hota hai, hawa ka tapman achanak gir jaata hai. Aisa lagta hai jaise koi apke bilkul peeche khada ho kar saans le raha ho.",
            "sound_cue": "Slow footsteps, distant cold whisper"
        },
        {
            "beat": "THE INCIDENT",
            "time_range": "1:00–1:35",
            "target_dur": 35.0,
            "visual_prompt": f"Tense shaky camera shot at {name}, sudden appearance of a dark sinister silhouette crossing through mist, cinematic horror, photorealistic horror, 8k resolution, portrait 9:16",
            "text_overlay": "The Unexplained Incident",
            "vo_text": f"Ek baar raat ko yahan aane wale logon ne daawa kiya — unke phone ka camera achanak band ho gaya, aur andhere mein unhe ajeeb si cheekh sunayi di. Subah tak wahan sirf unka samaan bacha tha.",
            "sound_cue": "Sudden sharp snap, heartbeat accelerates"
        },
        {
            "beat": "AFTERMATH",
            "time_range": "1:35–1:50",
            "target_dur": 15.0,
            "visual_prompt": f"Desolate and quiet night shot of {name}, single lantern flickering on ancient ground, heavy fog rolling, photorealistic horror, 8k resolution, portrait 9:16",
            "text_overlay": "Locals Still Avoid After Sunset",
            "vo_text": f"Aaj bhi locals aadhi raat ko yahan jaane se mana karte hain. Kehte hain kuch raaz aise hote hain jinhe andhere mein hi rehne dena chahiye.",
            "sound_cue": "Faint lingering drone"
        },
        {
            "beat": "OUTRO",
            "time_range": "1:50–2:00",
            "target_dur": 10.0,
            "visual_prompt": f"Vignette black screen with red glowing text and fog silhouette, cinematic horror, portrait 9:16",
            "text_overlay": f"PART {next_num} → {next_name.upper()}",
            "vo_text": f"Agli kahani {next_name} ki hai... wo isse bhi zyada darawani hai. Dekhte rehna.",
            "sound_cue": "Heartbeat fades into darkness"
        }
    ]

    slug = story_info["slug"]
    tags = [
        slug.replace("_", ""),
        "indianhorror",
        "horrorstories",
        "paranormal",
        "ghoststory",
        "shorts",
        "hauntedindia",
        loc.split(",")[0].strip().lower().replace(" ", "")
    ]

    return {
        "story_number": num,
        "title": story_info["title"],
        "location": loc,
        "tagline": hook,
        "category": cat,
        "beats": beats,
        "tags": tags
    }

def get_or_create_story(story_number=1):
    """Retrieves curated script or auto-generates procedural script for story_number (1-103)."""
    bank = load_master_bank()
    bank_map = {s["story_number"]: s for s in bank}

    if story_number not in bank_map:
        story_number = 1

    story_info = bank_map[story_number]
    slug = story_info["slug"]
    story_path = os.path.join(stories_dir, f"story_{story_number:02d}_{slug}.json")

    # If curated script exists in code, use it
    if story_number in CURATED_EPISODES:
        data = CURATED_EPISODES[story_number]
        with open(story_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return data

    # Check if saved on disk
    if os.path.exists(story_path):
        try:
            with open(story_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    # Generate procedural script
    next_num = (story_number % 103) + 1
    next_info = bank_map.get(next_num)
    data = generate_procedural_script(story_info, next_info)

    with open(story_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return data

if __name__ == "__main__":
    num = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    s = get_or_create_story(num)
    print(f"Generated Story #{s['story_number']}: {s['title']}")
    print(f"Beats count: {len(s['beats'])}")
    for b in s['beats']:
        print(f"[{b['beat']}] ({b['time_range']}): {b['vo_text']}")
