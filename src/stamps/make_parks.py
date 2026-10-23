#!/usr/bin/env python3
"""Build parks.json from the NPS API (developer.nps.gov). Keeps any existing visits."""
import json, os, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__))
REGIONS = {  # official NPS Passport regions (key: name, color, states)
 'north_atlantic': ('North Atlantic', '#c8102e', 'CT ME MA NH NJ NY RI VT'),
 'mid_atlantic': ('Mid-Atlantic', '#e87722', 'DE MD PA VA WV'),
 'national_capital': ('National Capital', '#7a2582', 'DC'),
 'southeast': ('Southeast', '#00843d', 'AL FL GA KY MS NC SC TN PR VI'),
 'midwest': ('Midwest', '#0072ce', 'AR IL IN IA KS MI MN MO NE ND OH SD WI'),
 'southwest': ('Southwest', '#b5651d', 'LA NM OK TX'),
 'rocky_mountain': ('Rocky Mountain', '#d4a017', 'CO MT UT WY'),
 'western': ('Western', '#2a9d8f', 'AZ CA HI NV GU AS MP'),
 'pacific_northwest_alaska': ('Pacific Northwest & Alaska', '#1b4d89', 'AK ID OR WA'),
}
OVERRIDE = {'YELL': ('rocky_mountain', 'WY')}  # multi-state units whose official region differs
def region_for(states):
    for st in states:
        for k, (_, _, ss) in REGIONS.items():
            if st in ss.split(): return k
    return 'national_capital'
if __name__ == '__main__':
    key = os.environ.get('NPS_API_KEY', 'DEMO_KEY')
    d = json.load(urllib.request.urlopen(f'https://developer.nps.gov/api/v1/parks?limit=1000&api_key={key}'))
    path = os.path.join(HERE, 'parks.json')
    old = {}
    if os.path.exists(path):
        for r in json.load(open(path))['regions'].values():
            for u in r['units']: old[u['code']] = u['visits']
    out = {k: {'name': n, 'color': c, 'units': []} for k, (n, c, _) in REGIONS.items()}
    for p in sorted(d['data'], key=lambda p: p['fullName']):
        sts = [s for s in p['states'].split(',') if s]
        code = p['parkCode'].upper(); rk, sst = OVERRIDE.get(code, (region_for(sts), None))
        if not sst: sst = next((s for s in sts if s in REGIONS[rk][2].split()), sts[0] if sts else '')
        out[rk]['units'].append({'code': code, 'name': p['fullName'],
            'state': ','.join(sts), 'stamp_state': sst, 'designation': p['designation'] or 'Affiliated Area',
            'visits': old.get(p['parkCode'].upper(), [])})
    json.dump({'source': 'NPS API developer.nps.gov/api/v1/parks', 'regions': out}, open(path, 'w'), indent=1, ensure_ascii=False)
    print('units:', sum(len(r['units']) for r in out.values()), {k: len(r['units']) for k, r in out.items()})
