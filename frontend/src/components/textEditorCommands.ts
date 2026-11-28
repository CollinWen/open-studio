/**
 * textEditorCommands: what the text editor's words and keys do to the text
 * in its field: mark words bold, italic or as code, make a link, start
 * lines as a list, quote or heading, carry a list on when Enter is pressed,
 * indent a list with Tab, and turn a pasted web address over some words
 * into a link.
 *
 * Every change goes through the browser's own typing (insertText), so undo
 * and redo keep working as if you had typed it. Used by TextEditor.tsx.
 */

type Field = HTMLTextAreaElement;

/** Put `text` in place of the selection, then select from `selectFrom` to `selectTo` within it. */
function replaceSelection(field: Field, text: string, selectFrom = text.length, selectTo = selectFrom) {
  const start = field.selectionStart;
  field.focus();
  // insertText keeps the browser's undo history; the fallback (very old browsers) still updates the field.
  if (!document.execCommand("insertText", false, text)) {
    field.setRangeText(text, start, field.selectionEnd, "end");
    field.dispatchEvent(new Event("input", { bubbles: true }));
  }
  field.setSelectionRange(start + selectFrom, start + selectTo);
}

/** Wrap the selection in a mark (`**`, `*`, `` ` ``), or take it off if it's already there. */
export function toggleMark(field: Field, mark: string) {
  const { value, selectionStart: start, selectionEnd: end } = field;
  const selected = value.slice(start, end);
  const before = value.slice(start - mark.length, start);
  const after = value.slice(end, end + mark.length);
  if (before === mark && after === mark) {
    field.setSelectionRange(start - mark.length, end + mark.length);
    replaceSelection(field, selected, 0, selected.length);
  } else if (selected.length > 2 * mark.length && selected.startsWith(mark) && selected.endsWith(mark)) {
    const inner = selected.slice(mark.length, -mark.length);
    replaceSelection(field, inner, 0, inner.length);
  } else {
    replaceSelection(field, `${mark}${selected}${mark}`, mark.length, mark.length + selected.length);
  }
}

const WEB_ADDRESS = /^(https?:\/\/|mailto:|\/(?!\/))\S+$/i;

/**
 * Make a link from the selection (or the word at the caret). Selected words become the link's words,
 * with "address" selected to type or paste over; a selected address becomes
 * the link's address, with "words" selected instead.
 */
export function makeLink(field: Field) {
  if (field.selectionStart === field.selectionEnd) selectWordAtCaret(field);
  const selected = field.value.slice(field.selectionStart, field.selectionEnd).trim();
  if (WEB_ADDRESS.test(selected)) {
    replaceSelection(field, `[words](${selected})`, 1, 6);
  } else {
    const words = selected || "words";
    replaceSelection(field, `[${words}](address)`, words.length + 3, words.length + 10);
  }
}

/** With nothing selected, the word the caret is in or just after becomes the selection. */
function selectWordAtCaret(field: Field) {
  const { value, selectionStart: at } = field;
  const start = at - (value.slice(0, at).match(/[^\s[\]()]*$/)?.[0].length ?? 0);
  const end = at + (value.slice(at).match(/^[^\s[\]()]*/)?.[0].length ?? 0);
  field.setSelectionRange(start, end);
}

/** Pasting a web address over selected words links them instead of replacing them. True when it did. */
export function pasteAsLink(field: Field, pasted: string): boolean {
  const selected = field.value.slice(field.selectionStart, field.selectionEnd);
  const address = pasted.trim();
  if (!selected.trim() || selected.includes("\n") || !WEB_ADDRESS.test(address)) return false;
  const link = `[${selected}](${address})`;
  replaceSelection(field, link);
  return true;
}

/** The start and end of the whole lines the selection touches. */
function selectedLines(field: Field): [number, number] {
  const { value, selectionStart, selectionEnd } = field;
  const from = value.lastIndexOf("\n", selectionStart - 1) + 1;
  const lineEnd = value.indexOf("\n", selectionEnd);
  return [from, lineEnd === -1 ? value.length : lineEnd];
}

/** Start every selected line with `prefix` ("- ", "> ", "## "), or take it off if they all have it. */
export function toggleLinePrefix(field: Field, prefix: string) {
  const [from, to] = selectedLines(field);
  const lines = field.value.slice(from, to).split("\n");
  const allHaveIt = lines.every((line) => line.startsWith(prefix));
  const changed = lines.map((line) => (allHaveIt ? line.slice(prefix.length) : prefix + line)).join("\n");
  field.setSelectionRange(from, to);
  replaceSelection(field, changed, changed.length);
}

const CONTINUED_LINE = /^(\s*)([-*+] |(\d+)([.)]) |> )/;

/**
 * Enter inside a list or quote starts the next item; Enter on an empty item
 * ends the list. True when it handled the key.
 */
export function continueList(field: Field): boolean {
  const { value, selectionStart, selectionEnd } = field;
  if (selectionStart !== selectionEnd) return false;
  const lineStart = value.lastIndexOf("\n", selectionStart - 1) + 1;
  const line = value.slice(lineStart, selectionStart);
  const match = line.match(CONTINUED_LINE);
  if (!match) return false;
  const [marker, indent, , number, closer] = match;
  if (line.trim() === marker.trim()) {
    field.setSelectionRange(lineStart, selectionStart);
    replaceSelection(field, "");
    return true;
  }
  const next = number ? `${parseInt(number, 10) + 1}${closer} ` : marker.slice(indent.length);
  replaceSelection(field, `\n${indent}${next}`);
  return true;
}

/** Tab and shift-Tab on list lines move them in and out a step. True when it handled the key. */
export function indentList(field: Field, outward: boolean): boolean {
  const [from, to] = selectedLines(field);
  const lines = field.value.slice(from, to).split("\n");
  const isList = (line: string) => CONTINUED_LINE.test(line) && !line.trimStart().startsWith(">");
  if (!lines.some(isList) || !lines.every((line) => isList(line) || !line.trim())) return false;
  const changed = lines.map((line) => (outward ? line.replace(/^ {1,2}/, "") : line && `  ${line}`)).join("\n");
  field.setSelectionRange(from, to);
  replaceSelection(field, changed, changed.length);
  return true;
}
