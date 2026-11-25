/**
 * TokenNotice: a token just issued, shown this once. It says which run it
 * is, what it reaches and when it stops working, shows the token with
 * "copy", then the ways to hand it to a harness, one at a time, each with
 * "copy": first the lines that set up a sandbox for Pi or Claude Code, then
 * environment, mcp, http and the prompt. Closing the window forgets the
 * token for good.
 *
 * Used by AgentManager, in a PaperWindow, after TokenForm. The setups'
 * text is built in tokenSetups.ts.
 */

import { useState } from "react";
import { CopyButton } from "../../components/CopyButton";
import { WordChoice } from "../../components/WordChoice";
import { ALL_BOARDS, type RunKit } from "../../types/run";
import { parseServerTime } from "../agents/formatTimeAgo";
import { buildTokenSetups } from "./tokenSetups";

interface Props {
  kit: RunKit;
  onDone: () => void;
}

export function TokenNotice({ kit, onDone }: Props) {
  const setups = buildTokenSetups(kit);
  const [shown, setShown] = useState(setups[0].label);
  const setup = setups.find((one) => one.label === shown) ?? setups[0];
  const { run } = kit;
  const boards = run.boards[0] === ALL_BOARDS ? "all its boards" : run.boards.join(", ");

  return (
    <div className="studio-form token-notice">
      <p>
        {run.agent}'s token for run {run.id} ({run.kind}, on {boards}), until{" "}
        {parseServerTime(run.expires_at).toLocaleString()}. It is shown only now: copy it before you close this.
      </p>
      <pre>{kit.token}</pre>
      <p className="word-list">
        <CopyButton text={kit.token} label="copy token" />
      </p>
      <p className="word-list" role="group" aria-label="how to hand it to a harness">
        {setups.map((one) => (
          <WordChoice
            key={one.label}
            label={one.label}
            active={one.label === shown}
            onPick={() => setShown(one.label)}
          />
        ))}
      </p>
      <pre>{setup.text}</pre>
      <p className="word-list studio-form-actions">
        <CopyButton text={setup.text} label="copy" />
        <button type="button" className="square is-primary" onClick={onDone}>
          done
        </button>
      </p>
    </div>
  );
}
