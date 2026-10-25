"""Original engraved-badge emblems (gold foil on navy). No NPS arrowhead / trademarked art."""
import math
NAVY = '#14233f'

def hatch(clip_id, poly, x0, y0, x1, y1, ang, gap, sw=.9, color=NAVY):
    """Parallel engraving lines at angle `ang` clipped to polygon."""
    s = [f'<clipPath id="{clip_id}"><polygon points="{poly}"/></clipPath><g clip-path="url(#{clip_id})" stroke="{color}" stroke-width="{sw}" stroke-linecap="round">']
    L = (x1 - x0) + (y1 - y0); a = math.radians(ang); dx, dy = math.cos(a), math.sin(a)
    nx, ny = -dy, dx; cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    k = -L
    while k <= L:
        px, py = cx + nx * k, cy + ny * k
        s.append(f'<line x1="{px-dx*L:.1f}" y1="{py-dy*L:.1f}" x2="{px+dx*L:.1f}" y2="{py+dy*L:.1f}"/>')
        k += gap
    return ''.join(s) + '</g>'

def foil_u(uid, R):
    return (f'<linearGradient id="fu{uid}" gradientUnits="userSpaceOnUse" x1="{-R}" y1="{-R}" x2="{R*.4}" y2="{R}">'
            '<stop offset="0" stop-color="#f6e3a1"/><stop offset=".28" stop-color="#d4ae55"/><stop offset=".5" stop-color="#a7802f"/>'
            '<stop offset=".7" stop-color="#e9cf82"/><stop offset="1" stop-color="#9c7629"/></linearGradient>')

def P(pts): return ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts)

def rope(R, n=72, w=7, sw=2.2):
    s = []
    for i in range(n):
        a = 2 * math.pi * i / n; x, y = R * math.cos(a), R * math.sin(a)
        s.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{w*.95:.1f}" ry="{w*.42:.1f}" transform="rotate({math.degrees(a)+62:.1f} {x:.1f} {y:.1f})" fill="none" stroke-width="{sw}"/>')
    return ''.join(s)

def beads(R, n, r):
    return ''.join(f'<circle cx="{R*math.cos(2*math.pi*i/n):.1f}" cy="{R*math.sin(2*math.pi*i/n):.1f}" r="{r}" stroke="none"/>' for i in range(n))

def pine_eng(x, base, h, uid='t'):
    """Engraved conifer: trunk + dense tapered, drooping branch strokes, symmetric."""
    o = [f'<line x1="{x}" y1="{base}" x2="{x}" y2="{base-h}" stroke-width="2.2"/>']
    n = 26
    for i in range(n):
        f = i / n; y = base - h * .1 - h * .88 * f; L = h * .26 * (1 - f) ** 1.05 + 3
        for sgn in (-1, 1):
            o.append(f'<path d="M{x},{y:.1f} Q{x+sgn*L*.55:.1f},{y+L*.12:.1f} {x+sgn*L:.1f},{y+L*.42:.1f}" fill="none" stroke-width="{1.7-f*.6:.2f}"/>')
            for j in (1, 2):  # needles
                px = x + sgn * L * j / 3; py = y + L * .1 * j
                o.append(f'<line x1="{px:.1f}" y1="{py:.1f}" x2="{px+sgn*3:.1f}" y2="{py+5:.1f}" stroke-width=".8"/>')
    body = "".join(o)
    return (f'<g fill="none" stroke-linecap="round"><g stroke="{NAVY}" stroke-width="3.6">{body.replace("stroke-width", "data-w")}</g>{body}</g>')

def sequoia(x, base, h, flip=1, uid='t'):
    """Tall conifer silhouette with layered drooping branches + navy notch engraving."""
    tiers = 11; pts_l, pts_r = [], []
    for t in range(tiers + 1):
        f = t / tiers; y = base - h * (.12 + .88 * f); w = h * .2 * (1 - f) ** .9 + 2
        pts_l += [(x - w, y + h * .035), (x - w * .45, y)]; pts_r += [(x + w * .45, y), (x + w, y + h * .035)]
    poly = [(x - 3, base)] + pts_l + [(x, base - h - 8)] + pts_r[::-1] + [(x + 3, base)]
    s = f'<polygon points="{P(poly)}" stroke="none"/>'
    s += f'<g stroke="{NAVY}" stroke-width=".8" fill="none">'
    for t in range(1, tiers):
        f = t / tiers; y = base - h * (.12 + .88 * f); w = h * .2 * (1 - f) ** .9
        s += f'<path d="M{x-w*.85:.1f},{y+h*.03:.1f} Q{x:.1f},{y-h*.02:.1f} {x+w*.85:.1f},{y+h*.03:.1f}"/>'
    # shadow hatching on the right half
    s += '</g>' + hatch(f'th{uid}', P([(x, base - h - 8)] + pts_r[::-1] + [(x + 3, base)]), x - 60, base - h - 20, x + 60, base, 70, 2.6, .55)
    return s

def peaks(cx, base, uid, scale=1.0):
    """Symmetric 3-peak range: lit left faces solid foil, shadow right faces navy-hatched, snow caps clean."""
    S = scale; out = []
    ranges = [  # (apex x offset, apex height, half width)
        (-62, 92, 70), (62, 92, 70), (0, 142, 92)]
    for i, (ox, ht, hw) in enumerate(ranges):
        ax, ay = cx + ox * S, base - ht * S; lx, rx = ax - hw * S, ax + hw * S
        out.append(f'<polygon points="{P([(lx, base), (ax, ay), (rx, base)])}" stroke="none"/>')
        # shadow face
        sh = [(ax, ay), (rx, base), (ax + hw * .18 * S, base), (ax + 6 * S, ay + ht * .45 * S), (ax - 2 * S, ay + ht * .22 * S)]
        out.append(hatch(f'pk{uid}{i}', P(sh), lx, ay, rx, base, 62, 2.8 * S, 1.15))
        # ridge cross-hatch on lit face lower part
        lit = [(lx, base), (ax - hw * .45 * S, base - ht * .45 * S), (ax - hw * .1 * S, base - ht * .2 * S), (ax - hw * .25 * S, base)]
        out.append(hatch(f'pl{uid}{i}', P(lit), lx, ay, rx, base, -30, 3.4 * S, .5))
        # snow line (jagged) – navy outline under the cap
        sn = ht * .3; pts = []
        for k in range(9):
            t = k / 8; x = ax - hw * (sn / ht) * S + 2 * hw * (sn / ht) * S * t
            y = ay + sn * S + (6 if k % 2 else -3) * S * (1 - abs(t - .5))
            pts.append((x, y))
        out.append(f'<polyline points="{P(pts)}" fill="none" stroke="{NAVY}" stroke-width="1.2"/>')
        out.append(f'<polyline points="{P([(lx, base), (ax, ay), (rx, base)])}" fill="none" stroke="{NAVY}" stroke-width="1.1"/>')
    return ''.join(out)

def lake(cx, y, w, rows, uid):
    s = [f'<g stroke-width="1.6" stroke-linecap="round" fill="none">']
    for i in range(rows):
        yy = y + 8 + i * 7.5; ww = w * (1 - i * .07)
        segs = 5 + i % 3; gap = ww / segs
        for k in range(segs):
            x0 = cx - ww / 2 + k * gap + (3 if (i + k) % 2 else 9); x1 = x0 + gap - 12 - (i % 2) * 6
            if x1 > x0: s.append(f'<line x1="{x0:.1f}" y1="{yy:.1f}" x2="{x1:.1f}" y2="{yy:.1f}"/>')
    # peak reflection: tapering centered lines
    for i in range(6):
        yy = y + 11 + i * 7.5; ww = 70 - i * 11
        s.append(f'<line x1="{cx-ww:.1f}" y1="{yy:.1f}" x2="{cx+ww:.1f}" y2="{yy:.1f}" stroke-width="2.6"/>')
    return ''.join(s) + '</g>'

def sky(R, y_hor, uid, gap=4.2):
    """Fine horizontal engraved sky lines + sunburst behind the central peak."""
    s = [f'<clipPath id="sky{uid}"><circle r="{R}"/></clipPath><g clip-path="url(#sky{uid})" fill="none">']
    for i in range(int((R + y_hor) / gap)):
        y = -R + i * gap
        if y < y_hor: s.append(f'<line x1="{-R}" y1="{y:.1f}" x2="{R}" y2="{y:.1f}" stroke-width=".55" opacity=".7"/>')
    for k in range(25):
        a = math.radians(180 + k * 7.5)
        s.append(f'<line x1="{30*math.cos(a):.1f}" y1="{y_hor-90+30*math.sin(a):.1f}" x2="{R*1.2*math.cos(a):.1f}" y2="{y_hor-90+R*1.2*math.sin(a):.1f}" stroke-width="{1.4 if k%2 else .6}" opacity=".8"/>')
    return ''.join(s) + '</g>'

def scene(R, uid):
    hor = 46
    return (foil_u(uid, R) + f'<g fill="url(#fu{uid})" stroke="url(#fu{uid})">' + sky(R - 2, hor, uid)
            + f'<clipPath id="sc{uid}"><circle r="{R-2}"/></clipPath><g clip-path="url(#sc{uid})">'
            + peaks(0, hor, uid, 1.0)
            + f'<rect x="{-R}" y="{hor-2}" width="{2*R}" height="6" stroke="none"/>'
            + lake(0, hor, 2 * R, 7, uid)
            + f'<path d="M{-R},{hor+64} C{-R*.6},{hor+52} {-R*.3},{hor+60} 0,{hor+58} C{R*.3},{hor+60} {R*.6},{hor+52} {R},{hor+64} L{R},{R} L{-R},{R} Z" stroke="none"/>'
            + hatch(f'gr{uid}', P([(-R, hor+64), (R, hor+64), (R, R), (-R, R)]), -R, hor, R, R, -20, 3.2, .7)
            + pine_eng(-R * .74, hor + 62, 170) + pine_eng(R * .74, hor + 62, 170)
            + pine_eng(-R * .57, hor + 64, 118) + pine_eng(R * .57, hor + 64, 118)
            + '</g></g>')

def emblem_a(cx, cy, R=170):
    """Circular seal: rope border, bead ring, engraved scene, banner-free."""
    r_in = R - 34
    return (f'<g transform="translate({cx},{cy})" fill="url(#foil)" stroke="url(#foil)" filter="url(#emboss)">'
            f'<circle r="{R}" fill="none" stroke-width="3.2"/>' + rope(R - 12, 84, 7.2, 2) +
            f'<circle r="{R-23}" fill="none" stroke-width="1.6"/>' + beads(R - 28.5, 96, 1.5) +
            f'<circle r="{r_in}" fill="none" stroke-width="2.6"/>' + scene(r_in - 3, 'A') + '</g>')

def emblem_b(cx, cy, R=170):
    """Shield badge with rope edge and scene; stars in chief."""
    w, h = R * 1.55, R * 1.95
    def shield(sx, sy):
        return (f'M{-sx},{-sy} L{sx},{-sy} L{sx},{sy*.15} C{sx},{sy*.65} {sx*.45},{sy*.9} 0,{sy} '
                f'C{-sx*.45},{sy*.9} {-sx},{sy*.65} {-sx},{sy*.15} Z')
    return (f'<g transform="translate({cx},{cy-10})" fill="url(#foil)" stroke="url(#foil)" filter="url(#emboss)">'
            f'<path d="{shield(w/2, h/2)}" fill="none" stroke-width="3.2"/>'
            f'<path d="{shield(w/2-9, h/2-9)}" fill="none" stroke-width="5" stroke-dasharray="2.2 3.2"/>'
            f'<path d="{shield(w/2-17, h/2-17)}" fill="none" stroke-width="1.6"/>'
            f'<clipPath id="shB"><path d="{shield(w/2-21, h/2-21)}"/></clipPath><g clip-path="url(#shB)" transform="translate(0,26)">'
            + scene(R * 1.05, 'B') + '</g>'
            + f'<line x1="{-w/2+17}" y1="{-h/2+56}" x2="{w/2-17}" y2="{-h/2+56}" stroke-width="1.6"/>'
            f'<rect x="{-w/2+17}" y="{-h/2+17}" width="{w-34}" height="39" stroke="none"/>'
            + ''.join(f'<path transform="translate({x},{-h/2+37}) scale(.9)" d="M0,-10 L2.9,-3.1 10,-3.1 4.3,1.2 6.5,8.1 0,3.9 -6.5,8.1 -4.3,1.2 -10,-3.1 -2.9,-3.1Z" fill="{NAVY}" stroke="none"/>' for x in (-60, -30, 0, 30, 60))
            + '</g>')

def emblem_c(cx, cy, R=170):
    """Circular seal with lettered ring (PASSPORT · NATIONAL PARKS) and elk-free scene, star separators."""
    r_in = R - 46
    return (f'<g transform="translate({cx},{cy})" fill="url(#foil)" stroke="url(#foil)" filter="url(#emboss)">'
            f'<circle r="{R}" fill="none" stroke-width="3"/>' + beads(R - 7, 120, 1.6) +
            f'<circle r="{R-14}" fill="none" stroke-width="1.4"/>'
            f'<path id="ringC" d="M{-(R-32)},0 A{R-32},{R-32} 0 1 1 {R-32},0" fill="none" stroke="none"/>'
            f'<path id="ringC2" d="M{-(R-23)},0 A{R-23},{R-23} 0 0 0 {R-23},0" fill="none" stroke="none"/>'
            f'<text font-family="\'Crimson Pro\',serif" font-weight="700" font-size="25" letter-spacing="6" stroke="none">'
            f'<textPath href="#ringC" startOffset="50%" text-anchor="middle">PASSPORT · NATIONAL PARKS</textPath></text>'
            f'<text font-family="\'Crimson Pro\',serif" font-weight="700" font-size="17" letter-spacing="5" stroke="none">'
            f'<textPath href="#ringC2" startOffset="50%" text-anchor="middle">★ EST. MMXXVI ★</textPath></text>'
            f'<circle r="{r_in+4}" fill="none" stroke-width="1.4"/>' + rope(r_in - 4, 64, 5.5, 1.6) +
            f'<circle r="{r_in-12}" fill="none" stroke-width="2"/>' + scene(r_in - 14, 'C') + '</g>')
