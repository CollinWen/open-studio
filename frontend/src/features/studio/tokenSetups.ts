/**
 * tokenSetups: the ways to hand a newly issued token to a harness, as text
 * to copy. First, per harness (Pi, Claude Code), the backend's two lines that
 * set up a sandbox for the run and start it: they fetch the run's skills,
 * studio connection and prompt with the token. Then the ways any harness can
 * use: environment variables (e.g. secrets on a Fly instance whose image runs
 * the sandbox script), an MCP client's config, plain HTTP, and the prompt.
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
        `OPEN_STUDIO_TOKEN=${kit.token}`,
        `OPEN_STUDIO_SANDBOX_URL=${kit.sandbox_url}?harness=pi`,
        `OPEN_STUDIO_MCP_URL=${kit.mcp_url}`,
        `OPEN_STUDIO_API_URL=${kit.api_url}`,
      ].join("\n"),
    },
    { label: "mcp", text: JSON.stringify(mcpConfig, null, 2) },
    { label: "http", text: `curl -H "${header}" ${kit.api_url}/api/runs/${kit.run.id}` },
    { label: "prompt", text: kit.prompt },
  ];
}
