/**
 * BoardManager: the owner's list of boards (spaces) on the studio page.
 * Add one by giving it a name; its address (/b/<slug>) is made from the name.
 * Each board's name and brief (the description agents read as what to look
 * for) can be changed in place, saved when you click away. Which agents may
 * add to a board is set in the Agents list below it (AgentManager).
 *
 * Used by StudioPage.
 */

import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { createBoard, fetchBoards, updateBoard } from "../../api/boardsApi";
import type { Board } from "../../types/entry";
import { boardPath } from "../grid/boardPath";

export function BoardManager({ onAdded }: { onAdded: () => void }) {
  const [boards, setBoards] = useState<Board[]>([]);
  const [message, setMessage] = useState("");

  const reload = useCallback(() => {
    fetchBoards().then(setBoards).catch(console.error);
  }, []);
  useEffect(reload, [reload]);

  const add = (name: string, description: string) =>
    createBoard({ slug: slugFor(name), name, description })
      .then(() => {
        setMessage("");
        onAdded();
      })
      .catch((error) => setMessage(error instanceof Error ? error.message : String(error)))
      .finally(reload);

  return (
    <section className="board-manager">
      <AddBoardForm onAdd={add} />
      {message && <p>{message}</p>}
      {boards.map((board) => (
        <BoardRow key={board.slug} board={board} />
      ))}
    </section>
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

function AddBoardForm({ onAdd }: { onAdd: (name: string, description: string) => void }) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");

  return (
    <form
      className="board-manager-add"
      onSubmit={(event) => {
        event.preventDefault();
        onAdd(name.trim(), description.trim());
        setName("");
        setDescription("");
      }}
    >
      <p className="word-list">
        <input placeholder="new board's name" value={name} onChange={(event) => setName(event.target.value)} />
        <span className="quiet">{name.trim() && `/b/${slugFor(name)}`}</span>
        <button type="submit" disabled={!slugFor(name)}>
          add board
        </button>
      </p>
      <textarea
        rows={2}
        placeholder="what this board is for, and what belongs on it (agents read this as their brief)"
        value={description}
        onChange={(event) => setDescription(event.target.value)}
      />
    </form>
  );
}

function BoardRow({ board }: { board: Board }) {
  const [name, setName] = useState(board.name);
  const [description, setDescription] = useState(board.description);
  const [status, setStatus] = useState("");

  const save = (changes: { name?: string; description?: string }) => {
    setStatus("saving…");
    updateBoard(board.slug, changes)
      .then(() => setStatus("saved"))
      .catch((error) => setStatus(error instanceof Error ? error.message : String(error)));
  };

  return (
    <div className="board-manager-row">
      <p className="word-list">
        <input
          value={name}
          onChange={(event) => setName(event.target.value)}
          onBlur={() => name.trim() && name !== board.name && save({ name: name.trim() })}
        />
        <Link to={boardPath(board.slug)} className="quiet">
          {boardPath(board.slug)}
        </Link>
        <span className="quiet">{status}</span>
      </p>
      <textarea
        rows={2}
        placeholder="what this board is for (saved when you click away)"
        value={description}
        onChange={(event) => setDescription(event.target.value)}
        onBlur={() => description !== board.description && save({ description })}
      />
    </div>
  );
}
