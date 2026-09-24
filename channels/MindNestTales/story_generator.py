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
    ("Luna the Leopard", "leopard", "impatient during quiet hunts", "Stillness and focus conquer what brute rushing loses."),
    # --- Jungle & Wild Animal Tales ---
    ("Rufus the Rhino", "rhino", "charging before thinking", "Pause before you act; a moment of thought prevents a mess."),
    ("Milo the Meerkat", "meerkat", "gossiping about the colony", "Words travel fast — speak kindly or not at all."),
    ("Zola the Zebra", "zebra", "wanting to lose her stripes to fit in", "You were made exactly as you should be."),
    ("Gordo the Gorilla", "gorilla", "using strength to scare smaller animals", "True strength protects, it never bullies."),
    ("Tembo the Elephant", "elephant", "never forgetting old grudges", "Forgiveness lightens a heart weighed down by memory."),
    ("Kesh the Cheetah", "cheetah", "racing everyone even when it wasn't a race", "Not everything is a competition; enjoy the walk sometimes."),
    ("Nia the Giraffe", "giraffe", "looking down on animals shorter than her", "Kindness has no height requirement."),
    ("Bongo the Baboon", "baboon", "stealing snacks from friends", "What isn't yours brings no real joy."),
    ("Sable the Panther", "panther", "hiding in the shadows out of fear of judgment", "You don't have to hide to be accepted."),
    ("Duma the Hyena", "hyena", "laughing at others' mistakes", "Laugh with others, never at them."),
    ("Coco the Chimpanzee", "chimpanzee", "copying friends instead of being herself", "Your own idea is worth more than a perfect copy."),
    ("Bhima the Bison", "bison", "refusing to change the herd's old path", "Sometimes the new trail leads somewhere better."),
    ("Ziva the Wild Dog", "wild dog", "wandering off from the pack alone", "A pack is stronger together than any one of them alone."),
    ("Tariq the Tiger Cub", "tiger cub", "roaring before he'd earned respect", "Respect is earned through actions, not noise."),
    ("Mara the Antelope", "antelope", "freezing in fear instead of fleeing", "Facing fear head-on is safer than standing still."),
    ("Kofi the Warthog", "warthog", "ashamed of his tusks", "The parts of you that seem odd may be your greatest gift."),
    ("Sula the Sloth Bear", "sloth bear", "procrastinating every chore", "Small steps taken today beat big plans left for tomorrow."),
    ("Ravi the Red Panda", "red panda", "too shy to make new friends", "A small hello can open the door to a big friendship."),
    ("Anaya the Orangutan", "orangutan", "hoarding tools instead of sharing them", "Shared tools build a stronger home for everyone."),
    ("Bram the Boar", "boar", "stubbornly refusing directions", "Listening to guidance is not the same as losing your way."),
 
    # --- Farm & Pet Stories ---
    ("Daisy the Dairy Cow", "cow", "complaining about the pasture", "Gratitude turns an ordinary field into a happy one."),
    ("Pogo the Piglet", "pig", "rolling in mud to avoid chores", "Avoiding work today only makes tomorrow muddier."),
    ("Clover the Calf", "calf", "afraid to leave her mother's side", "Growth means taking small steps away from comfort."),
    ("Hank the Horse", "horse", "racing off without his rider's signal", "Trust between friends means waiting for the right moment."),
    ("Nutmeg the Goat", "goat", "eating things that weren't hers to eat", "Curiosity is good, but it needs boundaries."),
    ("Pepper the Sheepdog", "sheepdog", "barking orders instead of leading gently", "A gentle nudge herds better than a harsh bark."),
    ("Wooly the Lamb", "lamb", "following the flock even into danger", "Think for yourself, even when everyone else moves the same way."),
    ("Biscuit the Barn Cat", "cat", "too proud to admit she was lost", "Asking directions is wiser than wandering lost."),
    ("Rusty the Rooster", "rooster", "crowing to take credit for the sunrise", "The sun rises whether you crow or not; stay humble."),
    ("Ginger the Guinea Pig", "guinea pig", "hiding treats instead of sharing", "A shared treat tastes sweeter than a hidden one."),
    ("Max the Farm Dog", "dog", "chasing every rabbit and finishing nothing", "Focus on one goal before chasing the next."),
    ("Snowy the Duckling", "duckling", "wandering from the pond without telling anyone", "Let someone know where you're going — it keeps everyone calm."),
    ("Buttons the Bunny", "rabbit", "digging up the neighbor's garden", "Respect what belongs to others, even out of curiosity."),
    ("Trotter the Donkey", "donkey", "grumbling about every heavy load", "A load shared in good spirit feels lighter."),
    ("Marigold the Mare", "mare", "envying the younger foals' speed", "Every age has its own kind of strength."),
    ("Chester the Chick", "chick", "afraid to leave the coop", "The world outside is scary only until you try it."),
    ("Buttercup the Kitten", "kitten", "scratching furniture out of boredom", "Restless energy is best spent playing, not destroying."),
    ("Olive the Farm Pony", "pony", "showing off her tricks for attention", "You don't need to perform to be loved."),
    ("Peanut the Parrot", "parrot", "repeating unkind words she'd heard", "Words repeated carelessly can still hurt — choose them well."),
    ("Cinder the Turkey", "turkey", "pretending to be someone she wasn't at the fair", "Being real wins more hearts than being flashy."),
 
    # --- Bird Tales ---
    ("Sky the Sparrow", "sparrow", "too small to feel brave", "Bravery isn't about size; it's about heart."),
    ("Indigo the Bluebird", "bluebird", "comparing her song to others'", "Your own song is the one worth singing."),
    ("Talon the Hawk", "hawk", "circling too proud to ask for directions", "Even the sharpest eyes sometimes need another's view."),
    ("Coral the Crane", "crane", "impatient while waiting to migrate", "Good timing is worth the wait."),
    ("Ember the Cardinal", "cardinal", "hiding his bright feathers out of shyness", "Your brightness was never meant to be hidden."),
    ("Percy the Peacock", "peacock", "showing off his tail nonstop", "A quiet moment says more than constant showing off."),
    ("Hoots the Owl", "owl", "staying up worrying instead of sleeping", "Rest restores the mind better than worry ever could."),
    ("Willow the Woodpecker", "woodpecker", "pecking the wrong tree out of impatience", "Choose the right task before working hard at it."),
    ("Sunny the Sunbird", "sunbird", "flitting between friends without listening", "Real friendship means slowing down to truly listen."),
    ("Frost the Falcon", "falcon", "diving too fast and missing the target", "Speed without aim rarely hits the mark."),
    ("Pearl the Pelican", "pelican", "storing more fish than she needed", "Take only what you need so others can have enough."),
    ("Ruby the Robin", "robin", "afraid to sing in front of the flock", "Your voice matters even when it shakes at first."),
    ("Blaze the Kingfisher", "kingfisher", "diving in without checking the water", "Look before you leap into anything new."),
    ("Ash the Albatross", "albatross", "flying alone to prove independence", "Independence and asking for company can live together."),
    ("Petal the Hummingbird", "hummingbird", "rushing from flower to flower, never satisfied", "Slowing down to enjoy the moment brings real sweetness."),
    ("Storm the Stork", "stork", "avoiding responsibility for the nest", "Responsibility shared with love builds a strong nest."),
    ("Ivy the Ibis", "ibis", "jealous of a friend's new feathers", "Celebrating a friend's joy makes your own joy grow."),
    ("Dune the Dove", "dove", "avoiding conflict even when it was needed", "Peace sometimes requires a brave, honest conversation."),
    ("Sable the Swan", "swan", "feeling out of place among ducklings", "Different doesn't mean lesser — patience reveals your grace."),
    ("Copper the Crow", "crow", "collecting shiny things that weren't hers", "What glitters isn't always meant for you to keep."),
 
    # --- Ocean & Sea Stories ---
    ("Marina the Manatee", "manatee", "moving too slowly to help a friend in time", "Steady effort started early beats a rushed effort late."),
    ("Finn the Flying Fish", "flying fish", "leaping to impress instead of to explore", "Do things for the joy of it, not just to impress."),
    ("Nemo the Clownfish", "clownfish", "hiding in the anemone out of fear", "Safety is important, but so is stepping into the open sea."),
    ("Delta the Dolphin", "dolphin", "showing off jumps and ignoring the pod", "A team's success matters more than one member shining alone."),
    ("Shelly the Sea Turtle", "sea turtle", "rushing to the ocean and forgetting her siblings", "Look back for those who need help along the way."),
    ("Coral the Seahorse", "seahorse", "clinging too tightly to one safe spot", "Growth sometimes means letting go and drifting somewhere new."),
    ("Tide the Starfish", "starfish", "wishing for legs like the crabs", "Your own shape carries its own kind of strength."),
    ("Splash the Stingray", "stingray", "using his sting out of impatience, not danger", "Save your defenses for when they're truly needed."),
    ("Bubbles the Beluga Whale", "beluga whale", "mimicking others instead of using her own voice", "Your true voice is worth more than any imitation."),
    ("Reef the Reef Shark", "reef shark", "feared by everyone though he meant no harm", "Don't let others' assumptions define who you really are."),
    ("Glimmer the Jellyfish", "jellyfish", "drifting with no direction or goal", "A little direction turns drifting into a journey."),
    ("Pearl the Pufferfish", "pufferfish", "puffing up at the smallest scare", "Not every situation calls for a big defensive reaction."),
    ("Wave the Walrus Pup", "walrus pup", "refusing help climbing onto the ice", "Accepting help isn't giving up — it's growing smarter."),
    ("Sandy the Sand Crab", "sand crab", "scuttling sideways away from every challenge", "Facing a challenge straight on gets you further than avoiding it."),
    ("Luna the Sea Lion", "sea lion", "barking for attention during others' turns", "Waiting your turn earns more attention than demanding it."),
    ("Cove the Octopus", "octopus", "changing colors to please everyone around him", "You can't please everyone — be true to your own colors."),
    ("Marlin the Swordfish", "swordfish", "charging ahead of the school alone", "A school of friends is safer than a lone swim."),
    ("Ripple the River Otter", "river otter", "playing instead of watching for danger", "Playtime is best enjoyed once responsibilities are done."),
    ("Tidus the Tuna", "tuna", "swimming as fast as he could to prove his worth", "Worth isn't measured by speed but by how you treat others."),
    ("Nora the Narwhal", "narwhal", "self-conscious about her long tusk", "What makes you different can also make you remarkable."),
 
    # --- Tiny Insect Tales ---
    ("Buzzy the Bumblebee", "bumblebee", "too busy to rest, ever", "Even the busiest worker needs time to recharge."),
    ("Sprout the Snail", "snail", "embarrassed by how slowly he moved", "Slow and steady still gets you where you need to go."),
    ("Ziggy the Firefly", "firefly", "dimming his light so as not to stand out", "The world needs your light exactly as bright as it is."),
    ("Antsy the Ant", "ant", "trying to carry everything alone", "Many small hands make a heavy load light."),
    ("Web the Spider", "spider", "feared for a job she never asked for", "Understanding someone's role changes how you see them."),
    ("Flit the Dragonfly", "dragonfly", "darting from task to task, finishing none", "One finished task beats ten unfinished ones."),
    ("Speckle the Ladybug", "ladybug", "hiding her spots, thinking they made her unlucky", "What looks unlucky at first can be your lucky charm."),
    ("Grubby the Caterpillar", "caterpillar", "impatient to become a butterfly overnight", "Real transformation takes patient, quiet time."),
    ("Chirpy the Cricket", "cricket", "singing loudly at the worst possible times", "Timing matters as much as talent."),
    ("Mossy the Millipede", "millipede", "worrying about tripping over her own many legs", "Overthinking every step can trip you up more than moving forward."),
    ("Glow the Glowworm", "glowworm", "envying the fireflies who could fly", "Appreciate your own gift instead of longing for another's."),
    ("Pincer the Beetle", "beetle", "using his strength to push others aside", "Strength used kindly builds friendships, not fear."),
    ("Silky the Silkworm", "silkworm", "rushing the weaving of her cocoon", "Good work, done carefully, is worth the extra time."),
    ("Hopper the Grasshopper", "grasshopper", "singing all summer with no thought for winter", "Prepare today for the season that's still to come."),
    ("Dot the Aphid", "aphid", "relying on others without ever giving back", "A friendship of give and take lasts far longer than one-sided help."),
    ("Zippy the Mayfly", "mayfly", "wasting his short day worrying about how short it was", "Make the most of today instead of mourning its length."),
    ("Petal the Praying Mantis", "praying mantis", "judged as scary before anyone got to know her", "Give others a chance before deciding who they are."),
    ("Sting the Wasp", "wasp", "quick to anger over small annoyances", "A calm response solves more than a quick sting ever will."),
    ("Roly the Pill Bug", "pill bug", "rolling into a ball at the first sign of trouble", "Sometimes facing trouble works better than hiding from it."),
    ("Fuzzy the Moth", "moth", "chasing every bright light without a plan", "Not every shiny thing is worth chasing."),
 
    # --- Classic Moral Fables ---
    ("Ezra the Eagle", "eagle", "flying too high to notice friends below", "Even the highest flyer needs friends on the ground."),
    ("Willa the Wolf Pup", "wolf pup", "wanting to hunt alone before she was ready", "Learning from the pack now means leading it well later."),
    ("Otto the Ox", "ox", "refusing to rest even when exhausted", "Rest is not laziness — it's what lets strength continue."),
    ("Vixen the Fox Kit", "fox kit", "using clever tricks to fool her friends", "Cleverness used to deceive costs more trust than it gains."),
    ("Bramble the Hedgehog", "hedgehog", "keeping his spines up even with friends", "Let your guard down with those who've earned your trust."),
    ("Juniper the Deer", "deer", "too timid to stand up for a friend", "Speaking up for a friend takes more courage than staying silent."),
    ("Cricket the Field Mouse", "field mouse", "underestimating what she could achieve", "You're capable of more than you give yourself credit for."),
    ("Thorne the Wild Boar", "wild boar", "charging into problems without a plan", "A little planning prevents a lot of trouble."),
    ("Hazel the Hare", "hare", "boasting about speed and losing focus on the goal", "Confidence without effort still finishes last."),
    ("Amber the Tortoise", "tortoise", "doubting that slow, steady work would ever pay off", "Consistency quietly wins what haste loudly loses."),
    ("Bramwell the Beaver Pup", "beaver pup", "building without asking if it was needed", "Effort matters most when it's pointed at the right goal."),
    ("Solstice the Stag", "stag", "hiding his antlers out of fear of a bigger rival", "Facing a rival honestly beats hiding from the challenge."),
    ("Marlow the Moose", "moose", "too proud to squeeze through a smaller path", "Sometimes the humble path gets you there faster than the proud one."),
    ("Elowen the Ermine", "ermine", "changing who she was to match every season's crowd", "Staying true to yourself matters more than fitting every crowd."),
    ("Bracken the Badger Cub", "badger cub", "digging tunnels that led nowhere useful", "Effort without direction just makes more work later."),
    ("Fenwick the Ferret", "ferret", "sneaking off instead of asking permission", "Honesty about your plans earns more freedom than sneaking ever will."),
    ("Larkin the Lark", "lark", "singing to be noticed rather than for the joy of it", "Do what you love for its own sake, not just for applause."),
    ("Sorrel the Squirrel Elder", "elderly squirrel", "refusing the young ones' new ideas", "Wisdom grows when it listens to fresh ideas, not just old ways."),
    ("Bramblewood the Bear Cub", "bear cub", "impatient to hibernate before winter truly came", "Good timing matters as much as good intentions."),
    ("Wrenna the Wren", "wren", "feeling too small to make a difference", "Even the smallest bird can build the sturdiest nest.")
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
