---
name: digital-immortals-studio
description: Autonomous 8K cinematic production, hardware-accelerated rendering, and YouTube publishing for the DigitalImmortals Hindu Mythology channel.
---

# Digital Immortals Studio Agent Skill

This skill guides the autonomous production, generation, encoding, and publication of 16:9 Landscape 8K cinematic docu-episodes for the **@DigitalImmortals** YouTube channel, featuring the definitive 54-episode **Valmiki Ramayana** series.

## Channel Profile
- **Channel ID**: `UCO_AVV1aoIjGEgbj50HTJLw`
- **Handle**: `@DigitalImmortals`
- **Target Episode Duration**: 18–24 minutes per episode
- **Visual Aesthetic**: 16:9 Landscape Hyper-Realistic 8K (Vedic stone temples, divine auras, glowing astras, atmospheric mist)
- **Language Standard**: 100% Shuddh Sanskritized Hindi (शुद्ध देवनागरी हिंदी), zero colloquialisms
- **Hardware Acceleration**: Local NVIDIA NVENC (`h264_nvenc`) + Intel Core i9-12900H 14-core multithreading

## Autonomous Execution Workflow

### Step 1: Pre-Upload Analytics Audit
Before creating or releasing a new episode, inspect the performance of previous uploads:
```powershell
python channels/DigitalImmortals/analytics_tracker.py
```
- Evaluate Like Ratio, Comment Ratio, and audience retention.
- Extract top audience questions/debates to address in the next episode's opening teaser.

### Step 2: Script & Dialogue Generation
Generate the complete scene-by-scene script based on the canonical TTD Valmiki Ramayana text:
```powershell
python channels/DigitalImmortals/story_generator.py --episode <N>
```
- Enforce the 0–5s Ultimate Hook, 30s pattern interrupts, and canonical Sanskrit shlokas.

### Step 3: 8K Visual Generation & Pillow SIMD Pre-Scaling
Create the 16:9 cinematic landscape scenes:
```powershell
python channels/DigitalImmortals/image_generator.py --episode <N>
```

### Step 4: Hardware-Accelerated Video Rendering
Render the episode using the local NVIDIA GPU:
```powershell
python channels/DigitalImmortals/video_producer.py --episode <N> --gpu
```

### Step 5: High-CTR Thumbnail Generation
Generate the 16:9 Landscape master thumbnail:
```powershell
python channels/DigitalImmortals/generate_thumbnail.py --episode <N>
```

### Step 6: YouTube Upload & Playlist Sync
Upload to YouTube, schedule for the optimal slot (Sunday 08:30 AM IST / Tuesday 18:30 IST), and synchronize to the Kanda and Master Playlists:
```powershell
python channels/DigitalImmortals/scheduler.py
```
