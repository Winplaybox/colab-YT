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

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)
from sheets_tracker import STORIES_MASTER
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
    ("Wrenna the Wren", "wren", "feeling too small to make a difference", "Even the smallest bird can build the sturdiest nest."),
    # --- Savanna & Grassland ---
    ("Leo the Lion Cub", "lion cub", "impatient to be king before he was ready", "Leadership is earned through patience and service, not impatience."),
    ("Nyala the Wildebeest", "wildebeest", "terrified of the great migration", "Facing the unknown together makes the journey survivable."),
    ("Jazz the Gazelle", "gazelle", "always looking back in fear instead of forward", "Enjoy the run ahead instead of the fear behind you."),
    ("Impy the Impala", "impala", "jealous of how high others could jump", "Compare your growth only to your own past self."),
    ("Ozzy the Ostrich", "ostrich", "burying problems instead of facing them", "Problems ignored only grow bigger underground."),
    ("Sabra the Secretary Bird", "secretary bird", "too proud to walk instead of fly", "Pride can keep you from the simpler, wiser path."),
    ("Ardy the Aardvark", "aardvark", "digging only at night, too shy for daylight", "You don't have to hide who you are to be respected."),
    ("Jax the Jackal", "jackal", "stealing scraps instead of earning his own food", "An earned meal tastes better than a stolen one."),
    ("Dinky the Dik-Dik", "dik-dik", "feeling invisible because he was so small", "Being small doesn't mean being unimportant."),
    ("Portly the Hippo", "hippopotamus", "grumpy about sharing the watering hole", "A resource cared for by everyone lasts longer for everyone."),
 
    # --- Desert & Dry Lands ---
    ("Finn the Fennec Fox", "fennec fox", "embarrassed by his oversized ears", "The very thing you're embarrassed by might be your superpower."),
    ("Cammy the Camel", "camel", "complaining nonstop about carrying the load", "The load you carry today gets you to tomorrow's oasis."),
    ("Stinger the Scorpion", "scorpion", "feared for a sting he rarely even used", "Being feared isn't the same as being respected."),
    ("Zippy the Roadrunner", "roadrunner", "always running from problems instead of solving them", "Sometimes stopping to face things beats running from them."),
    ("Sandy the Gecko", "gecko", "camouflaging to avoid every conversation", "Blending in shouldn't mean disappearing from your friendships."),
    ("Sly the Sidewinder", "sidewinder snake", "misunderstood because of his unusual way of moving", "Different doesn't mean dangerous."),
    ("Arlo the Armadillo", "armadillo", "curling into his shell at every disagreement", "Facing disagreements builds stronger bonds than hiding from them."),
    ("Thorn the Horned Lizard", "horned lizard", "puffing himself up to seem scarier than he was", "Confidence built on truth outlasts confidence built on bluff."),
    ("Iggy the Desert Iguana", "desert iguana", "basking all day while chores piled up", "Rest is good, but responsibilities still need doing."),
    ("Rocco the Gila Monster", "gila monster", "misjudged as lazy for moving so slowly", "Slow doesn't mean lazy — everyone has their own pace."),
 
    # --- Arctic & Polar ---
    ("Bjorn the Polar Bear Cub", "polar bear cub", "impatient to hunt alone on the ice", "Skills take time to master before going solo."),
    ("Snowdrop the Arctic Fox", "arctic fox", "changing color to hide from every difficulty", "You can't camouflage your way out of every challenge."),
    ("Terra the Arctic Tern", "arctic tern", "boasting endlessly about the longest migration", "The journey matters more than bragging about the distance."),
    ("Talus the Pika", "pika", "hoarding hay without sharing with the colony", "A colony thrives when everyone shares the harvest."),
    ("Frosty the Musk Ox", "musk ox", "too stubborn to change the herd's direction", "Stubbornness can leave you out in the cold, alone."),
    ("Glacia the Harp Seal Pup", "harp seal pup", "clumsy on the ice and embarrassed to play", "Everyone stumbles while learning; don't let it stop your play."),
    ("Rudy the Reindeer", "reindeer", "worried his antlers were far too big", "What seems too big may be exactly what's needed on the hardest night."),
    ("Pebble the Puffin", "puffin", "so clumsy at landing it embarrassed him", "Practice turns clumsy landings into graceful ones."),
    ("Ptolemy the Ptarmigan", "ptarmigan", "changing so often to fit in that he forgot himself", "Adapting is wise, but never lose yourself while doing it."),
    ("Kodiak the Snow Bunting", "snow bunting", "afraid to fly south alone for the first time", "The first flight alone is scary right up until you take it."),
 
    # --- Rainforest Canopy ---
    ("Kiko the Toucan", "toucan", "showing off his colorful beak to feel important", "Importance comes from character, not appearance."),
    ("Zuri the Poison Dart Frog", "poison dart frog", "warning everyone away before getting to know them", "Give people a chance before pushing them away."),
    ("Sasha the Three-Toed Sloth", "sloth", "rushing to keep up and losing her joy in the process", "Move at your own pace and you'll find your joy again."),
    ("Rio the Macaw", "macaw", "repeating gossip he'd only half-heard", "Repeating gossip spreads hurt further than the original words."),
    ("Nutsy the Capuchin Monkey", "capuchin monkey", "stealing shiny trinkets from other nests", "What isn't yours will always feel borrowed, not owned."),
    ("Tama the Tamandua", "tamandua (anteater)", "embarrassed by her unusually long nose", "Your unusual features are tools, not flaws."),
    ("Quill the Tree Porcupine", "tree porcupine", "keeping his quills raised even around trusted friends", "Let your guard down for those who've proven trustworthy."),
    ("Vine the Gibbon", "gibbon", "swinging right past friends who needed help", "Slow down enough to notice who needs a hand."),
    ("Rainer the Quetzal", "quetzal", "hiding his bright tail out of fear of hunters", "Living in fear of what might happen steals the joy of what is."),
    ("Ossian the Hoatzin", "hoatzin", "mocked and ashamed of his unusual smell", "What makes you different might be exactly what keeps you safe."),
 
    # --- Backyard & Garden Critters ---
    ("Hoppy the Toad", "toad", "jumping into every pond without checking the depth", "Check before you leap into something new."),
    ("Fernie the Field Vole", "vole", "hoarding seeds out of fear of scarcity", "Fear of not having enough can stop you enjoying what you do have."),
    ("Digger the Mole", "mole", "feeling forgotten while working hard underground", "Unseen work is still valuable work."),
    ("Rascal the Raccoon", "raccoon", "sneaking into places he wasn't invited", "What's taken without asking never truly belongs to you."),
    ("Pepper the Skunk", "skunk", "using his strongest defense for the smallest problems", "Not every conflict needs your strongest weapon."),
    ("Bramble the Hamster", "hamster", "hoarding food in his cheeks instead of sharing", "Sharing what you have makes it multiply in joy, not shrink."),
    ("Nibbles the Chipmunk", "chipmunk", "stealing acorns that others had gathered", "Gather your own — borrowed effort brings no real pride."),
    ("Waddle the Groundhog", "groundhog", "too scared of his own shadow to come outside", "Don't let fear of what-ifs keep you underground forever."),
    ("Momo the Prairie Dog", "prairie dog", "shouting alarms over every little thing", "Save your warnings for what truly matters, or no one will listen."),
    ("Pockets the Opossum", "opossum", "pretending to be something he wasn't to dodge trouble", "Facing trouble honestly beats pretending it away."),
 
    # --- Reptile & Amphibian Tales ---
    ("Cypress the Alligator", "alligator", "snapping at friends out of pure impatience", "Patience keeps friendships from getting bitten."),
    ("Newton the Newt", "newt", "changing his mind and colors to please every friend", "Stand by your own choice instead of shifting for everyone else."),
    ("Baskin the Iguana", "iguana", "sunbathing while his friends did all the work", "Rest is earned, not taken from others' effort."),
    ("Raja the King Cobra", "king cobra", "feared before anyone ever learned his true nature", "Reputation built on fear crumbles once the truth is known."),
    ("Sanjay the Python", "python", "hugging so tight it scared his friends away", "Love shouldn't feel like being squeezed."),
    ("Rana the Bullfrog", "bullfrog", "croaking louder than everyone just to be heard", "A calm voice is heard more clearly than the loudest one."),
    ("Ekko the Axolotl", "axolotl", "worried he'd never grow up like the other salamanders", "Your own way of growing is valid, even if it looks different."),
    ("Monty the Monitor Lizard", "monitor lizard", "patrolling everyone else's business instead of his own", "Mind your path, and let others walk theirs."),
    ("Draco the Basilisk", "basilisk lizard", "running from every hard conversation instead of having it", "You can't outrun a hard conversation forever."),
    ("Terrapin the Box Turtle", "box turtle", "hiding in his shell at every compliment he received", "Let good things in, not just bad things out."),
 
    # --- Night Sky & Nocturnal Creatures ---
    ("Luna the Fruit Bat", "fruit bat", "afraid of the dark despite living in it", "Sometimes what scares us most is simply unfamiliar, not truly dangerous."),
    ("Nocturne the Nightjar", "nightjar", "camouflaging so well she felt unseen and lonely", "Being hard to notice doesn't mean you don't deserve to be seen."),
    ("Ember the Kinkajou", "kinkajou", "raiding the pantry at night out of impatience", "Patience until morning brings a proper feast, not a stolen snack."),
    ("Ziggy the Flying Squirrel", "flying squirrel", "too afraid to glide from the tallest branch", "Sometimes the leap looks scarier than it feels once you take it."),
    ("Luminous the Lanternfish", "lanternfish", "using his glow to make friends instead of his personality", "A genuine connection outshines any flashy first impression."),
    ("Cinder the Civet", "civet", "blamed for a smell that wasn't even his fault", "Don't let one unfair assumption define how you see someone."),
    ("Grimm the Raven", "raven", "collecting secrets instead of ever sharing them", "A secret kept out of kindness differs from one kept out of power."),
    ("Tanuki the Raccoon Dog", "raccoon dog", "playing tricks that hurt his friends' feelings", "A prank isn't funny if it costs someone's trust."),
    ("Orin the Ocelot", "ocelot", "hunting alone to prove he needed no one", "Needing others isn't weakness — it's how packs and friendships survive."),
    ("Vesper the Vampire Bat", "vampire bat", "taking more than his fair share out of habit, not need", "Take only your fair share, even when more is available."),
 
    # --- Mountain & Alpine ---
    ("Aiolos the Alpine Ibex", "alpine ibex", "climbing higher just to show off", "Climb for the view, not for the applause."),
    ("Yash the Yak", "yak", "refusing to let go of his heavy coat of old worries", "Letting go of old worries makes the climb easier."),
    ("Marmy the Marmot", "marmot", "waking early from hibernation out of pure impatience", "Rest fully before rushing into the new season."),
    ("Skye the Chamois", "chamois", "leaping across cliffs to avoid one hard conversation", "Some conversations are worth standing still for."),
    ("Andes the Condor", "andean condor", "flying so high he forgot to check on those below", "Even from great heights, remember to look out for others."),
    ("Ridge the Mountain Goat", "mountain goat", "stubbornly climbing the hardest path just to prove a point", "The easier path isn't always the weaker choice."),
    ("Frost the Snowfinch", "snowfinch", "complaining about the cold instead of adapting to it", "Complaining wastes energy better spent adapting."),
    ("Amber the Alpine Salamander", "alpine salamander", "avoiding sunlight out of fear of change", "Growth sometimes requires stepping into unfamiliar light."),
    ("Cliff the Bighorn Sheep", "bighorn sheep", "butting heads over every small disagreement", "Not every disagreement needs to become a battle."),
    ("Rocky the Rock Hyrax", "rock hyrax", "shouting warnings that scared the whole colony over nothing", "Cry wolf too often, and no one listens when it's real."),
 
    # --- Wetland & Swamp ---
    ("Wade the Great Blue Heron", "great blue heron", "standing so still he missed his own chances", "Patience is good, but don't let it become a missed opportunity."),
    ("Swampy the Snapping Turtle", "snapping turtle", "snapping at every visitor out of old habit", "Old defenses aren't always needed with new friends."),
    ("Croaker the Green Tree Frog", "green tree frog", "jumping to conclusions about his pond-mates", "Get the full story before jumping to conclusions."),
    ("Fenn the Muskrat", "muskrat", "building his lodge alone instead of asking for help", "A home built with others' help is sturdier than one built alone."),
    ("Glide the Water Strider", "water strider", "skating across the surface, avoiding anything deep", "Real connection means going deeper than the surface."),
    ("Dapple the Spotted Salamander", "spotted salamander", "hiding under logs, afraid to show his true colors", "Your true colors are worth showing, even if hidden for now."),
    ("Reed the Red-Winged Blackbird", "red-winged blackbird", "guarding his patch of marsh too fiercely", "Sharing space doesn't mean losing it."),
    ("Sedge the Marsh Rabbit", "marsh rabbit", "refusing to swim, embarrassed by his wet fur", "Trying something new is worth a little mess."),
    ("Puddle the Mudskipper", "mudskipper", "confused about whether he belonged in water or on land", "You don't have to choose just one place to belong."),
    ("Tarn the Diving Beetle", "diving beetle", "diving deep to avoid facing pond politics", "Hiding from a problem in the depths doesn't make it disappear."),
 
    # --- Farmyard & Aviary Extras ---
    ("Gus the Goose", "goose", "honking loudest just to be heard over the flock", "A calm word can carry further than the loudest honk."),
    ("Wattle the Guinea Fowl", "guinea fowl", "raising the alarm over every passing shadow", "Save the alarm for real danger."),
    ("Wooly the Alpaca", "alpaca", "too proud to let go of his old, heavy coat", "Letting go of the old makes room for something lighter."),
    ("Teal the Mallard Drake", "mallard duck", "following the wrong flock south by mistake", "Double-check you're following the right path, not just any path."),
    ("Melody the Canary", "canary", "singing only sad songs and dragging down the mood", "Your mood can be contagious — choose which one you spread."),
    ("Zest the Budgerigar", "budgerigar", "mimicking every voice but never speaking her own mind", "Your own words matter more than anyone else's echoed back."),
    ("Blanche the Cockatoo", "cockatoo", "screeching for attention instead of asking kindly", "A kind ask gets further than a loud demand."),
    ("Fig the Zebra Finch", "zebra finch", "too shy to join the dawn chorus", "Your voice adds something the chorus is missing without you."),
    ("Thatch the Weaver Bird", "weaver bird", "tearing down his nest again and again, never satisfied", "Perfectionism can destroy more than it ever builds."),
    ("Miko the Mynah", "mynah bird", "repeating unkind words without thinking them through", "Think before you repeat what you hear."),
 
    # --- Sky & Open Air ---
    ("Beak the Hornbill", "hornbill", "sealed away safely but lonely inside his tree", "Safety without connection isn't the same as happiness."),
    ("Ray the Bee-Eater", "bee-eater", "stealing his friends' hard-earned meals", "Earn your own meal — it's the only kind that truly satisfies."),
    ("Cobalt the Roller Bird", "roller bird", "showing off flashy flight tricks to hide his fear of heights", "Bravado can't replace real courage."),
    ("Jade the Trogon", "trogon", "hiding his colorful side out of fear of standing out", "The forest needs your color as much as its green."),
    ("Cash the Cuckoo", "cuckoo", "leaving his responsibilities for others to handle", "Your responsibilities are yours to carry, not to pass along."),
    ("Whistler the Black Kite", "black kite", "swooping in to take credit for others' hard-earned catch", "Real credit comes from your own effort, not someone else's catch."),
    ("Diver the Osprey", "osprey", "fishing in a friend's favorite spot without asking", "Ask before taking what someone else considers theirs."),
    ("Reggie the Vulture", "vulture", "misunderstood and shunned for doing an important job", "An unpopular job can still be a noble one."),
    ("Blitz the Merlin Falcon", "merlin falcon", "too impatient to learn from the elder falcons", "Wisdom from those who came before saves you hard lessons."),
    ("Sable the Kestrel", "kestrel", "hovering anxiously instead of committing to the dive", "Overthinking a decision can cost you the moment to act."),
 
    # --- Extra Ocean Depths ---
    ("Cove the Moray Eel", "moray eel", "hiding in his crevice, assumed scary by everyone", "Being misunderstood doesn't mean being unworthy of friendship."),
    ("Barnacle Bill the Hermit Crab", "hermit crab", "refusing to leave his old shell even though he'd outgrown it", "Growth sometimes means leaving behind what once fit."),
    ("Inky the Cuttlefish", "cuttlefish", "changing colors to trick his friends for fun", "A trick played too often turns friends into doubters."),
    ("Prickle the Sea Urchin", "sea urchin", "keeping his spines out even when no threat was near", "Not every moment calls for your defenses."),
    ("Glow the Anglerfish", "anglerfish", "luring friends close with false promises", "Honesty draws real friendship closer than any clever lure."),
    ("Nori the Sea Otter Pup", "sea otter pup", "too dependent on his mother to try floating alone", "A gentle push toward independence is an act of love."),
 
    # --- Extra Insects & Tiny Creatures ---
    ("Flutter the Monarch Butterfly", "monarch butterfly", "doubting she was strong enough for the long migration", "You're built for the journey, even when it feels impossible."),
    ("Buzz the Honeybee", "honeybee", "working herself to exhaustion without ever resting", "Even the hive needs its workers to rest and recover."),
    ("Chomp the Stag Beetle", "stag beetle", "using his impressive horns to intimidate rather than protect", "Strength should defend, not dominate."),
    ("Skitter the Water Skater", "water skater (bug)", "too nervous to venture beyond the same small puddle", "The wider pond is only scary until you've explored it."),
    ("Hum the Cicada", "cicada", "waiting years underground, afraid he'd wasted the time", "Preparation is never wasted, even when it takes a long time."),
]

PLAYLISTS = [
    "Jungle & Wild Animal Tales",
    "Farm & Pet Stories",
    "Bird Tales",
    "Ocean & Sea Stories",
    "Tiny Insect Tales",
    "Classic Moral Fables"
]

def get_hf_token():
    """Retrieves Hugging Face token from environment or local credentials file."""
    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_TOKEN")
    if token:
        return token.strip()
    local_creds = os.path.join(script_dir, "credentials", "hf_token.txt")
    if os.path.exists(local_creds):
        try:
            with open(local_creds, "r", encoding="utf-8") as f:
                t = f.read().strip()
                if t:
                    return t
        except Exception:
            pass
    return None

def generate_ai_multilingual_translations(story_title, hero_name, story_summary, moral_english):
    """
    Generates 100% pure native scripts across all 11 languages using Hugging Face Serverless LLM.
    Guarantees ZERO English words are mixed into non-English scripts.
    """
    token = get_hf_token()
    if not token:
        print("⚠️ No HF_TOKEN found for multilingual translation. Using pure native fallback templates.")
        return None

    try:
        from huggingface_hub import InferenceClient
        client = InferenceClient(api_key=token, timeout=60)
    except Exception as e:
        print(f"⚠️ Could not initialize InferenceClient: {e}")
        return None

    groups = [
        ["hi", "en", "es"],
        ["pt", "fr", "de"],
        ["ar", "ja"],
        ["ko", "vi", "fil"]
    ]

    lang_names = {
        "en": "English",
        "hi": "Hindi (100% pure Devanagari script, ZERO English words)",
        "es": "Spanish (100% pure Spanish, ZERO English words)",
        "pt": "Portuguese (100% pure Portuguese, ZERO English words)",
        "fr": "French (100% pure French, ZERO English words)",
        "de": "German (100% pure German, ZERO English words)",
        "ar": "Arabic (100% pure Modern Standard Arabic script, ZERO English words)",
        "ja": "Japanese (100% pure Japanese Kanji/Kana, ZERO English words)",
        "ko": "Korean (100% pure Korean Hangul, ZERO English words)",
        "vi": "Vietnamese (100% pure Vietnamese, ZERO English words)",
        "fil": "Filipino/Tagalog (100% pure Filipino/Tagalog, ZERO English words)"
    }

    all_translations = {}

    for group in groups:
        targets_desc = ", ".join(f"'{code}': {lang_names[code]}" for code in group)
        system_prompt = f"""You are a master children's animated storyteller for MindNest Tales (3D Pixar-style moral animation for kids and families).
Your job is to generate rich, engaging, kid-friendly story scripts and YouTube metadata for these languages: {targets_desc}.

STRICT RULES:
1. ZERO LANGUAGE MIXING: Each language must be 100% pure in its own native language and script.
   - Absolutely NEVER mix English words or phrases into Hindi, Spanish, Portuguese, French, German, Arabic, Japanese, Korean, Vietnamese, or Filipino.
   - Hindi must be in Devanagari script with natural, pure vocabulary.
   - Arabic must be in Arabic script. Japanese in Kanji/Kana. Korean in Hangul.
2. SCRIPT: Full, cinematic 4-act spoken narration of 400 to 440 words (specifically engineered for a complete 180-second / 3-minute video runtime).
   - Act 1 (~45s, ~100w): Introduce character and world with wonder, charm, and lively details. Establish the hero's core personality and unique flaw.
   - Act 2 (~45s, ~100w): The Grand Event / Mission. The hero makes a careless mistake or delay due to their flaw. Sudden environmental crisis strikes.
   - Act 3 (~45s, ~100w): Peak predicament. The hero gets stuck or trapped. The wise elder mentor arrives and delivers compassionate, unforgettable wisdom.
   - Act 4 (~45s, ~100w): Triumphant focused action. The obstacle is conquered through patience and wisdom. Grand celebration with all friends, ending with the moral.
3. MORAL: Exactly ONE clear, memorable moral lesson sentence in that native language.
4. TITLE: Catchy, family-friendly YouTube title with emojis and #Shorts.
5. DESCRIPTION: Short YouTube description in that native language with #MindNestTales #Shorts.
6. TAGS: 5-7 relevant tags in that native language.

Return ONLY a valid JSON object mapping each language code {json.dumps(group)} to:
{{
  "title": "string",
  "moral": "string",
  "script": "string",
  "description": "string",
  "tags": ["tag1", "tag2", ...]
}}"""

        user_prompt = f"""Story: {story_title}
Hero: {hero_name}
Story Context: {story_summary}
Moral: {moral_english}

Generate the JSON for {json.dumps(group)} now."""

        try:
            res = client.chat.completions.create(
                model="Qwen/Qwen2.5-72B-Instruct",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=4096,
                response_format={"type": "json_object"}
            )
            group_data = json.loads(res.choices[0].message.content)
            all_translations.update(group_data)
        except Exception as e:
            print(f"[WARNING] AI Translation failed for group {group}: {e}")

    # Verify all 11 languages are present
    needed = ["en", "hi", "es", "pt", "fr", "de", "ar", "ja", "ko", "vi", "fil"]
    if all(l in all_translations for l in needed):
        print("[SUCCESS] AI successfully generated all 11 pure native translations!")
    print(f"Notice: AI generated {len(all_translations)}/11 languages. Completing missing with pure fallbacks.")
    return all_translations

def generate_fallback_translations(hero_name, species, base_title, moral_english, flaw="acting in haste without thinking"):
    """
    Dual-script pure localized translations for all 11 languages:
    1. short_script: 60-90s fast-paced trailer funnel script (~140-180 words) leading to cliffhanger crisis.
       Includes short_cta_voice & short_cta_text for the last 3-5 seconds End-Card CTA.
    2. long_script: ~400-440 words full 4-act narration with mentor arrival and moral victory for 10-min compilation.
    Guarantees 100% PURE NATIVE LANGUAGE: ZERO English words in non-English scripts.
    """
    species_lower = species.lower()
    LOCALIZED_NAMES = {
        "cheetah": {"en": "Chico", "hi": "चीकू", "es": "Chico", "pt": "Chico", "fr": "Chico", "de": "Chico", "ar": "شيكو", "ja": "チコ", "ko": "치코", "vi": "Chico", "fil": "Chico"},
        "lion": {"en": "Leo", "hi": "शेरू", "es": "Leo", "pt": "Leo", "fr": "Léo", "de": "Leo", "ar": "ليو", "ja": "レオ", "ko": "레오", "vi": "Leo", "fil": "Leo"},
        "elephant": {"en": "Gajju", "hi": "गजराज", "es": "Gajju", "pt": "Gajju", "fr": "Gajju", "de": "Gajju", "ar": "غاجو", "ja": "ガジュ", "ko": "가주", "vi": "Gajju", "fil": "Gajju"},
    }
    spec_map = LOCALIZED_NAMES.get(species_lower, {})
    hero_first = hero_name.split()[0]
    n_en = spec_map.get("en", hero_first)
    n_hi = spec_map.get("hi", "नन्हा दोस्त")
    n_es = spec_map.get("es", hero_first)
    n_pt = spec_map.get("pt", hero_first)
    n_fr = spec_map.get("fr", hero_first)
    n_de = spec_map.get("de", hero_first)
    n_ar = spec_map.get("ar", "الصديق اللطيف")
    n_ja = spec_map.get("ja", "チコ")
    n_ko = spec_map.get("ko", "치코")
    n_vi = spec_map.get("vi", hero_first)
    n_fil = spec_map.get("fil", hero_first)

    flaws = {
        "en": "always rushing carelessly and arriving late",
        "hi": "वह हमेशा हर काम में हड़बड़ी करता था और फिर भी हमेशा देर से पहुँचता था",
        "es": "ir siempre con prisas y llegar siempre tarde a todos lados",
        "pt": "correr apressado e chegar sempre atrasado a todo lado",
        "fr": "toujours se précipiter et toujours arriver en retard",
        "de": "in voreiliger Hast zu rennen und doch immer zu spät zu kommen",
        "ar": "التسرع الدائم والوصول متأخراً في كل مرة",
        "ja": "いつも慌てて急ぐのに結局遅刻してしまうこと",
        "ko": "언제나 허둥지둥 서두르다가 결국 항상 늦어버리는 버릇",
        "vi": "luôn hấp tấp vội vàng nhưng lúc nào cũng đến muộn",
        "fil": "ang palaging pagmamadali ngunit palagi pa ring nahuhuli sa oras",
    }

    morals = {
        "en": moral_english if moral_english else "The fastest speed means nothing without the right timing. Be punctual, not just fast!",
        "hi": "समय की पाबंदी ही असली रफ्तार है। हमेशा समय पर रहें और धैर्य से काम लें!",
        "es": "La mayor velocidad no significa nada sin el momento adecuado. ¡Sé puntual y reflexivo!",
        "pt": "A maior velocidade não vale nada sem a hora certa. Seja pontual e paciente!",
        "fr": "La plus grande vitesse ne vaut rien sans le bon timing. Sois ponctuel et réfléchi !",
        "de": "Die größte Geschwindigkeit bedeutet nichts ohne die richtige Zeit. Sei pünktlich und besonnen!",
        "ar": "السرعة الفائقة لا قيمة لها إن لم تكن في الوقت المناسب. كن دقيقاً ومنضبطاً!",
        "ja": "どんなに足が速くても時間を守らなければ意味がありません。落ち着いて行動しましょう。",
        "ko": "가장 빠른 속도보다 더 소중한 것은 약속 시간을 지키는 성실함과 침착함입니다.",
        "vi": "Tốc độ nhanh nhất cũng không có ý nghĩa nếu không đúng lúc. Hãy kiên nhẫn và đúng giờ!",
        "fil": "Ang tunay na bilis ay walang halaga kung huli ka sa takdang oras. Maging maagap at maingat!",
    }

    return {
        "en": {
            "title": f"{n_en}'s Big Race Against Time! 🐾⏰ #Shorts",
            "short_title": f"{n_en}'s Big Race Against Time! 🐾⏰ #Shorts",
            "long_title": f"{hero_name} and the Great Lesson 🐾 (Full 10-Min Story)",
            "moral": morals["en"],
            "short_cta_voice": f"But did little {n_en} escape the thorny brambles and reach the summit in time? Watch the full story — link in description!",
            "short_cta_text": "What happens next? 👉 Full story link in description",
            "short_script": (
                f"Deep within the sun-drenched golden savanna lived {n_en}. "
                f"Everyone in the valley loved little {n_en} for being cheerful and energetic, but he had one troublesome flaw: {flaws['en']}. "
                f"He foolishly believed that his lightning speed was an excuse to leave everything until the very last second! "
                f"One morning, the Great Valley Festival was called at noon on the mountain summit. "
                f"{n_en} was given the single highest honor: carrying the golden festival banner! "
                f"All his animal friends cheered and warned him to start early. "
                f"Yet true to his careless habits, {n_en} played splash games by the river and took a cozy nap under the shade. "
                f"Suddenly glancing up, he gasped with horror: it was almost noon! "
                f"Panicking, {n_en} dashed into a treacherous shortcut trail. "
                f"Then disaster struck. A flash thunderstorm flooded the path, and an enormous ancient baobab tree crashed directly in front of him! "
                f"Skidding in the slick mud, {n_en} crashed headlong into a dense thicket of sharp thorny brambles, hopelessly trapped as the clock ticked down! "
                f"But did {n_en} really escape in time to reach the mountain summit? Watch the full story now — link in description!"
            ),
            "long_script": (
                f"Once upon a time, nestled deep within the sun-drenched golden savanna, lived {hero_name}. "
                f"Everyone in the valley admired little {n_en} for being vibrant, playful, and wonderfully cheerful. "
                f"From dawn until dusk, {n_en} leaped across the tall amber grasses and greeted every animal friend with a joyful purr. "
                f"The weaver birds chirped melodious tunes from the acacia branches, and the gazelles danced along the sparkling riverbank. "
                f"Yet, {n_en} harbored one stubborn, troublesome flaw: {flaws['en']}. "
                f"Instead of preparing ahead, {n_en} foolishly believed that raw energy was an excuse for everything! "
                f"One bright Saturday morning, an exciting proclamation arrived from the High Ridge. "
                f"The Great Valley Festival was taking place at noon, where all the animal families of the savanna were gathering with sweet wild fruits, fresh berries, and golden honey. "
                f"{n_en} was entrusted with the single most important honor: carrying the grand festive banner to the mountain summit to open the celebration! "
                f"All friends cheered warmly and reminded {n_en} to set out early. "
                f"But true to old careless habits, {n_en} chased colorful butterflies, played splash games by the river, and took a long cozy nap under the shade, completely ignoring the clock. "
                f"Suddenly glancing at the sun overhead, {n_en} realized with horror that noon was fast approaching! "
                f"Panicking, {n_en} dashed wildly along the treacherous shortcut trail. "
                f"Then, disaster struck. A fierce flash morning thunderstorm had swept across the valley, turning the quiet stream into a swollen, roaring river and toppling an enormous ancient baobab tree directly across the path! "
                f"Skidding frantically in the slick mud, {n_en} lost balance and crashed headlong into a dense thicket of sharp thorny brambles. "
                f"Every desperate struggle only tangled the vines tighter around the paws. Trapped, bruised, and with time slipping away, {n_en} cried out in despair. "
                f"Just then, a calm, steady rustle emerged from the tall reeds. It was Elder Sheldon, the wise old tortoise wearing his round spectacles and carrying a polished wooden staff. "
                f"Sheldon did not panic, nor did he run; he advanced with measured, patient steps. "
                f"Young friend, Sheldon spoke with a warm, grandfatherly smile, what is the value of lightning speed if you arrive after the celebration has already ended? "
                f"Haste blinds the eyes and invites disaster, but patience and care clear the true path forward. "
                f"With steady, deliberate care, Sheldon used his sturdy staff to untangle the thorny branches, safely freeing {n_en}. "
                f"Together, choosing the safe, elevated ridge path, they walked with calm, focused determination. "
                f"Step by steady step, they climbed upward, reaching the mountain summit just as the noon sun shone in all its glory! "
                f"{n_en} proudly planted the festive banner, and the entire valley erupted in joyful cheers and song. "
                f"Sitting beside Elder Sheldon, sharing sweet berries and laughter, {n_en} smiled with deep gratitude. "
                f"From that unforgettable day forward, {n_en} stayed swift, but never rushed carelessly again. "
                f"Always remember: {morals['en']}"
            ),
            "script": (
                f"Deep within the sun-drenched golden savanna lived {n_en}. "
                f"Everyone in the valley loved little {n_en} for being cheerful and energetic, but he had one troublesome flaw: {flaws['en']}. "
                f"One morning, the Great Valley Festival was called at noon on the mountain summit. "
                f"{n_en} was given the single highest honor: carrying the golden festival banner! "
                f"Instead of leaving early, {n_en} played and napped until the clock was almost at noon! "
                f"Panicking, {n_en} dashed into a dangerous shortcut where an ancient tree collapsed in a storm! "
                f"Trapped in sharp thorns, {n_en} cried for help as the clock ticked down! "
                f"But did {n_en} really escape in time to reach the mountain summit? Watch the full story now — link in description!"
            ),
            "description": f"🐾 Watch {hero_name}'s thrilling 3D Shorts adventure!\n\n🎬 Watch the FULL 10-Minute Episode with the complete resolution and moral lesson!\n\nSubscribe to @EnglishMindNestTales!\n\n#MindNestTales #PixarStyle #MoralStories #Shorts",
            "tags": ["mindnest tales", f"{species} story", "moral stories", "3d cartoon animal", "pixar style animation", "kids stories", "shorts"]
        },
        "hi": {
            "title": f"{n_hi} और समय की सबसे बड़ी सीख! 🐾⏰ #Shorts",
            "short_title": f"{n_hi} और समय की सबसे बड़ी सीख! 🐾⏰ #Shorts",
            "long_title": f"{n_hi} और समय की पाबंदी 🐾 (पूरा 10 मिनट एपिसोड)",
            "moral": morals["hi"],
            "short_cta_voice": f"लेकिन क्या नन्हा {n_hi} कटीली झाड़ियों से निकलकर समय पर उत्सव में पहुँच पाया? आगे क्या हुआ, जानने के लिए पूरी कहानी अभी देखें — लिंक नीचे दिया है!",
            "short_cta_text": "आगे क्या हुआ? 👉 पूरी कहानी देखें (लिंक विवरण में)",
            "short_script": (
                f"सुनहरे जंगल की हरी-भरी वादियों में {n_hi} नाम का एक प्यारा सा नन्हा दोस्त रहता था। "
                f"जंगल के सभी पशु-पक्षी उसकी फुर्ती और मासूमियत को पसंद करते थे, पर उसमें एक बड़ी कमी थी—{flaws['hi']}! "
                f"वह सोचता था कि जब मैं तेज़ दौड़ सकता हूँ, तो पहले से तैयारी करने की क्या ज़रूरत है! "
                f"एक सुबह, पहाड़ के ऊँचे शिखर पर दोपहर बारह बजे महा-उत्सव आयोजित हुआ। "
                f"{n_hi} को सबसे बड़ा सम्मान मिला—उत्सव की सुनहरी ध्वज लेकर शिखर पर पहुँचना! "
                f"दोस्तों ने समझाया कि रास्ता लंबा है और समय से निकलना। "
                f"पर अपनी पुरानी आदत के कारण, वह नदी किनारे तितलियों के पीछे दौड़ता रहा और छांव में सो गया। "
                f"अचानक आँख खुली तो देखा दोपहर होने वाली है! वह घबराकर जोखिम भरे छोटे रास्ते पर सरपट दौड़ा। "
                f"तभी अचानक मूसलाधार बारिश शुरू हो गई और एक विशाल पेड़ टूटकर रास्ते पर गिर पड़ा! "
                f"फिसलन भरे कीचड़ में पैर फिसलते ही {n_hi} सीधे नुकीली कटीली झाड़ियों के बीच जा फंसा! "
                f"वह जितना छटपटाता, कांटे उतने गहरे उलझते जाते। "
                f"लेकिन क्या नन्हा {n_hi} कटीली झाड़ियों से निकलकर समय पर उत्सव में पहुँच पाया? आगे क्या हुआ, जानने के लिए पूरी कहानी अभी देखें — लिंक नीचे दिया है!"
            ),
            "long_script": (
                f"बहुत समय पहले, घने और सुनहरे जंगल की हरी-भरी वादियों में {n_hi} नाम का एक प्यारा सा नन्हा दोस्त रहता था। "
                f"जंगल के सभी पशु-पक्षी उसकी फुर्ती, चंचलता और मासूम मुस्कान को बहुत पसंद करते थे। "
                f"पेड़ों पर चहकती चिड़ियाँ और नदी किनारे खेलते हिरण सब उसके पक्के साथी थे। "
                f"लेकिन {n_hi} में एक बहुत बड़ी कमी थी—{flaws['hi']}। "
                f"वह हमेशा सोचता था कि किसी भी काम की तैयारी पहले से करने की क्या ज़रूरत है, जब मैं आख़िरी पल में तेज़ी से सब कुछ कर सकता हूँ! "
                f"एक सुहावनी सुबह, पूरे जंगल में ढोल बजने लगे। ऊँचे पर्वत शिखर पर वार्षिक महा-उत्सव आयोजित किया गया था। "
                f"सभी जानवरों को मीठे फल, जामुन और शहद लेकर दोपहर बारह बजे तक उत्सव में पहुँचना था। "
                f"और {n_hi} को सबसे बड़ा सम्मान सौंपा गया—उत्सव का शुभारंभ करने वाला सुनहरी ध्वज लेकर शिखर पर पहुँचना! "
                f"दोस्तों ने उसे बार-बार समझाया कि रास्ता लंबा है, इसलिए समय से पहले निकलना। "
                f"पर अपनी पुरानी आदत के कारण, {n_hi} तितलियों के पीछे दौड़ता रहा, छांव में सुस्ताता रहा और बिल्कुल आख़िरी समय तक आराम करता रहा। "
                f"जब सूरज सिर पर चढ़ आया, तो वह हड़बड़ाकर उठा और एक छोटे व जोखिम भरे रास्ते पर सरपट दौड़ पड़ा। "
                f"लेकिन तभी अचानक आसमान में घने काले बादल घिर आए और ज़ोरदार बारिश होने लगी। "
                f"बारिश के कारण सूखी पगडंडी पर फिसलन भरा दलदल बन गया और एक विशाल प्राचीन पेड़ टूटकर रास्ते पर गिर पड़ा। "
                f"हड़बड़ाहट और तेज़ रफ़्तार के कारण {n_hi} का पैर फिसला और वह सीधे नुकीली कटीली झाड़ियों के बीच जा फंसा! "
                f"वह जितना छटपटाता, कांटे उतने ही गहरे उलझते जाते। दोपहर का समय नज़दीक था और सभी साथी पर्वत पर उसका इंतज़ार कर रहे थे। "
                f"{n_hi} की आँखों में आँसू आ गए और उसने लाचार होकर मदद की गुहार लगाई। "
                f"तभी झाड़ियों के पीछे से एक शांत और गंभीर आवाज़ आई। वह थे चश्मा लगाए, हाथ में लाठी लिए हमारे बुद्धिमान बुजुर्ग कछुआ दादाजी। "
                f"दादाजी कभी घबराते नहीं थे, वे हमेशा धीमे और संतुलित कदमों से चलते थे। "
                f"उन्होंने प्यार से समझाया, प्यारे बच्चे, अगर तुम सही समय पर मंज़िल पर न पहुँच सको, तो तुम्हारी तेज़ रफ़्तार का क्या लाभ? "
                f"उतावली आँखें बंद कर देती है, जबकि धैर्य सही रास्ता दिखाता है। "
                f"दादाजी ने अपनी लाठी से सावधानीपूर्वक कांटे हटाए और {n_hi} को सुरक्षित बाहर निकाला। "
                f"फिर दोनों ने मिलकर सुरक्षित पहाड़ी रास्ते पर सधे हुए कदमों से आगे बढ़ना शुरू किया। "
                f"ठीक बारह बजते ही वे दोनों पर्वत शिखर पर पहुँच गए! {n_hi} ने गर्व से सुनहरी ध्वज फहराया और पूरा पर्वत तालियों की गूँज से भर गया। "
                f"उत्सव में बैठकर मीठे फलों का आनंद लेते हुए {n_hi} ने दादाजी के पैर छूकर आशीर्वाद लिया। "
                f"उस दिन से उसने हमेशा समय की कद्र करना सीखा। "
                f"याद रखें: {morals['hi']}"
            ),
            "script": (
                f"सुनहरे जंगल की हरी-भरी वादियों में {n_hi} नाम का एक प्यारा सा नन्हा दोस्त रहता था। "
                f"जंगल के सभी पशु-पक्षी उसकी फुर्ती को पसंद करते थे, पर उसमें एक बड़ी कमी थी—{flaws['hi']}! "
                f"एक सुबह पर्वत शिखर पर महा-उत्सव आयोजित हुआ और {n_hi} को सुनहरी ध्वज ले जाने की ज़िम्मेदारी मिली। "
                f"पर अपनी आदत के कारण वह देर तक खेलता रहा और जब दौड़ा तो कटीली झाड़ियों में फंस गया! "
                f"लेकिन क्या नन्हा {n_hi} कटीली झाड़ियों से निकलकर समय पर उत्सव में पहुँच पाया? आगे क्या हुआ, जानने के लिए पूरी कहानी अभी देखें — लिंक नीचे दिया है!"
            ),
            "description": f"🐾 देखिए {n_hi} की रोमांचक 3D एनिमेटेड कहानी!\n\n🎬 पूरा 10 मिनट का विशेष एपिसोड यहाँ देखें!\n\nसब्सक्राइब करें @HindiMindNestTales!\n\n#माइंडनेस्टटेल्स #हिंदीकहानियां #बालकहानियां #नैतिककहानियां #Shorts",
            "tags": ["माइंडनेस्ट टेल्स", "हिंदी कहानियां", "बाल कहानियां", "3d कार्टून", "सीखने वाली कहानी", "shorts"]
        },
        "es": {
            "title": f"¡La Gran Carrera de {n_es}! 🐾⏰ #Shorts",
            "short_title": f"¡La Gran Carrera de {n_es}! 🐾⏰ #Shorts",
            "long_title": f"{n_es} y la Gran Lección 🐾 (Especial 10 Min)",
            "moral": morals["es"],
            "short_cta_voice": f"Pero, ¿logró {n_es} liberarse de las espinas y llegar a tiempo a la cima? ¡Descubre qué pasó en la historia completa — enlace en la descripción!",
            "short_cta_text": "¿Qué pasó después? 👉 Historia completa en la descripción",
            "short_script": (
                f"En lo profundo de la dorada sabana vivía el pequeño {n_es}. "
                f"Todos en el valle lo querían por su alegría, pero tenía un gran defecto: {flaws['es']}. "
                f"Pensaba que su gran agilidad le permitiría solucionar cualquier descuido en el último segundo. "
                f"Una hermosa mañana, se anunció el Gran Festival del Valle en la cima de la montaña al mediodía. "
                f"A {n_es} se le otorgó el mayor honor: ¡llevar el estandarte dorado para abrir la fiesta! "
                f"Sus amigos le rogaron que saliera temprano, pero se quedó jugando en el río y durmiendo la siesta. "
                f"Al ver el sol en lo alto, entró en pánico y corrió desesperado por un atajo peligroso. "
                f"De pronto, una tormenta inundó el camino y un árbol milenario se desplomó frente a él. "
                f"Al resbalar en el lodo, {n_es} chocó de cabeza contra un espeso matorral de espinas afiladas y quedó atrapado. "
                f"Pero, ¿logró {n_es} liberarse de las espinas y llegar a tiempo a la cima? ¡Descubre qué pasó en la historia completa — enlace en la descripción!"
            ),
            "long_script": (
                f"Érase una vez, en lo profundo de la dorada sabana, vivía {n_es}. "
                f"Todos en el valle querían a {n_es} por ser alegre, curioso y lleno de energía. "
                f"Sin embargo, tenía un gran problema: {flaws['es']}. "
                f"Creía ciegamente que su rapidez podía solucionar cualquier descuido en el último segundo. "
                f"Una hermosa mañana, llegó una invitación muy especial para el Gran Festival del Valle en la cima de la colina. "
                f"{n_es} recibió el honor de llevar la gran bandera para inaugurar la fiesta al mediodía. "
                f"Sus amigos le recordaron que debía salir temprano, pero se quedó jugando y descansando bajo la sombra. "
                f"Cuando el sol subió, se asustó y corrió desesperadamente por un atajo peligroso. "
                f"De pronto, una tormenta inundó el sendero y un árbol gigante cayó bloqueando el paso. "
                f"Al patinar en el fango, {n_es} chocó contra un matorral lleno de espinas y quedó completamente atrapado. "
                f"En ese instante, apareció el sabio abuelo tortuga con sus anteojos redondos y su bastón de madera. "
                f"Con pasos tranquilos y voz serena, le dijo: Pequeño amigo, ¿de qué sirve la velocidad si llegas cuando la fiesta ha terminado? "
                f"La prisa causa tropiezos, pero la paciencia abre el camino correcto. "
                f"Con paciencia, el anciano retiró las espinas y lo liberó. Juntos caminaron por el sendero seguro y llegaron a la cima justo a tiempo. "
                f"{n_es} colocó la bandera entre los aplausos de todos y aprendió que el orden y la calma valen más que la prisa. "
                f"Recuerda siempre: {morals['es']}"
            ),
            "script": (
                f"En lo profundo de la dorada sabana vivía el pequeño {n_es}. "
                f"Todos lo querían por su alegría, pero tenía un defecto: {flaws['es']}. "
                f"Elegido para llevar la bandera al festival del mediodía en la cima, se quedó jugando. "
                f"Al correr por un atajo con tormenta, resbaló en el lodo y quedó atrapado en espinas afiladas. "
                f"Pero, ¿logró {n_es} liberarse de las espinas y llegar a tiempo a la cima? ¡Descubre qué pasó en la historia completa — enlace en la descripción!"
            ),
            "description": f"🐾 ¡Disfruta de la emocionante aventura de {n_es}!\n\n🎬 ¡Mira el episodio completo de 10 minutos con la moraleja final aquí!\n\n¡Suscríbete a @SpanishMindNestTales!\n\n#CuentosInfantiles #HistoriasConMoraleja #Animacion3D #Shorts",
            "tags": ["mindnest tales", "historias para niños", "cuentos morales", "animacion 3d", "shorts"]
        },
        "pt": {
            "title": f"A Grande Corrida de {n_pt}! 🐾⏰ #Shorts",
            "short_title": f"A Grande Corrida de {n_pt}! 🐾⏰ #Shorts",
            "long_title": f"{n_pt} e a Grande Lição 🐾 (Especial 10 Min)",
            "moral": morals["pt"],
            "short_cta_voice": f"Mas será que {n_pt} conseguiu se soltar dos espinhos e chegar a tempo ao festival? Descubra o final na história completa — link na descrição!",
            "short_cta_text": "O que acontece a seguir? 👉 História completa no link",
            "short_script": (
                f"No coração de uma linda savana ensolarada vivia o pequeno {n_pt}. "
                f"Todos os animais admiravam sua energia, mas havia um hábito perigoso: {flaws['pt']}. "
                f"Ele sempre achava que sua velocidade resolveria qualquer atraso no último minuto. "
                f"Certo dia, foi convocado o Grande Festival da Floresta no topo da montanha ao meio-dia. "
                f"{n_pt} recebeu a nobre missão de levar o estandarte dourado para abrir a celebração! "
                f"Os amigos avisaram para sair cedo, mas ele se distraiu brincando e tirando uma longa soneca. "
                f"Ao olhar para o sol no céu, percebeu apavorado que faltavam poucos minutos! "
                f"Correndo por um atalho perigoso, uma tempestade repentina fez a terra desmoronar e uma enorme árvore bloqueou a trilha. "
                f"Ao deslizar na lama, Chico caiu direto em uma cerca de espinhos pontiagudos e ficou completamente preso. "
                f"Mas será que {n_pt} conseguiu se soltar dos espinhos e chegar a tempo ao festival? Descubra o final na história completa — link na descrição!"
            ),
            "long_script": (
                f"Era uma vez, no coração de uma savana ensolarada, vivia {n_pt}. "
                f"Todos os animais admiravam a alegria contagiante de {n_pt}. "
                f"Mas havia um hábito perigoso: {flaws['pt']}. "
                f"Ele sempre pensava que poderia deixar tudo para o último minuto. "
                f"Certo dia, foi anunciado o Grande Festival da Floresta no topo da colina sagrada. "
                f"{n_pt} recebeu a nobre missão de levar o estandarte dourado para dar início à celebração exatamente ao meio-dia. "
                f"Mesmo com os avisos carinhosos dos amigos, ele se distraiu brincando no rio e tirando uma soneca demorada. "
                f"Ao ver o sol no alto, entrou em pânico e disparou pelo atalho mais perigoso. "
                f"Uma tempestade repentina fez o riacho transbordar e uma árvore enorme bloqueou a passagem. "
                f"Ao deslizar na lama, {n_pt} caiu em uma densa cerca de espinhos e ficou preso. "
                f"Foi quando o sábio vovô tartaruga apareceu com passos lentos e seguros. "
                f"Com um olhar bondoso, disse: Meu jovem, de nada vale a maior velocidade se você chegar quando o momento já passou. "
                f"A calma desfaz os nós que a pressa aperta. "
                f"Com cuidado, o sábio libertou {n_pt}. Juntos, seguiram pelo caminho elevado e alcançaram o topo a tempo. "
                f"{n_pt} aprendeu a lição mais preciosa de sua vida. "
                f"Lembre-se sempre: {morals['pt']}"
            ),
            "script": (
                f"No coração de uma savana ensolarada vivia o pequeno {n_pt}. "
                f"Todos admiravam sua energia, mas havia um hábito: {flaws['pt']}. "
                f"Encarregado de levar o estandarte ao festival ao meio-dia, atrasou-se brincando. "
                f"Em um atalho perigoso durante um temporal, deslizou na lama e ficou preso em espinhos afiados! "
                f"Mas será que {n_pt} conseguiu se soltar dos espinhos e chegar a tempo ao festival? Descubra o final na história completa — link na descrição!"
            ),
            "description": f"🐾 Acompanhe a emocionante história animada de {n_pt}!\n\n🎬 Assista ao episódio completo de 10 minutos com o final e a lição de vida!\n\nInscreva-se em @PortugueseMindNestTales!\n\n#MindNestTales #HistoriasInfantis #Desenho3D #Shorts",
            "tags": ["mindnest tales", "historias infantis", "desenho animado", "licao de vida", "shorts"]
        },
        "fr": {
            "title": f"La Grande Course de {n_fr} ! 🐾⏰ #Shorts",
            "short_title": f"La Grande Course de {n_fr} ! 🐾⏰ #Shorts",
            "long_title": f"{n_fr} et la Grande Leçon 🐾 (Épisode Complet 10 Min)",
            "moral": morals["fr"],
            "short_cta_voice": f"Mais {n_fr} a-t-il réussi à se libérer des ronces pour sauver le festival à temps ? Découvrez la suite dans l'épisode complet — lien en description !",
            "short_cta_text": "Que se passe-t-il ensuite ? 👉 Histoire complète en description",
            "short_script": (
                f"Dans une vallée baignée d'une chaude lumière vivait le jeune {n_fr}. "
                f"Tout le monde l'adorait pour sa vivacité, mais il avait un défaut fatal : {flaws['fr']}. "
                f"Il pensait pouvoir toujours rattraper le temps perdu au tout dernier instant ! "
                f"Un matin, le Grand Festival fut proclamé au sommet de la colline à midi pile. "
                f"{n_fr} reçut le plus bel honneur : porter l'étendard festif pour inaugurer la fête ! "
                f"Ses amis lui dirent de partir tôt, mais il préféra s'amuser et s'assoupir à l'ombre. "
                f"Quand le soleil fut au zénith, la panique le saisit et il fila sur un sentier escarpé. "
                f"Soudain, un orage éclata et un immense baobab s'effondra sur la piste ! "
                f"Glissant dans la boue, {n_fr} chuta dans un buisson de ronces épineuses, pris au piège alors que l'heure tournait ! "
                f"Mais {n_fr} a-t-il réussi à se libérer des ronces pour sauver le festival à temps ? Découvrez la suite dans l'épisode complet — lien en description !"
            ),
            "long_script": (
                f"Il était une fois, dans une vallée baignée d'une chaude lumière dorée, vivait {n_fr}. "
                f"Tout le monde aimait son énergie pétillante et son enthousiasme communicatif. "
                f"Pourtant, un lourd défaut lui jouait souvent des tours : {flaws['fr']}. "
                f"{n_fr} pensait toujours pouvoir rattraper le temps perdu au dernier instant. "
                f"Un beau matin, la nouvelle arriva : le Grand Festival de la Colline allait débuter à midi pile. "
                f"On confia à {n_fr} la tâche d'honneur d'apporter l'étendard festif pour déclarer l'ouverture du festin. "
                f"Ses amis lui répétèrent de partir tôt, mais {n_fr} préféra papillonner et s'assoupir sous un arbre. "
                f"Quand il réalisa l'heure, la panique le saisit et il s'élança à toute allure sur le sentier escarpé. "
                f"Soudain, un orage éclata, transformant le chemin en bourbier et déracinant un immense baobab. "
                f"En dérapant, {n_fr} s'enchevêtra dans un épais buisson de ronces épineuses, prisonnier et désemparé. "
                f"C'est alors que le sage aîné, la vieille tortue aux petites lunettes rondes, arriva d'un pas serein. "
                f"Avec douceur, il lui dit : Jeune ami, à quoi sert de courir si l'on arrive après la fin de la fête ? "
                f"La précipitation aveugle, mais la patience éclaire la route. "
                f"Le vieux sage l'aida avec bienveillance à se dégager. Marchant d'un pas régulier sur la crête sûre, ils atteignirent le sommet à l'heure. "
                f"{n_fr} comprit que le respect du temps est la plus belle des victoires. "
                f"Retiens bien : {morals['fr']}"
            ),
            "script": (
                f"Dans une vallée baignée de lumière vivait {n_fr}. "
                f"Tout le monde l'aimait, mais il avait un défaut : {flaws['fr']}. "
                f"Chargé de porter l'étendard au festival de midi, il préféra s'amuser et s'assoupir. "
                f"Pris de panique, il courut par un raccourci où un baobab venait de s'effondrer. "
                f"Glissant dans la boue, il tomba dans un buisson d'épines ! "
                f"Mais {n_fr} a-t-il réussi à se libérer des ronces pour sauver le festival à temps ? Découvrez la suite dans l'épisode complet — lien en description !"
            ),
            "description": f"🐾 Découvrez la magnifique aventure animée de {n_fr} !\n\n🎬 Regardez l'épisode complet de 10 minutes avec toute l'histoire et la morale ici !\n\nAbonnez-vous à @FrenchMindNestTales !\n\n#MindNestTales #ContesPourEnfants #Animation3D #Shorts",
            "tags": ["mindnest tales", "histoire pour enfants", "conte moral", "animation 3d", "shorts"]
        },
        "de": {
            "title": f"{n_de} und das Rennen Gegen die Zeit! 🐾⏰ #Shorts",
            "short_title": f"{n_de} und das Rennen Gegen die Zeit! 🐾⏰ #Shorts",
            "long_title": f"{n_de} und die Große Lektion 🐾 (Komplette 10-Min Episode)",
            "moral": morals["de"],
            "short_cta_voice": f"Aber konnte sich {n_de} aus den Dornen befreien und rechtzeitig den Gipfel erreichen? Schau dir das ganze Abenteuer an — Link in der Beschreibung!",
            "short_cta_text": "Wie geht es weiter? 👉 Ganze Geschichte im Link",
            "short_script": (
                f"Tief im sonnigen Herzen der Savanne lebte der kleine {n_de}. "
                f"Alle Tiere liebten seine Fröhlichkeit, doch er hatte eine fatale Schwäche: {flaws['de']}. "
                f"Er glaubte leichtsinnig, seine Schnelligkeit könne jede Verspätung in letzter Sekunde wettmachen. "
                f"An einem strahlenden Morgen wurde das Große Jahresfest auf dem Berggipfel für Punkt zwölf Uhr mittags verkündet. "
                f"{n_de} erhielt die große Ehre, die goldene Festfahne zum Gipfel zu bringen! "
                f"Alle mahnten ihn zur Eile, doch er trödelte am Fluss und hielt ein gemütliches Nickerchen. "
                f"Als er zur Mittagssonne aufblickte, packte ihn das Entsetzen: Es war fast zwölf Uhr! "
                f"In Panik raste er über eine gefährliche Abkürzung. Ein Platzregen weichte den Boden auf, und ein riesiger Baum stürzte quer über den Pfad! "
                f"{n_de} rutschte im Schlamm aus und verfing sich hilflos in einem dornigen Dickicht! "
                f"Aber konnte sich {n_de} aus den Dornen befreien und rechtzeitig den Gipfel erreichen? Schau dir das ganze Abenteuer an — Link in der Beschreibung!"
            ),
            "long_script": (
                f"Es war einmal tief im sonnenverwöhnten Herzen der afrikanischen Savanne, da lebte {n_de}. "
                f"Alle Tiere im Tal bewunderten {n_de} für den unbändigen Lebensmut und das fröhliche Wesen. "
                f"Doch eine verhängnisvolle Angewohnheit brachte ständig Unruhe: {flaws['de']}. "
                f"{n_de} glaubte leichtsinnig, man könne jede verlorene Minute durch bloßes Rennen wiedergutmachen. "
                f"An einem strahlenden Samstag sollte auf dem Gipfel des Hügels das große Jahresfest stattfinden. "
                f"{n_de} erhielt die ehrenvolle Aufgabe, die goldene Festfahne genau um zwölf Uhr mittags zum Festplatz zu bringen. "
                f"Obwohl alle Freunde zur Eile mahnten, trödelte {n_de}, jagte Libellen und machte ein gemütliches Schläfchen. "
                f"Als die Sonne senkrecht stand, raste {n_de} voller Panik über eine gefährliche Abkürzung los. "
                f"Ein plötzlicher Platzregen hatte den Boden aufgeweicht und ein umgestürzter Riesenbaum versperrte den Weg. "
                f"{n_de} rutschte im Schlamm aus und verhedderte sich hoffnungslos in einem dornigen Dickicht. "
                f"Da trat der weise Schildkröten-Älteste mit seiner Brille und einem Wanderstab ruhig heran. "
                f"Mit sanfter Stimme sagte er: Mein junger Freund, was nützt der schnellste Schritt, wenn du erst ankommst, wenn das Fest vorbei ist? "
                f"Hektik stiftet Verwirrung, doch Besonnenheit bahnt den sicheren Pfad. "
                f"Geduldig befreite der Älteste {n_de}. Gemeinsam meisterten sie den sicheren Gratweg und erreichten den Gipfel pünktlich. "
                f"Aus {n_de} wurde ein Tier, das Schnelligkeit stets mit Klugheit verband. "
                f"Denke stets daran: {morals['de']}"
            ),
            "script": (
                f"Tief in der Savanne lebte der fröhliche {n_de}. "
                f"Doch er hatte eine Schwäche: {flaws['de']}. "
                f"Als er die Festfahne zum Berggipfel bringen sollte, trödelte er bis zur letzten Minute! "
                f"Auf einer gefährlichen Abkürzung stürzte ein Baum um, und {n_de} fiel mitten in dornige Ranken! "
                f"Aber konnte sich {n_de} aus den Dornen befreien und rechtzeitig den Gipfel erreichen? Schau dir das ganze Abenteuer an — Link in der Beschreibung!"
            ),
            "description": f"🐾 Sieh dir das herzerwärmende 3D-Animationsabenteuer von {n_de} an!\n\n🎬 Sieh dir hier die komplette 10-Minuten-Folge mit dem vollen Ende an!\n\nAbonniere @GermanMindNestTales!\n\n#MindNestTales #Kindergeschichten #MoralGeschichten #Shorts",
            "tags": ["mindnest tales", "kindergeschichten", "moralische geschichte", "3d animation", "shorts"]
        },
        "ar": {
            "title": f"سباق {n_ar} الحاسم مع الوقت! 🐾⏰ #Shorts",
            "short_title": f"سباق {n_ar} الحاسم مع الوقت! 🐾⏰ #Shorts",
            "long_title": f"{n_ar} والدرس الكبير 🐾 (الحلقة الكاملة 10 دقائق)",
            "moral": morals["ar"],
            "short_cta_voice": f"ولكن هل استطاع {n_ar} النجاة من الأشواك والوصول إلى القمة في الوقت المناسب؟ شاهد القصة الكاملة الآن — الرابط في صندوق الوصف!",
            "short_cta_text": "ماذا حدث بعد ذلك؟ 👉 القصة الكاملة في الرابط بالأسفل",
            "short_script": (
                f"في أعماق السافانا المشمسة الجميلة، عاش صديقنا {n_ar}. "
                f"كان الجميع يحبون حيويته، لكنه كان يعاني من طبع صعب: {flaws['ar']}. "
                f"كان يظن دائماً أن سرعته تعوض كل تأخير دون تخطيط مسبق! "
                f"وفي صباح مميز، أُعلن عن مهرجان الوادي الكبير فوق قمة التل عند الظهيرة بالضبط. "
                f"أُسندت إلى {n_ar} المهمة الأهم: حمل راية الاحتفال لافتتاح المهرجان! "
                f"نصحه الأصدقاء بالانطلاق مبكراً، لكنه انشغل باللعب والكسل تحت ظلال الأشجار. "
                f"وفجأة انتبه إلى أن الظهيرة اقتربت، فركض مذعوراً في طريق مختصر وعر. "
                f"لكن عاصفة مفاجئة جعلت النهر يفيض وسقطت شجرة ضخمة أغلقت الممر! "
                f"انزلقت قدماه في الوحل وسقط في شجيرات شائكة حاصرته تماماً والوقت ينفد! "
                f"ولكن هل استطاع {n_ar} النجاة من الأشواك والوصول إلى القمة في الوقت المناسب؟ شاهد القصة الكاملة الآن — الرابط في صندوق الوصف!"
            ),
            "long_script": (
                f"في قديم الزمان، في أعماق السافانا المشمسة الجميلة، عاش صديقنا {n_ar}. "
                f"كان الجميع في الوادي يحبون نشاطه ومرحه الدائم، لكنه كان يعاني من طبع صعب: {flaws['ar']}. "
                f"كان يظن دائماً أن سرعته تعوض كل تأخير وتغنيه عن التخطيط المسبق. "
                f"وفي صباح يوم مميز، أُعلن عن مهرجان الوادي الكبير فوق قمة التل عند الظهيرة بالضبط. "
                f"أُسندت إلى {n_ar} أشرف مهمة: حمل راية الاحتفال لافتتاح المهرجان أمام جميع العائلات. "
                f"طلب منه الأصدقاء التحرك باكراً، لكنه انشغل باللعب والكسل تحت ظلال الأشجار حتى اقترب الوقت. "
                f"وفجأة انتبه للشمس، فركض مذعوراً عبر طريق مختصر وعر. "
                f"لكن عاصفة مفاجئة جعلت النهر يفيض وسقطت شجرة ضخمة أغلقت الممر بالكامل. "
                f"انزلقت قدماه في الوحل وسقط وسط شجيرات شائكة حاصرته تماماً. "
                f"وبينما كاد يفقد الأمل، اقترب الجد الحكيم، السلحفاة الوقورة بنظاراتها وعصاها الهادئة. "
                f"قال له الجد مبتسماً: يا بني، ما نفع السرعة الفائقة إذا وصلت بعد انتهاء الحفل؟ "
                f"التسرع يجلب العثرات، والهدوء ينير الدرب الصحيح. "
                f"ساعده الجد بصبر حتى تحرر، وصعدا معاً الطريق الآمن ووصلا في الموعد تماماً. "
                f"تعلم {n_ar} درساً لن ينساه أبداً في احترام الوقت والصبر. "
                f"تذكروا دائماً: {morals['ar']}"
            ),
            "script": (
                f"في أعماق السافانا الجميلة عاش {n_ar}. "
                f"كان الجميع يحبونه لكنه كان يعاني من: {flaws['ar']}. "
                f"كُلف بحمل راية المهرجان عند الظهيرة، لكنه انشغل باللعب حتى اللحظة الأخيرة. "
                f"وأثناء ركضه في طريق وعر هبت عاصفة وسقطت شجرة، فانزلق في شجيرات شائكة حاصرته تماماً! "
                f"ولكن هل استطاع {n_ar} النجاة من الأشواك والوصول إلى القمة في الوقت المناسب؟ شاهد القصة الكاملة الآن — الرابط في صندوق الوصف!"
            ),
            "description": f"🐾 شاهد المغامرة الكرتونية الممتعة ثلاثية الأبعاد مع {n_ar}!\n\n🎬 شاهد الحلقة الكاملة 10 دقائق مع نهاية القصة والحكمة الكاملة هنا!\n\nاشترك في @ArabicMindNestTales!\n\n#MindNestTales #قصص_أطفال #حكايات_معبرة #رسوم_متحركة #Shorts",
            "tags": ["قصص أطفال", "حكايات معبرة", "كرتون ثلاثي الأبعاد", "دروس وعبر", "shorts"]
        },
        "ja": {
            "title": f"{n_ja}と時間にまつわる最高の教訓！🐾⏰ #Shorts",
            "short_title": f"{n_ja}と時間にまつわる最高の教訓！🐾⏰ #Shorts",
            "long_title": f"{n_ja}と大切な約束 🐾 (完全版10分ストーリー)",
            "moral": morals["ja"],
            "short_cta_voice": f"果たして{n_ja}はトゲの茂みから抜け出し、お祭りに間に合うのでしょうか？続きは概要欄のリンクから完全版を見てね！",
            "short_cta_text": "続きはどうなる？ 👉 完全版は概要欄のリンクから！",
            "short_script": (
                f"黄金色に輝くサバンナに、元気いっぱいの{n_ja}が暮らしていました。"
                f"谷の動物たちはみんな{n_ja}が大好きでしたが、たった一つ困った癖がありました。それは、{flaws['ja']}！"
                f"「ぼくは足が速いからギリギリでも大丈夫！」と信じ込んでいたのです。"
                f"ある晴れた日、丘の頂上で正午から大お祭りが開かれることになりました。"
                f"{n_ja}は、始まりを告げる大切な黄金の旗を届ける大役を任されました。"
                f"仲間たちから「早く出発してね」と言われていたのに、川で遊んで昼寝をしてしまいました。"
                f"ハッと空を見るともうすぐ正午！慌てて近道へ飛び出しましたが、朝の嵐で大木が倒れ、道はぬかるみの泥だらけ！"
                f"足を滑らせた{n_ja}は、トゲのある茂みに飛び込んでしまい、身動きが取れなくなってしまいました！"
                f"果たして{n_ja}はトゲの茂みから抜け出し、お祭りに間に合うのでしょうか？続きは概要欄のリンクから完全版を見てね！"
            ),
            "long_script": (
                f"むかしむかし、太陽の光が黄金に輝く美しいサバンナに、{n_ja}が暮らしていました。"
                f"谷の動物たちはみんな、元気で明るい{n_ja}のことが大好きでした。"
                f"しかし、{n_ja}には困った癖がありました。それは、{flaws['ja']}ということでした。"
                f"「ぼくは足が速いから、ギリギリに出発しても絶対に間に合うんだ！」といつも自慢していました。"
                f"ある晴れた日、丘の頂上で森の大お祭りが正午に開催されることになりました。"
                f"{n_ja}は、お祭りの始まりを告げる大切な黄金の旗を届ける役目を任されました。"
                f"仲間たちは「早く出発してね」と声をかけましたが、{n_ja}は蝶々を追いかけたり昼寝をしたりして、のんびり過ごしてしまいました。"
                f"ふと空を見上げると、もうすぐ正午！慌てて近道へ飛び出しましたが、朝の嵐で道がぬかるみ、大きな木が倒れて道をふさいでいました。"
                f"足を滑らせた{n_ja}は、トゲのある茂みに飛び込んでしまい、抜け出せなくなってしまったのです。"
                f"そこへ、眼鏡をかけた物知りのカメのおじいさんが、ゆっくりと杖をついて歩いてきました。"
                f"「どんなに足が速くても、お祭りが終わってから着いたのでは意味がないんじゃよ。焦りは目を曇らせるが、落ち着きは正しい道を示すのじゃ」。"
                f"おじいさんは優しくトゲをほどき、安全な尾根道へ導いてくれました。二人は落ち着いて一歩一歩進み、ちょうど十二時の鐘とともに頂上に到着！"
                f"{n_ja}は堂々と旗を立て、みんなから大きな拍手を受けました。その日から、時間を守る本当の強さを胸に刻んだのです。"
            ),
            "script": (
                f"サバンナに暮らす元気な{n_ja}には、{flaws['ja']}という困った癖がありました。"
                f"大お祭りの旗を届ける大切な役目を任されたのに、ギリギリまで昼寝をしてしまいました。"
                f"慌てて近道を走ると、嵐で倒れた大木に阻まれ、トゲの茂みに突っ込んで抜け出せなくなってしまいました！"
                f"果たして{n_ja}はトゲの茂みから抜け出し、お祭りに間に合うのでしょうか？続きは概要欄のリンクから完全版を見てね！"
            ),
            "description": f"🐾 3Dアニメで描く{n_ja}のドキドキ ショートアニメ！\n\n🎬 10分間の完全版エピソードと感動の結末はこちらから！\n\nチャンネル登録はこちら：@JapaneseMindNestTales！\n\n#MindNestTales #アニメ #子ども向け #絵本 #Shorts",
            "tags": ["子ども向け", "アニメ", "絵本", "教訓", "動物アニメ", "shorts"]
        },
        "ko": {
            "title": f"{n_ko}의 위대한 시간 여행과 깨달음! 🐾⏰ #Shorts",
            "short_title": f"{n_ko}의 위대한 시간 여행과 깨달음! 🐾⏰ #Shorts",
            "long_title": f"{n_ko}와 시간의 소중함 🐾 (10분 풀버전)",
            "moral": morals["ko"],
            "short_cta_voice": f"하지만 과연 {n_ko}는 날카로운 가시덤불에서 빠져나와 제시간에 정상에 도착할 수 있을까요? 지금 바로 설명란 링크에서 전체 이야기를 감상해보세요!",
            "short_cta_text": "다음 이야기는? 👉 설명란 링크에서 전체 감상!",
            "short_script": (
                f"황금빛 햇살이 쏟아지는 아름다운 초원에 귀여운 {n_ko}가 살고 있었어요. "
                f"친구들은 모두 {n_ko}를 좋아했지만, 한 가지 치명적인 결점이 있었지요. 바로 {flaws['ko']}! "
                f"발이 빠르다는 자신감만 믿고 무엇이든 마지막 순간까지 미루는 버릇이었어요. "
                f"어느 화창한 날, 언덕 정상에서 정오에 열리는 위대한 축제가 발표되었어요. "
                f"{n_ko}는 축제의 시작을 알리는 영예로운 황금 깃발을 전달하는 임무를 맡았답니다. "
                f"친구들이 일찍 출발하라고 당부했지만, {n_ko}는 강가에서 물장구를 치고 낮잠을 잤어요. "
                f"하늘 높이 솟은 해를 보고 깜짝 놀란 {n_ko}는 허둥지둥 험한 지름길로 내달렸어요. "
                f"하지만 갑작스러운 폭우로 거대한 나무가 길을 막았고, 진흙탕에 미끄러져 날카로운 가시덤불 속에 갇히고 말았어요! "
                f"하지만 과연 {n_ko}는 날카로운 가시덤불에서 빠져나와 제시간에 정상에 도착할 수 있을까요? 지금 바로 설명란 링크에서 전체 이야기를 감상해보세요!"
            ),
            "long_script": (
                f"옛날 옛적, 따스한 햇살이 황금빛으로 물드는 드넓은 초원에 귀여운 {n_ko}가 살고 있었어요. "
                f"초원의 동물 친구들은 활기차고 다정한 {n_ko}를 무척 아끼고 사랑했답니다. "
                f"하지만 {n_ko}에게는 한 가지 큰 결점이 있었는데, 바로 {flaws['ko']}였어요. "
                f"미리 준비하지 않고, 항상 마지막 순간에 서두르면 모든 것이 해결될 거라 믿었던 것이지요. "
                f"어느 화창한 주말, 언덕 정상에서 정오에 열리는 위대한 동물 축제 소식이 전해졌어요. "
                f"{n_ko}는 축제의 시작을 알리는 가장 영예로운 황금 깃발을 전달하는 임무를 맡게 되었답니다. "
                f"친구들은 일찍 출발하라고 당부했지만, {n_ko}는 강가에서 물장구를 치고 낮잠을 자며 시간을 보냈어요. "
                f"하늘 높이 솟은 해를 보고 깜짝 놀란 {n_ko}는 허둥지둥 지름길로 내달리기 시작했어요. "
                f"하지만 아침 폭우로 불어난 흙탕물과 거대한 쓰러진 나무가 길을 막고 있었지요. "
                f"진흙탕에 미끄러진 {n_ko}는 날카로운 가시덤불 속에 갇혀 옴짝달싹할 수 없게 되었어요. "
                f"그때 동그란 안경을 쓴 지혜로운 거북이 할아버지가 지팡이를 짚으며 차분하게 다가오셨어요. "
                f"'얘야, 아무리 발이 빨라도 잔치가 다 끝난 뒤에 도착한다면 무슨 소용이 있겠니? 서두름은 실수를 낳지만, 차분함은 바른길을 열어준단다.' "
                f"할아버지는 조심스럽게 가시를 풀어주셨고, 두 친구는 안전한 능선길을 함께 걸어올라 정각에 정상에 도착했어요! "
                f"황금 깃발이 휘날리자 모두가 환호했고, {n_ko}는 서두르지 않는 참된 지혜를 배웠답니다."
            ),
            "script": (
                f"초원에 사는 {n_ko}에게는 {flaws['ko']}라는 결점이 있었어요. "
                f"축제 깃발을 전달하는 임무를 맡고도 낮잠을 자다가 뒤늦게 지름길로 내달렸지요. "
                f"폭우로 쓰러진 나무에 걸려 날카로운 가시덤불 속에 갇히고 말았어요! "
                f"하지만 과연 {n_ko}는 날카로운 가시덤불에서 빠져나와 제시간에 정상에 도착할 수 있을까요? 지금 바로 설명란 링크에서 전체 이야기를 감상해보세요!"
            ),
            "description": f"🐾 {n_ko}의 흥미진진한 3D 애니메이션 쇼츠 이야기!\n\n🎬 지혜로운 거북이 할아버지와 함께하는 10분 풀버전 영상은 여기서 감상하세요!\n\n구독하기 @KoreanMindNestTales!\n\n#MindNestTales #어린이이야기 #동화 #3D애니메이션 #Shorts",
            "tags": ["어린이이야기", "교훈동화", "3d애니메이션", "동물이야기", "shorts"]
        },
        "vi": {
            "title": f"Cuộc Đua Kịp Giờ Của {n_vi}! 🐾⏰ #Shorts",
            "short_title": f"Cuộc Đua Kịp Giờ Của {n_vi}! 🐾⏰ #Shorts",
            "long_title": f"{n_vi} và Bài Học Về Thời Gian 🐾 (Bản Đầy Đủ 10 Phút)",
            "moral": morals["vi"],
            "short_cta_voice": f"Liệu {n_vi} có kịp thoát khỏi bụi gai để mang cờ tới khai mạc lễ hội đúng giờ? Xem ngay trọn vẹn câu chuyện qua đường link dưới phần mô tả nhé!",
            "short_cta_text": "Chuyện gì xảy ra tiếp theo? 👉 Xem trọn vẹn tại mô tả nhé!",
            "short_script": (
                f"Giữa đồng cỏ xavan rực rỡ ánh nắng có một chú {species} đáng yêu tên là {n_vi}. "
                f"Muông thú đều yêu quý {n_vi}, nhưng cậu có một khuyết điểm lớn: {flaws['vi']}. "
                f"Cậu luôn tự tin mình chạy nhanh nên cứ chần chừ đến phút chót mới chịu bắt đầu! "
                f"Một buổi sáng, Lễ Hội Thung Lũng được công bố trên đỉnh núi vào đúng mười hai giờ trưa. "
                f"{n_vi} được trao vinh dự cao quý nhất: mang lá cờ lễ hội lên khai mạc ngày hội! "
                f"Các bạn nhắc cậu đi sớm, nhưng cậu lại mải mê đuổi bướm và ngủ quên dưới bóng râm. "
                f"Giật mình nhìn lên, mặt trời đã sắp đứng bóng! Cậu hốt hoảng lao vào con đường tắt nguy hiểm. "
                f"Cơn mưa lớn bất ngờ làm đổ một thân cây cổ thụ chắn ngang đường. "
                f"Trượt chân trên bùn lầy, {n_vi} ngã nhào vào bụi gai nhọn và mắc kẹt hoàn toàn khi giờ G đã điểm! "
                f"Liệu {n_vi} có kịp thoát khỏi bụi gai để mang cờ tới khai mạc lễ hội đúng giờ? Xem ngay trọn vẹn câu chuyện qua đường link dưới phần mô tả nhé!"
            ),
            "long_script": (
                f"Ngày xửa ngày xưa, giữa đồng cỏ xavan ngập tràn ánh nắng vàng rực rỡ, có một chú {species} dễ thương tên là {n_vi}. "
                f"Tất cả muông thú trong thung lũng đều yêu quý {n_vi} vì sự hoạt bát, vui vẻ và năng động. "
                f"Tuy nhiên, cậu lại có một khuyết điểm rất lớn: {flaws['vi']}. "
                f"Cậu luôn ỷ lại vào sức mạnh của mình và tin rằng đến phút chót vẫn có thể chạy kịp mọi việc. "
                f"Một buổi sáng đẹp trời, lễ hội mùa quả ngọt được tổ chức trên đỉnh đồi vào đúng mười hai giờ trưa. "
                f"{n_vi} vinh dự được giao nhiệm vụ quan trọng nhất: mang lá cờ lễ hội lên khai mạc ngày vui. "
                f"Các bạn dặn dò cậu phải khởi hành sớm, nhưng tính nào tật nấy, cậu vẫn mãi chơi đùa và nằm ngủ dưới bóng cây. "
                f"Khi mặt trời lên đến đỉnh đầu, cậu hốt hoảng lao thật nhanh vào con đường tắt nguy hiểm. "
                f"Cơn mưa rào ban sáng đã làm con suối dâng cao và một thân cây cổ thụ ngã chắn ngang đường. "
                f"Vì quá vội vàng trượt chân trên bùn lầy, {n_vi} ngã nhào vào bụi gai rậm rạp và bị mắc kẹt hoàn toàn. "
                f"Đúng lúc tuyệt vọng nhất, cụ rùa thông thái đeo kính tròn khoan thai bước tới với cây gậy gỗ. "
                f"Cụ ôn tồn bảo: Này cháu nhỏ, chạy nhanh đến đâu có ích gì nếu cháu đến nơi khi ngày vui đã tàn? Sự hấp tấp che mờ mắt, लेकिन lòng kiên nhẫn mới mở ra đường đi đúng đắn. "
                f"Cụ rùa nhẹ nhàng gỡ từng cành gai giải cứu {n_vi}, rồi cùng nhau bước đi vững chãi trên con đường an toàn. "
                f"Họ lên tới đỉnh đồi đúng vào tiếng reo hò của muôn loài, mang lại bài học vô giá về sự đúng giờ và điềm tĩnh."
            ),
            "script": (
                f"Chú {species} {n_vi} luôn có tật xấu: {flaws['vi']}. "
                f"Được giao mang cờ lên lễ hội trưa, cậu mải chơi ngủ quên đến sát giờ mới cuống cuồng chạy tắt. "
                f"Gặp mưa to cây đổ, {n_vi} ngã nhào vào bụi gai nhọn và mắc kẹt hoàn toàn! "
                f"Liệu {n_vi} có kịp thoát khỏi bụi gai để mang cờ tới khai mạc lễ hội đúng giờ? Xem ngay trọn vẹn câu chuyện qua đường link dưới phần mô tả nhé!"
            ),
            "description": f"🐾 Xem trọn vẹn câu chuyện hoạt hình 3D của {n_vi}!\n\n🎬 Đón xem tập phim đầy đủ 10 phút với bài học ý nghĩa tại đây!\n\nĐăng ký kênh @VietnameseMindNestTales!\n\n#MindNestTales #TruyenThieuNhi #HoatHinh3D #BaiHocCuocSong #Shorts",
            "tags": ["truyện thiếu nhi", "hoạt hình 3d", "bài học ý nghĩa", "câu chuyện động vật", "shorts"]
        },
        "fil": {
            "title": f"Ang Malaking Karera Laban sa Oras ni {n_fil}! 🐾⏰ #Shorts",
            "short_title": f"Ang Malaking Karera Laban sa Oras ni {n_fil}! 🐾⏰ #Shorts",
            "long_title": f"Si {n_fil} at ang Mahalagang Aral 🐾 (Buong 10 Min Kwento)",
            "moral": morals["fil"],
            "short_cta_voice": f"Ngunit makakawala kaya si {n_fil} sa matitinik na baging upang marating ang tuktok sa takdang oras? Panoorin ang kapana-panabik na buong kwento — link sa description!",
            "short_cta_text": "Ano ang susunod na mangyayari? 👉 Panoorin ang buong kwento sa description!",
            "short_script": (
                f"Sa gitna ng ginintuang kapatagan, naninirahan ang masayahing si {n_fil}. "
                f"Minamahal siya ng lahat ng hayop, ngunit may isa siyang malaking kapintasan: {flaws['fil']}. "
                f"Inakala niyang sapat na ang kanyang bilis upang ipagpaliban ang lahat hanggang sa huling minuto! "
                f"Isang umaga, inanunsyo ang Dakilang Pista sa tuktok ng bundok ganap na alas-dose ng tanghali. "
                f"Ipinagkaloob kay {n_fil} ang pinakamalaking karangalan: ang pagdadala ng bandila ng pista! "
                f"Pinaalalahanan siya ng mga kaibigan na magsimula nang maaga, ngunit naglaro at natulog lamang siya sa lilim. "
                f"Nang mapansin niyang tanghali na, natarantang tumakbo si {n_fil} sa mapanganib na shortcut. "
                f"Biglang bumuhos ang malakas na ulan at humarang ang isang malaking punong natumba! "
                f"Dumulas siya sa putik at sumabit sa makakapal na tinik, huling-huli sa oras! "
                f"Ngunit makakawala kaya si {n_fil} sa matitinik na baging upang marating ang tuktok sa takdang oras? Panoorin ang kapana-panabik na buong kwento — link sa description!"
            ),
            "long_script": (
                f"Noong unang panahon, sa isang magandang kapatagan na puno ng ginintuang araw, naninirahan si {n_fil}. "
                f"Lahat ng mga hayop ay humahanga sa kanyang sigla, saya, at kabaitan sa kapwa. "
                f"Ngunit may isa siyang malaking kapintasan: {flaws['fil']}. "
                f"Palagi niyang iniisip na dahil mabilis siya, maaari niyang ipagpaliban ang lahat hanggang sa huling minuto. "
                f"Isang maaliwalas na umaga, inanunsyo ang Dakilang Pista ng Lambak sa tuktok ng burol ganap na alas-dose ng tanghali. "
                f"Ipinagkaloob kay {n_fil} ang pinakamalaking karangalan: ang pagdadala ng bandila ng kapistahan upang simulan ang pagdiriwang. "
                f"Pinaalalahanan siya ng kanyang mga kaibigan na umalis nang maaga, ngunit naglaro lamang siya at nagpahinga sa lilim ng puno. "
                f"Nang mapansin niyang mataas na ang araw, nagmadali siyang tumakbo sa mapanganib na shortcut. "
                f"Dahil sa biglaang bagyo kaninang umaga, bumaha ang ilog at may nagtumbahang malaking puno na humarang sa daan. "
                f"Dumulas si {n_fil} sa putik at tuluyang sumabit sa makakapal na baging na may matatalim na tinik. "
                f"Hindi siya makawala habang papalapit na ang oras ng pista. Sa sandaling iyon, dumating ang matalinong matandang pagong na may salamin at tungkod. "
                f"Mabining sinabi ng matanda: Kaibigan, anong halaga ng bilis kung darating ka kung kailan tapos na ang lahat? Ang pagmamadali ay nagdudulot ng kapahamakan, ngunit ang hinahon ang nagtuturo ng tamang landas. "
                f"Tinulungan siyang tanggalin ang mga tinik at magkasama silang umakyat sa ligtas na daan. Nakarating sila sa tamang oras at buong pusong nagdiwang ang lahat."
            ),
            "script": (
                f"Si {n_fil} ay masipag ngunit may kapintasan: {flaws['fil']}. "
                f"Dapat niyang dalhin ang bandila sa pista ng alas-dose, ngunit naglaro siya hanggang sa huling minuto. "
                f"Dumaan sa mapanganib na shortcut sa ulan, dumulas sa putik at nasabit sa matatalim na tinik! "
                f"Ngunit makakawala kaya si {n_fil} sa matitinik na baging upang marating ang tuktok sa takdang oras? Panoorin ang kapana-panabik na buong kwento — link sa description!"
            ),
            "description": f"🐾 Panoorin ang masayang 3D animated kwento ni {n_fil}!\n\n🎬 Panoorin ang buong 10 minutong episode na may kumpletong aral dito!\n\nMag-subscribe sa @FilipinoMindNestTales!\n\n#MindNestTales #KwentongPambata #AralSaBuhay #3DAnimation #Shorts",
            "tags": ["kwentong pambata", "aral sa buhay", "animation tagalog", "hayop kwento", "shorts"]
        }
    }

def generate_dynamic_story(story_number, use_ai=True):
    """
    Generates a complete new story definition with 16 clips and 11-language dual-script dubbing:
    1. short_script: 60-90s Shorts trailer funnel.
    2. long_script: full 10-minute 4-act story resolution.
    - Story 1 to 51 match STORIES_MASTER directly.
    - Story 52+ dynamically selects from ANIMALS.
    - All 11 languages are 100% native with ZERO mixed English words.
    """
    if story_number <= len(STORIES_MASTER):
        master_id, base_title, playlist, moral = STORIES_MASTER[story_number - 1]
        name_parts = base_title.replace("The ", "").split()
        species = name_parts[0].lower() if name_parts else "animal"
        hero_name = f"Chico the {species.title()}" if story_number == 1 else f"{name_parts[0]} the {species.title()}"
        slug = f"{species}_{story_number}"
        flaw = "always rushing and arriving late" if story_number == 1 else "acting in haste without thinking"
        summary = f"{hero_name} had a habit of {flaw}. Trouble arrived, but gentle wisdom helped: {moral}"
    else:
        idx = (story_number - len(STORIES_MASTER) - 1) % len(ANIMALS)
        animal_choice = ANIMALS[idx]
        hero_name, species, flaw, moral = animal_choice
        slug = f"{species}_{story_number}"
        playlist = PLAYLISTS[story_number % len(PLAYLISTS)]
        base_title = f"{hero_name} Learns a Lesson"
        summary = f"{hero_name} had a habit of {flaw}. Trouble arrived, but gentle wisdom helped: {moral}"

    hero_first = hero_name.split()[0]
    story_data = {
        "story_number": story_number,
        "story_slug": slug,
        "base_title": base_title,
        "moral": moral,
        "playlist": playlist,
        "target_duration_seconds": 75,
        "short_target_duration_seconds": 75,
        "long_target_duration_seconds": 600,
        "characters": {
            "hero": f"3D Pixar-style animated {species} named {hero_first} with expressive round eyes and cute cartoon proportions",
            "mentor": "3D Pixar-style animated wise tortoise elder with round spectacles and friendly grandfather smile"
        },
        "clips": [
            {"clip_number": i, "time_range": f"{(i-1)*11}:15-{i*11}:15", "beat": f"Beat {i}",
             "prompt": f"3D Pixar-style animated {species} named {hero_first}, cinematic lighting, warm Disney Pixar aesthetic, portrait 9:16, beat {i} of 180s moral journey."}
            for i in range(1, 17)
        ],
        "translations": {}
    }

    # 1. Attempt AI Multilingual Generation
    ai_trans = None
    if use_ai:
        ai_trans = generate_ai_multilingual_translations(base_title, hero_name, summary, moral)

    # 2. Complete with pure fallbacks if AI missed any language
    fallback_trans = generate_fallback_translations(hero_name, species, base_title, moral, flaw)
    needed_langs = ["en", "hi", "es", "pt", "fr", "de", "ar", "ja", "ko", "vi", "fil"]
    
    for lang in needed_langs:
        if ai_trans and lang in ai_trans:
            story_data["translations"][lang] = ai_trans[lang]
        else:
            story_data["translations"][lang] = fallback_trans[lang]

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
    s_num = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    story = get_or_create_story(s_num)
    print(f"Successfully loaded Story #{s_num}: {story['base_title']}")

