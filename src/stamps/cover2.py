"""Classic-style cover (original vector interpretation): pebbled navy vinyl, flat gold foil type, eagle/flag/ribbon silhouette."""
W, H = 900, 1250
NAVY2 = '#22377a'
FONT = "Arimo, 'Liberation Sans', Helvetica, Arial, sans-serif"
COND = "'Roboto Condensed', 'Archivo Narrow', sans-serif"

def defs(seed=5):
    return f'''<defs>
<filter id="pebble" x="0" y="0" width="100%" height="100%">
 <feTurbulence type="fractalNoise" baseFrequency=".55" numOctaves="3" seed="{seed}" result="n"/>
 <feDiffuseLighting in="n" lighting-color="#ffffff" surfaceScale="1.3" result="l"><feDistantLight azimuth="235" elevation="58"/></feDiffuseLighting>
 <feColorMatrix in="l" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  .9 0 0 0 -.62" result="hi"/>
 <feComposite in="hi" in2="SourceGraphic" operator="in"/></filter>
<filter id="pebdark" x="0" y="0" width="100%" height="100%">
 <feTurbulence type="fractalNoise" baseFrequency=".55" numOctaves="3" seed="{seed}" result="n"/>
 <feDiffuseLighting in="n" lighting-color="#ffffff" surfaceScale="1.3" result="l"><feDistantLight azimuth="55" elevation="58"/></feDiffuseLighting>
 <feColorMatrix in="l" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 .03  -1 0 0 0 .75"/></filter>
<radialGradient id="cvsh" cx=".55" cy=".4" r=".9"><stop offset="0" stop-color="#fff" stop-opacity=".07"/><stop offset=".7" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".28"/></radialGradient>
<linearGradient id="gold" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{W}" y2="{H}">
 <stop offset="0" stop-color="#e6c766"/><stop offset=".35" stop-color="#f3dc86"/><stop offset=".55" stop-color="#d2ae4a"/>
 <stop offset=".78" stop-color="#f0d77c"/><stop offset="1" stop-color="#c79f3c"/></linearGradient>
<filter id="foilgrain" x="-2%" y="-2%" width="104%" height="104%">
 <feTurbulence type="fractalNoise" baseFrequency="1.4" numOctaves="2" seed="3" result="g"/>
 <feColorMatrix in="g" values="0 0 0 0 1  0 0 0 0 .95  0 0 0 0 .8  0 0 0 -1.2 .75" result="ga"/>
 <feComposite in="ga" in2="SourceAlpha" operator="in" result="sp"/>
 <feOffset in="SourceAlpha" dx=".6" dy=".9" result="o"/><feFlood flood-color="#0a1433" flood-opacity=".55"/><feComposite in2="o" operator="in" result="sh"/>
 <feMerge><feMergeNode in="sh"/><feMergeNode in="SourceGraphic"/><feMergeNode in="sp"/></feMerge></filter>
</defs>'''

def vinyl(spiral_side='left'):
    s = [f'<rect width="{W}" height="{H}" fill="{NAVY2}"/>',
         f'<rect width="{W}" height="{H}" fill="#000" filter="url(#pebdark)" opacity=".35"/>',
         f'<rect width="{W}" height="{H}" fill="#fff" filter="url(#pebble)" opacity=".22"/>',
         f'<rect width="{W}" height="{H}" fill="url(#cvsh)"/>']
    x = 30 if spiral_side == 'left' else W - 30
    for i in range(34):
        y = 30 + i * 35.6
        s.append(f'<circle cx="{x}" cy="{y+4:.1f}" r="4.2" fill="#0b1430"/>'
                 f'<path d="M{x-30 if spiral_side=="left" else x+30},{y-6:.1f} C{x-14 if spiral_side=="left" else x+14},{y-12:.1f} {x},{y-4:.1f} {x},{y+4:.1f}" '
                 f'fill="none" stroke="#e9ecf2" stroke-width="3.4" stroke-linecap="round"/>'
                 f'<path d="M{x-30 if spiral_side=="left" else x+30},{y-6:.1f} C{x-14 if spiral_side=="left" else x+14},{y-12:.1f} {x},{y-4:.1f} {x},{y+4:.1f}" '
                 f'fill="none" stroke="#9aa3b5" stroke-width="1" transform="translate(0,1.6)"/>')
    return ''.join(s)

def star(cx, cy, r):
    import math
    pts = []
    for k in range(10):
        a = math.radians(-90 + k * 36); rr = r if k % 2 == 0 else r * .4
        pts.append(f'{cx + rr*math.cos(a):.1f},{cy + rr*math.sin(a):.1f}')
    return f'<polygon points="{" ".join(pts)}"/>'

EAGLE = 'M100,92 L70,50 L50,20 L40,-4 L28,-2 L34,6 L18,6 L26,14 L8,16 L20,24 L0,30 L16,36 L4,46 L20,50 L22,62 L30,72 L38,80 L48,92 L58,98 L66,110 L76,114 L84,122 L86,140 L80,152 L70,164 L62,176 L74,174 L70,184 L80,186 L88,176 L100,166 L116,176 L140,192 L166,210 L176,222 L178,212 L192,220 L188,208 L204,212 L196,202 L210,200 L198,192 L206,186 L180,172 L150,150 L118,128 L122,124 L130,118 L140,114 L150,114 L156,110 L146,104 L136,100 L124,98 L112,96 Z'

def art():
    """Flag (lower-left) flowing into a ribbon road that sweeps up and right then down off the bottom; eagle above."""
    flag_top = 'M118,1000 C210,975 300,962 420,972'
    s = ['<g fill="url(#gold)" filter="url(#foilgrain)">']
    # ribbon / road (drawn first, flag overlaps its start)
    s.append('<path d="M360,1010 C520,1005 585,965 598,895 C612,815 640,760 715,748 L812,742" fill="none" stroke="url(#gold)" stroke-width="118"/>'
             '<path d="M752,760 C790,860 760,1060 650,1262" fill="none" stroke="url(#gold)" stroke-width="118"/>')
    # flag body with wavy top and curved right edge flowing off the bottom
    s.append('<path d="M115,925 C220,900 300,880 380,872 C420,900 440,960 460,1020 C490,1100 530,1170 570,1250 L115,1250 Z"/>')
    s.append('</g>')
    # navy cut-out stars on the flag
    s.append(f'<g fill="{NAVY2}">' + ''.join(star(x, y, 19) for x, y in
             [(150, 960), (232, 942), (314, 925), (128, 1040), (205, 1022), (285, 1005), (365, 990), (165, 1110), (245, 1094), (330, 1080), (412, 1070), (130, 1185), (210, 1170), (292, 1158), (375, 1148), (455, 1150), (180, 1240), (262, 1232)]) + '</g>')
    # slit in the descending ribbon (as in the classic)
    s.append(f'<path d="M806,930 C804,968 798,1000 788,1036 L779,1033 C788,998 794,966 796,930 Z" fill="{NAVY2}"/>')
    # eagle: wings raised, gliding right/down, over the ribbon
    s.append(f'<g fill="url(#gold)" filter="url(#foilgrain)" transform="translate(130,500) scale(1.85)"><path d="{EAGLE}" stroke="{NAVY2}" stroke-width="2.6" paint-order="stroke"/></g>')
    s.append(f'<circle cx="{130+141*1.85:.1f}" cy="{500+106*1.85:.1f}" r="2.4" fill="{NAVY2}"/>')
    return ''.join(s)

def title():
    return (f'<g fill="url(#gold)" filter="url(#foilgrain)">'
            f'<rect x="140" y="98" width="664" height="4.5"/>'
            f'<text x="138" y="250" font-family="Inter, Arimo, sans-serif" font-weight="800" font-size="168" letter-spacing="-6" textLength="664" lengthAdjust="spacingAndGlyphs">Passport</text>'
            f'<rect x="140" y="282" width="664" height="4.5"/>'
            f'<text x="140" y="352" font-family="Inter, Arimo, sans-serif" font-weight="800" font-size="56" letter-spacing="-3.2">To Your National Parks</text></g>')

def cover_svg(name=None):
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">', defs(), vinyl('left'), title(), art()]
    if name: s.append(f'<text x="840" y="1222" text-anchor="end" font-family="{COND}" font-size="16" letter-spacing="3" fill="#cfb35e" opacity=".55">{name}</text>')
    return ''.join(s) + '</svg>'

def back_svg(regions, esc):
    tot = sum(len(r['units']) for r in regions.values()); vis = sum(1 for r in regions.values() for u in r['units'] if u['visits'])
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">', defs(7), vinyl('right'),
         '<g fill="url(#gold)" filter="url(#foilgrain)">',
         f'<rect x="96" y="420" width="664" height="3"/>',
         f'<text x="428" y="560" text-anchor="middle" font-family="{FONT}" font-weight="700" font-size="104" letter-spacing="-3">{vis} / {tot}</text>',
         f'<text x="428" y="612" text-anchor="middle" font-family="{COND}" font-weight="700" font-size="30">Park Sites Visited</text>',
         f'<rect x="96" y="648" width="664" height="3"/>']
    for i, r in enumerate(regions.values()):
        v = sum(1 for u in r['units'] if u['visits']); y = 720 + i * 46
        s.append(f'<text x="200" y="{y}" font-family="{COND}" font-weight="700" font-size="24">{esc(r["name"])}</text>'
                 f'<text x="656" y="{y}" text-anchor="end" font-family="{COND}" font-weight="700" font-size="24">{v} / {len(r["units"])}</text>')
    s.append('</g>')
    for i, r in enumerate(regions.values()):
        y = 720 + i * 46
        s.append(f'<rect x="160" y="{y-19}" width="24" height="20" rx="3" fill="{r["color"]}" stroke="#e6c766" stroke-width="1.2"/>')
    return ''.join(s) + '</svg>'
