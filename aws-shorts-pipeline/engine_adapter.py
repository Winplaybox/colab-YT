"""
AWS Shorts Engine Adapter
=========================
Dual-Engine with Zero-Downtime Fallback:
- Primary: AWS Bedrock (Nova Micro) + AWS Polly (Generative 'Arjun'/'Kajal')
- Fallback: Free Local Story Bank + Microsoft Edge-TTS (hi-IN-MadhurNeural)
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
DEFAULT_MODE = "aws"  # Options: 'aws', 'free'

def get_boto3_clients():
    try:
        import boto3
        bedrock = boto3.client("bedrock-runtime", region_name=AWS_REGION)
        polly = boto3.client("polly", region_name=AWS_REGION)
        return bedrock, polly
    except Exception as e:
        print(f"[AWS INIT] Boto3 client init notice: {e}")
        return None, None

def generate_script_with_bedrock(topic="Kailash Parvat Ka Rahasya", deity="Lord Shiva"):
    """Generates viral 50-55 second Hinglish Shorts script using Amazon Bedrock."""
    bedrock, _ = get_boto3_clients()
    if not bedrock:
        raise RuntimeError("AWS Bedrock not available")

    prompt = f"""
You are an expert YouTube Shorts creator for '@EpicBharatSaga' (Indian Mythology & Sanatan Dharma).
Write a high-retention 50-second YouTube Short about: '{topic}' focusing on {deity}.

Language: Natural, conversational Hindi in Roman script (Hinglish), engaging and emotionally resonant.

Return ONLY a valid JSON object with these exact keys:
{{
  "title": "Short title with emoji (max 60 chars)",
  "youtube_title": "Viral click-worthy YouTube title with tags (max 80 chars)",
  "hook": "Electrifying 3-second opening hook",
  "voiceover_script": "Full continuous voiceover script in Hinglish, roughly 110-130 words (approx 50 seconds speaking time). Ends with an engaging question asking viewers to comment 'Har Har Mahadev' and subscribe.",
  "pinned_comment": "Engaging question for viewers to comment",
  "description": "SEO description with hashtags #Shorts #Mahadev #Shiva #HinduMythology",
  "tags": ["Shiva", "Mahadev", "Kailash", "HinduMythology", "SanatanDharma", "Shorts"],
  "shots": [
    {{"shot_index": 1, "duration": 5, "subtitle": "First line of hook", "prompt": "Cinematic visual description 9:16 portrait"}},
    {{"shot_index": 2, "duration": 6, "subtitle": "Second scene subtitle", "prompt": "Cinematic visual description 9:16 portrait"}},
    {{"shot_index": 3, "duration": 7, "subtitle": "Third scene subtitle", "prompt": "Cinematic visual description 9:16 portrait"}},
    {{"shot_index": 4, "duration": 7, "subtitle": "Fourth scene subtitle", "prompt": "Cinematic visual description 9:16 portrait"}},
    {{"shot_index": 5, "duration": 7, "subtitle": "Fifth scene subtitle", "prompt": "Cinematic visual description 9:16 portrait"}},
    {{"shot_index": 6, "duration": 8, "subtitle": "Climax scene subtitle", "prompt": "Cinematic visual description 9:16 portrait"}},
    {{"shot_index": 7, "duration": 8, "subtitle": "Conclusion & subscribe CTA", "prompt": "Divine Lord Shiva blessing visual 9:16 portrait"}}
  ]
}}
"""

    messages = [{"role": "user", "content": [{"text": prompt}]}]
    response = bedrock.converse(
        modelId="amazon.nova-micro-v1:0",
        messages=messages
    )
    content = response["output"]["message"]["content"][0]["text"].strip()
    
    # Strip markdown fences if present
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:].strip()
    return json.loads(content)

def synthesize_with_polly(text, output_file, voice="Arjun", engine="generative"):
    """Synthesizes natural voiceover using AWS Polly."""
    _, polly = get_boto3_clients()
    if not polly:
        raise RuntimeError("AWS Polly not available")

    # AWS Polly generative engine produces hyper-realistic studio speech
    response = polly.synthesize_speech(
        Engine=engine,
        VoiceId=voice,
        OutputFormat="mp3",
        Text=text
    )
    with open(output_file, "wb") as f:
        f.write(response["AudioStream"].read())
    return output_file

async def synthesize_with_edgetts(text, output_file, voice="hi-IN-MadhurNeural"):
    """Free fallback using Microsoft Edge-TTS."""
    import edge_tts
    communicate = edge_tts.Communicate(text, voice, rate="+6%", pitch="+1Hz")
    await communicate.save(output_file)
    return output_file

def smart_synthesize_voice(text, output_file, prefer_aws=True, voice="Arjun"):
    """Dual-Mode voice synthesis: Tries AWS Polly first, falls back to Edge-TTS."""
    if prefer_aws:
        try:
            print(f"[TTS] Synthesizing with AWS Polly (Voice: {voice}, Engine: Generative)...")
            synthesize_with_polly(text, output_file, voice=voice, engine="generative")
            print(f"[TTS] AWS Polly voiceover saved: {output_file}")
            return output_file
        except Exception as e:
            print(f"[TTS FALLBACK] AWS Polly encountered notice ({e}). Switching to Free Edge-TTS...")

    # Free Fallback
    print("[TTS] Synthesizing with Free Edge-TTS (hi-IN-MadhurNeural)...")
    asyncio.run(synthesize_with_edgetts(text, output_file))
    print(f"[TTS] Free Edge-TTS voiceover saved: {output_file}")
    return output_file

def smart_generate_story(topic="Kailash Parvat Ka Rahasya", deity="Lord Shiva", prefer_aws=True):
    """Dual-Mode story generator: Tries AWS Bedrock first, falls back to Local Story Bank."""
    if prefer_aws:
        try:
            print(f"[AI] Generating story script with AWS Bedrock (Model: Nova Micro)...")
            story = generate_script_with_bedrock(topic=topic, deity=deity)
            print(f"[AI] AWS Bedrock generated: '{story.get('title')}'")
            return story
        except Exception as e:
            print(f"[AI FALLBACK] AWS Bedrock encountered notice ({e}). Switching to Local Story Bank...")

    # Free Fallback Story
    print("[AI] Using Local EpicBharatSaga Story Bank...")
    return {
        "title": f"{deity}: {topic} ðŸ”±",
        "youtube_title": f"{deity} Ka Adbhut Chamatkar: {topic} #Mahadev #Shorts",
        "hook": f"Kya aap jaante hain {topic} ke peeche ka asali rahasya?",
        "voiceover_script": f"Sanatan parampara mein {deity} ko srishti ka aadi aur anant mana gaya hai. Jab bhi srishti par sankat aaya, Mahadev ne aage aakar sabko bachaya. Kailash parvat unka nivas sthal hai jahan shanti aur anant shakti ka vaas hai. Comment mein Har Har Mahadev likhein aur aisi pavitra gaathaon ke liye subscribe karein.",
        "pinned_comment": "ðŸ”± Har Har Mahadev! Mahadev ki kripa aap sabhi par bani rahe.",
        "description": f"{deity} {topic}\n\n#Shiva #Mahadev #EpicBharatSaga #SanatanDharma #Shorts",
        "tags": ["Shiva", "Mahadev", "Kailash", "HinduMythology", "Shorts"],
        "shots": [
            {"shot_index": 1, "duration": 7, "subtitle": f"{topic} ka adbhut rahasya!", "prompt": "Divine Lord Shiva meditating on Mount Kailash cosmic energy 9:16"}
        ]
    }
