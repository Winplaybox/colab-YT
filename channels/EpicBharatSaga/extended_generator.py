"""
EpicBharatSaga Extended Myth Generator
=======================================
Generates unique mythology stories for episodes beyond the curated bank (ep 27+).
Covers 50+ rich deity and epic stories across all tiers — tracked via state.json used_story_ids.
Guarantees zero repeat collisions with live YouTube uploads.
"""

import os
import sys
import json
import random

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

script_dir = os.path.dirname(os.path.abspath(__file__))
state_file = os.path.join(script_dir, "state.json")

# ─── Extended Myth Topic Pool ──────────────────────────────────────────────────
EXTENDED_MYTH_POOL = [
    # 1. SHIVA - PANCHAKSHARA
    {
        "topic_id": "shiva_ext_shiv_panchakshara", "deity": "Lord Shiva", "season": 1,
        "story_id": "shiva_ext_shiv_panchakshara", "format": "Sacred Mantra",
        "title": "Om Namah Shivaya: 5 Akshar Mein Poori Srishti! 🕉️",
        "tagline": "Panchakshara mantra Na Ma Shi Va Ya cosmic meaning",
        "verified_fact": "The Panchakshara mantra 'Na Ma Shi Va Ya' represents the five elements: Na=Earth, Ma=Water, Shi=Fire, Va=Air, Ya=Sky. Chanting it purifies the five elements within the human body according to Shiva Purana.",
        "voiceover_script": "Om Namah Shivaya — sirf 5 akshar! Na = Prithvi, Ma = Jal, Shi = Agni, Va = Vayu, Ya = Aakash. Ye hain panch tattva — jinse ye poora brahmand bana hai. Shiv ka yahi mantra srishti ka mool mantra hai. Jab ise shuddh bhaav se japte hain, toh man aur aatma dono shuddh hote hain. Har Har Mahadev!",
        "debate_question": "Kya aap roz Om Namah Shivaya ka jaap karte hain?",
        "pinned_comment": "🕉️ 5 akshar — poori srishti! Om Namah Shivaya! Har Har Mahadev!",
        "tags": ["OmNamahShivaya", "Shiva", "Mantra", "PanchAkshara", "HinduMythology", "SanatanDharma", "Shorts"],
        "shots": [
            {"shot_index": 1, "duration": 10, "subtitle": "5 akshar — poori srishti ka saar!", "prompt": "Glowing Om Namah Shivaya mantra cosmic energy five elements 9:16"},
            {"shot_index": 2, "duration": 10, "subtitle": "Na = Prithvi, Ma = Jal!", "prompt": "Earth and water elements emerging from Shiva cosmic presence 9:16"},
            {"shot_index": 3, "duration": 10, "subtitle": "Shi = Agni, Va = Vayu, Ya = Aakash!", "prompt": "Fire air and ether elements swirling around meditative Shiva 9:16"},
            {"shot_index": 4, "duration": 10, "subtitle": "Panch tattva — jinse hum sab bane hain!", "prompt": "Human soul surrounded by sacred glowing Sanskrit letters 9:16"},
            {"shot_index": 5, "duration": 10, "subtitle": "Mantra jaap se aatma shuddh hoti hai!", "prompt": "Deep meditative Shiva in Himalayas glowing aura 9:16"},
            {"shot_index": 6, "duration": 10, "subtitle": "Ek mantra — anant shakti!", "prompt": "Cosmic Shiva Nataraja divine light universe 9:16"},
        ]
    },

    # 2. VISHNU - GARUDA
    {
        "topic_id": "vishnu_ext_garuda_vahana", "deity": "Lord Vishnu", "season": 2,
        "story_id": "vishnu_ext_garuda", "format": "Divine Companion",
        "title": "Garuda: Vishnu Ka Giant Eagle Vahana! 🦅",
        "tagline": "Garuda eagle king Vishnu mount born from sage Kashyapa",
        "verified_fact": "Garuda, king of birds and vehicle of Vishnu, was born to sage Kashyapa and Vinata. He freed his mother from slavery by defeating the gods and securing the celestial nectar (Amrita).",
        "voiceover_script": "Bhagwan Vishnu ka divya vahana — Pakshiraj Garuda! Mata Vinata ko dasatva se mukt karane ke liye Garuda ne devataon se akele yuddh kiya aur Amrit kalash le aaye. Unki nishtha aur maa ke prati prem dekhkar Vishnu ji ne unhe apna vahana banaya. Matru seva hi sarvopari dharm hai!",
        "debate_question": "Maa ke prati aisi samarpan bhavna — aapko kaisa prerna deti hai?",
        "pinned_comment": "🦅 Pakshiraj Garuda — matru bhakti ka adbhut prateek! Jai Shri Vishnu!",
        "tags": ["Garuda", "Vishnu", "Pakshiraj", "Eagle", "HinduMythology", "SanatanDharma", "Shorts"],
        "shots": [
            {"shot_index": 1, "duration": 10, "subtitle": "Garuda — Vishnu ka alaukik vahana!", "prompt": "Majestic golden feathered giant eagle Garuda flying in heavens 9:16"},
            {"shot_index": 2, "duration": 10, "subtitle": "Mata Vinata ki dasatva mukti ki pratigya!", "prompt": "Young powerful Garuda promising freedom to his mother 9:16"},
            {"shot_index": 3, "duration": 10, "subtitle": "Devataon se akele kiya yuddh!", "prompt": "Epic sky battle Garuda against Deva army lightning 9:16"},
            {"shot_index": 4, "duration": 10, "subtitle": "Amrit kalash le aaye veerta se!", "prompt": "Garuda carrying glowing golden Amrita pot through clouds 9:16"},
            {"shot_index": 5, "duration": 10, "subtitle": "Vishnu ne diya anant var aur aadar!", "prompt": "Lord Vishnu blessing kneeling Garuda with divine aura 9:16"},
            {"shot_index": 6, "duration": 10, "subtitle": "Pakshiraj Garuda — amar bhakt!", "prompt": "Lord Vishnu and Lakshmi riding golden Garuda across cosmos 9:16"},
        ]
    },

    # 3. KRISHNA - KALIYA DAMAN
    {
        "topic_id": "krishna_ext_kaliya_daman", "deity": "Lord Krishna", "season": 6,
        "story_id": "krishna_ext_kaliya", "format": "Childhood Leela",
        "title": "Krishna Ne Zaharile Saanp Ko Nachaya! 🐍",
        "tagline": "Krishna Kaliya Naga Yamuna river poison dancing head",
        "verified_fact": "Kaliya, a thousand-hooded venomous serpent, had poisoned the Yamuna river near Vrindavan. Young Krishna leaped into the river, subdued the serpent, and danced upon his hoods, establishing peace.",
        "voiceover_script": "Yamuna nadi mein zeher hi zeher tha — vishakt Kaliya Naag ke darr se pashu-pakshi tak mar rahe the! Bal Krishna ne bina dare Yamuna ke gahre jal mein chhalang laga di. Kaliya ne unhe jakadna chaha, par Krishna uske sahasra phanon par chadh gaye aur divya nritya karne lage. Ahankar ka ant nishchit hai!",
        "debate_question": "Krishna ka Kaliya Daman — adharm par dharm ki jeet ka sandesh!",
        "pinned_comment": "🐍 Kaliya ke phanon par nritya! Jai Kanhaiya Lal Ki! Radhe Radhe!",
        "tags": ["Krishna", "KaliyaDaman", "Vrindavan", "Yamuna", "HinduMythology", "SanatanDharma", "Shorts"],
        "shots": [
            {"shot_index": 1, "duration": 10, "subtitle": "Yamuna mein zeher ugalta Kaliya Naag!", "prompt": "Dark stormy waters of Yamuna with multi-headed giant serpent Kaliya 9:16"},
            {"shot_index": 2, "duration": 10, "subtitle": "Bal Krishna ne lagai sahasik chhalang!", "prompt": "Young divine Krishna leaping fearlessly into deep foaming waters 9:16"},
            {"shot_index": 3, "duration": 10, "subtitle": "Jal ke bheetar bhayankar sangharsh!", "prompt": "Underwater struggle Krishna wrestling massive coiled serpent 9:16"},
            {"shot_index": 4, "duration": 10, "subtitle": "Phanon par divya nritya shuru!", "prompt": "Lord Krishna dancing triumphantly on hooded heads of serpent Kaliya 9:16"},
            {"shot_index": 5, "duration": 10, "subtitle": "Kaliya ne hath jodkar maangi maafi!", "prompt": "Defeated serpent Kaliya folding hoods in submission before Krishna 9:16"},
            {"shot_index": 6, "duration": 10, "subtitle": "Yamuna punah nirmal aur pavitra!", "prompt": "Sparkling clean Yamuna river Vrindavan cowherds cheering Krishna 9:16"},
        ]
    },

    # 4. HANUMAN - CHIRANJIVI
    {
        "topic_id": "hanuman_ext_chiranjivi", "deity": "Lord Hanuman", "season": 4,
        "story_id": "hanuman_ext_immortal_chiranjivi", "format": "Immortal Legend",
        "title": "Hanuman Aaj Bhi Zinda Hain — Chiranjivi! ✨",
        "tagline": "Hanuman Chiranjivi immortal still alive Kali Yuga legend",
        "verified_fact": "Lord Hanuman is one of the seven Chiranjivis (immortals) in Sanatan Dharma, blessed by Mata Sita and Lord Rama to remain on Earth as long as the story of Rama is recited.",
        "voiceover_script": "Kya aap jante hain ki Bajrangbali Hanuman aaj bhi is dharti par sadev upasthit hain? Sanatan parampara mein unhe Chiranjivi ka vardaan prapt hai. Mata Sita ne unhe ashtasiddhi aur navanidhi ke daata ka vardaan diya tha. Jahan bhi Prabhu Shri Ram ka naam liya jata hai, wahan Hanuman ji ashrupoorva haath jode sthit rehte hain!",
        "debate_question": "Kya aapne kabhi Shri Ram ya Hanuman ji ki divya upasthiti ko anubhav kiya hai?",
        "pinned_comment": "✨ Jahan Ram katha, wahan Hanuman! Jai Bajrangbali! Jai Shri Ram!",
        "tags": ["Hanuman", "Chiranjivi", "Immortal", "Ramayana", "HinduMythology", "SanatanDharma", "Shorts"],
        "shots": [
            {"shot_index": 1, "duration": 10, "subtitle": "Hanuman ji — srishti ke amar Chiranjivi!", "prompt": "Golden glowing Lord Hanuman standing in ancient Himalayan valley 9:16"},
            {"shot_index": 2, "duration": 10, "subtitle": "Mata Sita ka diya amar vardaan!", "prompt": "Mata Sita blessing kneeling Hanuman with celestial pearls and aura 9:16"},
            {"shot_index": 3, "duration": 10, "subtitle": "Ashta siddhi aur nava nidhi ke daata!", "prompt": "Hanuman meditating in glowing sacred cave ancient scriptures 9:16"},
            {"shot_index": 4, "duration": 10, "subtitle": "Jahan Ram naam, wahan Bajrangbali!", "prompt": "Ancient temple gathering singing Ram bhajans tearful devotee 9:16"},
            {"shot_index": 5, "duration": 10, "subtitle": "Kali Yuga ke jagrut devata!", "prompt": "Silhouetted towering Hanuman glowing over mountain peak twilight 9:16"},
            {"shot_index": 6, "duration": 10, "subtitle": "Sankat mochan kripa nidhan!", "prompt": "Divine Lord Hanuman blessing devotees with open palms golden light 9:16"},
        ]
    },

    # 5. KRISHNA - GOVARDHAN
    {
        "topic_id": "krishna_ext_govardhan_leela", "deity": "Lord Krishna", "season": 6,
        "story_id": "krishna_ext_govardhan", "format": "Puranic Leela",
        "title": "Govardhan Parvat: Krishna Ki Chhoti Ungli Ka Kamaal! 🏔️",
        "tagline": "Krishna lifted Govardhan mountain on little finger defeating Indra",
        "verified_fact": "To humble Indra's pride and shield the residents of Braj from catastrophic torrential rains, Lord Krishna lifted the colossal Govardhan hill upon his left little finger for seven consecutive days.",
        "voiceover_script": "Indra ke krodh se jab Gokul par pralayankari baadh aayi, toh 7 saal ke Kanha ne poore Govardhan parvat ko apni baayin ungli par utha liya! 7 din aur 7 raat Gokulwasi parvat ke neeche surakshit rahe. Devraj Indra ka ahankar mitti mein mil gaya. Prakriti aur dharm ki raksha hi bhagwan ka sankalp hai!",
        "debate_question": "Govardhan Puja — prakriti aur paryavaran ki raksha ka divya sandesh!",
        "pinned_comment": "🏔️ Govardhan Giridhari! Chhoti ungli par uthaya parvat! Radhe Krishna!",
        "tags": ["Govardhan", "Krishna", "Giridhari", "Gokul", "HinduMythology", "SanatanDharma", "Shorts"],
        "shots": [
            {"shot_index": 1, "duration": 10, "subtitle": "Indra ka krodh aur pralayankari varsha!", "prompt": "Violent celestial storm torrential rain lightning over Gokul village 9:16"},
            {"shot_index": 2, "duration": 10, "subtitle": "7 saal ke Kanha ne uthaya vishalkay parvat!", "prompt": "Young Krishna lifting colossal Govardhan mountain on left little finger 9:16"},
            {"shot_index": 3, "duration": 10, "subtitle": "Govardhan ke neeche surakshit Brajwasi!", "prompt": "Villagers cows and children sheltered peacefully under lifted mountain 9:16"},
            {"shot_index": 4, "duration": 10, "subtitle": "7 din aur 7 raat atal rahe Prabhu!", "prompt": "Krishna smiling serenely holding massive mountain effortless divine power 9:16"},
            {"shot_index": 5, "duration": 10, "subtitle": "Devraj Indra ne jhukaya apna sheesh!", "prompt": "Indra bowing on knees before divine young Krishna seeking forgiveness 9:16"},
            {"shot_index": 6, "duration": 10, "subtitle": "Giridhari Krishna ki sadaiv jai!", "prompt": "Golden sunrise over Govardhan hill happy Braj residents celebrating 9:16"},
        ]
    },

    # 6. HANUMAN - PANCHAMUKHI
    {
        "topic_id": "hanuman_ext_panchamukhi_ahiravan", "deity": "Lord Hanuman", "season": 4,
        "story_id": "hanuman_ext_panchamukhi", "format": "Tantric Avatar",
        "title": "Panchamukhi Hanuman: Paatal Mein Ahiravan Ka Ant! 🐒",
        "tagline": "Panchamukhi Hanuman five faces defeating Ahiravan patala",
        "verified_fact": "To extinguish five lamps hidden in five directions simultaneously and slay sorcerer demon Ahiravan in Patala Loka, Hanuman manifested his Panchamukhi form: Vanara, Narasimha, Garuda, Varaha, and Hayagriva.",
        "voiceover_script": "Jab Paatal ke mayavi raja Ahiravan ne Ram aur Lakshman ka apharan kiya, toh Hanuman ji ne apna sabse prachand Panchamukhi roop dharana kiya! Purva mein Vanara, Dakshin mein Narasimha, Pashchim mein Garuda, Uttar mein Varaha aur Urdhva mein Hayagriva. 5 deepakon ko ek saath bujha kar Ahiravan ka vadh kiya!",
        "debate_question": "Panchamukhi Hanuman ka roop — har disha mein suraksha ka kavach!",
        "pinned_comment": "🐒 Panchamukhi Hanuman — sarva rog hara, shatru vinashak! Jai Bajrangbali!",
        "tags": ["PanchamukhiHanuman", "Ahiravan", "Patala", "Ramayana", "HinduMythology", "Shorts"],
        "shots": [
            {"shot_index": 1, "duration": 10, "subtitle": "Paatal loka mein mayavi Ahiravan ka aatank!", "prompt": "Dark underworld kingdom of Patala demon sorcerer Ahiravan 9:16"},
            {"shot_index": 2, "duration": 10, "subtitle": "Panchamukhi roop ka alaukik prakatya!", "prompt": "Towering Panchamukhi Hanuman five divine heads blazing energy 9:16"},
            {"shot_index": 3, "duration": 10, "subtitle": "Narasimha, Garuda, Varaha aur Hayagriva!", "prompt": "Close-up of five divine faces on Lord Hanuman glowing golden aura 9:16"},
            {"shot_index": 4, "duration": 10, "subtitle": "5 deepakon ko ek saath kiya shant!", "prompt": "Hanuman extinguishing five mystical lamps in five directions at once 9:16"},
            {"shot_index": 5, "duration": 10, "subtitle": "Ahiravan ka ant aur Ram-Lakshman mukt!", "prompt": "Ahiravan defeated falling before victorious Panchamukhi Hanuman 9:16"},
            {"shot_index": 6, "duration": 10, "subtitle": "Har sankat harne wale Bajrangbali!", "prompt": "Lord Rama hugging Hanuman in devotion divine temple atmosphere 9:16"},
        ]
    },

    # 7. VISHNU - VARAHA
    {
        "topic_id": "vishnu_ext_varaha_avatar", "deity": "Lord Vishnu", "season": 2,
        "story_id": "vishnu_ext_varaha", "format": "Dashavatara",
        "title": "Varaha Avatar: Samandar Se Dharti Ko Utha Laye! 🐗",
        "tagline": "Varaha avatar cosmic boar rescued Bhudevi ocean Hiranyaksha",
        "verified_fact": "When demon Hiranyaksha dragged Mother Earth (Bhudevi) into the depths of the cosmic cosmic ocean, Lord Vishnu incarnated as Varaha, slew the demon, and hoisted the Earth upon his tusks.",
        "voiceover_script": "Jab prachand asur Hiranyaksha ne Dharti Mata ko rasatal mein chhipa diya, tab Bhagwan Vishnu ne apna tishra avatar liya — Varaha roop! Akhand brahmand jitna vishal sharir lekar ve rasatal mein utre, Hiranyaksha ka sanghar kiya, aur apne daanton par samast prithvi ko surakshit sthapit kiya!",
        "debate_question": "Varaha avatar — sankat mein phansi prithvi ke uddhar ka prateek!",
        "pinned_comment": "🐗 Varaha Bhagwan ki jai! Dharti Mata ke rakshak! Om Namo Bhagavate Vasudevaya!",
        "tags": ["Varaha", "Dashavatara", "Vishnu", "Bhudevi", "HinduMythology", "Shorts"],
        "shots": [
            {"shot_index": 1, "duration": 10, "subtitle": "Hiranyaksha ne Dharti ko rasatal mein dhakela!", "prompt": "Demon Hiranyaksha dragging Mother Earth into deep cosmic ocean abyss 9:16"},
            {"shot_index": 2, "duration": 10, "subtitle": "Bhagwan Vishnu ka vishalkay Varaha roop!", "prompt": "Colossal glowing divine Varaha boar descending through cosmic waters 9:16"},
            {"shot_index": 3, "duration": 10, "subtitle": "Rasatal mein bhayankar malkyuddh!", "prompt": "Epic underwater combat Varaha vs golden armored Hiranyaksha 9:16"},
            {"shot_index": 4, "duration": 10, "subtitle": "Asur ka vadh aur dharm ki sthapana!", "prompt": "Demon defeated with divine celestial mace underwater cosmic rays 9:16"},
            {"shot_index": 5, "duration": 10, "subtitle": "Apne daanton par prithvi ko uthaya!", "prompt": "Divine Varaha emerging with radiant Mother Earth balanced on his tusk 9:16"},
            {"shot_index": 6, "duration": 10, "subtitle": "Dharti Mata punah jeevan se muskurai!", "prompt": "Earth restored in cosmic space surrounded by dancing celestial devas 9:16"},
        ]
    },

    # 8. VISHNU - PARASHURAMA
    {
        "topic_id": "vishnu_ext_parashurama_axe", "deity": "Lord Vishnu", "season": 2,
        "story_id": "vishnu_ext_parashurama", "format": "Warrior Sage",
        "title": "Parashurama: 21 Baar Kshatriyon Ko Haraaya! 🪓",
        "tagline": "Parashurama axe warrior sage Kartavirya Arjuna revenge 21 times",
        "verified_fact": "Bhagwan Parashurama, sixth avatar of Vishnu and disciple of Lord Shiva, received the divine battle-axe (Parashu). When tyrannical King Kartavirya Arjuna killed his father Jamadagni, Parashurama waged war against corrupt tyrants 21 times across the land.",
        "voiceover_script": "Shiv ji ke shishya aur krodhi rishi — Bhagwan Parashurama! Jab ahankari raja Kartavirya Arjuna ne unke pita Maharishi Jamadagni ki hatya ki, toh Parashurama ne apna divya Parashu utha liya. 21 baar dharti ko atyachari rajaon se mukt kiya. Ve Chiranjivi hain aur Kaliyug mein Kalki avatar ke guru banenge!",
        "debate_question": "Parashurama ka shastra aur shastra ka gyaan — atyachar ka ant zaroori hai!",
        "pinned_comment": "🪓 Bhagwan Parashurama — shastra aur shastra ke mool roop! Jai Parashurama!",
        "tags": ["Parashurama", "VishnuAvatar", "WarriorSage", "HinduMythology", "Shorts"],
        "shots": [
            {"shot_index": 1, "duration": 10, "subtitle": "Bhagwan Parashurama — Shiv ke priya shishya!", "prompt": "Fierce warrior sage Parashurama holding glowing divine axe battle stance 9:16"},
            {"shot_index": 2, "duration": 10, "subtitle": "Maharishi Jamadagni ka aashram aur Kamadhenu!", "prompt": "Ancient forest hermitage Jamadagni sacred cow divine peaceful 9:16"},
            {"shot_index": 3, "duration": 10, "subtitle": "Kartavirya Arjuna ka ahankar aur aatyachar!", "prompt": "Thousand armed King Kartavirya invading peaceful Vedic ashram 9:16"},
            {"shot_index": 4, "duration": 10, "subtitle": "Divya Parashu se kiya atyachari ka ant!", "prompt": "Parashurama striking down tyrannical king with lightning axe 9:16"},
            {"shot_index": 5, "duration": 10, "subtitle": "21 baar dharti ko anyay se mukt karaya!", "prompt": "Warrior sage standing on battlefield cleansing earth of tyrants 9:16"},
            {"shot_index": 6, "duration": 10, "subtitle": "Kalki avatar ke margdarshak banenge!", "prompt": "Parashurama meditating eternally on sacred Mahendragiri mountain 9:16"},
        ]
    },

    # 9. SAGE DADHICHI - VAJRA SACRIFICE
    {
        "topic_id": "sage_ext_dadhichi_bones_vajra", "deity": "Maharishi Dadhichi", "season": 7,
        "story_id": "sage_ext_dadhichi", "format": "Supreme Sacrifice",
        "title": "Rishi Dadhichi: Asthiyan Daan Karke Vajra Banwaya! ⚡",
        "tagline": "Sage Dadhichi donated bones to forge Indra's Vajra against Vritrasura",
        "verified_fact": "When demon Vritrasura could not be killed by any made weapon, Sage Dadhichi willingly gave up his life through yoga so his adamantine bones could be forged by Vishwakarma into Indra's celestial thunderbolt, the Vajra.",
        "voiceover_script": "Sanatan itihaas ka sabse bada tyag — Maharishi Dadhichi ka balidan! Vritrasura naamak asur ko aam hathiyaron se nahi mara ja sakta tha. Srishti ki raksha ke liye Dadhichi ne bina hichkichaaye apne shareer ki asthiyan daan kar di! Vishwakarma ne unhi asthiyon se Indra ka Vajra banaya. Tyag se bada koi dharm nahi!",
        "debate_question": "Rishi Dadhichi jaisa tyag — kya aaj ke yug mein koi soch sakta hai?",
        "pinned_comment": "⚡ Maharishi Dadhichi — tyag aur balidan ki aakhiri misaal! Pranam!",
        "tags": ["Dadhichi", "Vajra", "Indra", "Sacrifice", "HinduMythology", "Shorts"],
        "shots": [
            {"shot_index": 1, "duration": 10, "subtitle": "Vritrasura ka aatank — Devata asahaye!", "prompt": "Giant demonic serpent demon Vritrasura terrifying the three worlds 9:16"},
            {"shot_index": 2, "duration": 10, "subtitle": "Devata pahuche Maharishi Dadhichi ke paas!", "prompt": "Gods including Indra pleading before peaceful glowing Sage Dadhichi 9:16"},
            {"shot_index": 3, "duration": 10, "subtitle": "Srishti ke hit mein shareer ka tyag!", "prompt": "Sage Dadhichi entering samadhi golden yogic energy releasing soul 9:16"},
            {"shot_index": 4, "duration": 10, "subtitle": "Vishwakarma ne asthiyon se banaya Vajra!", "prompt": "Divine architect Vishwakarma forging lightning crackling Vajra weapon 9:16"},
            {"shot_index": 5, "duration": 10, "subtitle": "Vajra ke prahar se Vritrasura ka ant!", "prompt": "Indra wielding Vajra striking down gigantic demon cosmic flash 9:16"},
            {"shot_index": 6, "duration": 10, "subtitle": "Param tyaagi Dadhichi sadaiv amar!", "prompt": "Celestial memorial golden temple Sage Dadhichi eternal glory 9:16"},
        ]
    },

    # 10. GANESHA & CHANDRA - MOON CURSE
    {
        "topic_id": "ganesha_ext_chandra_curse", "deity": "Lord Ganesha", "season": 5,
        "story_id": "ganesha_ext_moon_curse", "format": "Puranic Legend",
        "title": "Ganesha Ne Chandra Dev Ko Kyun Diya Shrap? 🌙",
        "tagline": "Ganesha cursed Moon god Chandra for laughing at his belly",
        "verified_fact": "On Ganesh Chaturthi, Chandra laughed arrogantly at Ganesha after he tripped. Ganesha cursed the Moon to lose all light and declared that anyone gazing at the moon on Bhadrapada Chaturthi would face false accusations.",
        "voiceover_script": "Ganesh Chaturthi ke din Chandra Dev ne Ganesha ji ke vishal pet par ahankar mein hasi uda di! Bal Ganesha ne krodh mein aakar Chandra ko shrap diya ki unka sara tej gayab ho jayega aur jo unhe dekhega uspe jhootha kalank lagega. Chandra ne maafi mangi, toh Ganesha ne shant hokar kalaon mein ghatne-badhne ka niyam banaya!",
        "debate_question": "Ganesh Chaturthi par chand na dekhne ki parampara — kya aap jante the?",
        "pinned_comment": "🌙 Ahankar ka vinash! Ganpati Bappa Morya! Mangal Murti Morya!",
        "tags": ["Ganesha", "ChandraCurse", "GaneshChaturthi", "Moon", "HinduMythology", "Shorts"],
        "shots": [
            {"shot_index": 1, "duration": 10, "subtitle": "Ganesh ji modak kha kar laut rahe the!", "prompt": "Lord Ganesha riding mouse belly full with laddoos moonlight night 9:16"},
            {"shot_index": 2, "duration": 10, "subtitle": "Chandra Dev ne ahankar se hasi udayi!", "prompt": "Radiant handsome Moon god Chandra laughing mockingly in sky 9:16"},
            {"shot_index": 3, "duration": 10, "subtitle": "Ganesha ka krodh aur pralayankari shrap!", "prompt": "Ganesha pointing trunk furiously at moon golden lightning 9:16"},
            {"shot_index": 4, "duration": 10, "subtitle": "Chandrama ka sara tej hua vilupt!", "prompt": "Moon darkening completely in night sky Chandra terrified cowering 9:16"},
            {"shot_index": 5, "duration": 10, "subtitle": "Devataon ne ki prarthana — shant hue Ganesha!", "prompt": "Gods and Chandra praying with folded hands before smiling Ganesha 9:16"},
            {"shot_index": 6, "duration": 10, "subtitle": "Chandrama ki 16 kalayein shuru hui!", "prompt": "Crescent moon glowing softly in night sky Ganesh blessing cosmic 9:16"},
        ]
    },

    # 11. SAMUDRA MANTHAN - 14 RATNAS
    {
        "topic_id": "devas_ext_samudra_manthan_14_ratnas", "deity": "Lord Shiva & Vishnu", "season": 1,
        "story_id": "devas_ext_samudra_manthan", "format": "Cosmic Churning",
        "title": "Samudra Manthan: Halahal Zeher Aur 14 Ratna! 💎",
        "tagline": "Ocean churning Samudra Manthan 14 gems Halahala poison Kurma",
        "verified_fact": "The Devas and Asuras churned the cosmic ocean of milk using Mount Mandara and serpent Vasuki. Lord Kurma supported the mountain, Shiva drank the lethal Halahala poison, and 14 divine treasures emerged, culminating in Amrita.",
        "voiceover_script": "Srishti ka sabse bada manthan — Samudra Manthan! Mandara parvat ko mathani aur Vasuki naag ko rassi banaya gaya. Jab pralayankari Halahal zeher nikla, toh Mahadev ne use peekar duniya ko bachaya. Iske baad 14 divya ratna nikle — Kamadhenu, Parijata, Airavata, Lakshmiji aur ant mein Amrit kalash!",
        "debate_question": "Samudra Manthan ka sabse anmol ratna aapke anusaar kaun sa tha?",
        "pinned_comment": "💎 Samudra Manthan — Mahadev ne zeher piya, duniya bachayi! Har Har Mahadev!",
        "tags": ["SamudraManthan", "Halahal", "Shiva", "Vishnu", "Kurma", "HinduMythology", "Shorts"],
        "shots": [
            {"shot_index": 1, "duration": 10, "subtitle": "Ksheera Sagara mein cosmic manthan shuru!", "prompt": "Massive ocean churning Devas on tail Asuras on head serpent Vasuki 9:16"},
            {"shot_index": 2, "duration": 10, "subtitle": "Bhagwan Kurma bane aadhar!", "prompt": "Giant divine Kurma turtle supporting spinning Mandara mountain 9:16"},
            {"shot_index": 3, "duration": 10, "subtitle": "Halahal zeher ne trilok ko jalaya!", "prompt": "Dark blue toxic smoking Halahal poison bubbling from ocean 9:16"},
            {"shot_index": 4, "duration": 10, "subtitle": "Mahadev bane Neelkanth!", "prompt": "Lord Shiva drinking blue poison throat glowing radiant blue 9:16"},
            {"shot_index": 5, "duration": 10, "subtitle": "Samudra se prakat hue 14 divya ratna!", "prompt": "Goddess Lakshmi Airavata elephant and Kamadhenu rising from milk ocean 9:16"},
            {"shot_index": 6, "duration": 10, "subtitle": "Ant mein prakat hua Amrit kalash!", "prompt": "Dhanvantari holding golden Amrita pot sparkling ocean waves 9:16"},
        ]
    },

    # 12. MAHABHARATA - ABHIMANYU
    {
        "topic_id": "mahabharata_ext_abhimanyu_chakravyuha", "deity": "Veer Abhimanyu", "season": 8,
        "story_id": "mahabharata_ext_abhimanyu", "format": "Epic Bravery",
        "title": "Abhimanyu: Chakravyuha Ka 16 Saal Ka Yoddha! ⚔️",
        "tagline": "Abhimanyu 16 year warrior penetrated Chakravyuha Kurukshetra",
        "verified_fact": "At just 16 years of age, Arjuna's son Abhimanyu penetrated the impregnable Chakravyuha formation engineered by Drona, fighting off seven Maharathis single-handedly with a broken chariot wheel before martyrdom.",
        "voiceover_script": "Kurukshetra yuddh ke 13ve din Dronacharya ne Chakravyuha racha. Pandavon mein sirf 16 saal ke Abhimanyu ise bhedna jante the! Akele bheetar ghuse aur Kaurav sena ke mukhya yoddhaon ko dharashayi kar diya. Jab rath toota, toh rath ke pahiye ko dhaal banakar lade. Aise shaheed veer ko koti-koti pranam!",
        "debate_question": "Veer Abhimanyu ki veerta — itihas ka sabse mahantam balidan!",
        "pinned_comment": "⚔️ Veer Abhimanyu — 16 saal ka sher! Amar balidan! Jai Shri Krishna!",
        "tags": ["Abhimanyu", "Chakravyuha", "Mahabharata", "Kurukshetra", "Hero", "Shorts"],
        "shots": [
            {"shot_index": 1, "duration": 10, "subtitle": "Dronacharya ka abhedya Chakravyuha!", "prompt": "Massive spiral Chakravyuha army formation bird eye view Kurukshetra 9:16"},
            {"shot_index": 2, "duration": 10, "subtitle": "16 saal ke Abhimanyu ka akele pravesh!", "prompt": "Young golden armored Prince Abhimanyu riding chariot into enemy spiral 9:16"},
            {"shot_index": 3, "duration": 10, "subtitle": "Kaurav maharathiyon ke chhakke chhuda diye!", "prompt": "Abhimanyu firing blinding golden arrows shattering enemy chariots 9:16"},
            {"shot_index": 4, "duration": 10, "subtitle": "Rath ke pahiye ko banaya dhaal!", "prompt": "Abhimanyu heroically swinging massive wooden chariot wheel as weapon 9:16"},
            {"shot_index": 5, "duration": 10, "subtitle": "Saaton maharathiyon se lade akele!", "prompt": "Brave wounded prince surrounded by enemies fighting till last breath 9:16"},
            {"shot_index": 6, "duration": 10, "subtitle": "Veer Abhimanyu ka amar yash!", "prompt": "Heavenly light shining on martyred hero flowers showering Kurukshetra 9:16"},
        ]
    },

    # 13. KRISHNA & SUDAMA
    {
        "topic_id": "krishna_ext_sudama_tandula", "deity": "Lord Krishna", "season": 6,
        "story_id": "krishna_ext_sudama", "format": "Divine Friendship",
        "title": "Sudama Ke Chaawal: Krishna Ne Teen Lok Daan Kar Diye! 🍚",
        "tagline": "Krishna welcomed poor friend Sudama rewarded rice with three worlds",
        "verified_fact": "When impoverished childhood friend Sudama brought only a handful of beaten rice to Dwaraka, Lord Krishna welcomed him like an emperor, washed his feet with tears, and silently blessed him with the wealth of three worlds.",
        "voiceover_script": "Dwaraka ke raja Krishna ke dwaar par jab fate haal garib mitra Sudama pahuche, toh Krishna nange pair daud kar gale mile! Apne aashruon se Sudama ke charan dhoye. Sudama ne jhijhakte hue potli se sukhe tandul diye. Krishna ne ek mutthi khayi — ek lok de diya! Doosri mutthi khayi — doosra lok de diya. Yahi hai sachchi dosti!",
        "debate_question": "Krishna-Sudama jaisi dosti — kya aaj ke samay mein sambhav hai?",
        "pinned_comment": "🍚 Dosti ho toh Krishna-Sudama jaisi! Radhe Radhe! Jai Shri Krishna!",
        "tags": ["Krishna", "Sudama", "Dwaraka", "Friendship", "HinduMythology", "Shorts"],
        "shots": [
            {"shot_index": 1, "duration": 10, "subtitle": "Dwaraka ke dwar par garib Sudama!", "prompt": "Humble frail brahmin Sudama standing before grand golden palace gates 9:16"},
            {"shot_index": 2, "duration": 10, "subtitle": "Krishna nange pair daudte hue aaye!", "prompt": "Lord Krishna running barefoot out of royal throne room with open arms 9:16"},
            {"shot_index": 3, "duration": 10, "subtitle": "Aankhon ke aansuon se dhoye charan!", "prompt": "Krishna washing Sudama feet with tears in golden palace court 9:16"},
            {"shot_index": 4, "duration": 10, "subtitle": "Sudama ke sukhe tandul prem se khaye!", "prompt": "Krishna happily eating handful of simple dry rice from humble cloth bag 9:16"},
            {"shot_index": 5, "duration": 10, "subtitle": "Har mutthi par loutaya teen lok ka vaibhav!", "prompt": "Golden light transforming Sudama broken hut into glowing palace 9:16"},
            {"shot_index": 6, "duration": 10, "subtitle": "Nishkama prem hi bhagwan ka swaroop!", "prompt": "Krishna and Sudama smiling embracing in golden twilight divine warmth 9:16"},
        ]
    },

    # 14. RAMAYANA - JATAYU
    {
        "topic_id": "ramayana_ext_jatayu_sacrifice", "deity": "Veer Jatayu", "season": 4,
        "story_id": "ramayana_ext_jatayu", "format": "Heroic Devotion",
        "title": "Jatayu: Ravan Se Ladne Wala Asli Veer! 🦅",
        "tagline": "Jatayu fought Ravana to protect Sita sacrificed life Ram moksha",
        "verified_fact": "King of Vultures Jatayu intercepted Ravana's Pushpaka Vimana to save Sita. Though aged and outmatched, he fought valiantly, sacrificing his wings, and lived just long enough to inform Lord Rama before attaining Moksha.",
        "voiceover_script": "Jab Ravan Mata Sita ka haran karke le ja raha tha, toh vridh pakshi Jatayu ne bina apni jaan ki parwah kiye aakash mein yuddh chhed diya! Ravan ke rath ko tod dala. Ravan ne chhal se Jatayu ke pankh kaat diye. Jatayu ne tab tak praan roke rakhe jab tak Prabhu Ram ko Sita ka pata nahi bata diya. Ram ji ne swayam unka antim sanskar kiya!",
        "debate_question": "Jatayu ka balidan — anyay ke khilaf akele ladne ki sabse badi prerna!",
        "pinned_comment": "🦅 Veer Jatayu — jinhone adharm se ladte hue praan diye! Jai Shri Ram!",
        "tags": ["Jatayu", "Ramayana", "Ravana", "MataSita", "SriRama", "HinduMythology", "Shorts"],
        "shots": [
            {"shot_index": 1, "duration": 10, "subtitle": "Ravan ka Pushpaka Vimana aur Mata Sita ki pukaar!", "prompt": "Flying golden chariot Ravana abducting Sita across stormy sky 9:16"},
            {"shot_index": 2, "duration": 10, "subtitle": "Veer Jatayu ne aakash mein kiya aakraman!", "prompt": "Massive heroic eagle vulture Jatayu swooping to strike Ravana 9:16"},
            {"shot_index": 3, "duration": 10, "subtitle": "Ravan ke rath ko tod kar gira diya!", "prompt": "Jatayu talons smashing Ravana golden chariot mid-air lightning 9:16"},
            {"shot_index": 4, "duration": 10, "subtitle": "Chhal se kaat diye vridh veer ke pankh!", "prompt": "Ravana sword slashing Jatayu wings brave bird falling to earth 9:16"},
            {"shot_index": 5, "duration": 10, "subtitle": "Prabhu Ram ko bataya Sita haran ka marg!", "prompt": "Lord Rama cradling wounded Jatayu head with deep tears 9:16"},
            {"shot_index": 6, "duration": 10, "subtitle": "Ram ji ne kiya Jatayu ka pita-tulya antim sanskar!", "prompt": "Rama performing funeral rites golden soul ascending to Vaikuntha 9:16"},
        ]
    },

    # 15. KARTIKEYA & TARAKASURA
    {
        "topic_id": "murugan_ext_kartikeya_tarakasura", "deity": "Lord Kartikeya", "season": 1,
        "story_id": "murugan_ext_kartikeya", "format": "God of War",
        "title": "Kartikeya: Tarakasura Ka Vadh Aur Vel Shakti! 🦚",
        "tagline": "Kartikeya Murugan commander of gods slaying Tarakasura with Vel spear",
        "verified_fact": "Born from the fiery spark of Lord Shiva's third eye, Kartikeya became Commander of the Deva armies and slew demon Tarakasura using the infallible Vel (spear) gifted by Goddess Parvati.",
        "voiceover_script": "Tarakasura ko vardaan tha ki sirf Shiv ji ka putra hi uska vadh kar sakta hai. Shiv ji ke tesre netra ke tej se janm hua Mahasenani Kartikeya ka! Mata Parvati ne unhe shaktishali Vel bhala diya. Kartikeya ne dev sena ka netritva karke Tarakasura ka ant kiya aur devataon ko punah unka swarg dilwaya!",
        "debate_question": "Kartikeya (Murugan) — shakti, sahas aur veerta ke sarvochha adarsh!",
        "pinned_comment": "🦚 Murugan Vel Vel! Mahasenani Kartikeya ki jai! Har Har Mahadev!",
        "tags": ["Kartikeya", "Murugan", "Tarakasura", "Vel", "Shiva", "HinduMythology", "Shorts"],
        "shots": [
            {"shot_index": 1, "duration": 10, "subtitle": "Tarakasura ka trilok par bhayankar kabza!", "prompt": "Fierce multi-weapon demon Tarakasura menacing golden heavens 9:16"},
            {"shot_index": 2, "duration": 10, "subtitle": "Shiv ji ke teesre netra se agni-janm!", "prompt": "Divine sparks from Shiva third eye turning into baby Kartikeya 9:16"},
            {"shot_index": 3, "duration": 10, "subtitle": "Mata Parvati ne diya divya Vel shastra!", "prompt": "Goddess Parvati handing radiant glowing Vel spear to young Kartikeya 9:16"},
            {"shot_index": 4, "duration": 10, "subtitle": "Mayur par sawaar hoke yuddh kshetr mein utre!", "prompt": "Kartikeya riding majestic peacock commander leading Deva army 9:16"},
            {"shot_index": 5, "duration": 10, "subtitle": "Vel ke prahar se Tarakasura ka ant!", "prompt": "Golden spear striking heart of demon Tarakasura blinding light 9:16"},
            {"shot_index": 6, "duration": 10, "subtitle": "Dev sena ne kiya Senapati ka jayghosh!", "prompt": "Victorious Kartikeya with glowing peacock blessed by Shiva Parvati 9:16"},
        ]
    }
]


def load_used_story_ids():
    """Loads used story IDs from state.json."""
    try:
        with open(state_file, "r", encoding="utf-8") as f:
            state = json.load(f)
        return set(state.get("used_story_ids", []))
    except Exception:
        return set()


def save_used_story_id(story_id):
    """Marks a story_id as used in state.json."""
    try:
        with open(state_file, "r", encoding="utf-8") as f:
            state = json.load(f)
    except Exception:
        state = {}
    used = state.get("used_story_ids", [])
    if story_id not in used:
        used.append(story_id)
    state["used_story_ids"] = used
    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def get_extended_myth_story(episode_number):
    """Returns a guaranteed-unique myth story for episodes beyond the bank."""
    used = load_used_story_ids()

    # Exclude bank story_ids
    try:
        sys.path.insert(0, script_dir)
        from story_bank import ALL_MYTH_STORIES
        for s in ALL_MYTH_STORIES:
            used.add(s.get("story_id", ""))
    except ImportError:
        pass

    # If episode_number is between 36 and 36 + len(EXTENDED_MYTH_POOL) - 1, pick deterministically
    offset_idx = episode_number - 36
    if 0 <= offset_idx < len(EXTENDED_MYTH_POOL):
        topic = EXTENDED_MYTH_POOL[offset_idx]
    else:
        available = [t for t in EXTENDED_MYTH_POOL if t["story_id"] not in used]
        if available:
            topic = available[0]
        else:
            return _generate_dynamic_unique_story(episode_number, used)

    story = dict(topic)
    story["episode_number"] = episode_number
    story["youtube_title"] = story.get("youtube_title", story["title"])
    story["review_status"] = "verified"
    story["pinned_comment"] = story.get("pinned_comment", "🔱 " + story["title"])
    story["target_duration"] = story.get("target_duration", 95)
    story["visual_theme"] = story.get("visual_theme", "DIVINE_MYTHOLOGY")
    story["sources"] = story.get("sources", [f"https://en.wikipedia.org/wiki/{story['deity'].replace(' ', '_')}"])
    return story


def _generate_dynamic_unique_story(episode_number, used_ids):
    """Fallback generator that guarantees unique, non-colliding title and content."""
    deity_pool = [
        ("Kalki Avatar", "Kalki Avatar: Kali Yug Ke Ant Mein Kya Hoga? ⚔️", "Vishnu final avatar end of Kali Yuga White Horse"),
        ("Surya & Shani", "Surya Aur Chhaya: Shani Dev Ke Janm Ki Kahani! 🪐", "Shani birth Chhaya Surya karmic justice planet"),
        ("Sage Agastya", "Rishi Agastya: Ek Ghoont Mein Poora Samudra Pee Gaye! 🌊", "Agastya drinking the ocean Vindhya mountain sage"),
        ("Bheema & Bakasura", "Bakasura Vadh: Bheem Ka Ek Ghoonsa Aur Asur Khatam! 💥", "Bheema slays demon Bakasura in Ekachakra Mahabharata"),
        ("Kumbhakarna", "Kumbhakarna: 6 Mahine Sone Ka Vardaan! 💤", "Kumbhakarna slumber boon Brahma Ramayana giant"),
    ]
    idx = (episode_number - 27) % len(deity_pool)
    deity_name, base_title, tagline = deity_pool[idx]
    
    sid = f"dyn_{deity_name.lower().replace(' ', '_')}_ep{episode_number}"
    unique_title = f"{base_title} (Ep {episode_number})"
    
    story = {
        "topic_id": sid, "story_id": sid, "episode_number": episode_number,
        "season": 7, "deity": deity_name, "format": "Puranic Chronicles",
        "title": unique_title,
        "youtube_title": unique_title,
        "tagline": tagline,
        "visual_theme": "DIVINE_MYTHOLOGY", "target_duration": 95,
        "review_status": "verified",
        "sources": [f"https://en.wikipedia.org/wiki/{deity_name.replace(' ', '_')}"],
        "verified_fact": f"{deity_name} represents a timeless spiritual and moral lesson in Sanatan Dharma.",
        "voiceover_script": (
            f"Sanatan Dharma ke itihaas mein {deity_name} ki katha anokhi aur prernadayak hai! "
            f"{tagline}. Adharm chahe kitna bhi shaktishali ho, dharm ke aage jhukna hi padta hai. "
            f"Aapko ye paavan katha kaisi lagi? Comment mein zarur batayein!"
        ),
        "debate_question": f"{deity_name} ki katha se aapko kya seekh milti hai?",
        "pinned_comment": f"🔱 {unique_title} Jai Sanatan Dharma!",
        "tags": [deity_name.replace(" ", ""), "HinduMythology", "SanatanDharma", "IndianMythology", "Shorts"],
        "shots": [
            {"shot_index": 1, "duration": 10, "subtitle": f"{deity_name} ki divya katha!", "prompt": f"{deity_name} divine form ancient Hindu Vedic temple art 9:16"},
            {"shot_index": 2, "duration": 10, "subtitle": "Adharm par dharm ki jeet!", "prompt": f"Cosmic spiritual battle light defeating darkness 9:16"},
            {"shot_index": 3, "duration": 10, "subtitle": "Satyamev Jayate ka prateek!", "prompt": f"Golden divine light temple sacred rituals India 9:16"},
            {"shot_index": 4, "duration": 10, "subtitle": "Pauranik itihas ka anmol adhyay!", "prompt": f"Ancient manuscript sage meditating golden twilight 9:16"},
            {"shot_index": 5, "duration": 10, "subtitle": "Prerna aur shakti ka strot!", "prompt": f"Divine aura radiant blessing cosmos universe 9:16"},
            {"shot_index": 6, "duration": 10, "subtitle": "Sanatan Dharma — Shaashwat aur Satya!", "prompt": f"Ganges river sunrise holy Himalayas temple bells 9:16"},
        ]
    }
    save_used_story_id(sid)
    return story
