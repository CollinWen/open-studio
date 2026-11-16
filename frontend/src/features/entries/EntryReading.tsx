/**
 * EntryReading: for the owner only, a quiet row at the foot of an entry page
 * saying what the studio read from the entry: each part (its source link,
 * each picture, described in words) and the exact text it embedded, so it's
 * easy to see why an entry is tagged, found or related the way it is.
 * Closed until asked ("show"). "read again" reads every part afresh.
 *
 * Reading happens in the background after a save; while it's under way this
 * checks back every few seconds and, once done, reloads the page (tags may
 * have arrived). Used by EntryPage. Visitors never get readings.
 */

import { useCallback, useEffect, useState } from "react";
import { fetchEntryReading, readEntryAgain } from "../../api/entriesApi";
import { LabelRow } from "../../components/LabelRow";
import { Ledger } from "../../components/Ledger";
import { LedgerRow } from "../../components/LedgerRow";
import { LoadingWord } from "../../components/LoadingWord";
import type { EntryReading as Reading } from "../../types/entry";

const CHECK_AGAIN_MS = 3000;
const COLUMNS = [
  { label: "part", span: 3 },
  { label: "what the studio read", span: 9 },
];

export function EntryReading({ entryId, onReadingDone }: { entryId: string; onReadingDone: () => void }) {
  const [reading, setReading] = useState<Reading | null>(null);
  const [open, setOpen] = useState(false);

  const load = useCallback(() => {
    fetchEntryReading(entryId)
      .then(setReading)
      .catch(() => setReading(null));
  }, [entryId]);

  useEffect(load, [load]);

  const waiting = reading?.waiting ?? false;
  useEffect(() => {
    if (!waiting) return;
    const timer = window.setTimeout(() => {
      fetchEntryReading(entryId).then((next) => {
        setReading(next);
        if (!next.waiting) onReadingDone();
      });
    }, CHECK_AGAIN_MS);
    return () => window.clearTimeout(timer);
  }, [waiting, reading, entryId, onReadingDone]);

  if (!reading) return null;
  const readAgain = () => readEntryAgain(entryId).then(setReading);

  return (
    <LabelRow rule="single" label="Read by the studio">
      <p className="word-list">
        <button type="button" className="quiet" onClick={() => setOpen(!open)}>
          {open ? "hide" : "show"}
        </button>
        {waiting ? <LoadingWord>reading</LoadingWord> : <span className="quiet">{embeddingState(reading)}</span>}
        {!waiting && (
          <button type="button" className="quiet" onClick={readAgain}>
            read again
          </button>
        )}
      </p>
      {open && (
        <Ledger columns={COLUMNS}>
          {reading.parts.map((part) => (
            <LedgerRow
              key={`${part.part} ${part.address}`}
              cells={[
                <a className="quiet" href={part.address} target="_blank" rel="noreferrer">
                  {part.part}
                </a>,
                <p className="entry-reading-text">{part.text}</p>,
              ]}
            />
          ))}
          <LedgerRow cells={[<span className="quiet">embedded</span>, <p className="entry-reading-text">{reading.embedding_text}</p>]} />
        </Ledger>
      )}
    </LabelRow>
  );
}

function embeddingState(reading: Reading): string {
  const read = `${reading.parts.length} ${reading.parts.length === 1 ? "part" : "parts"} read`;
  if (!reading.has_embedding) return `${read} · not embedded`;
  if (!reading.embedding_is_current) return `${read} · embedded by ${reading.embedding_model}, an older model`;
  return `${read} · embedded`;
}
