/**
 * RunList: the studio's "runs". A Ledger of every run, newest first: the
 * task kind with the owner's note under it (and, once it's done, the agent's
 * summary), the agent, the board, its state and how long ago, and a link to
 * the harness's own session (a claude.ai/code page, say) when the agent left
 * one, to watch how it worked. A run that ran out without finishing is faded.
 *
 * Used by StudioPage, which loads the runs. Runs are started from an agent's
 * kit (backend/app/features/runs/), not here. What agents write while they
 * work is public at /agents; the session link is shown only here.
 */

import { Link } from "react-router-dom";
import { LabelRow } from "../../components/LabelRow";
import { Ledger } from "../../components/Ledger";
import { LedgerRow } from "../../components/LedgerRow";
import type { Run } from "../../types/run";
import { formatTimeAgo } from "../agents/formatTimeAgo";
import { boardPath } from "../grid/boardPath";

const COLUMNS = [
  { label: "run", span: 4 },
  { label: "agent", span: 2 },
  { label: "board", span: 2 },
  { label: "state", span: 2 },
  { label: "session", span: 2 },
];

export function RunList({ runs }: { runs: Run[] }) {
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
              </>,
              run.agent,
              <Link to={boardPath(run.board)}>{run.board}</Link>,
              <span className="quiet">{describeState(run)}</span>,
              run.session_url ? (
                <a href={run.session_url} target="_blank" rel="noreferrer">
                  watch
                </a>
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

function describeState(run: Run): string {
  if (run.state === "finished" && run.finished_at) return `finished ${formatTimeAgo(run.finished_at)}`;
  if (run.state === "expired") return `ran out ${formatTimeAgo(run.expires_at)}`;
  return `running, started ${formatTimeAgo(run.created_at)}`;
}
