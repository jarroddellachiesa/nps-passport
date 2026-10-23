#!/usr/bin/env python3
"""NPS Passport renderer. Reads parks.json, writes passport_<pagekey>.png (900x1250).
Usage: python3 passport.py [--pages] [--cover] [--back] [--page=REGIONKEY]   (no args = everything)
Pages: one or more per region (6 cancellations per page; blank page when no visits)."""
import html, json, math, os, subprocess, sys, zlib, datetime
HERE = os.path.dirname(os.path.abspath(__file__)); BUILD = os.path.join(HERE, 'build')
W, H = 900, 1250; PER = 6
esc = lambda s: html.escape(str(s), quote=True)

def render(svg, out):
    os.makedirs(BUILD, exist_ok=True)
    p = os.path.join(BUILD, os.path.basename(out)[:-4] + '.svg'); open(p, 'w').write(svg)
    subprocess.run(['google-chrome', '--headless=new', '--no-sandbox', '--disable-gpu', '--hide-scrollbars',
        '--force-device-scale-factor=1', f'--window-size={W},{H}', f'--screenshot={out}', 'file://' + p],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); print('wrote', out)

def pages():
    """[(pagekey, regionkey, region, [ (unit, visit) ... ], idx, n)] in passport order."""
    data = json.load(open(os.path.join(HERE, 'parks.json')))['regions']; out = []
    for rk, r in data.items():
        vs = sorted(((u, v) for u in r['units'] for v in u['visits']), key=lambda t: t[1]['date'])
        n = max(1, math.ceil(len(vs) / PER))
        for i in range(n):
            out.append((rk if i == 0 else f'{rk}_{i+1}', rk, r, vs[i*PER:(i+1)*PER], i, n))
    return out

def svg_open(bg='#f3ecd8'):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
      '<defs><filter id="ink"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="3"/>'
      '<feColorMatrix values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -1.4 1.6"/>'
      '<feComposite in="SourceGraphic" operator="in"/></filter>'
      '<filter id="fiber"><feTurbulence type="fractalNoise" baseFrequency=".8" numOctaves="2" seed="9"/>'
      '<feColorMatrix values="0 0 0 0 .4  0 0 0 0 .33  0 0 0 0 .2  0 0 0 -1.2 .55"/></filter></defs>'
      f'<rect width="{W}" height="{H}" fill="{bg}"/>')

def guilloche(color, op=.13):
    s = [f'<g fill="none" stroke="{color}" stroke-width=".8" opacity="{op}">']
    for k in range(18):
        a = k * math.pi / 9; pts = []
        for t in range(0, 361, 4):
            th = math.radians(t); r = 260 + 40 * math.sin(6 * th + a)
            pts.append(f'{450 + r*math.cos(th):.1f},{640 + r*1.25*math.sin(th):.1f}')
        s.append(f'<polygon points="{" ".join(pts)}"/>')
    return ''.join(s) + '</g>'

INKS = ['#4b2a7a', '#1d2f6f', '#8a1c1c', '#1f1f1f', '#2b5a2e']

def stamp(u, v, cx, cy, seed):
    h = zlib.crc32((u['code'] + v['date'] + v.get('location', '')).encode())
    ink = INKS[h % len(INKS)]; rot = (h >> 4) % 21 - 10; name0 = u['name']; oval = (h >> 9) % 3 == 0 or len(name0) > 30
    rx, ry = (150, 105) if oval else (115, 115)
    name = u['name'].upper(); fs = max(11, min(19, int(560 / max(len(name), 1) * (1.15 if oval else 1))))
    pid = f'arc{seed}'
    # arc for name on top (left -> right over the top)
    ar_x, ar_y = rx - 24, ry - 24; t0 = math.radians(192)
    arc = (f'M{ar_x*math.cos(t0):.1f},{-ar_y*math.sin(t0):.1f} '
           f'A{ar_x},{ar_y} 0 1 1 {-ar_x*math.cos(t0):.1f},{-ar_y*math.sin(t0):.1f}')
    alen = math.pi * (ar_x + ar_y) / 2 * 204 / 180
    fs = max(8, min(19, (alen - 1.5 * len(name)) / (len(name) * 0.76)))
    try: d = datetime.date.fromisoformat(v['date']).strftime('%b %d %Y').upper()
    except ValueError: d = v['date'].upper()
    st = v.get('state') or u.get('stamp_state') or u['state'].split(',')[0]
    loc = v.get('location', '').upper(); lfs = max(8, min(17, (2 * rx - 84) / (max(len(loc), 1) * 0.68)))
    return (f'<g transform="translate({cx},{cy}) rotate({rot})" filter="url(#ink)" fill="{ink}" stroke="{ink}" opacity=".95">'
      f'<ellipse rx="{rx}" ry="{ry}" fill="none" stroke-width="4"/><ellipse rx="{rx-8}" ry="{ry-8}" fill="none" stroke-width="1.5"/>'
      f'<path id="{pid}" d="{arc}" fill="none" stroke="none"/>'
      f'<text font-family="DejaVu Sans" font-weight="bold" font-size="{fs}" stroke="none" letter-spacing="1">'
      f'<textPath href="#{pid}" startOffset="50%" text-anchor="middle">{esc(name)}</textPath></text>'
      f'<line x1="{-rx+34}" y1="-4" x2="{rx-34}" y2="-4" stroke-width="1.5"/><line x1="{-rx+30}" y1="44" x2="{rx-30}" y2="44" stroke-width="1.5"/>'
      f'<text y="14" text-anchor="middle" font-family="DejaVu Sans" font-weight="bold" font-size="{lfs}" stroke="none">{esc(loc)}</text>'
      f'<text y="34" text-anchor="middle" font-family="DejaVu Sans" font-size="13" stroke="none" letter-spacing="2">{esc(st)}</text>'
      f'<text y="{ry-34}" text-anchor="middle" font-family="DejaVu Sans Mono" font-weight="bold" font-size="20" stroke="none" letter-spacing="1">{esc(d)}</text>'
      '</g>')

def region_page(key, r, items, idx, n, pageno):
    c = r['color']; s = [svg_open(), guilloche(c)]
    s.append(f'<rect width="{W}" height="120" fill="{c}"/><rect y="120" width="{W}" height="6" fill="#000" opacity=".15"/>'
      f'<text x="450" y="58" text-anchor="middle" font-family="DejaVu Serif" font-weight="bold" font-size="40" fill="#fff" letter-spacing="4">{esc(r["name"].upper())}</text>'
      f'<text x="450" y="96" text-anchor="middle" font-family="DejaVu Sans" font-size="17" fill="#fff" opacity=".85" letter-spacing="5">'
      f'REGION · {len(r["units"])} UNITS{f" · PAGE {idx+1} OF {n}" if n > 1 else ""}</text>')
    slots = [(240, 320), (660, 320), (240, 640), (660, 640), (240, 960), (660, 960)]
    for (cx, cy), _ in zip(slots, range(PER)):
        s.append(f'<ellipse cx="{cx}" cy="{cy}" rx="160" ry="135" fill="none" stroke="{c}" stroke-opacity=".18" stroke-width="1.2" stroke-dasharray="5 6"/>')
    for i, (u, v) in enumerate(items):
        s.append(stamp(u, v, *slots[i], f'{key}{i}'))
    s.append(f'<rect width="{W}" height="{H}" filter="url(#fiber)" opacity=".25"/>'
      f'<text x="450" y="1215" text-anchor="middle" font-family="DejaVu Serif" font-size="16" fill="{c}">— {pageno} —</text></svg>')
    render(''.join(s), os.path.join(HERE, f'passport_{key}.png'))

def cover():
    s = [svg_open('#173d2b'), guilloche('#d8b96a', .25),
      '<rect x="30" y="30" width="840" height="1190" fill="none" stroke="#d8b96a" stroke-width="3"/>',
      '<rect x="44" y="44" width="812" height="1162" fill="none" stroke="#d8b96a" stroke-width="1"/>',
      '<g fill="#d8b96a" font-family="DejaVu Serif" font-weight="bold" text-anchor="middle">'
      '<text x="450" y="300" font-size="44" letter-spacing="10">PASSPORT</text>'
      '<text x="450" y="350" font-size="22" letter-spacing="8">TO YOUR NATIONAL PARKS</text>'
      '<path d="M450 470 L560 690 L340 690 Z" fill="none" stroke="#d8b96a" stroke-width="6"/>'
      '<path d="M380 690 L450 560 L520 690" fill="none" stroke="#d8b96a" stroke-width="4"/>'
      '<text x="450" y="900" font-size="26" letter-spacing="6">JARROD DELLACHIESA</text>'
      '<text x="450" y="1120" font-size="15" letter-spacing="5" font-weight="normal">A VIRTUAL CANCELLATION BOOK</text></g></svg>']
    render(''.join(s), os.path.join(HERE, 'passport_cover.png'))

def back_cover():
    data = json.load(open(os.path.join(HERE, 'parks.json')))['regions']
    tot = sum(len(r['units']) for r in data.values()); vis = sum(1 for r in data.values() for u in r['units'] if u['visits'])
    s = [svg_open('#173d2b'), guilloche('#d8b96a', .2), '<g fill="#d8b96a" font-family="DejaVu Serif" text-anchor="middle">',
      f'<text x="450" y="560" font-size="70" font-weight="bold">{vis} / {tot}</text>',
      '<text x="450" y="620" font-size="22" letter-spacing="6">UNITS VISITED</text>']
    for i, r in enumerate(data.values()):
        v = sum(1 for u in r['units'] if u['visits']); y = 720 + i * 44
        s.append(f'<rect x="250" y="{y-22}" width="18" height="18" fill="{r["color"]}"/>'
                 f'<text x="285" y="{y-7}" font-size="19" text-anchor="start">{esc(r["name"])}</text>'
                 f'<text x="650" y="{y-7}" font-size="19" text-anchor="end">{v} / {len(r["units"])}</text>')
    render(''.join(s) + '</g></svg>', os.path.join(HERE, 'passport_back.png'))

def main():
    a = sys.argv[1:]; only = [x.split('=', 1)[1] for x in a if x.startswith('--page=')]
    allp = not a
    for no, (key, rk, r, items, i, n) in enumerate(pages(), 1):
        if allp or '--pages' in a or rk in only or key in only: region_page(key, r, items, i, n, no)
    if allp or '--cover' in a: cover()
    if allp or '--back' in a or only: back_cover()
if __name__ == '__main__': main()
