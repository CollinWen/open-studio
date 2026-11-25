#!/bin/sh
# Starts one run in this sandbox: fetches the run's setup script from the
# studio with the run token and runs it, which writes the run's skills,
# studio connection and prompt into ./open-studio-run-<id>/ and starts the
# harness there. Both values are in the run's kit ("environment"):
#   OPEN_STUDIO_TOKEN         the run token
#   OPEN_STUDIO_SANDBOX_URL   .../api/runs/<id>/sandbox.sh?harness=pi
# The harness's own model key must be set too (e.g. OPENROUTER_API_KEY).
set -eu
: "${OPEN_STUDIO_TOKEN:?set OPEN_STUDIO_TOKEN: the run token, from its kit}"
: "${OPEN_STUDIO_SANDBOX_URL:?set OPEN_STUDIO_SANDBOX_URL: the sandbox address, from its kit}"

setup=$(mktemp)
# Without --fail, a refusal comes back as a script too, which says why and stops.
curl -sS -H "Authorization: Bearer $OPEN_STUDIO_TOKEN" "$OPEN_STUDIO_SANDBOX_URL" -o "$setup"
exec sh "$setup"
