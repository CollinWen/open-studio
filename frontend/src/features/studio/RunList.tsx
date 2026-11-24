/**
 * RunList: the studio's "runs": every token issued, since each is a run (one
 * session). A Ledger of them, newest first: the
 * task kind (open, or a task) with the owner's note under it (and, once it's done, the agent's
 * summary), then links to its lines in the agent log and to each entry it
 * added; the agent, the board, its state and how long ago, and a link to
 * the harness's own session (a claude.ai/code page, say) when the agent left
 * one, to watch how it worked. The agent sets that link, so the site it goes
 * to is written beside it. A run that ran out without finishing is faded.
 *
 * Used by StudioPage, which loads the runs and the entries (for the titles
 * of what each run added), and narrows them to one agent on ?agent=. Tokens
 * are issued from the agents list (AgentManager); before, from an agent's
 * kit (backend/app/features/runs/), not here. What agents write while they
 * work is public at /agents; the session link is shown only here.
 */

import { Link } from "react-router-dom";
import { LabelRow } from "../../components/LabelRow";
import { Ledger } from "../../components/Ledger";
import { LedgerRow } from "../../components/LedgerRow";
import { ALL_BOARDS } from "../../types/run";
import type { Entry } from "../../types/entry";
import type { Run } from "../../types/run";
import { boardPath } from "../grid/boardPath";
import { describeRunState } from "./describeRunState";
import { linkSite } from "./linkSite";

const COLUMNS = [
  { label: "run", span: 4 },
  { label: "agent", span: 2 },
  { label: "boards", span: 2 },
  { label: "state", span: 2 },
  { label: "session", span: 2 },
];

interface Props {
  runs: Run[];
  entries: Entry[];
  /** Set when the list is narrowed to one agent's runs. */
  agent?: string;
}

export function RunList({ runs, entries, agent }: Props) {
  const titles = new Map(entries.map((entry) => [entry.id, entry.title]));
  const narrowed = agent && (
    <LabelRow>
      <p className="word-list quiet">
        <span>{agent}'s runs</span>
        <Link to="/studio/runs">all runs</Link>
      </p>
    </LabelRow>
  );
  if (runs.length === 0) {
    return (
      <>
        {narrowed}
        <LabelRow>
          <p className="quiet">No runs yet. Issue an agent a token (under agents) to start one.</p>
        </LabelRow>
      </>
    );
  }
  return (
    <>
      {narrowed}
      <LabelRow wide>
        <Ledger columns={COLUMNS}>
          {runs.map((run) => (
            <LedgerRow
              key={run.id}
              className={run.state === "expired" ? "is-faded" : undefined}
              cells={[
                <>
                  {run.kind}
                  {run.brief && <span className="quiet ledger-note">{run.brief}</span>}
                  {run.summary && <span className="ledger-note">{run.summary}</span>}
                  <span className="ledger-note">
                    <span className="word-list">
                      <Link to={`/agents?run=${run.id}`}>its log</Link>
                      {run.added.map((id) => (
                        <Link key={id} to={`/entry/${id}`}>
                          {titles.get(id) ?? id}
                        </Link>
                      ))}
                    </span>
                  </span>
                </>,
                run.agent,
                run.boards[0] === ALL_BOARDS ? (
                  <span className="quiet">all its boards</span>
                ) : (
                  <span className="word-list">
                    {run.boards.map((slug) => (
                      <Link key={slug} to={boardPath(slug)}>
                        {slug}
                      </Link>
                    ))}
                  </span>
                ),
                <span className="quiet">{describeRunState(run)}</span>,
                run.session_url ? (
                  <>
                    <a href={run.session_url} target="_blank" rel="noreferrer">
                      watch
                    </a>
                    <span className="quiet ledger-note">{linkSite(run.session_url)}</span>
                  </>
                ) : (
                  <span className="quiet">none left</span>
                ),
              ]}
            />
          ))}
        </Ledger>
      </LabelRow>
    </>
  );
}
