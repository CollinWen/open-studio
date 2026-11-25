/**
 * ToolkitGrantForm: the lines of the agent window for one toolkit grant:
 * the toolkit's name (only when adding), its tools picked as ovals from the
 * toolkit's catalog on Composio (searchable; pointing at one says what it
 * does and whether it only reads), the connected account the agent acts as,
 * and the pinned arguments as one line ("repo=open-studio, proto-*"). When
 * the catalog can't be read (Composio not set up), tools are typed instead,
 * comma separated. "keep" hands the grant back; nothing is saved until the
 * agent is.
 *
 * Used by ToolkitGrantsEditor, inside AgentForm.
 */

import { useEffect, useState } from "react";
import { fetchToolkitCatalog } from "../../api/toolkitsApi";
import { LoadingWord } from "../../components/LoadingWord";
import { SearchField } from "../../components/SearchField";
import { WordChoice } from "../../components/WordChoice";
import { TOOLKIT_NAME, type CatalogTool, type ToolkitGrant } from "../../types/toolkit";
import { formatPins, parsePins } from "./toolkitPins";

interface Props {
  /** The toolkit being changed, or "" to add one. */
  toolkit: string;
  grant: ToolkitGrant | null;
  onKeep: (toolkit: string, grant: ToolkitGrant) => void;
  onCancel: () => void;
}

const READ_ONLY = "readOnlyHint";
const DESTRUCTIVE = "destructiveHint";

export function ToolkitGrantForm({ toolkit, grant, onKeep, onCancel }: Props) {
  const [name, setName] = useState(toolkit);
  const [tools, setTools] = useState<string[]>(grant?.tools ?? []);
  const [account, setAccount] = useState(grant?.connected_account ?? "");
  const [pinsText, setPinsText] = useState(formatPins(grant?.pins ?? {}));
  const [words, setWords] = useState("");
  const [catalog, setCatalog] = useState<CatalogTool[] | null>(null);
  const [problem, setProblem] = useState("");
  const validName = TOOLKIT_NAME.test(name);

  useEffect(() => {
    if (!validName) return;
    setCatalog(null);
    fetchToolkitCatalog(name, words)
      .then((found) => (setCatalog(found), setProblem("")))
      .catch((error) => setProblem(error instanceof Error ? error.message : String(error)));
  }, [name, words, validName]);

  const toggle = (tool: string) => setTools(tools.includes(tool) ? tools.filter((one) => one !== tool) : [...tools, tool]);
  const offered = catalog?.filter((item) => !tools.includes(item.tool)) ?? [];
  const hint = (item: CatalogTool) =>
    `${item.description}${item.tags.includes(READ_ONLY) ? " Only reads." : item.tags.includes(DESTRUCTIVE) ? " Can change or delete things." : ""}`;

  return (
    <div className="toolkit-grant" role="group" aria-label={`toolkit ${name || "to add"}`}>
      {toolkit && (
        <p className="word-list">
          <span>{toolkit}</span>
          <span className="quiet">its tools, the account it acts as, its pinned arguments</span>
        </p>
      )}
      {!toolkit && (
        <input
          placeholder="toolkit, as Composio names it (e.g. github, exa)"
          value={name}
          onChange={(e) => setName(e.target.value.trim().toLowerCase())}
        />
      )}
      <p className="word-list is-ovals" role="group" aria-label="its tools">
        <span className="quiet">tools</span>
        {tools.map((tool) => (
          <WordChoice key={tool} label={tool} look="oval" active onPick={() => toggle(tool)} />
        ))}
        {tools.length === 0 && <span className="quiet">none yet</span>}
      </p>
      {validName && !problem && (
        <>
          <SearchField value={words} onSearch={setWords} placeholder={`find ${name} tools`} />
          <p className="word-list is-ovals" role="group" aria-label="tools to add">
            {!catalog && <LoadingWord>reading</LoadingWord>}
            {offered.map((item) => (
              <WordChoice key={item.tool} label={item.tool} look="oval" hint={hint(item)} active={false} onPick={() => toggle(item.tool)} />
            ))}
          </p>
        </>
      )}
      {problem && (
        <>
          <p className="quiet">{problem}</p>
          <input
            placeholder={`tools, comma separated (e.g. ${name.toUpperCase() || "GITHUB"}_GET_A_REPOSITORY)`}
            value={tools.join(", ")}
            onChange={(e) => setTools(e.target.value.split(",").map((tool) => tool.trim().toUpperCase()).filter(Boolean))}
          />
        </>
      )}
      <label className="word-list toolkit-grant-field">
        <span className="quiet">acts as</span>
        <input
          placeholder="a connected account (ca_…), or empty for the studio's own"
          value={account}
          onChange={(e) => setAccount(e.target.value.trim())}
        />
      </label>
      <label className="word-list toolkit-grant-field">
        <span className="quiet">pinned</span>
        <input
          placeholder="e.g. owner=CollinWen; repo=open-studio, proto-*"
          value={pinsText}
          onChange={(e) => setPinsText(e.target.value)}
        />
      </label>
      <p className="word-list">
        <button
          type="button"
          className="square is-primary"
          disabled={!validName || tools.length === 0}
          onClick={() => onKeep(name, { tools, connected_account: account, pins: parsePins(pinsText) })}
        >
          keep
        </button>
        <button type="button" className="square quiet" onClick={onCancel}>
          cancel
        </button>
      </p>
    </div>
  );
}
