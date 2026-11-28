/**
 * EntryNotes: an entry's "why it's here" on its entry page, as running text
 * at a readable measure, its markdown (lists, links, bold) shown as the
 * site's own text. Used by EntryPage.
 */

import { MarkdownText } from "../../components/MarkdownText";

export function EntryNotes({ text }: { text: string }) {
  if (!text) return null;
  return <MarkdownText text={text} className="prose" />;
}
