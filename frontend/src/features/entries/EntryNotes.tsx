/**
 * EntryNotes: an entry's "why it's here" on its entry page, as running text
 * at a readable measure, one paragraph per blank line. Used by EntryPage.
 */

export function EntryNotes({ text }: { text: string }) {
  if (!text) return null;
  return (
    <div className="prose">
      {text.split(/\n{2,}/).map((paragraph, index) => (
        <p key={index}>{paragraph}</p>
      ))}
    </div>
  );
}
