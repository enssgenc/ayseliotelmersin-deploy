"""Ayseli 2026-11-11: yeni oda fotograflari. Base: ayseli-contact-20261026 release."""
import hashlib, json, pathlib, re, shutil, tarfile

ROOT = pathlib.Path(__file__).resolve().parent
BASE = ROOT / 'rel' / 'out'
IMG = ROOT / 'newimg'
OUT = ROOT / 'build' / 'out'
sha = lambda b: hashlib.sha256(b).hexdigest()

if OUT.exists():
    shutil.rmtree(OUT)
shutil.copytree(BASE, OUT)
for p in IMG.glob('*.webp'):
    shutil.copy2(p, OUT / 'images' / p.name)
# og:image / twitter:image / schema.org image -> /images/hero.jpg (onceden 404 donuyordu).
# Lobi fotografinin 1200x630 kirpimi.
assert not (OUT / 'images' / 'hero.jpg').exists()
shutil.copy2(IMG / 'hero.jpg', OUT / 'images' / 'hero.jpg')

OLD_CHUNK = 'ayseli-page-c8ccbb278e70.js'
chunk_path = OUT / '_next/static/chunks' / OLD_CHUNK
js = chunk_path.read_text(encoding='utf-8')
html = (OUT / 'index.html').read_text(encoding='utf-8')

def once(src, before, after, what):
    n = src.count(before)
    assert n == 1, (what, n)
    return src.replace(before, after)

# --- Oda kartlari (D) ---
js = once(js, 'image:"double-room",description:', 'image:"room-double",description:', 'D double')
js = once(js, 'image:"twin-room",description:', 'image:"room-twin",description:', 'D twin')

# --- Hero kucuk oda karti ---
js = once(js, '"hero-room-peek",children:[(0,i.jsx)("img",{src:"/images/double-room-480.webp"',
          '"hero-room-peek",children:[(0,i.jsx)("img",{src:"/images/gal-bed-480.webp"', 'peek js')
html = once(html, '<div class="hero-room-peek"><img src="/images/double-room-480.webp"',
            '<div class="hero-room-peek"><img src="/images/gal-bed-480.webp"', 'peek html')
html = once(html, '<link rel="preload" as="image" href="/images/double-room-480.webp"/>',
            '<link rel="preload" as="image" href="/images/gal-bed-480.webp"/>', 'peek preload')

# --- Galeri (O) ---
NEW_GALLERY = [
    ('gal-seating', 'Odalarda oturma köşesi'),
    ('gal-bathroom', 'Ferah ve modern banyolar'),
    ('gal-bed', 'Özenle hazırlanan yataklar'),
    ('gal-shower', 'Yağmur duşlu banyo'),
]
js = once(js, '{image:"double-room",label:', '{image:"gal-double",label:', 'O double')
js = once(js, '{image:"twin-room",label:', '{image:"gal-twin",label:', 'O twin')
last = 'label:"Güne güzel bir başlangıç",category:"Kahvaltı"}]'
extra = ''.join(',{image:"%s",label:"%s",category:"Odalar"}' % (k, l) for k, l in NEW_GALLERY)
js = once(js, last, last[:-1] + extra + ']', 'O append')

# --- SSR HTML: oda kartlari ve galeri ---
gs = html.index('<div class="gallery-grid ')
ge = html.index('<a class="instagram-link"', gs)
before, grid, after = html[:gs], html[gs:ge], html[ge:]

# Oda kartlarindaki double/twin (galeri disindaki) -> room-*
def swap_rooms(seg):
    seg = seg.replace('/images/double-room-', '/images/room-double-')
    seg = seg.replace('/images/twin-room-', '/images/room-twin-')
    return seg
assert before.count('/images/double-room-') == 3 and before.count('/images/twin-room-') == 3, \
    (before.count('/images/double-room-'), before.count('/images/twin-room-'))
before = swap_rooms(before)
grid = grid.replace('/images/double-room-', '/images/gal-double-').replace('/images/twin-room-', '/images/gal-twin-')

# Yeni galeri butonlari: mevcut photo-7 butonunu sablon al
m = re.search(r'<button class="gallery-photo photo-7".*?</button>', grid, re.S)
tpl = m.group(0)
tpl_label = 'Güne güzel bir başlangıç'
assert tpl.count('restaurant-') == 3 and tpl.count(tpl_label) == 3, (tpl.count('restaurant-'), tpl.count(tpl_label))
new_buttons = ''
for idx, (key, label) in enumerate(NEW_GALLERY, start=8):
    b = tpl.replace('photo-7', 'photo-%d' % idx).replace('restaurant-', key + '-').replace(tpl_label, label)
    new_buttons += b
grid = grid[:m.end()] + new_buttons + grid[m.end():]
assert grid.count('class="gallery-photo ') == 12
html = before + grid + after

for old in ('double-room', 'twin-room'):
    assert old not in html and old not in js, old

new_chunk = 'ayseli-page-' + sha(js.encode())[:12] + '.js'
(chunk_path.parent / new_chunk).write_text(js, encoding='utf-8', newline='\n')
chunk_path.unlink()
assert html.count(OLD_CHUNK) >= 1
html = html.replace(OLD_CHUNK, new_chunk)
(OUT / 'index.html').write_text(html, encoding='utf-8', newline='\n')

# Kullanilmayan eski oda gorsellerini kaldir
for old in ('double-room', 'twin-room'):
    for w in (480, 960):
        (OUT / 'images' / f'{old}-{w}.webp').unlink()

for p in OUT.rglob('*'):
    if p.is_file() and p.suffix in ('.html', '.js', '.txt', '.css') and p.name != new_chunk:
        assert OLD_CHUNK not in p.read_text(encoding='utf-8', errors='ignore'), p

rel = json.loads((OUT / 'ayseli-release.json').read_text(encoding='utf-8'))
rel.update({'release': 'ayseli-photos-og-20261111', 'base_release': 'ayseli-contact-20261026',
            'page_chunk': new_chunk, 'files': sum(p.is_file() for p in OUT.rglob('*'))})
(OUT / 'ayseli-release.json').write_text(json.dumps(rel, ensure_ascii=False, indent=2), encoding='utf-8')

archive = ROOT / 'build' / 'ayseli-photos-og-release.tar.gz'
with tarfile.open(archive, 'w:gz') as tar:
    for p in sorted(OUT.rglob('*')):
        if p.is_file():
            tar.add(p, arcname=p.relative_to(OUT).as_posix())
print(json.dumps({**rel, 'archive_bytes': archive.stat().st_size, 'archive_sha256': sha(archive.read_bytes())},
                 ensure_ascii=False, indent=1))
