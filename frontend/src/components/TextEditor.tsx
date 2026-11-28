/**
 * TextEditor: the one field for writing more than a line, used everywhere
 * the site takes running text (an entry's notes, a board's brief, a tag's
 * description, a run's note). It grows with what you write instead of
 * scrolling inside itself, and reads markdown: **bold**, *italic*, `code`,
 * [links](address), lists, quotes and headings.
 *
 * Under the field sits a quiet line of words: bold · italic · link · list ·
 * quote, then write · preview (preview shows the text as the site will).
 * Keys: ⌘/Ctrl B, I, K for bold, italic and link; ⌘/Ctrl Enter saves the
 * form; Enter carries a list on; Tab moves list lines in. Pasting a web
 * address over selected words links them. What each does to the text lives
 * in textEditorCommands.ts. A compact editor (inside a ledger row) shows
 * its line of words only while you're writing in it.
 *
 * Looks: .text-editor in styles/controls.css. Shown text: MarkdownText.
 */

import { useLayoutEffect, useRef, useState, type FocusEvent, type KeyboardEvent } from "react";
import { MarkdownText } from "./MarkdownText";
import { continueList, indentList, makeLink, pasteAsLink, toggleLinePrefix, toggleMark } from "./textEditorCommands";
import { WordChoice } from "./WordChoice";

interface Props {
  value: string;
  onChange: (text: string) => void;
  placeholder?: string;
  /** The fewest lines it shows when empty. */
  rows?: number;
  /** Called when focus leaves the whole editor (field and its words), not when you click one of its words. */
  onBlur?: () => void;
  autoFocus?: boolean;
  /** Hide the line of words until the editor is being used: for fields inside a list. */
  compact?: boolean;
}

type Tool = { label: string; run: (field: HTMLTextAreaElement) => void };

const TOOLS: Tool[] = [
  { label: "bold", run: (field) => toggleMark(field, "**") },
  { label: "italic", run: (field) => toggleMark(field, "*") },
  { label: "link", run: makeLink },
  { label: "list", run: (field) => toggleLinePrefix(field, "- ") },
  { label: "quote", run: (field) => toggleLinePrefix(field, "> ") },
];

const SHORTCUTS: Record<string, (field: HTMLTextAreaElement) => void> = {
  b: TOOLS[0].run,
  i: TOOLS[1].run,
  k: TOOLS[2].run,
};

export function TextEditor({ value, onChange, placeholder, rows = 3, onBlur, autoFocus, compact }: Props) {
  const fieldRef = useRef<HTMLTextAreaElement>(null);
  const [previewing, setPreviewing] = useState(false);

  // Grow to fit the text, so the field never scrolls inside itself.
  useLayoutEffect(() => {
    const field = fieldRef.current;
    if (!field) return;
    field.style.height = "auto";
    field.style.height = `${field.scrollHeight}px`;
  }, [value, previewing]);

  function onKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    const field = event.currentTarget;
    const withModifier = event.metaKey || event.ctrlKey;
    if (withModifier && event.key === "Enter") {
      event.preventDefault();
      field.form?.requestSubmit();
    } else if (withModifier && !event.shiftKey && !event.altKey && SHORTCUTS[event.key.toLowerCase()]) {
      event.preventDefault();
      SHORTCUTS[event.key.toLowerCase()](field);
    } else if (event.key === "Enter" && !event.shiftKey && !withModifier && continueList(field)) {
      event.preventDefault();
    } else if (event.key === "Tab" && !withModifier && indentList(field, event.shiftKey)) {
      event.preventDefault();
    }
  }

  function leave(event: FocusEvent<HTMLDivElement>) {
    if (!event.currentTarget.contains(event.relatedTarget)) onBlur?.();
  }

  function showWriting() {
    setPreviewing(false);
    requestAnimationFrame(() => fieldRef.current?.focus());
  }

  const classes = ["text-editor", compact && "is-compact", previewing && "is-previewing"].filter(Boolean).join(" ");
  return (
    <div className={classes} onBlur={leave}>
      {previewing ? (
        // Clicking the preview (anywhere but a link) goes back to writing.
        <div className="text-editor-preview" onClick={(event) => !(event.target as Element).closest("a") && showWriting()}>
          {value.trim() ? <MarkdownText text={value} /> : <span className="faint">nothing written yet</span>}
        </div>
      ) : (
        <textarea
          ref={fieldRef}
          rows={rows}
          value={value}
          placeholder={placeholder}
          aria-label={placeholder}
          autoFocus={autoFocus}
          onChange={(event) => onChange(event.target.value)}
          onKeyDown={onKeyDown}
          onPaste={(event) => pasteAsLink(event.currentTarget, event.clipboardData.getData("text")) && event.preventDefault()}
        />
      )}
      <p className="word-list text-editor-tools">
        {!previewing &&
          TOOLS.map((tool) => (
            <button
              key={tool.label}
              type="button"
              className="square quiet"
              // Keep the caret and selection in the field while the word acts on them.
              onMouseDown={(event) => event.preventDefault()}
              onClick={() => fieldRef.current && tool.run(fieldRef.current)}
            >
              {tool.label}
            </button>
          ))}
        <span className="text-editor-modes">
          <WordChoice label="write" active={!previewing} onPick={showWriting} />
          <WordChoice label="preview" active={previewing} onPick={() => setPreviewing(true)} />
        </span>
      </p>
    </div>
  );
}
