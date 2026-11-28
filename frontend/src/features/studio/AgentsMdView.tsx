/**
 * AgentsMdView: one agent's AGENTS.md, as its next run will get it, from
 * its settings as saved: what it's for, each add-on with its guide and the
 * owner's instructions for it, its skills, its boards, and how to reach
 * the studio. The plain way to check what an agent has and has been told,
 * with "copy".
 *
 * Used by AgentManager, in a PaperWindow (?agents-md=<name>). The file is
 * written by the backend (backend/app/features/agents/agents_md.py), the
 * same one the run's sandbox setup writes.
 */

import { useEffect, useState } from "react";
import { fetchAgentsMd } from "../../api/agentsApi";
import { CopyButton } from "../../components/CopyButton";
import { LoadingWord } from "../../components/LoadingWord";

interface Props {
  agent: string;
  onDone: () => void;
}

export function AgentsMdView({ agent, onDone }: Props) {
  const [text, setText] = useState<string | null>(null);
  const [problem, setProblem] = useState("");

  useEffect(() => {
    fetchAgentsMd(agent)
      .then(setText)
      .catch((error) => setProblem(error instanceof Error ? error.message : String(error)));
  }, [agent]);

  return (
    <div className="studio-form agents-md">
      {problem && <p className="quiet">{problem}</p>}
      {text === null && !problem && <LoadingWord>reading</LoadingWord>}
      {text !== null && <pre>{text}</pre>}
      <p className="word-list studio-form-actions">
        {text !== null && <CopyButton text={text} label="copy" />}
        <button type="button" className="square is-primary" onClick={onDone}>
          done
        </button>
      </p>
    </div>
  );
}
