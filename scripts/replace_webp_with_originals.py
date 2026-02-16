import os, re

ROOT = '.'
IMG_DIR = os.path.join(ROOT, 'img')
WEBP_DIR = os.path.join(IMG_DIR, 'webp')
INDEX = os.path.join('.', 'index.html')

def slug(name: str) -> str:
    name = name.lower()
    name = re.sub(r"\s+", "_", name)
    name = re.sub(r"[^a-z0-9_\.-]", "", name)
    name = name.replace('..', '.')
    return name

# build lookup of possible slugs -> original relative path
lookup = {}
for root, dirs, files in os.walk(IMG_DIR):
    if os.path.abspath(root) == os.path.abspath(WEBP_DIR):
        continue
    for f in files:
        if not f.lower().endswith(('.jpg', '.jpeg', '.png')):
            continue
        rel = os.path.relpath(os.path.join(root, f), ROOT).replace('\\','/')
        base = os.path.splitext(f)[0]
        s1 = slug(base)  # filename slug
        # slug of rel path components joined by _ (like conversion did)
        parts = rel.split('/')
        if parts[0] == 'img':
            parts = parts[1:]
        s2 = slug('_'.join(parts))
        lookup.setdefault(s1, []).append(rel)
        lookup.setdefault(s2, []).append(rel)

# read index.html
with open(INDEX, 'r', encoding='utf-8') as fh:
    html = fh.read()

pattern = re.compile(r"([\"'])\.\/img\/webp\/([^\"']+?)\.(webp)\1")
replacements = {}

for m in pattern.finditer(html):
    quote = m.group(1)
    webp_name = m.group(2)  # without extension
    candidates = lookup.get(webp_name.lower(), [])
    chosen = None
    if candidates:
        chosen = candidates[0]
    else:
        # try partial match: find any lookup key that equals webp_name after stripping leading _
        key = webp_name.lower()
        if key.startswith('_'):
            k2 = key[1:]
            candidates = lookup.get(k2, [])
            if candidates:
                chosen = candidates[0]
    if chosen:
        old = f"{quote}./img/webp/{webp_name}.webp{quote}"
        new = f"{quote}{chosen}{quote}"
        replacements[old] = new
    else:
        # fallback: replace with jpg of same base in img root
        trial = f"img/{webp_name}.jpg"
        if os.path.exists(os.path.join(ROOT, trial)):
            old = f"{quote}./img/webp/{webp_name}.webp{quote}"
            new = f"{quote}{trial}{quote}"
            replacements[old] = new

# apply replacements
if not replacements:
    print('No replacements found.')
else:
    new_html = html
    for old, new in replacements.items():
        new_html = new_html.replace(old, new)
    # backup
    with open(INDEX + '.bak', 'w', encoding='utf-8') as fh:
        fh.write(html)
    with open(INDEX, 'w', encoding='utf-8') as fh:
        fh.write(new_html)
    print('Applied replacements:')
    for old, new in replacements.items():
        print(old, '->', new)
    print('\nBackup saved to index.html.bak')
