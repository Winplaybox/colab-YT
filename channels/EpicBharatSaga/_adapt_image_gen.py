
import shutil, os

src = 'channels/AllTrainReels/image_generator.py'
dst = 'channels/EpicBharatSaga/image_generator.py'

with open(src, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('AllTrainReelsBot/1.0 (https://youtube.com/@alltrainreels; contact@alltrainreels.com)', 'EpicBharatSagaBot/1.0 (https://youtube.com/@epicbharatsaga; epicbharat.official@gmail.com)')
content = content.replace('@AllTrainReels', '@EpicBharatSaga')
content = content.replace('ALL TRAIN REELS | Har Patri Ki Kahani', 'EPIC BHARAT SAGA | Sanatan Dharma Ki Gaatha')
content = content.replace('color=(11, 31, 58)', 'color=(26, 10, 0)')
content = content.replace('fill=(11, 31, 58)', 'fill=(26, 10, 0)')
content = content.replace('fill=(20, 50, 90)', 'fill=(40, 20, 0)')
content = content.replace('fill=(230, 57, 70)', 'fill=(255, 107, 0)')
content = content.replace('fill=(255, 195, 0)', 'fill=(255, 215, 0)')
content = content.replace('queries.append(f"{slug} train")', 'queries.append(f"{slug} Hindu mythology")\n        queries.append(f"{slug} India temple")')
content = content.replace(
    'AllTrainReels Real Railway Photography & Asset Engine',
    'EpicBharatSaga Hindu Mythology Photography & Asset Engine'
)
content = content.replace(
    'authentic, high-resolution public-domain railway photography.',
    'authentic, high-resolution public-domain Hindu mythology & temple photography.'
)
# Route to IndianHorrorTapes for HF token search as well
content = content.replace(
    'os.path.join(script_dir, \'..\', \'IndianHorrorTapes\', \'credentials\', \'hf_token.txt\')',
    'os.path.join(script_dir, \'..\', \'IndianHorrorTapes\', \'credentials\', \'hf_token.txt\')'
)

with open(dst, 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')
