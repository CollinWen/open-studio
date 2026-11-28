#!/bin/sh
# Starts one run in this sandbox from its token alone: fetches the run's
# setup script from the studio with the token and runs it, which writes the
# run's AGENTS.md, skills, studio connection and prompt into
# ./open-studio-run-<id>/ and starts the harness there.
#   OPEN_STUDIO_TOKEN   the run token, from its kit: the one thing each run needs
#   OPEN_STUDIO_URL     the studio's API address (https://api.yourdomain.com):
#                       set once for every run, e.g. on the sandbox app
#   OPEN_STUDIO_HARNESS optional: pi (the default) or claude_code
# The harness's own model key must be set too (e.g. OPENROUTER_API_KEY).
set -eu
: "${OPEN_STUDIO_TOKEN:?set OPEN_STUDIO_TOKEN: the run token, from its kit}"
: "${OPEN_STUDIO_URL:?set OPEN_STUDIO_URL: the studio API address, e.g. https://api.yourdomain.com}"

setup=$(mktemp)
# Without --fail, a refusal comes back as a script too, which says why and stops.
curl -sS -H "Authorization: Bearer $OPEN_STUDIO_TOKEN" \
  "${OPEN_STUDIO_URL%/}/api/runs/current/sandbox.sh?harness=${OPEN_STUDIO_HARNESS:-pi}" -o "$setup"
exec sh "$setup"
