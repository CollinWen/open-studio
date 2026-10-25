/**
 * BoardManager: the studio's "boards" (spaces). The control band adds one:
 * a name (its address, /b/<slug>, is made from it), a brief (what agents
 * read as what to look for), and a plus. Below, a Ledger of every board,
 * whose name and brief can be changed in place, saved when you click away.
 * Which agents may add to a board is set in the studio's "agents".
 *
 * Used by StudioPage, which loads the boards.
 */

import { useState } from "react";
import { Link } from "react-router-dom";
import { createBoard, updateBoard } from "../../api/boardsApi";
import { ControlBand } from "../../components/ControlBand";
import { Icon } from "../../components/Icon";
import { LabelRow } from "../../components/LabelRow";
import { LoadingWord } from "../../components/LoadingWord";
import { Ledger } from "../../components/Ledger";
import { LedgerRow } from "../../components/LedgerRow";
import type { Board } from "../../types/entry";
import { boardPath } from "../grid/boardPath";

interface Props {
  boards: Board[];
  onChanged: () => void;
}

const COLUMNS = [
  { label: "board", span: 3 },
  { label: "brief: what belongs here (agents read this)", span: 9 },
];

export function BoardManager({ boards, onChanged }: Props) {
  const [name, setName] = useState("");
  const [brief, setBrief] = useState("");
  const [message, setMessage] = useState("");

  const add = () =>
    createBoard({ slug: slugFor(name), name: name.trim(), description: brief.trim() })
      .then(() => {
        setName("");
        setBrief("");
        setMessage("");
        onChanged();
      })
      .catch((error) => setMessage(error instanceof Error ? error.message : String(error)));

  return (
    <>
      <ControlBand
        label="Add"
        controls={
          <form
            className="browse-controls"
            onSubmit={(event) => {
              event.preventDefault();
              add();
            }}
          >
            <input placeholder="name" value={name} onChange={(event) => setName(event.target.value)} />
            <input
              className="is-long"
              placeholder="what it's for"
              value={brief}
              onChange={(event) => setBrief(event.target.value)}
            />
            <button type="submit" className="icon-button" aria-label="add board" disabled={!slugFor(name)}>
              <Icon name="plus" />
            </button>
            <span className="quiet">{message || (slugFor(name) && `/b/${slugFor(name)}`)}</span>
          </form>
        }
      />
      <LabelRow wide>
        <Ledger columns={COLUMNS}>
          {boards.map((board) => (
            <BoardRow key={board.slug} board={board} />
          ))}
        </Ledger>
      </LabelRow>
    </>
  );
}

/** Lowercase letters, digits and dashes, as the backend expects: "Paper Folding" → "paper-folding". */
function slugFor(name: string): string {
  return name
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 40);
}

const SAVING = "saving…";

function BoardRow({ board }: { board: Board }) {
  const [name, setName] = useState(board.name);
  const [description, setDescription] = useState(board.description);
  const [status, setStatus] = useState("");

  const save = (changes: { name?: string; description?: string }) => {
    setStatus(SAVING);
    updateBoard(board.slug, changes)
      .then(() => setStatus("saved"))
      .catch((error) => setStatus(error instanceof Error ? error.message : String(error)));
  };

  return (
    <LedgerRow
      cells={[
        <>
          <input
            value={name}
            onChange={(event) => setName(event.target.value)}
            onBlur={() => name.trim() && name !== board.name && save({ name: name.trim() })}
          />
          <span className="ledger-note">
            <Link to={boardPath(board.slug)} className="quiet">
              {boardPath(board.slug)}
            </Link>
            <span className="quiet"> {status === SAVING ? <LoadingWord>{status}</LoadingWord> : status}</span>
          </span>
        </>,
        <textarea
          rows={2}
          placeholder="what this board is for (saved when you click away)"
          value={description}
          onChange={(event) => setDescription(event.target.value)}
          onBlur={() => description !== board.description && save({ description })}
        />,
      ]}
    />
  );
}
