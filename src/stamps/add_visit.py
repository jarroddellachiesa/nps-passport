#!/usr/bin/env python3
"""Add a cancellation.  add_visit.py CODE YYYY-MM-DD "Location" [--state ST] [--notes "..."] [--no-deploy]
Then rebuilds that region's page(s) and deploys via build.sh."""
import argparse, json, os, subprocess, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser(); ap.add_argument('code'); ap.add_argument('date'); ap.add_argument('location')
ap.add_argument('--state'); ap.add_argument('--notes', default=''); ap.add_argument('--no-deploy', action='store_true')
ap.add_argument('--no-build', action='store_true'); a = ap.parse_args()
datetime.date.fromisoformat(a.date)
p = os.path.join(HERE, 'parks.json'); d = json.load(open(p))
for rk, r in d['regions'].items():
    for u in r['units']:
        if u['code'] == a.code.upper():
            v = {'date': a.date, 'location': a.location, 'notes': a.notes}
            if a.state: v['state'] = a.state.upper()
            u['visits'].append(v); json.dump(d, open(p, 'w'), indent=1, ensure_ascii=False)
            print(f"added {u['name']} {a.date} {a.location} -> region {rk}")
            if not a.no_build:
                subprocess.run([os.environ.get('NPS_SITE', '/workspace/nps-site') + '/build.sh', f'--page={rk}'] + (['--no-deploy'] if a.no_deploy else []), check=True)
            raise SystemExit
raise SystemExit(f'unknown unit code {a.code}; search parks.json')
