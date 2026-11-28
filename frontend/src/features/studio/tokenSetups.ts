/**
 * tokenSetups: the ways to hand a newly issued token to a harness, as text
 * to copy. First, per harness (Pi, Claude Code), the backend's one line
 * that sets up a sandbox for the run in an empty folder and starts it: it
 * fetches the run's AGENTS.md, skills, studio connection and prompt with
 * the token. Then the ways any harness can use: the two environment
 * variables the sandbox image needs (sandbox/start-run.sh, e.g. on a Fly
 * machine), an MCP client's config, plain HTTP, and the prompt.
 *
 * Used by TokenNotice.
 */

import type { RunKit } from "../../types/run";

export interface TokenSetup {
  label: string;
  text: string;
}

const MCP_SERVER_NAME = "open-studio";
const HARNESS_NAMES: Record<string, string> = { pi: "pi", claude_code: "claude code" };

export function buildTokenSetups(kit: RunKit): TokenSetup[] {
  const header = `Authorization: Bearer ${kit.token}`;
  const mcpConfig = {
    mcpServers: {
      [MCP_SERVER_NAME]: { type: "http", url: kit.mcp_url, headers: { Authorization: `Bearer ${kit.token}` } },
    },
  };
  return [
    ...Object.entries(kit.setups).map(([name, setup]) => ({ label: HARNESS_NAMES[name] ?? name, text: setup.command })),
    {
      label: "environment",
      text: [
        `OPEN_STUDIO_URL=${kit.api_url}`,
        `OPEN_STUDIO_TOKEN=${kit.token}`,
      ].join("\n"),
    },
    { label: "mcp", text: JSON.stringify(mcpConfig, null, 2) },
    { label: "http", text: `curl -H "${header}" ${kit.api_url}/api/runs/${kit.run.id}` },
    { label: "prompt", text: kit.prompt },
  ];
}
