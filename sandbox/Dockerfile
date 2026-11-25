# The harness image: what every agent sandbox has before any run starts.
# Pi, git and a few tools; nothing about a particular run, and no keys. At
# start, start-run.sh fetches the run's setup from the studio with the run
# token (skills, studio connection, prompt) and runs it.
#
# The model key (e.g. OPENROUTER_API_KEY) and Pi's model choice belong to
# whoever runs this container, never to the studio: pass them at run time
# (docker run -e, or Fly secrets on the app that runs it). See README.md.
FROM node:24-bookworm-slim

RUN apt-get update \
  && apt-get install -y --no-install-recommends bash ca-certificates curl git ripgrep python3 \
  && rm -rf /var/lib/apt/lists/*
# Pinned: the sandbox setup relies on Pi's MCP support and Agent Skills (1.6 or later).
RUN npm install -g --ignore-scripts @earendil-works/pi-coding-agent@1.6.1

COPY start-run.sh /usr/local/bin/start-run
RUN chmod +x /usr/local/bin/start-run

WORKDIR /work
ENTRYPOINT ["start-run"]
