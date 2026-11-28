/**
 * markdownParser: reads the small markdown the studio's text fields accept
 * into blocks (paragraphs, headings, lists, quotes, code, rules) and inline
 * pieces (bold, italic, code, links, bare web addresses), and turns
 * markdown back into plain text for places that show one quiet line.
 *
 * Pure: no React, no HTML strings. MarkdownText.tsx draws what it returns,
 * so nothing a person types can become markup that runs. Links keep only
 * safe addresses (web, mail, or a path on this site); anything else stays
 * as plain words.
 */

export type Inline =
  | { type: "text"; text: string }
  | { type: "strong"; children: Inline[] }
  | { type: "em"; children: Inline[] }
  | { type: "code"; text: string }
  | { type: "link"; href: string; children: Inline[] }
  | { type: "break" };

export type Block =
  | { type: "paragraph"; inline: Inline[] }
  | { type: "heading"; level: 1 | 2 | 3; inline: Inline[] }
  | { type: "list"; ordered: boolean; start: number; items: Block[][] }
  | { type: "quote"; blocks: Block[] }
  | { type: "code"; text: string }
  | { type: "rule" };

const LIST_ITEM = /^(\s*)([-*+]|\d+[.)])\s+(.*)$/;
const HEADING = /^(#{1,3})\s+(.*)$/;
const RULE = /^\s*([-*_])(\s*\1){2,}\s*$/;
const FENCE = /^\s*```/;

/** The whole text as blocks, top to bottom. */
export function parseMarkdown(text: string): Block[] {
  return parseLines(text.replace(/\r\n?/g, "\n").split("\n"));
}

function parseLines(lines: string[]): Block[] {
  const blocks: Block[] = [];
  let index = 0;
  while (index < lines.length) {
    const line = lines[index];
    if (!line.trim()) {
      index += 1;
    } else if (FENCE.test(line)) {
      const end = lines.findIndex((next, at) => at > index && FENCE.test(next));
      const stop = end === -1 ? lines.length : end;
      blocks.push({ type: "code", text: lines.slice(index + 1, stop).join("\n") });
      index = stop + 1;
    } else if (HEADING.test(line)) {
      const [, hashes, words] = line.match(HEADING)!;
      blocks.push({ type: "heading", level: hashes.length as 1 | 2 | 3, inline: parseInline(words) });
      index += 1;
    } else if (RULE.test(line)) {
      blocks.push({ type: "rule" });
      index += 1;
    } else if (/^\s*>/.test(line)) {
      const quoted: string[] = [];
      while (index < lines.length && /^\s*>/.test(lines[index])) {
        quoted.push(lines[index].replace(/^\s*>\s?/, ""));
        index += 1;
      }
      blocks.push({ type: "quote", blocks: parseLines(quoted) });
    } else if (LIST_ITEM.test(line)) {
      index = readList(lines, index, blocks);
    } else {
      const words: string[] = [];
      while (index < lines.length && startsParagraphLine(lines[index], words.length === 0)) {
        words.push(lines[index]);
        index += 1;
      }
      blocks.push({ type: "paragraph", inline: parseInline(words.join("\n")) });
    }
  }
  return blocks;
}

/** A paragraph runs until a blank line or a line that starts another kind of block. */
function startsParagraphLine(line: string, first: boolean): boolean {
  if (first) return true;
  return Boolean(line.trim()) && !FENCE.test(line) && !HEADING.test(line) && !/^\s*>/.test(line) && !LIST_ITEM.test(line);
}

/** One list: its items, each with the lines indented under it read as blocks of their own (a nested list). */
function readList(lines: string[], index: number, blocks: Block[]): number {
  const [, indent, marker] = lines[index].match(LIST_ITEM)!;
  const ordered = /\d/.test(marker);
  const items: string[][] = [];
  while (index < lines.length) {
    const line = lines[index];
    const item = line.match(LIST_ITEM);
    if (item && item[1].length <= indent.length && /\d/.test(item[2]) === ordered) {
      items.push([item[3]]);
    } else if (items.length && line.trim() && /^\s+/.test(line) && line.search(/\S/) > indent.length) {
      items[items.length - 1].push(line.slice(indent.length + 2));
    } else {
      break;
    }
    index += 1;
  }
  blocks.push({
    type: "list",
    ordered,
    start: ordered ? parseInt(marker, 10) : 1,
    items: items.map((itemLines) => {
      const [first, ...rest] = itemLines;
      return [{ type: "paragraph", inline: parseInline(first) }, ...parseLines(rest)];
    }),
  });
  return index;
}

// In order of strength: code first (nothing inside it is read), then links, bare addresses, bold, italic.
const INLINE =
  /`([^`\n]+)`|\[([^\]\n]+)\]\(([^)\s]+)\)|(https?:\/\/[^\s<>()]+[^\s<>().,;:!?'"])|\*\*(.+?)\*\*|__(.+?)__|\*([^*\s](?:[^*]*[^*\s])?)\*|(?<![\w])_([^_\s](?:[^_]*[^_\s])?)_(?![\w])|\n/g;

/** One line or paragraph's words, with its marks read. */
export function parseInline(text: string): Inline[] {
  const pieces: Inline[] = [];
  let last = 0;
  for (const match of text.matchAll(INLINE)) {
    const at = match.index ?? 0;
    if (at > last) pieces.push({ type: "text", text: text.slice(last, at) });
    pieces.push(readMark(match));
    last = at + match[0].length;
  }
  if (last < text.length) pieces.push({ type: "text", text: text.slice(last) });
  return pieces;
}

function readMark(match: RegExpMatchArray): Inline {
  const [whole, code, linkText, linkHref, bare, strong, strongUnder, em, emUnder] = match;
  if (code !== undefined) return { type: "code", text: code };
  if (linkText !== undefined) {
    return isSafeHref(linkHref) ? { type: "link", href: linkHref, children: parseInline(linkText) } : { type: "text", text: whole };
  }
  if (bare !== undefined) return { type: "link", href: bare, children: [{ type: "text", text: bare }] };
  if (strong !== undefined || strongUnder !== undefined) return { type: "strong", children: parseInline(strong ?? strongUnder) };
  if (em !== undefined || emUnder !== undefined) return { type: "em", children: parseInline(em ?? emUnder) };
  return { type: "break" };
}

/** Only web and mail addresses, and paths on this site, can be links. A path on this site has no
 * backslash: browsers read "\" as "/", so "/\evil.example" would open another site while
 * looking like a link within this one. */
export function isSafeHref(href: string): boolean {
  if (/^(https?:\/\/|mailto:)/i.test(href) || href.startsWith("#")) return true;
  return /^\/(?!\/)/.test(href) && !href.includes("\\");
}

/** The words alone, marks dropped, lines run together: for a card's one quiet line. */
export function markdownToPlainText(text: string): string {
  return parseMarkdown(text).map(blockText).join(" ").replace(/\s+/g, " ").trim();
}

function blockText(block: Block): string {
  switch (block.type) {
    case "paragraph":
    case "heading":
      return inlineText(block.inline);
    case "list":
      return block.items.map((item) => item.map(blockText).join(" ")).join(" · ");
    case "quote":
      return block.blocks.map(blockText).join(" ");
    case "code":
      return block.text;
    case "rule":
      return "";
  }
}

function inlineText(pieces: Inline[]): string {
  return pieces
    .map((piece) => {
      if (piece.type === "text" || piece.type === "code") return piece.text;
      if (piece.type === "break") return " ";
      return inlineText(piece.children);
    })
    .join("");
}
