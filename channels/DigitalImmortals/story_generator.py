"""
DigitalImmortals Canonical Story & Script Generation Engine
===========================================================
Source: Srimad Valmiki Ramayanam (Prof. Y.V. Chalapathi, TTD)
Format: 100% Shuddh Sanskritized Hindi (शुद्ध देवनागरी हिंदी)
Generates scene-by-scene narration, audio, and visual prompts for each episode.
"""

import os
import sys
import json
import asyncio

script_dir = os.path.dirname(os.path.abspath(__file__))
episodes_dir = os.path.join(script_dir, "episodes")
os.makedirs(episodes_dir, exist_ok=True)

# Episode 01: Canonical Master Story Data
EPISODE_01_DATA = {
    "episode_number": 1,
    "kanda": "बालकाण्ड (Bala Kanda)",
    "title_hindi": "क्रौंच वध और आदि-श्लोक: रामायण की रहस्यमयी शुरुआत",
    "title_youtube": "एक पक्षी की मौत से कैसे रचा गया पूरा इतिहास? 🏹 (Ep 01)",
    "description_hook": "क्या रामायण का पहला श्लोक वास्तव में एक शिकारी को दिया गया भयंकर शाप था? वाल्मीकि रामायण की इस ऐतिहासिक और प्रामाणिक शृंखला के पहले एपिसोड में जानिए वह सत्य, जो सदियों से इतिहास के पन्नों में दबा रहा।",
    "scenes": [
        {
            "scene_id": 1,
            "title": "प्रलयंकारी प्रस्तावना (The Ultimate Hook)",
            "visual_prompt": "Hyper-realistic 8K cinematic, extreme close-up of a barbed bronze arrow severing misty air and piercing a majestic male Krauncha bird, twilight ancient Indian forest, blood droplets turning into glowing golden Sanskrit letters mid-air, 45Hz sub-bass atmosphere, volumetric lighting, Octane render.",
            "narration": "क्या आप जानते हैं कि मानव इतिहास का सबसे महान महाकाव्य किसी उत्सव या राजसी आदेश से नहीं... बल्कि एक तड़पते हुए पक्षी के खून और एक शांत ऋषि के भयंकर शाप से जन्मा था? यह कथा उस आदि-काव्य की है, जिसने सम्पूर्ण ब्रह्मांड को धर्म की मर्यादा सिखाई।",
            "music_cue": "dark_suspense_drone"
        },
        {
            "scene_id": 2,
            "title": "देवर्षि नारद का दिव्य आगमन",
            "visual_prompt": "Cinematic wide shot 8K, celestial sage Narada descending from glowing golden clouds into a lush green Vedic hermitage, carrying a divine golden Mahati Veena, serene river Tamasa flowing in background, ancient banyan trees, soft radiant god rays, hyper-detailed photorealistic.",
            "narration": "एक दिन महर्षि वाल्मीकि के तपोवन में देवर्षि नारद का शुभागमन हुआ। वाल्मीकि जी ने हाथ जोड़कर पूछा— 'हे देवर्षि! क्या इस संपूर्ण मृत्युलोक में कोई ऐसा पुरुष है जो सर्वगुण संपन्न, सत्यवादी, पराक्रमी, धर्मज्ञ, जितेंद्रिय और समस्त जीवों का कल्याणकारी हो?' नारद जी मुस्कुराए और बोले— 'हे मुनि! दुर्लभ हैं ऐसे गुण, किंतु इक्ष्वाकु वंश में जन्मे राजा दशरथ के ज्येष्ठ पुत्र श्री राम में ये समस्त सोलह दिव्य गुण विद्यमान हैं।'",
            "music_cue": "celestial_harp_strings"
        },
        {
            "scene_id": 3,
            "title": "तमसा नदी का पावन तट और निषाद का क्रूर बाण",
            "visual_prompt": "8K landscape shot, crystalline holy river Tamasa reflecting evening twilight sky, two beautiful sarus crane birds mating and dancing joyfully on the riverbank, dense ancient jungle, sudden flash of a hunter's bronze arrow, cinematic tension, photorealistic hyper-detail.",
            "narration": "नारद जी के प्रस्थान के उपरांत, महर्षि वाल्मीकि अपने शिष्य भारद्वाज के साथ तमसा नदी के तट पर स्नान करने पहुंचे। वहां एक मनोहर दृश्य था— दो क्रौंच पक्षी आकाश में प्रेमपूर्वक किलोल कर रहे थे। तभी एक दुष्ट निषाद शिकारी ने बिना किसी दया के अपने धनुष से बाण चला दिया। बाण लगते ही नर क्रौंच रक्त से लथपथ होकर पृथ्वी पर गिर पड़ा और मादा क्रौंच अपने जीवनसाथी के वियोग में चीत्कार कर उठी।",
            "music_cue": "tragic_sorrow_violin"
        },
        {
            "scene_id": 4,
            "title": "आदि-श्लोक का प्रकटीकरण (मा निषाद...)",
            "visual_prompt": "Cinematic 8K portrait shot of Maharishi Valmiki standing in river water, eyes blazing with divine sorrow and righteous anger, tears on cheeks, glowing golden Sanskrit typography hovering in the air: मा निषाद प्रतिष्ठां त्वमगमः शाश्वतीः समाः, epic mythical aesthetic, intense atmospheric lighting.",
            "narration": "उस निर्दोष पक्षी की मृत्यु देखकर महर्षि वाल्मीकि का हृदय अपार करुणा और क्षोभ से भर उठा। उनके मुख से अनायास ही यह प्रथम आदि-श्लोक शाप बनकर फूट पड़ा— 'मा निषाद प्रतिष्ठां त्वमगमः शाश्वतीः समाः। यत्क्रौञ्चमिथुनादेकमवधीः काममोहितम्॥' अर्थात— 'हे दुष्ट शिकारी! तूने काम-मोहित निर्दोष क्रौंच जोड़े में से एक का वध किया है, इसलिए तुझे संसार में कभी शांति और प्रतिष्ठा प्राप्त नहीं होगी!'",
            "music_cue": "epic_mantra_climax"
        },
        {
            "scene_id": 5,
            "title": "परमपिता ब्रह्मा का साक्षात प्रकटीकरण",
            "visual_prompt": "Cinematic grand 8K, Lord Brahma manifesting in golden cosmic luminescence, four radiant serene faces, holding Vedas, lotus in hand, divine white beard, floating above the hermitage floor, Maharishi Valmiki prostrating in awe, sacred smoke from sacrificial fire, ethereal Vedic atmosphere.",
            "narration": "जब वाल्मीकि जी आश्रम लौटे, तो वे स्तब्ध थे कि उनके मुख से 32 अक्षरों का यह अनुपम छंद कैसे प्रकट हुआ! तभी चतुर्मुख ब्रह्मा साक्षात उनके कुटीर में प्रकट हुए। ब्रह्मा जी ने कहा— 'हे वाल्मीकि! विस्मित मत होओ। यह श्लोक मेरी ही प्रेरणा से तुम्हारे मुख से निकला है। इसी छंद में तुम मर्यादा पुरुषोत्तम श्री राम के संपूर्ण जीवन चरित्र की रचना करो। जब तक इस पृथ्वी पर पर्वत और नदियां रहेंगी, तब तक तुम्हारी यह रामायण लोक में अमर रहेगी!'",
            "music_cue": "triumphant_brass_fanfare"
        },
        {
            "scene_id": 6,
            "title": "सूर्यवंशी अयोध्या का दिव्य साम्राज्य",
            "visual_prompt": "Massive wide-angle cinematic 8K, golden city of Ayodhya situated on the banks of holy Sarayu, massive stone ramparts, grand palaces with golden kalash, bustling Vedic markets, cavalry, chariots, majestic Emperor Dasharatha seated on a lion throne with sages Vasishtha and Vamadeva, cinematic majesty.",
            "narration": "अब कथा आरंभ होती है सरयू तट पर बसी अजय और स्वर्णिम नगरी अयोध्या की। जहां इक्ष्वाकु वंश के चक्रवर्ती सम्राट दशरथ धर्मपूर्वक राज्य करते थे। अयोध्या में न कोई दरिद्र था, न कोई अधर्मी। समस्त प्रजा सुखी थी। किंतु चक्रवर्ती सम्राट दशरथ के विशाल अंतःपुर में एक गहरा अंधकार था— उनका कोई पुत्र नहीं था जो इस सूर्यवंश के गौरवशाली सिंहासन को आगे बढ़ा सके।",
            "music_cue": "royal_court_strings"
        },
        {
            "scene_id": 7,
            "title": "महा-उत्सुकता पूर्ण समापन (The Cliffhanger)",
            "visual_prompt": "8K cinematic shot, King Dasharatha in royal prayer chamber holding sacred fire oblations, dark storm clouds rising in the southern sky over a silhouette of ten-headed Ravana, epic cliffhanger lighting, glowing golden title card: DIGITAL IMMORTALS, cinematic masterpiece.",
            "narration": "इक्ष्वाकु कुल के इस गहन संकट को मिटाने के लिए कौन सा महायज्ञ रचा जाएगा? कौन हैं महर्षि ऋष्यशृंग, और कैसे होगा नारायण के चारों अंशों का दिव्य अवतार? जानिए अगले पावन एपिसोड में। धर्म की इस अमर यात्रा से जुड़ने के लिए डिजिटल इम्मोर्टल्स को अभी सब्सक्राइब करें। जय श्री राम।",
            "music_cue": "epic_orchestral_outro"
        }
    ]
}

def get_episode_script(episode_num=1):
    """Returns the master structured script for the specified episode."""
    if episode_num == 1:
        return EPISODE_01_DATA
    # Generic placeholder for future episodes
    return {
        "episode_number": episode_num,
        "kanda": "बालकाण्ड",
        "title_hindi": f"वाल्मीकि रामायण - अध्याय {episode_num:02d}",
        "title_youtube": f"वाल्मीकि रामायण: रहस्यमयी गाथा (4K Ep {episode_num:02d})",
        "scenes": []
    }

def save_episode_json(episode_num=1):
    data = get_episode_script(episode_num)
    path = os.path.join(episodes_dir, f"episode_{episode_num:02d}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved Episode {episode_num:02d} Master Script to {path}")
    return path

if __name__ == "__main__":
    ep = 1
    if len(sys.argv) > 2 and sys.argv[1] == "--episode":
        ep = int(sys.argv[2])
    save_episode_json(ep)
