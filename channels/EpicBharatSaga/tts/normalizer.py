"""
AllTrainReels Hinglish Text Normalizer & Pacer
==============================================
Normalizes conversational Hinglish scripts before TTS synthesis:
- Expands railway engineering units (km/h -> kilometer per hour, HP -> horsepower, tonnes -> ton)
- Normalizes currency and numbers (₹ -> rupaye)
- Splits text into natural breathing clauses and pauses
- Ensures crisp phonetics for both local neural models (IndicVoice) and cloud engines
"""

import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Common Railway Unit Normalizations
UNIT_REPLACEMENTS = [
    (r"\b(\d+)\s*km/h\b", r"\1 kilometer per hour"),
    (r"\b(\d+)\s*kmph\b", r"\1 kilometer per hour"),
    (r"\b(\d+)\s*km\b", r"\1 kilometer"),
    (r"\b(\d+)\s*cm\b", r"\1 centimeter"),
    (r"\b(\d+)\s*mm\b", r"\1 millimeter"),
    (r"\b(\d+)\s*m\b", r"\1 meter"),
    (r"\b(\d+)\s*hp\b", r"\1 horsepower"),
    (r"\b(\d+)\s*HP\b", r"\1 horsepower"),
    (r"₹\s*(\d+)\s*(lakh|crore|hazar)\b", r"\1 \2 rupaye"),
    (r"₹\s*(\d+)", r"\1 rupaye"),
    (r"\b(\d+)\s*tonnes\b", r"\1 ton"),
    (r"\b(\d+)\s*tons\b", r"\1 ton"),
    (r"\b0-100\b", r"zero se sau"),
    (r"\b(\d+)\s*sec\b", r"\1 second"),
]

def normalize_hinglish_script(text):
    """
    Cleans and expands numbers, units, and punctuation in a Hinglish script
    to produce natural, fluent speech pronunciation.
    """
    cleaned = text.strip()

    # Apply unit expansions
    for pattern, replacement in UNIT_REPLACEMENTS:
        cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)

    # Normalize double dashes and colons to gentle pauses
    cleaned = cleaned.replace("—", ", ").replace("--", ", ")
    cleaned = cleaned.replace(":", " - ")

    # Strip emojis that could cause phoneme errors in local TTS
    cleaned = re.sub(r'[\U00010000-\U0010ffff]', '', cleaned)
    cleaned = re.sub(r'[\u2600-\u27BF]', '', cleaned)

    # Collapse multiple whitespaces
    cleaned = " ".join(cleaned.split())

    return cleaned

def split_into_sentence_chunks(text, max_words=18):
    """
    Splits long narration into breath-sized sentence chunks.
    Useful for future local TTS engines that require shorter inputs.
    Edge-TTS handles full-length text natively (no chunking needed).
    """
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    for s in sentences:
        s = s.strip()
        if not s:
            continue
        words = s.split()
        if len(words) <= max_words:
            chunks.append(s)
        else:
            sub_clauses = re.split(r'(?<=[,;])\s+', s)
            current = []
            for sc in sub_clauses:
                if len(current) + len(sc.split()) <= max_words:
                    current.append(sc)
                else:
                    if current:
                        chunks.append(" ".join(current))
                    current = [sc]
            if current:
                chunks.append(" ".join(current))
    return chunks

if __name__ == "__main__":
    test_text = "603 km/h ki speed se daudi! WAG-12B mein 12000 HP hai, aur ₹1 Lakh ka ticket nahi hai."
    print("Original:", test_text)
    print("Normalized:", normalize_hinglish_script(test_text))
    print("Chunks:", split_into_sentence_chunks(normalize_hinglish_script(test_text)))
