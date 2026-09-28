"""
IndianHorrorTapes YouTube Community Tab Post & Poll Engine
==========================================================
Generates high-engagement Community Posts to boost channel impressions between video uploads:
- Interactive Audience Polls (4 dilemma choices) designed to explode votes and comments
- Episode Premiere Teasers with Thumbnail & Story Previews (Wednesday & Sunday 9:00 PM IST)
- Declassified Historical Trivia & Police FIR highlights
- Real Eyewitness Submission Calls ("Share your encounter to be featured in the next episode")
Persists generated assets to channels/IndianHorrorTapes/community_posts/.
"""

import os
import sys
import json
from datetime import datetime

script_dir = os.path.dirname(os.path.abspath(__file__))
posts_dir = os.path.join(script_dir, "community_posts")
os.makedirs(posts_dir, exist_ok=True)

def generate_community_poll(story_data):
    """Generates a high-friction 4-option audience dilemma poll."""
    num = story_data.get("story_number", 1)
    name = story_data.get("name", "Is Jagah")
    loc = story_data.get("location", "India")
    arch = story_data.get("archetype", "ARCHIVAL_EXPEDITION")

    if arch == "POLICE_DISPATCH_LOG" or "road" in name.lower() or "highway" in name.lower():
        question = (
            f"🚨 NIGHT HIGHWAY DILEMMA: Maan lijiye aadhi raat ke 2:30 baje {loc} ke {name} stretch par "
            f"aapki gaadi achanak band ho jati hai aur rearview mirror mein koi saaya dikhta hai... Aap kya karenge?"
        )
        options = [
            "1. Gaadi ke andar lock hokar police ko call karenge 🔒",
            "2. Headlights high-beam par karke bahar check karenge 🔦",
            "3. Gaadi chhodkar highway par tezi se daudenge 🏃‍♂️",
            "4. Aankhein band karke subah ke ujaale ka wait karenge 👁️"
        ]
    elif arch == "SOLITARY_TRAVELER_TAPE" or "station" in name.lower() or "tunnel" in name.lower():
        question = (
            f"🚂 {name.upper()}: Indian Railways ne is railway station ko saalon tak band rakha tha... "
            f"Agar aapko raat ko akele yahan 1 ghanta rukne ke ₹5 Lakh milein, toh kya aap rukenge?"
        )
        options = [
            "1. Haan, bilkul! Main darta nahi hoon 💰",
            "2. Kabhi nahi! Jaan se badhkar kuch nahi 💀",
            "3. Sirf tab agar sath mein 4 dost aur camera ho 🎥",
            "4. Pehle din mein dekhna chahunga ☀️"
        ]
    elif arch == "FORBIDDEN_ZONE_BREACH" or "village" in name.lower():
        question = (
            f"🏚️ {name.upper()} KA SHRAAP: Kaha jaata hai ki {loc} ke is khandar mein sunset ke baad jo bhi kadam rakhta hai, "
            f"uska dimaag bhatak jata hai... Kya aap paranormal powers par vishwas karte hain?"
        )
        options = [
            "1. 100% Sach! Maine khud aisi cheezein mehsoos ki hain 👁️",
            "2. Sirf darr aur dimaag ka veham hai 🧠",
            "3. Kuch jagahon par negative energy zaroor hoti hai ⚡",
            "4. Mujhe abhi tak koi solid saboot nahi mila 🤔"
        ]
    else:
        question = (
            f"🏰 ASI BAN QUESTION: Archaeological Survey of India ka board kehta hai ki {name} mein "
            f"sunset ke baad jana kanoon aur jaan dono ke khilaaf hai... Aapke mutabiq aisi jagahon par sarkar kyu ban lagati hai?"
        )
        options = [
            "1. Asli roohon aur aatmaon ke khatre ki wajah se 👻",
            "2. Wild animals aur khandar girne ke risk se 🦁",
            "3. Tantrik aur kaali shaktiyon ke darr se 🪔",
            "4. Dono — Paranormal + Physical risk ⚠️"
        ]

    return {
        "poll_type": "MULTIPLE_CHOICE_DILEMMA",
        "question": question,
        "options": options,
        "context_episode": f"Ep #{num}: {name}"
    }

def generate_premiere_teaser(story_data):
    """Generates an episode premiere teaser community update."""
    num = story_data.get("story_number", 1)
    name = story_data.get("name", "Unknown Incident")
    loc = story_data.get("location", "India")
    tagline = story_data.get("tagline", "Khaufnaak Raaz")
    year = story_data.get("year", "Historical")
    sub = story_data.get("subtitle", "")

    teaser_text = f"""🔴 TONIGHT AT 9:00 PM IST: DECLASSIFIED TAPE #{num:03d} ⚠️

📍 Location: {name} ({loc})
📜 Archival Record: {year}

"{tagline}"

Kehte hain India ki kuch deewaron ke peeche aisi sachi ghatnayein dabi hain jinka jawab modern science ke paas bhi nahi hai. Aaj raat ghadi mein theek 9:00 baje ek naya case file open hone ja raha hai.

Reminder set kar lijiye aur headphones laga kar sunna mat bhoolna 🎧

Subscribe: @IndianHorrorTapes
#IndianHorrorTapes #Shorts #RealHorrorStories #HauntedIndia
"""
    return {
        "type": "PREMIERE_TEASER",
        "text": teaser_text,
        "suggested_image": f"stories/thumbnails/story_{num:02d}_thumbnail.jpg"
    }

def generate_trivia_post(story_data):
    """Generates an archival declassified trivia community update."""
    num = story_data.get("story_number", 1)
    name = story_data.get("name", "Unknown")
    loc = story_data.get("location", "India")
    year = story_data.get("year", "Historical")

    trivia_text = f"""📜 DID YOU KNOW? DECLASSIFIED ARCHIVE #{num:03d} 👁️

{name} ({loc}) ke baare mein police files aur colonial records mein darj hai ki {year} ke baad se kai aisi thermal anomalies capture hui hain jise koi physicist explain nahi kar saka.

Wahan raat ko phone ka battery percentage achanak 90% se girkar 0% ho jata hai aur ambient temperature ek jhatke mein 15°C drop karta hai.

Kya aapke shaher ya gaon mein bhi aisi koi jagah hai?
Niche comments mein apna experience zaroor share karein — sabse terrifying story agle episode mein feature hogi! 👇
"""
    return {
        "type": "ARCHIVAL_TRIVIA",
        "text": trivia_text
    }

def build_community_bundle(story_data):
    """Generates the complete community tab content bundle for an episode."""
    num = story_data.get("story_number", 1)
    slug = story_data.get("slug") or story_data.get("name", "").lower().replace(" ", "_")

    bundle = {
        "story_number": num,
        "name": story_data.get("name"),
        "generated_at": datetime.now().isoformat(),
        "poll": generate_community_poll(story_data),
        "teaser": generate_premiere_teaser(story_data),
        "trivia": generate_trivia_post(story_data)
    }

    out_file = os.path.join(posts_dir, f"community_post_ep_{num:02d}_{slug}.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(bundle, f, indent=2, ensure_ascii=False)

    md_file = os.path.join(posts_dir, f"community_post_ep_{num:02d}_{slug}.md")
    with open(md_file, "w", encoding="utf-8") as f:
        f.write(f"# 📢 COMMUNITY POSTS: Case File #{num:03d} — {story_data.get('name')}\n\n")
        f.write(f"## 1. 📊 HIGH-ENGAGEMENT AUDIENCE POLL\n")
        f.write(f"**Question**: {bundle['poll']['question']}\n\n")
        f.write(f"**Options**:\n")
        for opt in bundle['poll']['options']:
            f.write(f"- {opt}\n")
        f.write(f"\n---\n\n## 2. 🎬 PREMIERE TEASER POST (Wed / Sun 9:00 PM IST)\n\n")
        f.write(f"```\n{bundle['teaser']['text']}\n```\n")
        f.write(f"\n---\n\n## 3. 📜 ARCHIVAL TRIVIA & VIEWER SUBMISSION CALL\n\n")
        f.write(f"```\n{bundle['trivia']['text']}\n```\n")

    print(f"✅ Generated Community Posts & Poll for Episode #{num}:")
    print(f"   - JSON: {os.path.basename(out_file)}")
    print(f"   - Markdown: {os.path.basename(md_file)}")

    return bundle

if __name__ == "__main__":
    import sys
    from story_generator import get_or_create_story
    s_num = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 1
    story = get_or_create_story(s_num)
    bundle = build_community_bundle(story)
    print("\n--- SAMPLE POLL QUESTION ---")
    print(bundle["poll"]["question"])
    for o in bundle["poll"]["options"]:
        print(f"  {o}")
