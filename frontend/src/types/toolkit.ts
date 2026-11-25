/**
 * Toolkit data shapes, matching backend/app/features/toolkits/schemas.py:
 * what the owner grants an agent for one toolkit (an outside service whose
 * tools the studio runs through Composio for it), and one tool of a
 * toolkit's catalog, for picking. Names are Composio's own: toolkit
 * "github", tool "GITHUB_CREATE_AN_ISSUE", connected account "ca_...".
 */

export interface ToolkitGrant {
  /** The toolkit's tools it may call. */
  tools: string[];
  /** The Composio connected account it acts as; "" for the studio user's own. */
  connected_account: string;
  /** Arguments it may not choose freely, each with its allowed values ("proto-*": any starting with proto-). */
  pins: Record<string, string[]>;
}

/** One tool of a toolkit on Composio. */
export interface CatalogTool {
  tool: string;
  name: string;
  description: string;
  /** Composio's hints, e.g. "readOnlyHint", "destructiveHint". */
  tags: string[];
}

/** A toolkit's name, as Composio writes it: lowercase letters, digits and underscores. */
export const TOOLKIT_NAME = /^[a-z0-9][a-z0-9_]{0,59}$/;
