"""
MindNest Tales Google Sheets Synchronization Engine:
- Live synchronization of the 51-Story Master Roadmap
- Tracks multi-language video release status across all 11 channels
- Target Google Sheet: https://docs.google.com/spreadsheets/d/1TqPmsJ_cbk9rTbMeKvWcCm8FCCVZjOUT6_tMTS4VyiI/edit?gid=0#gid=0
"""

import os
import sys
import json
from datetime import datetime

SPREADSHEET_ID = "1TqPmsJ_cbk9rTbMeKvWcCm8FCCVZjOUT6_tMTS4VyiI"
SPREADSHEET_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit#gid=0"

LANGUAGES = ["hi", "en", "es", "pt", "fr", "de", "ar", "ja", "ko", "vi", "fil"]
HEADERS = [
    "Story #", "Story Title", "Playlist", "Moral",
    "Hindi (HI)", "English (EN)", "Spanish (ES)", "Portuguese (PT)",
    "French (FR)", "German (DE)", "Arabic (AR)", "Japanese (JA)",
    "Korean (KO)", "Vietnamese (VI)", "Filipino (FIL)", "Last Updated"
]

STORIES_MASTER = [
    (1, "The Cheetah Who Was Always Late", "Jungle & Wild Animal Tales", "The fastest speed means nothing without the right timing. Be punctual, not just fast!"),
    (2, "Lion King's Bad Hair Day", "Jungle & Wild Animal Tales", "True leadership comes from kindness and wisdom, not your crown or appearance."),
    (3, "The Elephant Who Forgot Nothing (except his manners)", "Jungle & Wild Animal Tales", "Intelligence without courtesy is useless. Good manners make true greatness."),
    (4, "Zebra's Identity Crisis", "Jungle & Wild Animal Tales", "Embrace your unique self. Comparison steals your joy."),
    (5, "The Monkey Business Meeting", "Jungle & Wild Animal Tales", "Too much chatter and no action leads to chaos. Focus gets things done."),
    (6, "Giraffe's Fear of Heights", "Jungle & Wild Animal Tales", "Courage is facing fear, even when people expect you to be fearless."),
    (7, "The Slowest Sloth Race", "Jungle & Wild Animal Tales", "Rushing through life makes you miss the view. Consistency wins."),
    (8, "Tiger's Stripes Went Missing", "Jungle & Wild Animal Tales", "Your worth is inside you, not on the surface."),
    (9, "The Hyena Who Couldn't Stop Laughing", "Jungle & Wild Animal Tales", "There is a time to laugh and a time to listen. Respect others."),
    (10, "Rhino's Anger Management Class", "Jungle & Wild Animal Tales", "Losing your temper breaks your own peace. Breathe before charging."),
    (11, "The Wise Old Elephant and the Water Hole", "Jungle & Wild Animal Tales", "Sharing scarce resources saves everyone. Selfishness destroys."),
    (12, "Panda's Bamboo Diet Disaster", "Jungle & Wild Animal Tales", "Moderation in all things leads to a happy, balanced life."),
    (13, "The Dog Who Thought He Was a Cat", "Farm & Pet Stories", "Be proud of who you are. Every animal has a unique gift."),
    (14, "Lazy Cow's Morning Alarm Problem", "Farm & Pet Stories", "Early risers catch the freshest grass. Do not sleep through opportunity."),
    (15, "The Rooster Who Lost His Voice", "Farm & Pet Stories", "Teamwork covers individual flaws. Everyone has a role to play."),
    (16, "Piglet's Mud Bath Obsession", "Farm & Pet Stories", "Balance pure fun with everyday responsibility."),
    (17, "The Sheep Who Wanted to Be a Wolf", "Farm & Pet Stories", "Peaceful strength is more admirable than pretending to be scary."),
    (18, "Horse vs Donkey: The Race", "Farm & Pet Stories", "Do not judge by speed; stamina and endurance outlast flashiness."),
    (19, "The Cat Who Was Scared of Mice", "Farm & Pet Stories", "Face your irrational fears; they are often smaller than you imagine."),
    (20, "Goat's Great Escape Plan", "Farm & Pet Stories", "The grass is not always greener on the other side of the fence."),
    (21, "The Duck Who Couldn't Swim", "Farm & Pet Stories", "Practice and patience turn weakness into your greatest strength."),
    (22, "Farmer's Smartest Pet Competition", "Farm & Pet Stories", "Cooperation is far greater than competition."),
    (23, "The Parrot Who Repeated Everything Wrong", "Bird Tales", "Listen carefully before you speak. Words have consequences."),
    (24, "Owl's Night Shift Complaints", "Bird Tales", "Every role has its challenge; find joy in your unique duty."),
    (25, "The Peacock's Ego Problem", "Bird Tales", "Humility makes beauty shine brighter. Arrogance repels friends."),
    (26, "Eagle's Fear of Flying", "Bird Tales", "You will never soar until you spread your wings and leave the nest."),
    (27, "The Pigeon Who Delivered Wrong Messages", "Bird Tales", "Attention to detail prevents huge misunderstandings."),
    (28, "Crow's Shiny Object Addiction", "Bird Tales", "Greed for glittering trinkets blinds you to true treasure."),
    (29, "The Flamingo Who Couldn't Balance", "Bird Tales", "Balance in life comes with practice and inner calm."),
    (30, "Woodpecker's Headache Story", "Bird Tales", "Work smart, not just hard. Protect your head while building."),
    (31, "The Shy Octopus's Eight Left Feet", "Ocean & Sea Stories", "Your quirks and clumsiness make you uniquely lovable."),
    (32, "Dolphin's Talent Show", "Ocean & Sea Stories", "True talent lifts others up rather than demanding the spotlight."),
    (33, "The Turtle Who Was Afraid of His Own Shell", "Ocean & Sea Stories", "Your shell is your sanctuary, not your prison."),
    (34, "Crab's Sideways Walking Problem", "Ocean & Sea Stories", "There is more than one way to move forward in life."),
    (35, "The Fish Who Forgot Where Home Was", "Ocean & Sea Stories", "Stay close to those who guide you and never forget your roots."),
    (36, "Whale's Singing Competition", "Ocean & Sea Stories", "Sing your own song with all your heart; harmony beats perfection."),
    (37, "The Jellyfish With No Bones", "Ocean & Sea Stories", "Flexibility and resilience are greater than brute rigidity."),
    (38, "Seahorse Dad's Parenting Struggle", "Ocean & Sea Stories", "Patience and love conquer the chaos of raising a family."),
    (39, "The Ant Who Skipped Work", "Tiny Insect Tales", "Procrastination today creates hardship tomorrow. Small habits matter."),
    (40, "Butterfly's Ugly Duckling Phase", "Tiny Insect Tales", "Patience through the dark cocoon leads to wings of flight."),
    (41, "The Bee Who Was Afraid of Flowers", "Tiny Insect Tales", "Step outside your comfort zone to find life's sweetest nectar."),
    (42, "Spider's Web Redesign Fails", "Tiny Insect Tales", "Do not overcomplicate what already works perfectly."),
    (43, "The Firefly Who Lost His Light", "Tiny Insect Tales", "When your inner fire dims, connection with community restores it."),
    (44, "Grasshopper's Winter Regret", "Tiny Insect Tales", "Prepare during seasons of plenty so you never fear times of need."),
    (45, "The Tortoise and the Hare (Comedy Remix)", "Classic Moral Fables", "Slow and steady wins the race, but humbleness keeps the trophy."),
    (46, "The Thirsty Crow", "Classic Moral Fables", "Resourcefulness and determination overcome any obstacle."),
    (47, "The Fox and the Grapes", "Classic Moral Fables", "Do not despise what you cannot get; work harder or move forward."),
    (48, "The Lion and the Mouse", "Classic Moral Fables", "No act of kindness is ever wasted. Even the smallest friend can save the king."),
    (49, "The Boy Who Cried Wolf", "Classic Moral Fables", "Trust takes years to build and seconds to break with a single lie."),
    (50, "The Ant and the Grasshopper", "Classic Moral Fables", "Diligence brings peace of mind; laziness brings anxiety."),
    (51, "The Monkey and the Crocodile", "Classic Moral Fables", "Quick thinking and presence of mind can save you from any trap.")
]

def get_gspread_client():
    """Resolves gspread client using Google Colab auth, service account, or local token."""
    try:
        import gspread
    except ImportError:
        return None

    # Option A: Google Colab Environment
    try:
        from google.colab import auth
        auth.authenticate_user()
        from google.auth import default
        creds, _ = default()
        return gspread.authorize(creds)
    except Exception:
        pass

    # Option B: Service Account JSON
    for sa_path in ["service_account.json", "channels/MindNestTales/service_account.json"]:
        if os.path.exists(sa_path):
            try:
                return gspread.service_account(filename=sa_path)
            except Exception:
                pass

    # Option C: Environment Variable
    if "GOOGLE_SHEETS_CREDENTIALS_JSON" in os.environ and os.environ["GOOGLE_SHEETS_CREDENTIALS_JSON"].strip():
        try:
            creds_dict = json.loads(os.environ["GOOGLE_SHEETS_CREDENTIALS_JSON"])
            return gspread.service_account_from_dict(creds_dict)
        except Exception:
            pass

    return None

def init_tracking_sheet():
    """Initializes and verifies the Google Sheet structure with all 51 stories."""
    client = get_gspread_client()
    if not client:
        print("Note: Google Sheets client not authenticated. Progress will be logged locally.")
        return False

    try:
        sheet = client.open_by_key(SPREADSHEET_ID).sheet1
        existing_values = sheet.get_all_values()

        # Check or add headers
        if not existing_values or existing_values[0] != HEADERS:
            sheet.clear()
            sheet.append_row(HEADERS)
            print("Initialized Google Sheet headers.")

            # Pre-populate all 51 stories
            rows = []
            for item in STORIES_MASTER:
                row = [str(item[0]), item[1], item[2], item[3]] + ["Pending"] * len(LANGUAGES) + [""]
                rows.append(row)
            sheet.append_rows(rows)
            print("Populated all 51 stories in Google Sheet.")
        return True
    except Exception as e:
        print(f"Google Sheet init note: {e}")
        return False

def record_story_status(story_number, lang_code, status_text):
    """
    Updates a specific story's cell in the Google Sheet for a target language.
    Example: record_story_status(1, 'hi', 'Uploaded (https://youtu.be/xxx)')
    """
    client = get_gspread_client()
    if not client:
        return False

    try:
        sheet = client.open_by_key(SPREADSHEET_ID).sheet1
        
        # Col 1 is Story #. Row 1 is headers, so row index = story_number + 1
        target_row = story_number + 1

        # Determine column index
        # 0: Story #, 1: Title, 2: Playlist, 3: Moral
        # 4: hi, 5: en, 6: es, 7: pt, 8: fr, 9: de, 10: ar, 11: ja, 12: ko, 13: vi, 14: fil, 15: Last Updated
        lang_to_col = {l: i + 5 for i, l in enumerate(LANGUAGES)}
        col_idx = lang_to_col.get(lang_code.lower())

        if col_idx:
            sheet.update_cell(target_row, col_idx, status_text)
            sheet.update_cell(target_row, len(HEADERS), datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            print(f"📊 Google Sheet updated: Story #{story_number} [{lang_code.upper()}] -> {status_text}")
            return True
    except Exception as e:
        print(f"Google Sheet update note: {e}")
        return False

if __name__ == "__main__":
    print(f"Target Sheet URL: {SPREADSHEET_URL}")
    init_tracking_sheet()
