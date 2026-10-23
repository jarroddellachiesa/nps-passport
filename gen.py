#!/usr/bin/env python3
"""Build the static NPS Passport site from /workspace/nps-stamps/parks.json + rendered PNGs."""
import json, os, html, shutil, sys
from PIL import Image
SITE = os.path.dirname(os.path.abspath(__file__))
STAMPS = os.environ.get('STAMPS_DIR', '/workspace/nps-stamps'); sys.path.insert(0, STAMPS)
import passport
regions = json.load(open(os.path.join(STAMPS, 'parks.json')))['regions']
img = os.path.join(SITE, 'img'); shutil.rmtree(img, ignore_errors=True); os.makedirs(img)
W, H = 900, 1250
def conv(src, name):
    im = Image.open(os.path.join(STAMPS, src)).convert('RGB')
    im.save(os.path.join(img, name + '.webp'), 'WEBP', quality=82, method=6)
    im.resize((W*2//3, H*2//3), Image.LANCZOS).save(os.path.join(img, name + '.jpg'), 'JPEG', quality=84, optimize=True, progressive=True)
conv('passport_cover.png', 'cover'); pages = [('cover', 'NPS Passport — cover')]
for key, rk, r, items, i, n in passport.pages():
    conv(f'passport_{key}.png', key); pages.append((key, f'{r["name"]} region stamp page'))
conv('passport_back.png', 'back'); pages.append(('back', 'NPS Passport — back cover'))
e = html.escape
leaves = [f'<div class="leaf" style="z-index:{len(pages)-i}"><div class="front"><picture>'
          f'<source srcset="img/{nm}.webp" type="image/webp"><img src="img/{nm}.jpg" alt="{e(alt)}" '
          f'width="{W}" height="{H}" {"" if i < 2 else "loading=lazy"} draggable="false"></picture></div><div class="back"></div></div>'
          for i, (nm, alt) in enumerate(pages)]
dots = ''.join(f'<button class="dot" aria-label="Page {i}"></button>' for i in range(len(pages)))
total = sum(len(r['units']) for r in regions.values())
visited = sum(1 for r in regions.values() for u in r['units'] if u['visits'])
reg = ''.join(f'<tr><td><i style="background:{r["color"]}"></i>{e(r["name"])}</td>'
              f'<td class="rt">{sum(1 for u in r["units"] if u["visits"])}<small> / {len(r["units"])}</small></td></tr>'
              for r in regions.values())
vis = sorted(((v['date'], u, v, r) for r in regions.values() for u in r['units'] for v in u['visits']), key=lambda t: t[0], reverse=True)
vrows = ''.join(f'<tr><td class="dt">{e(d)}</td><td><b>{e(u["name"])}</b><span>{e(v.get("location",""))}, '
                f'{e(v.get("state") or u.get("stamp_state",""))} · {e(r["name"])}</span>'
                f'{f"<em>{e(v["notes"])}</em>" if v.get("notes") else ""}</td></tr>' for d, u, v, r in vis) \
        or '<tr><td class="empty">No cancellations yet.</td></tr>'
units = [[u['code'], u['name'], u['state'], u['designation'], r['name'], len(u['visits'])] for r in regions.values() for u in r['units']]
units.sort(key=lambda x: x[1])
out = open(os.path.join(SITE, 'tpl.html')).read()
for k, v in {'{{LEAVES}}': '\n'.join(leaves), '{{DOTS}}': dots, '{{REGROWS}}': reg, '{{VISITS}}': vrows,
             '{{UNITS}}': json.dumps(units, ensure_ascii=False).replace('</', '<\\/'), '{{VISITED}}': str(visited),
             '{{TOTAL}}': str(total), '{{NREG}}': str(len(regions)), '{{NVIS}}': str(len(vis))}.items():
    out = out.replace(k, v)
open(os.path.join(SITE, 'index.html'), 'w').write(out)
print(f'built index.html: {len(pages)} pages, {visited}/{total} units visited, {len(vis)} cancellations')
