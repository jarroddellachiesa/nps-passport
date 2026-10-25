"""Original vector bald eagle + waving American flag/banner for the cover (flat gold foil)."""
import math
NAVY2 = '#22377a'

def smooth(pts, closed=True):
    """Catmull-Rom -> cubic bezier path through points. Points tagged with 'c' (corner) stay sharp."""
    n = len(pts); P = [(p[0], p[1]) for p in pts]; d = f'M{P[0][0]:.1f},{P[0][1]:.1f}'
    for i in range(n if closed else n - 1):
        p0, p1, p2, p3 = P[(i-1) % n], P[i], P[(i+1) % n], P[(i+2) % n]
        t = .18
        c1 = (p1[0] + (p2[0]-p0[0])*t, p1[1] + (p2[1]-p0[1])*t) if len(pts[i]) < 3 else p1
        c2 = (p2[0] - (p3[0]-p1[0])*t, p2[1] - (p3[1]-p1[1])*t) if len(pts[(i+1) % n]) < 3 else p2
        d += f' C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}'
    return d + (' Z' if closed else '')

def rot(x, y, a):
    c, s = math.cos(a), math.sin(a); return x*c - y*s, x*s + y*c

def wing(sx, sy, ang, L, Wd, nf=5, spread=38, flen=.34, sec=9):
    """Wing from shoulder (sx,sy) pointing at angle ang (deg, 0=right, -90=up). Returns point list.
    Leading edge, splayed primary fingers, scalloped trailing edge."""
    a = math.radians(ang)
    def T(u, v):  # u along wing, v perpendicular (+v = leading side)
        x, y = rot(u, -v, a); return (sx + x, sy + y)
    pts = [T(0, Wd*.5), T(L*.25, Wd*.62), T(L*.5, Wd*.58), T(L*.68, Wd*.5)]  # leading edge (arm, wrist bulge)
    hand = L*.7
    # fingers: fan from leading to trailing
    for k in range(nf):
        f = k / (nf - 1); fa = math.radians(spread*(f - .2))  # fan angle relative to wing axis
        base_v = Wd*(.4 - .85*f)
        bl = T(hand + L*.02, base_v + Wd*.075); br = T(hand + L*.02, base_v - Wd*.075)
        fl = L*flen*(1 - .25*abs(f - .3))
        tipu, tipv = rot(fl, 0, -fa)
        tip = T(hand + L*.02 + tipu, base_v - tipv)
        mid1 = T(hand + L*.02 + tipu*.6, base_v - tipv*.6 + Wd*.045)
        mid2 = T(hand + L*.02 + tipu*.6, base_v - tipv*.6 - Wd*.045)
        pts += [bl + ('c',), mid1, tip, mid2, br + ('c',)]
    # trailing edge back to body with secondary feather scallops
    for k in range(sec):
        f = k / sec; u = hand*(1 - f); v = -Wd*(.55 + .12*math.sin(math.pi*f))
        pts += [T(u, v - Wd*.1), T(u - hand/sec*.5, v) + ('c',)]
    pts.append(T(0, -Wd*.45))
    return pts

def fingers(b0, b1, a0, a1, n, L0, L1, w):
    """Splayed primary feathers along hand base b0->b1; angles a0->a1 (deg); returns point list b0 ... b1."""
    pts = []
    for k in range(n):
        f = k / (n - 1); bx = b0[0] + (b1[0]-b0[0])*f; by = b0[1] + (b1[1]-b0[1])*f
        a = math.radians(a0 + (a1-a0)*f); L = L0 + (L1-L0)*f
        ux, uy = math.cos(a), math.sin(a); px, py = -uy, ux
        bx -= ux*16; by -= uy*16; L += 16
        pts += [(bx - px*w/2, by - py*w/2, 'c'), (bx + ux*L*.55 - px*w*.55, by + uy*L*.55 - py*w*.55),
                (bx + ux*L, by + uy*L), (bx + ux*L*.55 + px*w*.55, by + uy*L*.55 + py*w*.55), (bx + px*w/2, by + py*w/2, 'c')]
    return pts

def scallop(a, b, n, depth):
    pts = []
    for k in range(n):
        f0, f1 = k/n, (k+.5)/n
        x0, y0 = a[0] + (b[0]-a[0])*f0, a[1] + (b[1]-a[1])*f0
        xm, ym = a[0] + (b[0]-a[0])*f1, a[1] + (b[1]-a[1])*f1
        dx, dy = b[0]-a[0], b[1]-a[1]; l = math.hypot(dx, dy); nx, ny = dy/l, -dx/l
        pts += [(x0, y0, 'c'), (xm - nx*depth, ym - ny*depth)]
    return pts

def eagle(ox, oy, s):
    """Bald eagle flying right, wings raised in a V, splayed primaries, hooked beak, fanned tail. Local ~0..400."""
    near = ([(195, 222), (180, 178), (150, 122), (112, 72)]
            + fingers((112, 72), (52, 142), -112, -178, 5, 80, 68, 20)
            + scallop((52, 142), (190, 258), 7, 12) + [(205, 250)])
    far = ([(238, 215), (262, 160), (290, 104), (318, 62)]
           + fingers((318, 62), (360, 118), -95, -28, 5, 64, 52, 18)
           + scallop((360, 118), (262, 240), 6, 10) + [(250, 238)])
    body = [(175, 246), (215, 222), (262, 214), (300, 210), (322, 196), (346, 192), (364, 196), (380, 206),
            (388, 218, 'c'), (384, 230), (378, 236, 'c'), (376, 226), (366, 228), (352, 236), (336, 246),
            (318, 262), (290, 280), (250, 290), (212, 286), (182, 274)]
    tail = [(186, 250)]
    for k in range(5):
        a = math.radians(158 + k*13); r = 104
        cx, cy = 186 + r*math.cos(a), 262 + r*math.sin(a)
        tail += [(cx + 7*math.sin(a), cy - 7*math.cos(a)), (cx - 6*math.cos(a), cy - 6*math.sin(a)), (cx - 7*math.sin(a), cy + 7*math.cos(a), 'c')]
    tail += [(196, 282)]
    talon = [(244, 284), (256, 304), (262, 318, 'c'), (270, 308), (280, 318, 'c'), (278, 300), (262, 282)]
    return ''.join([f'<g transform="translate({ox},{oy}) scale({s})">',
         f'<path d="{smooth(far)}" stroke="{NAVY2}" stroke-width="5" paint-order="stroke"/>',
         f'<path d="{smooth(tail)}"/><path d="{smooth(talon)}"/><path d="{smooth(body)}"/>',
         f'<path d="{smooth(near)}" stroke="{NAVY2}" stroke-width="5" paint-order="stroke"/>',
         f'<path d="M322,198 C314,214 314,236 326,252" fill="none" stroke="{NAVY2}" stroke-width="3.5"/>',
         f'<circle cx="358" cy="205" r="3.6" fill="{NAVY2}"/>',
         f'<path d="M372,214 C376,216 380,218 384,222" fill="none" stroke="{NAVY2}" stroke-width="2.4"/>', '</g>'])

def star(cx, cy, r):
    pts = []
    for k in range(10):
        a = math.radians(-90 + k*36); rr = r if k % 2 == 0 else r*.4
        pts.append(f'{cx + rr*math.cos(a):.1f},{cy + rr*math.sin(a):.1f}')
    return f'<polygon points="{" ".join(pts)}"/>'

def wave(x, y0):  # fabric ripple displacement
    return y0 + 22*math.sin(x/95 + .6) + 9*math.sin(x/37) - (x - 110)*.09

def flag(x0=110, x1=600, top=975, H=1250):
    """Waving flag: canton with stars, navy gap stripes, rippled; right side flows into banner."""
    out = []
    xs = list(range(x0, x1 + 1, 10))
    topline = [(x, wave(x, top)) for x in xs]
    shape = 'M' + ' L'.join(f'{x:.0f},{y:.1f}' for x, y in topline) + f' L{x1+40},{H} L{x0},{H} Z'
    out.append(f'<clipPath id="flagclip"><path d="{shape}"/></clipPath>')
    out.append(f'<path d="{shape}"/>')
    out.append(f'<g clip-path="url(#flagclip)" fill="none" stroke="{NAVY2}" stroke-width="18">')
    sh = 40  # stripe pitch
    canton_w, canton_rows = 230, 3
    for i in range(1, 8):
        y = top + i*sh
        xa = x0 + canton_w + 14 if i <= canton_rows else x0
        out.append('<polyline points="' + ' '.join(f'{x},{wave(x, y):.1f}' for x in range(xa, x1 + 60, 10)) + '"/>')
    # canton edge
    out.append('<polyline stroke-width="5" points="' + ' '.join(f'{x0+canton_w+4+ (wave(x0+canton_w, top+k*10)-top-k*10)*0:.0f},{wave(x0+canton_w, top+k*10)+0:.1f}' for k in range(0, int(canton_rows*sh/10)+3)) + '"/>')
    out.append(f'<polyline stroke-width="6" points="' + ' '.join(f'{x},{wave(x, top+canton_rows*sh+12):.1f}' for x in range(x0, x0+canton_w+10, 10)) + '"/>')
    out.append('</g>')
    out.append(f'<g fill="{NAVY2}">')
    for r in range(3):
        for c in range(4 if r % 2 == 0 else 3):
            x = x0 + 30 + c*58 + (29 if r % 2 else 0); y = wave(x, top + 30 + r*38)
            out.append(star(x, y, 17))
    out.append('</g>')
    return ''.join(out)

def banner():
    """Banner rising to the right out of the flag, with concentric stripes so it reads as the flag continuing."""
    d = 'M455,1150 C620,1150 690,1060 696,960 C702,860 740,790 860,780'
    s = [f'<path d="{d}" fill="none" stroke="{NAVY2}" stroke-width="162"/>', f'<path d="{d}" fill="none" stroke="url(#gold)" stroke-width="150"/>']
    for w, c in [(124, NAVY2), (106, 'url(#gold)'), (78, NAVY2), (60, 'url(#gold)'), (32, NAVY2), (14, 'url(#gold)')]:
        s.append(f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{w}"/>')
    d2 = 'M800,810 C850,910 820,1075 720,1262'
    s.append(f'<path d="{d2}" fill="none" stroke="url(#gold)" stroke-width="120"/>')
    return ''.join(s)
