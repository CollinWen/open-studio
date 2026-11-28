/**
 * AddonToolList: what a Composio add-on can do: its toolkit's tools on
 * Composio, searchable, each with what it does and Composio's own hint of
 * whether it only reads or can change and delete things. Agents with the
 * add-on can call any of them that Composio allows: to keep one from an
 * agent, or have it ask you first, set that on Composio, which checks
 * every call.
 *
 * Used by AddonManager, under the add-on's guide.
 */

import { useEffect, useState } from "react";
import { fetchAddonCatalog } from "../../api/addonsApi";
import { Ledger } from "../../components/Ledger";
import { LedgerRow } from "../../components/LedgerRow";
import { LoadingWord } from "../../components/LoadingWord";
import { SearchField } from "../../components/SearchField";
import type { Addon, CatalogTool } from "../../types/addon";

interface Props {
  addon: Addon;
}

const COLUMNS = [
  { label: "tool", span: 5 },
  { label: "what it does", span: 7 },
];

export function AddonToolList({ addon }: Props) {
  const [words, setWords] = useState("");
  const [tools, setTools] = useState<CatalogTool[] | null>(null);
  const [problem, setProblem] = useState("");

  useEffect(() => {
    setTools(null);
    fetchAddonCatalog(addon.name, words)
      .then((found) => (setTools(found), setProblem("")))
      .catch((error) => setProblem(error instanceof Error ? error.message : String(error)));
  }, [addon.name, words]);

  return (
    <div className="addon-tools">
      <p className="word-list">
        <span className="quiet">its tools on Composio</span>
        <SearchField value={words} onSearch={setWords} placeholder={`find ${addon.service} tools`} />
      </p>
      {problem && <p className="quiet">{problem}</p>}
      {!tools && !problem && <LoadingWord>reading</LoadingWord>}
      {tools && (
        <Ledger columns={COLUMNS}>
          {tools.map((tool) => (
            <LedgerRow
              key={tool.tool}
              cells={[
                tool.tool,
                <span className="quiet">
                  {tool.description}
                  {describeHints(tool.tags) && <span className="ledger-note">{describeHints(tool.tags)}</span>}
                </span>,
              ]}
            />
          ))}
        </Ledger>
      )}
    </div>
  );
}

/** Composio's hints, in words. */
function describeHints(tags: string[]): string {
  if (tags.includes("destructiveHint")) return "can change or delete things";
  if (tags.includes("readOnlyHint")) return "only reads";
  if (tags.includes("createHint") || tags.includes("updateHint")) return "adds or changes things";
  return "";
}
