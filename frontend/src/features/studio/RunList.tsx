/**
 * RunList: the studio's "runs". A Ledger of every run, newest first: the
 * task kind with the owner's note under it (and, once it's done, the agent's
 * summary), then links to its lines in the agent log and to each entry it
 * added; the agent, the board, its state and how long ago, and a link to
 * the harness's own session (a claude.ai/code page, say) when the agent left
 * one, to watch how it worked. The agent sets that link, so the site it goes
 * to is written beside it. A run that ran out without finishing is faded.
 *
 * Used by StudioPage, which loads the runs and the entries (for the titles
 * of what each run added). Runs are started from an agent's
 * kit (backend/app/features/runs/), not here. What agents write while they
 * work is public at /agents; the session link is shown only here.
 */

import { Link } from "react-router-dom";
import { LabelRow } from "../../components/LabelRow";
import { Ledger } from "../../components/Ledger";
import { LedgerRow } from "../../components/LedgerRow";
import type { Entry } from "../../types/entry";
import type { Run } from "../../types/run";
import { boardPath } from "../grid/boardPath";
import { describeRunState } from "./describeRunState";
import { linkSite } from "./linkSite";

const COLUMNS = [
  { label: "run", span: 4 },
  { label: "agent", span: 2 },
  { label: "board", span: 2 },
  { label: "state", span: 2 },
  { label: "session", span: 2 },
];

export function RunList({ runs, entries }: { runs: Run[]; entries: Entry[] }) {
  const titles = new Map(entries.map((entry) => [entry.id, entry.title]));
  if (runs.length === 0) {
    return (
      <LabelRow>
        <p className="quiet">No runs yet. An agent's runs show here once its kit is used.</p>
      </LabelRow>
    );
  }
  return (
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
              <Link to={boardPath(run.board)}>{run.board}</Link>,
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
  );
}
