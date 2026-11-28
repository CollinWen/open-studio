/**
 * Add-on data shapes, matching backend/app/features/addons/schemas.py: one
 * thing an agent can use beyond the studio, defined once for every agent
 * (one of the sandbox's own tools, or an outside service's tools run on
 * Composio), with the guide that explains it in AGENTS.md; and one tool of
 * a Composio toolkit, to look through.
 */

export type AddonKind = "sandbox" | "composio";

export interface Addon {
  /** How agents and runs name it: lowercase letters, digits and dashes. */
  name: string;
  /** "sandbox": a tool of the sandbox itself; "composio": an outside service's tools, run on Composio. */
  kind: AddonKind;
  /** web, code or github for a sandbox add-on; Composio's toolkit name ("gmail") otherwise. */
  service: string;
  /** The Composio connected account it acts as ("ca_…"); "" until it's connected, and always for the sandbox's own. */
  account: string;
  /** Markdown: what it is, what it's for, how it works, what to watch. Goes into the AGENTS.md of every run that has it. */
  guide: string;
  created_at: string;
  /** web, code and github: always there, can't be removed. */
  built_in: boolean;
}

/** The sandbox's own tools a sandbox add-on can stand for. */
export const SANDBOX_SERVICES = ["web", "code", "github"] as const;

/** An add-on's name, as the backend takes it. */
export const ADDON_NAME = /^[a-z0-9][a-z0-9-]{0,39}$/;

/** A Composio toolkit's name, as Composio writes it: "gmail", "googledrive", "exa". */
export const TOOLKIT_NAME = /^[a-z0-9][a-z0-9_]{0,59}$/;

/** One tool of a Composio toolkit. */
export interface CatalogTool {
  /** Composio's name for it, e.g. "GMAIL_CREATE_EMAIL_DRAFT". */
  tool: string;
  name: string;
  description: string;
  /** Composio's hints, e.g. "readOnlyHint", "destructiveHint". */
  tags: string[];
}
