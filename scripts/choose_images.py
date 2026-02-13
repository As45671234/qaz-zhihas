from PIL import Image
import os
import colorsys

WEBP_DIR = './img/webp'
EXCLUDE = {'logo.webp', 'warehouse1.webp','warehouse2.webp','warehouse3.webp','warehouse4.webp'}
CANDIDATES = [f for f in os.listdir(WEBP_DIR) if f.lower().endswith('.webp') and f not in EXCLUDE]

def analyze(path):
    with Image.open(path) as im:
        im = im.convert('RGB')
        im = im.resize((200,200))
        px = list(im.getdata())
        r = sum(p[0] for p in px)/len(px)/255.0
        g = sum(p[1] for p in px)/len(px)/255.0
        b = sum(p[2] for p in px)/len(px)/255.0
        h,s,v = colorsys.rgb_to_hsv(r,g,b)
        return {'r':r,'g':g,'b':b,'h':h,'s':s,'v':v}

results = {}
for f in CANDIDATES:
    path = os.path.join(WEBP_DIR, f)
    try:
        results[f] = analyze(path)
    except Exception as e:
        print('Failed', f, e)

# scoring heuristics
scores = { 'kitchen':{}, 'wardrobe':{}, 'bedroom':{}, 'hallway':{}, 'kids':{} }
for f,stats in results.items():
    h,s,v = stats['h'], stats['s'], stats['v']
    # kitchen: bright, low saturation
    scores['kitchen'][f] = (v*1.5) - (s*1.0)
    # wardrobe: warm hue (around 0.05-0.15 -> orange/brown) and medium saturation
    warm_score = max(0, 1 - abs(h-0.09)*10)
    scores['wardrobe'][f] = warm_score * (s+v)/2
    # bedroom: medium brightness, lower saturation
    scores['bedroom'][f] = (1 - abs(v-0.5)) + (1 - s)
    # hallway: higher contrast -> approximate by mid v and mid s
    scores['hallway'][f] = (1 - abs(v-0.5)) + (s*0.3)
    # kids: colorful -> high saturation and high variance (approx by s and v)
    scores['kids'][f] = s*1.2 + (v*0.5)

# pick top for each
chosen = {}
for cat,mp in scores.items():
    best = sorted(mp.items(), key=lambda x: x[1], reverse=True)[0]
    chosen[cat] = best[0]

print('Proposed mapping:')
for cat,img in chosen.items():
    stats = results[img]
    print(f"{cat}: {img} (h={stats['h']:.2f}, s={stats['s']:.2f}, v={stats['v']:.2f})")

# write mapping to file for review
with open('./scripts/proposed_mapping.txt','w',encoding='utf-8') as fh:
    for cat,img in chosen.items():
        fh.write(f"{cat}:{img}\n")

print('\nWrote ./scripts/proposed_mapping.txt')
