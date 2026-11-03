"""
AWS Shorts Engine Adapter - Pure Hindi Cinematic Storytelling
============================================================
- AI Script: AWS Bedrock (Model: amazon.nova-micro-v1:0) in 100% Pure Hindi
- Primary Voice: AWS Polly Generative Engine (Voice: 'Arjun')
- Zero-Downtime Fallback Voice: Microsoft Edge-TTS (Voice: 'hi-IN-MadhurNeural')
"""

import os
import sys
import json
import asyncio

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

AWS_REGION = "ap-southeast-2"

def get_boto3_clients():
    try:
        import boto3
        bedrock = boto3.client("bedrock-runtime", region_name=AWS_REGION)
        polly = boto3.client("polly", region_name=AWS_REGION)
        return bedrock, polly
    except Exception as e:
        print(f"[AWS BOTO3 INIT] {e}")
        return None, None

def generate_pure_hindi_script(topic="Kailash Parvat Ka Rahasya", deity="भगवान शिव"):
    """
    Generates a 100% pure Hindi script with high emotional engagement,
    intense curiosity hook, and natural storytelling cadence.
    """
    bedrock, _ = get_boto3_clients()
    if not bedrock:
        raise RuntimeError("AWS Bedrock not available")

    prompt = f"""
आप 'EpicBharatSaga' के लिए एक अत्यंत अनुभवी और सम्मोहक हिंदू पौराणिक कथाकार हैं।
विषय: '{topic}' ({deity}) पर 45-50 सेकंड का अत्यंत रहस्यमयी और रोमांचक YouTube Short स्क्रिप्ट लिखें।

कड़े नियम (Strict Rules):
1. भाषा: 100% शुद्ध, सरल और भावनात्मक हिंदी (देवनागरी लिपि में)।
2. एक भी अंग्रेजी या हिंग्लिश शब्द का प्रयोग न करें (no "episode", "channel", "video", "subscribe", "comment", "like")।
3. पहले 3 सेकंड में ऐसा रहस्यमयी प्रश्न (Hook) पूछें जिससे रोंगटे खड़े हो जाएं।
4. कहानी में सस्पेंस, दिव्यता और गति होनी चाहिए।
5. अंत में भावनात्मक समापन: "कमेंट में 'हर हर महादेव' लिखकर सनातन धर्म की इस अमर शक्ति को नमन करें।"
6. कुल शब्द: लगभग 100 से 115 शब्द (45-50 सेकंड बोलने का समय)।

केवल और केवल वैध JSON आउटपुट दें:
{{
  "title": "हिंदी शीर्षक (इमोजी के साथ)",
  "youtube_title": "वायरल हिंदी शीर्षक #Shorts #Mahadev #SanatanDharma",
  "hook": "शुरुआती 3 सेकंड का शक्तिशाली हुक",
  "voiceover_script": "पूरी 100% शुद्ध हिंदी कथा (लगभग 105 शब्द)।",
  "pinned_comment": "दर्शकों के लिए भक्तिमय प्रश्न",
  "description": "विस्तृत विवरण और हैशटैग #Shorts #SanatanDharma #Mahadev",
  "tags": ["महादेव", "शिव", "कैलाश", "सनातन_धर्म", "Shorts"],
  "shots": [
    {{"shot_index": 1, "duration": 6, "subtitle": "हुक पंक्ति", "prompt": "Lord Shiva divine cosmic weapon 9:16 portrait"}},
    {{"shot_index": 2, "duration": 7, "subtitle": "रहस्य का खुलासा", "prompt": "Ancient Himalayan mountains glowing with cosmic energy 9:16"}},
    {{"shot_index": 3, "duration": 8, "subtitle": "कथा का विस्तार", "prompt": "Lord Shiva meditating in intense divine flames 9:16"}},
    {{"shot_index": 4, "duration": 8, "subtitle": "दिव्य शक्ति का प्रदर्शन", "prompt": "Divine golden light spreading across universe 9:16"}},
    {{"shot_index": 5, "duration": 8, "subtitle": "गहन रहस्य", "prompt": "Cosmic balance of creation preservation and destruction 9:16"}},
    {{"shot_index": 6, "duration": 7, "subtitle": "अंतिम संदेश", "prompt": "Lord Shiva benevolent blessing darshan 9:16"}},
    {{"shot_index": 7, "duration": 6, "subtitle": "हर हर महादेव नमन", "prompt": "Sacred Om and Trishul glowing in golden light 9:16"}}
  ]
}}
"""

    messages = [{"role": "user", "content": [{"text": prompt}]}]
    response = bedrock.converse(
        modelId="amazon.nova-micro-v1:0",
        messages=messages
    )
    content = response["output"]["message"]["content"][0]["text"].strip()
    
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:].strip()
    return json.loads(content)

def synthesize_with_polly_arjun(text, output_file):
    """Synthesizes using AWS Polly Generative Engine (Voice: Arjun)."""
    _, polly = get_boto3_clients()
    if not polly:
        raise RuntimeError("AWS Polly not available")
    
    clean_text = text.replace("#", "").replace("•", "").replace("---", "").strip()
    response = polly.synthesize_speech(
        Engine="generative",
        VoiceId="Arjun",
        OutputFormat="mp3",
        Text=clean_text
    )
    with open(output_file, "wb") as f:
        f.write(response["AudioStream"].read())
    return output_file

async def synthesize_fallback_edgetts(text, output_file):
    """Fallback using Microsoft Edge-TTS."""
    import edge_tts
    clean_text = text.replace("#", "").replace("•", "").replace("---", "").strip()
    communicate = edge_tts.Communicate(clean_text, "hi-IN-MadhurNeural", rate="+2%", pitch="-1Hz")
    await communicate.save(output_file)
    return output_file

def smart_synthesize_voice(text, output_file, prefer_aws=True):
    """
    Synthesizes voiceover:
    Primary: AWS Polly Generative (Arjun) - High-Fidelity Human Cadence
    Fallback: Free Edge-TTS (hi-IN-MadhurNeural)
    """
    if prefer_aws:
        try:
            print("[VOICE] Synthesizing with AWS Polly (Voice: Arjun, Engine: Generative)...")
            synthesize_with_polly_arjun(text, output_file)
            print(f"[VOICE] AWS Polly Generative audio rendered successfully: {output_file}")
            return output_file
        except Exception as e:
            print(f"[VOICE NOTICE] AWS Polly notice ({e}). Switching to Edge-TTS fallback...")

    # Fallback
    print("[VOICE] Synthesizing with Free Edge-TTS (hi-IN-MadhurNeural)...")
    asyncio.run(synthesize_fallback_edgetts(text, output_file))
    print(f"[VOICE] Edge-TTS audio rendered successfully: {output_file}")
    return output_file

def smart_generate_story(topic="Kailash Parvat Ka Rahasya", deity="भगवान शिव", prefer_aws=True):
    """
    Generates story script using AWS Bedrock in 100% pure Hindi.
    """
    if prefer_aws:
        try:
            print(f"[AI] Generating 100% Pure Hindi Script with AWS Bedrock (Nova Micro)...")
            story = generate_pure_hindi_script(topic=topic, deity=deity)
            print(f"[AI] Bedrock generated title: '{story.get('title')}'")
            return story
        except Exception as e:
            print(f"[AI NOTICE] Bedrock fallback: {e}")

    # Fallback Pure Hindi Script
    return {
        "title": f"महादेव के त्रिशूल का दिव्य रहस्य 🔱",
        "youtube_title": f"महादेव के त्रिशूल का रहस्य जो कोई नहीं जानता #Shorts #SanatanDharma",
        "hook": "क्या आप जानते हैं महादेव के त्रिशूल का सबसे बड़ा रहस्य?",
        "voiceover_script": "क्या आप जानते हैं महादेव के त्रिशूल का सबसे बड़ा रहस्य? सनातन धर्म में भगवान शिव का त्रिशूल केवल एक अस्त्र नहीं है, बल्कि संपूर्ण ब्रह्मांड के संतुलन का प्रतीक है। इसके तीन शूल सत्य, रज और तम—प्रकृति के तीनों गुणों को दर्शाते हैं। जब भी अधर्म ने सृष्टि की मर्यादा को तोड़ा, महादेव ने इसी त्रिशूल से उसका संहार कर पुनः धर्म की स्थापना की। यह त्रिशूल हमें सिखाता है कि मन, वाणी और कर्म पर नियंत्रण ही सच्ची साधना है। कमेंट में 'हर हर महादेव' लिखकर सनातन धर्म की इस अमर शक्ति को नमन करें।",
        "pinned_comment": "🔱 हर हर महादेव! महादेव की कृपा आप सब पर बनी रहे।",
        "description": "महादेव के त्रिशूल का रहस्य\n\n#Shorts #SanatanDharma #Mahadev #Shiva",
        "tags": ["महादेव", "शिव", "त्रिशूल", "सनातन_धर्म", "Shorts"],
        "shots": [
            {"shot_index": 1, "duration": 7, "subtitle": "महादेव के त्रिशूल का दिव्य रहस्य!", "prompt": "Lord Shiva Trishul divine cosmic golden light 9:16"}
        ]
    }
