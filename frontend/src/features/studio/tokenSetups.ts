/**
 * tokenSetups: the ways to hand a newly issued token to a harness, as text
 * to copy. All but the last work with any harness: environment variables
 * (e.g. secrets on a Fly instance running Pi), an MCP client's config, plain
 * HTTP, and the run's prompt for the model. Ready-made setups the backend
 * adds for particular harnesses (today a `claude` command) come after.
 *
 * Used by TokenNotice.
 */

import type { RunKit } from "../../types/run";

export interface TokenSetup {
  label: string;
  text: string;
}

const MCP_SERVER_NAME = "open-studio";
const HARNESS_NAMES: Record<string, string> = { claude_code: "claude code" };

export function buildTokenSetups(kit: RunKit): TokenSetup[] {
  const header = `Authorization: Bearer ${kit.token}`;
  const mcpConfig = {
    mcpServers: {
      [MCP_SERVER_NAME]: { type: "http", url: kit.mcp_url, headers: { Authorization: `Bearer ${kit.token}` } },
    },
  };
  return [
    {
      label: "environment",
      text: [
        `OPEN_STUDIO_TOKEN=${kit.token}`,
        `OPEN_STUDIO_MCP_URL=${kit.mcp_url}`,
        `OPEN_STUDIO_API_URL=${kit.api_url}`,
      ].join("\n"),
    },
    { label: "mcp", text: JSON.stringify(mcpConfig, null, 2) },
    { label: "http", text: `curl -H "${header}" ${kit.api_url}/api/runs/${kit.run.id}` },
    { label: "prompt", text: kit.prompt },
    ...Object.entries(kit.setups).map(([name, setup]) => ({ label: HARNESS_NAMES[name] ?? name, text: setup.command })),
  ];
}
