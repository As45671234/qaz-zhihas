from PIL import Image
import os
import re

SRC_DIRS = ['./img']
OUT_DIR = './img/webp'
ALLOWED_EXT = {'.jpg', '.jpeg', '.png'}

def slug(name: str) -> str:
    name = name.lower()
    name = re.sub(r"\s+", "_", name)
    name = re.sub(r"[^a-z0-9_\.-]", "", name)
    name = name.replace('..', '.')
    return name

os.makedirs(OUT_DIR, exist_ok=True)

converted = 0
for src_dir in SRC_DIRS:
    for root, dirs, files in os.walk(src_dir):
        for fname in files:
            base, ext = os.path.splitext(fname)
            if ext.lower() not in ALLOWED_EXT:
                continue
            src_path = os.path.join(root, fname)
            # include parent folder name to avoid collisions
            rel = os.path.relpath(src_path, src_dir)
            parts = rel.split(os.sep)
            if len(parts) > 1:
                out_base = slug('_'.join(parts))
            else:
                out_base = slug(base)
            out_name = out_base + '.webp'
            out_path = os.path.join(OUT_DIR, out_name)
            try:
                with Image.open(src_path) as im:
                    im = im.convert('RGB')
                    im.save(out_path, 'WEBP', quality=80, method=6)
                    print(f"Saved: {out_path}")
                    converted += 1
            except Exception as e:
                print(f"Failed converting {src_path}: {e}")

print(f'Done, converted {converted} images')
