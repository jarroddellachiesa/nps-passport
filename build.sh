#!/usr/bin/env bash
# Regenerate region pages from parks.json, rebuild the site, back up the source into the repo, and redeploy.
# Usage: /workspace/nps-site/build.sh                 render all pages + back cover, build, deploy
#        /workspace/nps-site/build.sh --page=KEY      render only that region key (e.g. rocky_mountain) (others untouched)
#        /workspace/nps-site/build.sh --no-render     reuse existing PNGs
#        add --no-deploy to any of the above to build without pushing
# Restore after a box reset:  git clone https://github.com/jarroddellachiesa/nps-passport /workspace/nps-site
#                             && cp -r /workspace/nps-site/src/stamps /workspace/nps-stamps
set -euo pipefail
SITE="$(cd "$(dirname "$0")" && pwd)"; STAMPS="${STAMPS_DIR:-/workspace/nps-stamps}"
RENDER=(--pages --back); DEPLOY=1
for a in "$@"; do case "$a" in
  --page=*) RENDER=("$a");; --no-render) RENDER=();; --no-deploy) DEPLOY=0;;
  *) echo "unknown option $a"; exit 2;; esac; done
[[ ${#RENDER[@]} -gt 0 ]] && (cd "$STAMPS" && python3 passport.py "${RENDER[@]}")
python3 "$SITE/gen.py"
mkdir -p "$SITE/src/stamps"
cp "$STAMPS"/{passport.py,emblems.py,cover2.py,eagleflag.py,make_parks.py,add_visit.py,parks.json,us-states.json} "$STAMPS"/passport_*.png "$SITE/src/stamps/"
[[ $DEPLOY == 1 ]] || { echo "built (not deployed): $SITE/index.html"; exit 0; }
cd "$SITE"; touch .nojekyll
git add -A
git commit -qm "Update passport $(date '+%Y-%m-%d %H:%M')" || echo "no changes to commit"
git push -q origin main
echo "deployed: https://jarroddellachiesa.github.io/nps-passport/ (live in ~1 min)"
