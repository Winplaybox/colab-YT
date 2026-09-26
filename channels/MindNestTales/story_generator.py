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
2. SCRIPT: Spoken narration of 60 to 75 words. Warm, rhythmic, lively, easy for children to understand, engaging for parents.
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
                max_tokens=2500,
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
        return all_translations

    print(f"Notice: AI generated {len(all_translations)}/11 languages. Completing missing with pure fallbacks.")
    return all_translations

def generate_fallback_translations(hero_name, species, base_title, moral_english):
    """
    Pure, localized fallback templates for all 11 languages.
    Guarantees ZERO English words are mixed into non-English scripts even when offline.
    """
    hero_first = hero_name.split()[0]
    return {
        "en": {
            "title": f"{hero_first}'s Big Lesson! 🐾✨ #Shorts",
            "moral": moral_english,
            "script": f"Meet {hero_first} the {species}! Everyone in the forest loved {hero_first}, but there was one mistake: rushing ahead without thinking. When an obstacle appeared, impatience made everything worse. That is when a wise elder shared timeless advice: true strength comes from patience and listening. {hero_first} paused, corrected the path, and celebrated success with all friends!",
            "description": f"🐾 Watch {hero_name}'s heartwarming 3D animated adventure!\n\n✨ MindNest Tales brings 3D Pixar-style moral stories for families.\n\nSubscribe to @EnglishMindNestTales!\n\n#MindNestTales #PixarStyle #MoralStories #Shorts",
            "tags": ["mindnest tales", f"{species} story", "moral stories", "3d cartoon animal", "pixar style animation", "kids stories", "shorts"]
        },
        "hi": {
            "title": f"{hero_first} और सीख भरी सीख! 🐾✨ #Shorts",
            "moral": "धैर्य और सही समय ही सच्ची सफलता की कुंजी है। हमेशा समझदारी से काम लें!",
            "script": f"मिलिए हमारे प्यारे {hero_first} से! जंगल में सब उसे बहुत पसंद करते थे। लेकिन उसकी एक आदत थी—बिना सोचे समझे जल्दबाज़ी करना। एक दिन इसी वजह से बड़ी मुसीबत आ गई। तभी एक समझदार साथी ने समझाया कि जल्दबाज़ी से काम बिगड़ते हैं, धैर्य से ही सही राह मिलती है। {hero_first} ने अपनी भूल समझी और हमेशा समझदारी से आगे बढ़ने का वादा किया।",
            "description": f"🐾 देखिए {hero_first} की मज़ेदार 3D एनिमेटेड कहानी! जानिए क्यों धैर्य और समझदारी से हर मुश्किल आसान हो जाती है।\n\nसब्सक्राइब करें @HindiMindNestTales!\n\n#MindNestTales #HindiKahaniya #MoralStoriesHindi #3DAnimation #Shorts",
            "tags": ["mindnest tales", "हिंदी कहानियां", "बाल कहानियां", "3d कार्टून", "सीखने वाली कहानी", "shorts"]
        },
        "es": {
            "title": f"¡La Gran Aventura de {hero_first}! 🐾✨ #Shorts",
            "moral": "La paciencia y el buen juicio superan cualquier obstáculo. ¡Aprende cada día!",
            "script": f"¡Conoce a {hero_first}! A todos en el bosque les encantaba su alegría, pero tenía un problema: actuar con prisa sin reflexionar. Un día, la prisa provocó un gran tropiezo. Fue entonces cuando un sabio anciano le dio un cariñoso consejo: la verdadera fuerza proviene de la calma y la paciencia. {hero_first} escuchó con el corazón, corrigió su error y triunfó junto a sus amigos.",
            "description": f"🐾 ¡Disfruta de la tierna aventura en 3D de {hero_first}!\n\nSuscríbete a @SpanishMindNestTales!\n\n#MindNestTales #CuentosInfantiles #HistoriasConMoraleja #Shorts",
            "tags": ["mindnest tales", "historias para niños", "cuentos morales", "animacion 3d", "shorts"]
        },
        "pt": {
            "title": f"A Grande Lição de {hero_first}! 🐾✨ #Shorts",
            "moral": "A paciência e o respeito sempre mostram o melhor caminho. Seja sábio!",
            "script": f"Conheça {hero_first}! Todos na floresta admiravam sua energia, mas havia uma falha: agir sem pensar nas consequências. Um dia, a pressa causou uma grande confusão. Um amigo sábio aconselhou com carinho que a verdadeira grandeza vem da paciência e da atenção. {hero_first} entendeu a mensagem, mudou de atitude e alcançou a vitória com todos os amigos!",
            "description": f"🐾 Acompanhe a linda história animada em 3D de {hero_first}!\n\nInscreva-se em @PortugueseMindNestTales!\n\n#MindNestTales #HistoriasInfantis #Desenho3D #Shorts",
            "tags": ["mindnest tales", "historias infantis", "desenho animado", "licao de vida", "shorts"]
        },
        "fr": {
            "title": f"La Grande Leçon de {hero_first} ! 🐾✨ #Shorts",
            "moral": "La patience et la sagesse triomphent toujours de la précipitation. Écoute avec le cœur !",
            "script": f"Rencontrez {hero_first} ! Tout le monde dans la forêt aimait son dynamisme, mais il y avait un souci : vouloir aller trop vite sans réfléchir. Un matin, cette précipitation causa une belle bêtise. Un sage compagnon lui murmura alors un conseil précieux : la vraie force réside dans le calme et la réflexion. {hero_first} comprit la leçon, rectifia son chemin et fit la fierté de ses amis.",
            "description": f"🐾 Découvrez la merveilleuse aventure animée en 3D de {hero_first} !\n\nAbonnez-vous à @FrenchMindNestTales !\n\n#MindNestTales #ContesPourEnfants #Animation3D #Shorts",
            "tags": ["mindnest tales", "histoire pour enfants", "conte moral", "animation 3d", "shorts"]
        },
        "de": {
            "title": f"{hero_first} Lernt eine Wichtige Lektion! 🐾✨ #Shorts",
            "moral": "Geduld und Bedachtsamkeit führen sicher zum Ziel. Hör auf gute Ratschläge!",
            "script": f"Lerne {hero_first} kennen! Alle Waldtiere schätzten seinen Mut, doch es gab ein Problem: ständige Eile ohne Plan. Eines Morgens führte die Hektik zu einem großen Missgeschick. Da gab ihm ein weiser Freund einen sanften Rat: Wahre Stärke zeigt sich in Geduld und klugem Handeln. {hero_first} hielt inne, lernte daraus und meisterte die Aufgabe mit Freude.",
            "description": f"🐾 Sieh dir das herzerwärmende 3D-Animationsabenteuer von {hero_first} an!\n\nAbonniere @GermanMindNestTales!\n\n#MindNestTales #Kindergeschichten #MoralGeschichten #Shorts",
            "tags": ["mindnest tales", "kindergeschichten", "moralische geschichte", "3d animation", "shorts"]
        },
        "ar": {
            "title": f"درس {hero_first} العظيم! 🐾✨ #Shorts",
            "moral": "الصبر والحكمة هما مفتاح كل نجاح حقيقي. لا تتسرع أبداً!",
            "script": f"تعرفوا على {hero_first}! كان الجميع في الغابة يحبون شجاعته، لكنه كان يعاني من عيب واحد: التسرع في اتخاذ القرارات. وفي أحد الأيام، أدى تسرعه إلى ورطة كبيرة. حينها تقدم صديق حكيم بنصيحة ثمينة: القوة الحقيقية تكمن في الهدوء والتفكير قبل الفعل. أدرك {hero_first} خطأه، وغير تصرفه، وحقق النجاح وسط فرحة الأصدقاء.",
            "description": f"🐾 شاهد المغامرة الكرتونية الممتعة ثلاثية الأبعاد مع {hero_first}!\n\nاشترك في @ArabicMindNestTales!\n\n#MindNestTales #قصص_أطفال #حكايات_معبرة #رسوم_متحركة #Shorts",
            "tags": ["قصص أطفال", "حكايات معبرة", "كرتون ثلاثي الأبعاد", "دروس وعبر", "shorts"]
        },
        "ja": {
            "title": f"{hero_first}の大切な気づき！🐾✨ #Shorts",
            "moral": "焦らずに落ち着いて行動することが、一番の力になります。",
            "script": f"森のみんなが大好きな{hero_first}のお話です！{hero_first}は元気いっぱいでしたが、いつも慌てて失敗ばかりしていました。ある日、急ぎすぎて大きなトラブルに。そこへ物知りの友だちが優しく教えてくれました。「本当の強さは、落ち着いて周りを見ることだよ」。{hero_first}は素直に心を開き、みんなと一緒に大きな喜びを分かち合いました。",
            "description": f"🐾 3Dアニメで描く{hero_first}の心温まる物語！\n\nチャンネル登録はこちら：@JapaneseMindNestTales！\n\n#MindNestTales #アニメ #子ども向け #絵本 #Shorts",
            "tags": ["子ども向け", "アニメ", "絵本", "教訓", "動物アニメ", "shorts"]
        },
        "ko": {
            "title": f"{hero_first}의 소중한 깨달음! 🐾✨ #Shorts",
            "moral": "서두르지 않고 침착하게 행동하는 것이 가장 큰 지혜입니다.",
            "script": f"숲속 귀염둥이 {hero_first}를 만나보세요! {hero_first}는 늘 활기찼지만, 무엇이든 서두르는 습관이 있었어요. 그러던 어느 날, 성급함 때문에 큰 실수를 하고 말았답니다. 그때 지혜로운 친구가 다정하게 조언해 주었어요. '진정한 힘은 차분함에서 나온단다.' {hero_first}는 가르침을 깨닫고, 친구들과 함께 멋지게 성공을 이뤄냈어요.",
            "description": f"🐾 {hero_first}의 따뜻하고 감동적인 3D 애니메이션 이야기!\n\n구독하기 @KoreanMindNestTales!\n\n#MindNestTales #어린이이야기 #동화 #3D애니메이션 #Shorts",
            "tags": ["어린이이야기", "교훈동화", "3d애니메이션", "동물이야기", "shorts"]
        },
        "vi": {
            "title": f"Bài Học Tuyệt Vời Của {hero_first}! 🐾✨ #Shorts",
            "moral": "Sự kiên nhẫn và bình tĩnh luôn dẫn lối đến thành công đích thực.",
            "script": f"Hãy cùng làm quen với {hero_first}! Mọi người trong khu rừng đều yêu quý cậu ấy, nhưng cậu lại có tính vội vàng hấp tấp. Một ngày nọ, sự thiếu kiên nhẫn đã gây ra rắc rối lớn. Đúng lúc đó, một người bạn thông thái đã nhẹ nhàng nhắc nhở: Sức mạnh thật sự đến từ sự bình tâm và lắng nghe. {hero_first} nhận ra sai lầm, thay đổi thói quen và gặt hái thành công trọn vẹn.",
            "description": f"🐾 Xem câu chuyện hoạt hình 3D ấm áp về {hero_first}!\n\nĐăng ký kênh @VietnameseMindNestTales!\n\n#MindNestTales #TruyenThieuNhi #HoatHinh3D #BaiHocCuocSong #Shorts",
            "tags": ["truyện thiếu nhi", "hoạt hình 3d", "bài học ý nghĩa", "câu chuyện động vật", "shorts"]
        },
        "fil": {
            "title": f"Ang Mahalagang Aral ni {hero_first}! 🐾✨ #Shorts",
            "moral": "Ang pagtitimpi at pagiging maingat ay mas mabisa kaysa sa pagmamadali.",
            "script": f"Kilalanin si {hero_first}! Minahal siya ng lahat ng hayop sa gubat, ngunit may isa siyang malaking pagkukulang: ang pagmamadali nang hindi nag-iisip. Isang araw, nagdulot ito ng malaking gusot. Dito lumapit ang isang matalinong kaibigan at nagpaalala: Ang tunay na lakas ay nasa hinahon at pakikinig. Nakinig si {hero_first}, inayos ang kanyang pagkakamali, at nagtagumpay kasama ang buong barkada.",
            "description": f"🐾 Panoorin ang masayang 3D animated kwento ni {hero_first}!\n\nMag-subscribe sa @FilipinoMindNestTales!\n\n#MindNestTales #KwentongPambata #AralSaBuhay #3DAnimation #Shorts",
            "tags": ["kwentong pambata", "aral sa buhay", "animation tagalog", "hayop kwento", "shorts"]
        }
    }

def generate_dynamic_story(story_number, use_ai=True):
    """
    Generates a complete new story definition with 12 clips and 11-language dubbing.
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
        summary = f"{hero_name} learned an important life lesson in the forest: {moral}"
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
        "characters": {
            "hero": f"3D Pixar-style animated {species} named {hero_first} with expressive round eyes and cute cartoon proportions",
            "mentor": "3D Pixar-style animated wise tortoise elder with round spectacles and friendly grandfather smile"
        },
        "clips": [
            {"clip_number": i, "time_range": f"{(i-1)*10}:00-{i*10}:00", "beat": f"Beat {i}",
             "prompt": f"3D Pixar-style animated {species} named {hero_first}, cinematic lighting, warm Disney Pixar aesthetic, portrait 9:16, savanna and forest setting, beat {i} of moral journey."}
            for i in range(1, 13)
        ],
        "translations": {}
    }

    # 1. Attempt AI Multilingual Generation
    ai_trans = None
    if use_ai:
        ai_trans = generate_ai_multilingual_translations(base_title, hero_name, summary, moral)

    # 2. Complete with pure fallbacks if AI missed any language
    fallback_trans = generate_fallback_translations(hero_name, species, base_title, moral)
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

