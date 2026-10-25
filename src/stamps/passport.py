#!/usr/bin/env python3
"""NPS Passport renderer (look-alike of the classic passport book; all artwork original).
Reads parks.json (+ us-states.json for maps) and writes passport_<pagekey>.png at 2x (1800x2500).
Usage: python3 passport.py [--pages] [--cover] [--back] [--page=REGIONKEY]   (no args = everything)
Per region: an intro page (<rk>_intro: color band, region map with park dots, numbered park list)
followed by cancellation pages (<rk>, <rk>_2, ...; 6 spaces each, blank when no visits)."""
import html, json, math, os, subprocess, sys, zlib, datetime, random
HERE = os.path.dirname(os.path.abspath(__file__)); BUILD = os.path.join(HERE, 'build')
W, H = 900, 1250; PER = 6; SCALE = 2
esc = lambda s: html.escape(str(s), quote=True)
SANS, SERIF = "'Fira Sans', 'DejaVu Sans', sans-serif", "'Crimson Pro', 'DejaVu Serif', serif"
NAVY, GOLD = '#14233f', '#c9a44c'
ST = {'Alabama':'AL','Alaska':'AK','Arizona':'AZ','Arkansas':'AR','California':'CA','Colorado':'CO','Connecticut':'CT','Delaware':'DE',
 'District of Columbia':'DC','Florida':'FL','Georgia':'GA','Hawaii':'HI','Idaho':'ID','Illinois':'IL','Indiana':'IN','Iowa':'IA','Kansas':'KS',
 'Kentucky':'KY','Louisiana':'LA','Maine':'ME','Maryland':'MD','Massachusetts':'MA','Michigan':'MI','Minnesota':'MN','Mississippi':'MS',
 'Missouri':'MO','Montana':'MT','Nebraska':'NE','Nevada':'NV','New Hampshire':'NH','New Jersey':'NJ','New Mexico':'NM','New York':'NY',
 'North Carolina':'NC','North Dakota':'ND','Ohio':'OH','Oklahoma':'OK','Oregon':'OR','Pennsylvania':'PA','Rhode Island':'RI',
 'South Carolina':'SC','South Dakota':'SD','Tennessee':'TN','Texas':'TX','Utah':'UT','Vermont':'VT','Virginia':'VA','Washington':'WA',
 'West Virginia':'WV','Wisconsin':'WI','Wyoming':'WY','Puerto Rico':'PR'}
ABBR = [('National Historical Park', 'NHP'), ('National Historic Site', 'NHS'), ('National Historic Trail', 'NHT'),
 ('National Scenic Trail', 'NST'), ('National Military Park', 'NMP'), ('National Battlefield Park', 'NBP'),
 ('National Battlefield Site', 'NBS'), ('National Battlefield', 'NB'), ('National Memorial', 'N MEM'), ('National Monument', 'NM'),
 ('National Preserve', 'N PRES'), ('National Recreation Area', 'NRA'), ('National Seashore', 'NS'), ('National Lakeshore', 'NL'),
 ('National Scenic Riverway', 'NSR'), ('National Scenic River', 'NSR'), ('National Wild and Scenic River', 'NWSR'),
 ('National River', 'NR'), ('National Parkway', 'PKWY'), ('National Park', 'NP'), ('National Heritage Area', 'NHA')]
def short(n):
    for a, b in ABBR:
        if n.endswith(a): return n[:-len(a)].strip() + ' ' + b
    return n

def render(svg, out):
    os.makedirs(BUILD, exist_ok=True)
    p = os.path.join(BUILD, os.path.basename(out)[:-4] + '.svg'); open(p, 'w').write(svg)
    subprocess.run(['google-chrome', '--headless=new', '--no-sandbox', '--disable-gpu', '--hide-scrollbars',
        f'--force-device-scale-factor={SCALE}', f'--window-size={W},{H}', f'--screenshot={out}', 'file://' + p],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); print('wrote', out)

def load(): return json.load(open(os.path.join(HERE, 'parks.json')))['regions']

def pages():
    """[(pagekey, kind, regionkey, region, items, idx, n)] in book order. kind: 'intro' | 'cancel'."""
    out = []
    for rk, r in load().items():
        out.append((rk + '_intro', 'intro', rk, r, [], 0, 1))
        vs = sorted(((u, v) for u in r['units'] for v in u['visits']), key=lambda t: t[1]['date'])
        n = max(1, math.ceil(len(vs) / PER))
        for i in range(n): out.append((rk if i == 0 else f'{rk}_{i+1}', 'cancel', rk, r, vs[i*PER:(i+1)*PER], i, n))
    return out

# ------------------------------------------------------------------ shared defs / art
def defs(seed=1):
    return f'''<defs>
<linearGradient id="paper" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f7f1e1"/><stop offset=".5" stop-color="#f3ecd9"/><stop offset="1" stop-color="#ece2c8"/></linearGradient>
<radialGradient id="vign" cx=".5" cy=".5" r=".75"><stop offset=".6" stop-color="#7a5a20" stop-opacity="0"/><stop offset="1" stop-color="#7a5a20" stop-opacity=".22"/></radialGradient>
<filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="1.6" numOctaves="3" seed="{seed}"/>
 <feColorMatrix values="0 0 0 0 .35  0 0 0 0 .28  0 0 0 0 .16  0 0 0 -1.6 .9"/></filter>
<filter id="fibers" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".03 .2" numOctaves="2" seed="{seed+7}"/>
 <feColorMatrix values="0 0 0 0 .55  0 0 0 0 .45  0 0 0 0 .3  0 0 0 -3 1.45"/></filter>
<filter id="blotch" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".006" numOctaves="3" seed="{seed+3}"/>
 <feColorMatrix values="0 0 0 0 .6  0 0 0 0 .45  0 0 0 0 .2  0 0 0 -2.4 1.25"/></filter>
<filter id="ink" x="-10%" y="-10%" width="120%" height="120%">
 <feTurbulence type="fractalNoise" baseFrequency=".045" numOctaves="2" seed="{seed+11}" result="warp"/>
 <feDisplacementMap in="SourceGraphic" in2="warp" scale="2.6" result="d"/>
 <feMorphology in="d" operator="dilate" radius=".35" result="bleed"/><feGaussianBlur in="bleed" stdDeviation=".45" result="soft"/>
 <feTurbulence type="fractalNoise" baseFrequency=".011" numOctaves="2" seed="{seed+5}" result="press"/>
 <feColorMatrix in="press" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -2.6 2.1" result="pressA"/>
 <feTurbulence type="fractalNoise" baseFrequency="1.1" numOctaves="2" seed="{seed+9}" result="spk"/>
 <feColorMatrix in="spk" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -2.2 1.75" result="spkA"/>
 <feComposite in="soft" in2="pressA" operator="in" result="p1"/><feComposite in="p1" in2="spkA" operator="in"/></filter>
<pattern id="ruled" width="10" height="22" patternUnits="userSpaceOnUse"><line x1="0" y1="21.5" x2="10" y2="21.5" stroke="#9fb0c4" stroke-width=".6" opacity=".55"/></pattern>
<pattern id="micro" width="300" height="12" patternUnits="userSpaceOnUse"><text y="9" font-family="{SANS}" font-size="5.2" letter-spacing=".6" fill="#8a7b56" opacity=".55">PASSPORT · NATIONAL PARKS · PASSPORT · NATIONAL PARKS · PASSPORT · NATIONAL PARKS · PASSPORT ·</text></pattern>
</defs>'''

def guilloche(cx, cy, R, A, k, copies, color, op, sw=.5, sy=1.0):
    s = [f'<g fill="none" stroke="{color}" stroke-width="{sw}" opacity="{op}">']
    for c in range(copies):
        ph = 2 * math.pi * c / copies; pts = []
        for t in range(0, 721):
            th = math.radians(t / 2); r = R + A * math.sin(k * th + ph) + A * .35 * math.sin((k * 3 + 1) * th - ph)
            pts.append(f'{cx + r*math.cos(th):.1f},{cy + sy*r*math.sin(th):.1f}')
        s.append(f'<polygon points="{" ".join(pts)}"/>')
    return ''.join(s) + '</g>'

def wave_band(y0, y1, color, op, n=16, amp=7, per=90):
    s = [f'<g fill="none" stroke="{color}" stroke-width=".45" opacity="{op}">']
    for i in range(n):
        y = y0 + (y1 - y0) * i / (n - 1); ph = i * .55; pts = []
        for x in range(0, W + 1, 6):
            pts.append(f'{x},{y + amp*math.sin(2*math.pi*x/per + ph) + amp*.4*math.sin(2*math.pi*x/(per*.37) - ph):.1f}')
        s.append(f'<polyline points="{" ".join(pts)}"/>')
    return ''.join(s) + '</g>'

def pine(x, base, h, hatch=True):
    tiers, s = 6, []
    for t in range(tiers):
        w = h * .32 * (1 - t / tiers * .75); y = base - h * t / tiers * .9
        s.append(f'M{x-w:.1f},{y:.1f} L{x:.1f},{y-h*.28:.1f} L{x+w:.1f},{y:.1f}')
    s.append(f'M{x},{base} L{x},{base-h}')
    return ' '.join(s)

def bison(x, y, s=1.0):
    d = ('M0,0 C8,-26 30,-40 58,-38 C80,-37 96,-30 110,-22 C122,-16 128,-4 126,10 L122,34 L114,34 L112,14 C100,18 80,18 66,16 '
         'L62,36 L54,36 L52,14 C40,12 30,10 22,12 L20,36 L12,36 L10,16 C4,14 -8,14 -14,20 C-22,22 -30,16 -30,6 C-30,-4 -24,-10 -18,-10 '
         'C-12,-12 -6,-8 0,0 Z M-22,-6 C-26,-10 -28,-16 -24,-18')
    return f'<path transform="translate({x},{y}) scale({s})" d="{d}"/>'

def engraving(color, op, y=1000):
    """Original landscape engraving: hatched mountain ridges, pines, bison."""
    s = [f'<g fill="none" stroke="{color}" stroke-width=".7" opacity="{op}" stroke-linecap="round">']
    rnd = random.Random(42)
    for layer, (base, hgt, peaks) in enumerate([(y, 250, 5), (y + 40, 170, 7), (y + 80, 90, 9)]):
        xs = [i * W / (peaks - 1) for i in range(peaks)]; pts = []
        for i, x in enumerate(xs):
            pts.append((x, base - hgt * (.45 + .55 * rnd.random())))
            if i < peaks - 1: pts.append((x + W / (peaks - 1) / 2, base - hgt * .25 * rnd.random()))
        s.append('<polyline points="' + ' '.join(f'{a:.0f},{b:.0f}' for a, b in pts) + '"/>')
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):   # hatching under each slope
            for k in range(0, 14 - layer * 3):
                t = k / 14; hx, hy = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
                s.append(f'<line x1="{hx:.0f}" y1="{hy:.0f}" x2="{hx - 9 + 18*(y1>y0):.0f}" y2="{hy + 28 - layer*6:.0f}"/>')
    s.append(f'<path d="{" ".join(pine(60 + i*62 + rnd.randint(-10, 10), y + 160, 70 + rnd.randint(-15, 25)) for i in range(14))}"/>')
    s.append(f'<g stroke-width=".9">{bison(560, y + 140, .9)}{bison(690, y + 150, .7)}</g>')
    for i in range(10): s.append(f'<line x1="0" y1="{y+175+i*7}" x2="{W}" y2="{y+175+i*7}" stroke-width=".4"/>')
    return ''.join(s) + '</g>'

def corner(x, y, sx, sy, color, op=.8):
    d = ('M0,40 L0,0 L40,0 M6,46 L6,6 L46,6 M14,14 C30,14 30,30 46,30 M14,14 C14,30 30,30 30,46 '
         'M20,20 m-3,0 a3,3 0 1,0 6,0 a3,3 0 1,0 -6,0')
    return f'<path transform="translate({x},{y}) scale({sx},{sy})" d="{d}" fill="none" stroke="{color}" stroke-width="1.1" opacity="{op}"/>'

def border(color, inset=26):
    s = [f'<rect x="{inset}" y="{inset}" width="{W-2*inset}" height="{H-2*inset}" fill="none" stroke="{color}" stroke-width="1.6" opacity=".8"/>',
         f'<rect x="{inset+6}" y="{inset+6}" width="{W-2*inset-12}" height="{H-2*inset-12}" fill="none" stroke="{color}" stroke-width=".6" opacity=".7"/>',
         f'<rect x="{inset+9}" y="{inset+9}" width="{W-2*inset-18}" height="{H-2*inset-18}" fill="none" stroke="url(#micro)" stroke-width="0"/>']
    for x, y, sx, sy in [(inset, inset, 1, 1), (W-inset, inset, -1, 1), (inset, H-inset, 1, -1), (W-inset, H-inset, -1, -1)]:
        s.append(corner(x, y, sx, sy, color))
    return ''.join(s)

def paper(seed, tint='#f3ecd9'):
    return (f'<rect width="{W}" height="{H}" fill="url(#paper)"/>'
            f'<rect width="{W}" height="{H}" filter="url(#blotch)" opacity=".18"/>'
            f'<rect width="{W}" height="{H}" filter="url(#fibers)" opacity=".14"/>'
            f'<rect width="{W}" height="{H}" filter="url(#grain)" opacity=".22"/>')

def finish():
    return f'<rect width="{W}" height="{H}" fill="url(#vign)"/>'

def svg(body, seed=1):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
            f'{defs(seed)}{body}</svg>')

def tab(c, name, y=250):
    """Thumb tab on the outer edge with the region name, like the book's page tabs."""
    return (f'<path d="M{W} {y} h-30 a8 8 0 0 0 -8 8 v204 a8 8 0 0 0 8 8 h30 z" fill="{c}"/>'
            f'<text transform="translate({W-14},{y+118}) rotate(90)" text-anchor="middle" font-family="{SANS}" font-weight="700" '
            f'font-size="12.5" letter-spacing="2" fill="#fff">{esc(name.upper())}</text>')

def band(c, title, sub):
    return (f'<rect x="0" y="0" width="{W}" height="150" fill="{c}"/>'
            + wave_band(10, 140, '#ffffff', .16, 14, 5, 120)
            + f'<rect x="0" y="150" width="{W}" height="4" fill="#000" opacity=".18"/>'
            f'<rect x="0" y="154" width="{W}" height="2" fill="{GOLD}" opacity=".9"/>'
            f'<text x="60" y="78" font-family="{SERIF}" font-weight="700" font-size="50" fill="#fff" letter-spacing="1">{esc(title)}</text>'
            f'<text x="62" y="116" font-family="{SANS}" font-size="16" fill="#fff" opacity=".9" letter-spacing="4">{esc(sub)}</text>')

def folio(n, c):
    side = 'end' if n % 2 else 'start'; x = W - 70 if n % 2 else 70
    return f'<text x="{x}" y="{H-44}" text-anchor="{side}" font-family="{SANS}" font-size="14" font-weight="600" fill="{c}">{n}</text>'

# ------------------------------------------------------------------ region map
_geo = None
def geo():
    global _geo
    if _geo is None:
        _geo = {}
        for f in json.load(open(os.path.join(HERE, 'us-states.json')))['features']:
            ab = ST.get(f['properties']['name']); g = f['geometry']
            polys = [g['coordinates']] if g['type'] == 'Polygon' else g['coordinates']
            if ab: _geo[ab] = [p[0] for p in polys]
    return _geo

def proj_fn(bbox, box):
    (lo0, la0, lo1, la1), (x, y, w, h) = bbox, box
    k = math.cos(math.radians((la0 + la1) / 2))
    sx = w / ((lo1 - lo0) * k); sy = h / (la1 - la0); s = min(sx, sy)
    ox = x + (w - (lo1 - lo0) * k * s) / 2; oy = y + (h - (la1 - la0) * s) / 2
    return lambda lo, la: (ox + (lo - lo0) * k * s, oy + (la1 - la) * s)

def region_map(rk, r, box, states_in, c):
    G = geo(); x, y, w, h = box
    main = [s for s in states_in if s not in ('AK', 'HI', 'PR') and s in G]
    pts = [p for s in main for ring in G[s] for p in ring]
    lo0, lo1 = min(p[0] for p in pts), max(p[0] for p in pts); la0, la1 = min(p[1] for p in pts), max(p[1] for p in pts)
    pad = max(max(lo1 - lo0, la1 - la0) * .12, .35)
    insets = [s for s in ('AK', 'HI') if s in states_in]
    mw = w - (200 if insets else 0)
    P = proj_fn((lo0 - pad, la0 - pad, lo1 + pad, la1 + pad), (x, y, mw, h))
    out = [f'<rect x="{x-8}" y="{y-8}" width="{w+16}" height="{h+16}" rx="6" fill="#e8eef0" opacity=".55" stroke="{c}" stroke-opacity=".5"/>']
    # light graticule
    for g in range(-180, 180, 5):
        a, b = P(g, la0 - pad), P(g, la1 + pad)
        if x <= a[0] <= x + mw: out.append(f'<line x1="{a[0]:.0f}" y1="{y}" x2="{b[0]:.0f}" y2="{y+h}" stroke="#7d93a8" stroke-width=".4" opacity=".4"/>')
    for g in range(0, 90, 5):
        a = P(lo0 - pad, g)
        if y <= a[1] <= y + h: out.append(f'<line x1="{x}" y1="{a[1]:.0f}" x2="{x+mw}" y2="{a[1]:.0f}" stroke="#7d93a8" stroke-width=".4" opacity=".4"/>')
    clip = f'clip{rk}'
    out.append(f'<clipPath id="{clip}"><rect x="{x}" y="{y}" width="{mw}" height="{h}"/></clipPath><g clip-path="url(#{clip})">')
    def poly(ab, Pf, fill, op, sw):
        return ''.join('<polygon points="' + ' '.join('%.1f,%.1f' % Pf(*p) for p in ring) +
                       f'" fill="{fill}" fill-opacity="{op}" stroke="#3b4a5a" stroke-width="{sw}" stroke-linejoin="round"/>' for ring in G[ab])
    for ab in G:
        if ab not in states_in and ab not in ('AK', 'HI'): out.append(poly(ab, P, '#d9d3c2', .7, .5))
    for ab in main: out.append(poly(ab, P, c, .38, .9))
    for ab in main:
        cxs = [P(*p) for ring in G[ab][:1] for p in ring]
        mx = sum(a for a, _ in cxs) / len(cxs); my = sum(b for _, b in cxs) / len(cxs)
        out.append(f'<text x="{mx:.0f}" y="{my:.0f}" text-anchor="middle" font-family="{SANS}" font-weight="700" font-size="13" fill="#2c3a48" opacity=".45">{ab}</text>')
    out.append('</g>')
    projs = {s: P for s in main}
    for i, s in enumerate(insets):  # inset boxes for AK / HI
        bx, by, bw, bh = x + mw + 20, y + i * (h / len(insets)) + (10 if i else 0), 180, h / len(insets) - 10
        pp = [p for ring in G[s] for p in ring]
        if s == 'AK': pp = [p for p in pp if p[0] < -129 and p[0] > -170]
        l0, l1 = min(p[0] for p in pp), max(p[0] for p in pp); a0, a1 = min(p[1] for p in pp), max(p[1] for p in pp)
        Pi = proj_fn((l0 - .5, a0 - .5, l1 + .5, a1 + .5), (bx + 6, by + 22, bw - 12, bh - 28)); projs[s] = Pi
        out.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" fill="#f4f1e6" stroke="{c}" stroke-opacity=".6"/>'
                   f'<text x="{bx+8}" y="{by+16}" font-family="{SANS}" font-size="11" font-weight="700" fill="#2c3a48" letter-spacing="1.5">{"ALASKA" if s=="AK" else "HAWAII"}</text>'
                   f'<clipPath id="{clip}{s}"><rect x="{bx}" y="{by}" width="{bw}" height="{bh}"/></clipPath><g clip-path="url(#{clip}{s})">{poly(s, Pi, c, .38, .7)}</g>')
    # park dots, numbered like the list
    for n, u in enumerate(r['units'], 1):
        if u.get('lat') is None: continue
        st = u.get('stamp_state') or u['state'].split(',')[0]
        Pf = projs.get(st) or (P if st not in ('AK', 'HI', 'PR', 'VI', 'GU', 'AS', 'MP') else None)
        if not Pf: continue
        px, py = Pf(u['lon'], u['lat'])
        if not (x - 4 <= px <= x + w + 4 and y - 4 <= py <= y + h + 4): continue
        vis = bool(u['visits'])
        out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="3.6" fill="{"#1b6b2e" if vis else "#fff"}" stroke="#1d2733" stroke-width="1.1"/>'
                   f'<text x="{px+4.5:.1f}" y="{py-3.5:.1f}" font-family="{SANS}" font-size="7.5" font-weight="700" fill="#1d2733">{n}</text>')
    return ''.join(out)

REG_STATES = {}
def region_states(rk):
    if not REG_STATES:
        sys.path.insert(0, HERE); from make_parks import REGIONS
        for k, (_, _, ss) in REGIONS.items(): REG_STATES[k] = ss.split()
    return REG_STATES[rk]

# ------------------------------------------------------------------ pages
def intro_page(key, rk, r, pageno):
    c = r['color']; units = r['units']; seed = zlib.crc32(key.encode()) % 997
    s = [paper(seed), guilloche(450, 700, 300, 34, 9, 10, c, .07, .45, 1.3), engraving(c, .07, 1000), band(c, r['name'] + ' Region',
         f'{len(units)} PARK SITES · {sum(1 for u in units if u["visits"])} VISITED'), tab(c, r['name'])]
    s.append(region_map(rk, r, (60, 186, 760, 400), region_states(rk), c))
    s.append(f'<text x="60" y="628" font-family="{SERIF}" font-weight="700" font-size="22" fill="{c}">Park Sites in the {esc(r["name"])} Region</text>'
             f'<line x1="60" y1="638" x2="830" y2="638" stroke="{c}" stroke-width="1.2"/>')
    cols = 3; rows = math.ceil(len(units) / cols); top, bot = 662, H - 80
    lh = min(20, (bot - top) / max(rows, 1)); fs = min(11.5, lh * .62); cw = 770 / cols
    for n, u in enumerate(units):
        col, row = divmod(n, rows); xx = 60 + col * cw; yy = top + row * lh
        nm = short(u['name']); st = (u.get('stamp_state') or u['state'].split(',')[0])
        maxch = int((cw - 52) / (fs * .5))
        if len(nm) > maxch: nm = nm[:maxch - 1] + '…'
        box = ('<rect x="%.0f" y="%.1f" width="%.1f" height="%.1f" fill="none" stroke="#3b4a5a" stroke-width=".7"/>' %
               (xx, yy - fs * .82, fs * .82, fs * .82))
        chk = (f'<path d="M{xx+1.5:.1f},{yy-fs*.4:.1f} l{fs*.25:.1f},{fs*.3:.1f} l{fs*.5:.1f},-{fs*.75:.1f}" stroke="#1b6b2e" stroke-width="1.6" fill="none"/>'
               if u['visits'] else '')
        s.append(box + chk + f'<text x="{xx+fs+4:.1f}" y="{yy:.1f}" font-family="{SANS}" font-size="{fs:.1f}" fill="#1f2a36">'
                 f'<tspan font-weight="700" fill="{c}">{n+1}</tspan> {esc(nm)}, {esc(st)}</text>')
    s += [folio(pageno, c), finish()]
    render(svg(''.join(s), seed), os.path.join(HERE, f'passport_{key}.png'))

INKS = ['#4a2a7c', '#1c2f72', '#8c1d1d', '#202020', '#24572b']
SLOTS = [(250, 345), (650, 345), (250, 680), (650, 680), (250, 1015), (650, 1015)]

def stamp(u, v, cx, cy, uid):
    h = zlib.crc32((u['code'] + v['date'] + v.get('location', '')).encode())
    ink = INKS[h % len(INKS)]; rot = (h >> 4) % 23 - 11; oval = (h >> 9) % 3 == 0 or len(u['name']) > 30
    rx, ry = (150, 105) if oval else (115, 115)
    name = u['name'].upper(); pid = f'arc{uid}'
    ar_x, ar_y = rx - 24, ry - 24; t0 = math.radians(192)
    arc = (f'M{ar_x*math.cos(t0):.1f},{-ar_y*math.sin(t0):.1f} A{ar_x},{ar_y} 0 1 1 {-ar_x*math.cos(t0):.1f},{-ar_y*math.sin(t0):.1f}')
    alen = math.pi * (ar_x + ar_y) / 2 * 204 / 180
    fs = max(8, min(19, (alen - 1.5 * len(name)) / (len(name) * 0.76)))
    try: d = datetime.date.fromisoformat(v['date']).strftime('%b %d %Y').upper()
    except ValueError: d = v['date'].upper()
    st = v.get('state') or u.get('stamp_state') or u['state'].split(',')[0]
    loc = v.get('location', '').upper(); lfs = max(8, min(17, (2 * rx - 84) / (max(len(loc), 1) * 0.68)))
    op = .78 + ((h >> 14) % 15) / 100
    return (f'<g transform="translate({cx},{cy}) rotate({rot})" filter="url(#ink)" fill="{ink}" stroke="{ink}" opacity="{op:.2f}">'
      f'<ellipse rx="{rx}" ry="{ry}" fill="none" stroke-width="4.2"/><ellipse rx="{rx-8}" ry="{ry-8}" fill="none" stroke-width="1.6"/>'
      f'<path id="{pid}" d="{arc}" fill="none" stroke="none"/>'
      f'<text font-family="{SANS}" font-weight="700" font-size="{fs:.1f}" stroke="none" letter-spacing="1">'
      f'<textPath href="#{pid}" startOffset="50%" text-anchor="middle">{esc(name)}</textPath></text>'
      f'<line x1="{-rx+34}" y1="-4" x2="{rx-34}" y2="-4" stroke-width="1.5"/><line x1="{-rx+30}" y1="44" x2="{rx-30}" y2="44" stroke-width="1.5"/>'
      f'<text y="14" text-anchor="middle" font-family="{SANS}" font-weight="700" font-size="{lfs:.1f}" stroke="none">{esc(loc)}</text>'
      f'<text y="34" text-anchor="middle" font-family="{SANS}" font-size="13" stroke="none" letter-spacing="2">{esc(st)}</text>'
      f'<text y="{ry-34}" text-anchor="middle" font-family="DejaVu Sans Mono" font-weight="bold" font-size="20" stroke="none" letter-spacing="1">{esc(d)}</text>'
      '</g>')

def cancel_page(key, rk, r, items, idx, n, pageno):
    c = r['color']; seed = zlib.crc32(key.encode()) % 997
    s = [paper(seed), guilloche(450, 690, 330, 40, 11, 12, c, .06, .45, 1.35), guilloche(450, 690, 210, 22, 17, 8, c, .05, .4, 1.35),
         engraving(c, .05, 1010),
         f'<rect x="0" y="0" width="{W}" height="96" fill="{c}"/>', wave_band(6, 90, '#ffffff', .15, 10, 4, 120),
         f'<rect x="0" y="96" width="{W}" height="2" fill="{GOLD}"/>',
         f'<text x="60" y="58" font-family="{SERIF}" font-weight="700" font-size="34" fill="#fff">{esc(r["name"])} Region</text>',
         f'<text x="{W-60}" y="58" text-anchor="end" font-family="{SANS}" font-size="15" fill="#fff" letter-spacing="4">CANCELLATIONS{f" · {idx+1}/{n}" if n > 1 else ""}</text>',
         tab(c, r['name'], 470)]
    for i, (cx, cy) in enumerate(SLOTS):
        x0, y0 = cx - 180, cy - 150
        s.append(f'<rect x="{x0}" y="{y0}" width="360" height="300" rx="4" fill="#fffdf6" fill-opacity=".35" stroke="{c}" stroke-width="1" stroke-opacity=".55"/>'
                 f'<rect x="{x0+5}" y="{y0+5}" width="350" height="290" rx="2" fill="url(#ruled)" opacity=".5"/>'
                 f'<text x="{x0+10}" y="{y0+293}" font-family="{SANS}" font-size="9" fill="{c}" opacity=".7" letter-spacing="1.5">PARK · DATE</text>')
    for i, (u, v) in enumerate(items): s.append(stamp(u, v, *SLOTS[i], f'{key}{i}'))
    s += [folio(pageno, c), finish()]
    render(svg(''.join(s), seed), os.path.join(HERE, f'passport_{key}.png'))

def cover_texture(seed):
    return f'''<filter id="leather" x="0" y="0" width="100%" height="100%">
 <feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="4" seed="{seed}" result="n"/>
 <feDiffuseLighting in="n" lighting-color="#2a3d62" surfaceScale="1.6" result="l"><feDistantLight azimuth="225" elevation="52"/></feDiffuseLighting>
 <feComposite in="l" in2="SourceGraphic" operator="arithmetic" k1="1.25" k2="0" k3="0" k4="0"/></filter>
<filter id="linen"><feTurbulence type="turbulence" baseFrequency=".02 .9" numOctaves="1" seed="4"/><feColorMatrix values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -2 .7"/></filter>
<linearGradient id="foil" x1="0" y1="0" x2=".35" y2="1"><stop offset="0" stop-color="#f6e3a1"/><stop offset=".28" stop-color="#d4ae55"/>
 <stop offset=".5" stop-color="#a7802f"/><stop offset=".7" stop-color="#e9cf82"/><stop offset="1" stop-color="#9c7629"/></linearGradient>
<filter id="emboss" x="-5%" y="-5%" width="110%" height="110%">
 <feGaussianBlur in="SourceAlpha" stdDeviation="1.1" result="b"/>
 <feSpecularLighting in="b" surfaceScale="3" specularConstant=".9" specularExponent="18" lighting-color="#fff6d8" result="sp"><fePointLight x="250" y="-300" z="400"/></feSpecularLighting>
 <feComposite in="sp" in2="SourceAlpha" operator="in" result="spc"/>
 <feOffset in="SourceAlpha" dx="1.2" dy="1.6" result="o"/><feGaussianBlur in="o" stdDeviation="1" result="ob"/>
 <feFlood flood-color="#000" flood-opacity=".6"/><feComposite in2="ob" operator="in" result="sh"/>
 <feTurbulence type="fractalNoise" baseFrequency="2.2" numOctaves="1" seed="8" result="g"/><feColorMatrix in="g" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -1 1.25" result="ga"/>
 <feComposite in="SourceGraphic" in2="ga" operator="in" result="worn"/>
 <feMerge><feMergeNode in="sh"/><feMergeNode in="worn"/><feMergeNode in="spc"/></feMerge></filter>'''

def emblem(cx, cy, R):
    """Original emblem: double ring with mountains, pine, sun and river (not the NPS arrowhead)."""
    return (f'<g transform="translate({cx},{cy})" fill="url(#foil)" stroke="url(#foil)" filter="url(#emboss)">'
      f'<circle r="{R}" fill="none" stroke-width="5"/><circle r="{R-11}" fill="none" stroke-width="1.6"/>'
      + ''.join(f'<circle cx="{(R-5.5)*math.cos(a*math.pi/18):.1f}" cy="{(R-5.5)*math.sin(a*math.pi/18):.1f}" r="1.6" stroke="none"/>' for a in range(36))
      + f'<circle cx="38" cy="-38" r="17" fill="none" stroke-width="2.5"/>'
      + ''.join(f'<line x1="{38+23*math.cos(a*math.pi/6):.1f}" y1="{-38+23*math.sin(a*math.pi/6):.1f}" x2="{38+30*math.cos(a*math.pi/6):.1f}" y2="{-38+30*math.sin(a*math.pi/6):.1f}" stroke-width="2"/>' for a in range(12))
      + f'<path d="M-92,40 L-40,-46 L-14,-8 L12,-52 L80,40 Z" stroke="none"/>'
      f'<path d="M-40,-46 L-30,-30 L-38,-26 L-48,-32 Z M12,-52 L24,-32 L14,-28 L2,-34 Z" fill="#14233f" stroke="none" opacity=".6"/>'
      f'<path d="{pine(-66, 64, 74)}" fill="none" stroke-width="3"/>'
      f'<path d="M-92,58 C-40,48 0,70 40,56 C60,50 80,54 92,52" fill="none" stroke-width="3"/>'
      f'<path d="M-86,72 C-40,64 0,82 40,70 C60,66 80,68 88,66" fill="none" stroke-width="2"/></g>')

def cover():
    seed = 21
    s = [f'<defs>{cover_texture(seed)}</defs>',
         f'<rect width="{W}" height="{H}" fill="{NAVY}" filter="url(#leather)"/>',
         f'<rect width="{W}" height="{H}" filter="url(#linen)" opacity=".18"/>',
         f'<radialGradient id="cv" cx=".45" cy=".35" r=".85"><stop offset="0" stop-color="#3c5683" stop-opacity=".35"/><stop offset="1" stop-color="#000" stop-opacity=".55"/></radialGradient>',
         f'<rect width="{W}" height="{H}" fill="url(#cv)"/>',
         # spiral binding holes along the left edge
         ''.join(f'<ellipse cx="22" cy="{50+i*38}" rx="6" ry="9" fill="#05080f" stroke="#55627a" stroke-width="1"/>' for i in range(31)),
         f'<g filter="url(#emboss)">{guilloche(470, 620, 250, 28, 13, 14, "url(#foil)", .55, .55, 1.25)}</g>',
         f'<g filter="url(#emboss)" fill="none" stroke="url(#foil)"><rect x="62" y="48" width="804" height="1154" stroke-width="3"/>'
         f'<rect x="72" y="58" width="784" height="1134" stroke-width="1"/>'
         + ''.join(corner(x, y, sx, sy, 'url(#foil)', 1) for x, y, sx, sy in [(72, 58, 1, 1), (856, 58, -1, 1), (72, 1192, 1, -1), (856, 1192, -1, -1)]) + '</g>',
         f'<g filter="url(#emboss)" fill="url(#foil)" text-anchor="middle">'
         f'<text x="465" y="250" font-family="{SERIF}" font-weight="700" font-size="104" letter-spacing="10">Passport</text>'
         f'<text x="465" y="318" font-family="{SERIF}" font-weight="600" font-style="italic" font-size="42" letter-spacing="2">To Your National Parks</text>'
         f'<rect x="300" y="350" width="330" height="2"/><rect x="300" y="356" width="330" height="1"/></g>',
         emblem(465, 640, 165),
         f'<g filter="url(#emboss)" fill="url(#foil)" text-anchor="middle" font-family="{SANS}">'
         f'<text x="465" y="900" font-size="20" letter-spacing="9" font-weight="600">UNITED STATES OF AMERICA</text>'
         f'<text x="465" y="1010" font-size="26" letter-spacing="7" font-weight="700">JARROD DELLACHIESA</text>'
         f'<text x="465" y="1120" font-size="13" letter-spacing="6">A VIRTUAL CANCELLATION BOOK</text></g>']
    render(svg(''.join(s), seed), os.path.join(HERE, 'passport_cover.png'))

def back_cover():
    data = load(); seed = 33
    tot = sum(len(r['units']) for r in data.values()); vis = sum(1 for r in data.values() for u in r['units'] if u['visits'])
    s = [f'<defs>{cover_texture(seed)}</defs>', f'<rect width="{W}" height="{H}" fill="{NAVY}" filter="url(#leather)"/>',
         f'<rect width="{W}" height="{H}" filter="url(#linen)" opacity=".18"/>',
         ''.join(f'<ellipse cx="{W-22}" cy="{50+i*38}" rx="6" ry="9" fill="#05080f" stroke="#55627a" stroke-width="1"/>' for i in range(31)),
         f'<g filter="url(#emboss)" fill="none" stroke="url(#foil)"><rect x="34" y="48" width="804" height="1154" stroke-width="3"/><rect x="44" y="58" width="784" height="1134" stroke-width="1"/></g>',
         f'<g filter="url(#emboss)">{engraving("url(#foil)", .5, 260)}</g>',
         f'<g filter="url(#emboss)" fill="url(#foil)" text-anchor="middle"><text x="436" y="610" font-family="{SERIF}" font-size="84" font-weight="700">{vis} / {tot}</text>'
         f'<text x="436" y="660" font-family="{SANS}" font-size="20" letter-spacing="7">PARK SITES VISITED</text></g>']
    for i, r in enumerate(data.values()):
        v = sum(1 for u in r['units'] if u['visits']); y = 740 + i * 46
        s.append(f'<rect x="230" y="{y-24}" width="34" height="22" rx="3" fill="{r["color"]}" stroke="#d4ae55" stroke-width="1"/>'
                 f'<text x="280" y="{y-7}" font-family="{SANS}" font-size="19" fill="#e8d7a6">{esc(r["name"])}</text>'
                 f'<text x="640" y="{y-7}" text-anchor="end" font-family="{SANS}" font-size="19" fill="#e8d7a6">{v} / {len(r["units"])}</text>')
    render(svg(''.join(s), seed), os.path.join(HERE, 'passport_back.png'))

def main():
    a = sys.argv[1:]; only = [x.split('=', 1)[1] for x in a if x.startswith('--page=')]
    allp = not a
    for no, (key, kind, rk, r, items, i, n) in enumerate(pages(), 2):
        if allp or '--pages' in a or rk in only or key in only:
            (intro_page(key, rk, r, no) if kind == 'intro' else cancel_page(key, rk, r, items, i, n, no))
    if allp or '--cover' in a: cover()
    if allp or '--back' in a or only: back_cover()
if __name__ == '__main__': main()
