from PIL import Image
import os, colorsys

WEBP_DIR = './img/webp'
EXCLUDE = {'logo.webp','warehouse1.webp','warehouse2.webp','warehouse3.webp','warehouse4.webp'}
CURRENT = 'whatsapp_image_2026-02-12_at_15.48.55.webp'

candidates = [f for f in os.listdir(WEBP_DIR) if f.lower().endswith('.webp') and f not in EXCLUDE]

scores = []
for f in candidates:
    path = os.path.join(WEBP_DIR,f)
    try:
        with Image.open(path) as im:
            im = im.convert('RGB').resize((200,200))
            px = list(im.getdata())
            r = sum(p[0] for p in px)/len(px)/255.0
            g = sum(p[1] for p in px)/len(px)/255.0
            b = sum(p[2] for p in px)/len(px)/255.0
            h,s,v = colorsys.rgb_to_hsv(r,g,b)
            score = s*1.2 + v*0.5
            scores.append((f,score,h,s,v))
    except Exception as e:
        pass

scores.sort(key=lambda x:x[1], reverse=True)
print('Top candidates for kids (excluding current):')
count=0
for f,score,h,s,v in scores:
    if f==CURRENT: 
        continue
    print(f"{f}  s={s:.2f} v={v:.2f} score={score:.2f}")
    count+=1
    if count>=6: break

# choose first different from current
for f,score,h,s,v in scores:
    if f!=CURRENT:
        print('\nChosen:', f)
        open('./scripts/chosen_kids.txt','w',encoding='utf-8').write(f)
        break
