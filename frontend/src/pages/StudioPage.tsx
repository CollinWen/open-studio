/**
 * StudioPage ( /studio, /studio/<section> ): the owner's back room, laid
 * out like every page: an intro, a section line, controls, then one list.
 * Asks the owner to sign in once (OwnerSignInForm). The sections, each with its count:
 *
 *   entries  ( /studio )         every entry, to edit or delete; the plus
 *                                opens the entry form (?add)
 *   boards   ( /studio/boards )  add a board, change its name or brief
 *   tags     ( /studio/tags )    describe and rank each tag
 *   agents   ( /studio/agents )  add, pause, re-key, remove; which boards
 *                                and outside tools each may use
 *
 * This page loads all four lists (for the counts) and reloads them after
 * any change; "loading" sweeps in the header until all four are in, and the
 * large studio mark holds the section until its own list is in. ?q=
 * searches entries or tags. Adding and editing an entry happen in the form
 * that opens over the page (features/studio/EntryFormModal.tsx). Linked as "owner" ("studio" once signed in) in the header.
 */

import { useCallback, useEffect, useState } from "react";
import { useParams, useSearchParams } from "react-router-dom";
import { fetchAgents } from "../api/agentsApi";
import { fetchBoards } from "../api/boardsApi";
import { fetchEntries } from "../api/entriesApi";
import { isOwnerSignedIn, signOwnerOut } from "../api/ownerSignIn";
import { fetchTags } from "../api/tagsApi";
import { LabelRow } from "../components/LabelRow";
import { LoadingMark } from "../components/LoadingMark";
import { LoadingWord } from "../components/LoadingWord";
import { SectionLine } from "../components/SectionLine";
import { SiteFooter } from "../components/SiteFooter";
import { SiteHeader } from "../components/SiteHeader";
import { AgentManager } from "../features/studio/AgentManager";
import { BoardManager } from "../features/studio/BoardManager";
import { EntryIndex } from "../features/studio/EntryIndex";
import { OwnerSignInForm } from "../features/studio/OwnerSignInForm";
import { TagNotesEditor } from "../features/studio/TagNotesEditor";
import { useOnEntrySaved } from "../features/studio/entrySavedEvent";
import { useEntryFormParam } from "../features/studio/useEntryFormParam";
import type { Agent } from "../types/agent";
import type { Board, Entry, Tag } from "../types/entry";

const SECTIONS = ["entries", "boards", "tags", "agents"] as const;
type Section = (typeof SECTIONS)[number];

export function StudioPage() {
  const asked = useParams().section as Section | undefined;
  const section: Section = asked && SECTIONS.includes(asked) ? asked : "entries";
  const [params, setParams] = useSearchParams();
  const query = params.get("q") ?? "";
  const [signedIn, setSignedIn] = useState(isOwnerSignedIn());
  // null until loaded, so a section's count only shows once it's known.
  const [entries, setEntries] = useState<Entry[] | null>(null);
  const [boards, setBoards] = useState<Board[] | null>(null);
  const [tags, setTags] = useState<Tag[] | null>(null);
  const [agents, setAgents] = useState<Agent[] | null>(null);
  const { openEntryEdit } = useEntryFormParam();

  const reload = useCallback(() => {
    fetchEntries().then(setEntries).catch(console.error);
    fetchBoards().then(setBoards).catch(console.error);
    fetchTags().then(setTags).catch(console.error);
    fetchAgents().then(setAgents).catch(console.error);
  }, []);

  useEffect(() => {
    if (signedIn) reload();
  }, [signedIn, reload]);
  useOnEntrySaved(reload);

  const search = (words: string) => setParams(words ? { q: words } : {}, { replace: true });
  const counts: Record<Section, number | undefined> = {
    entries: entries?.length,
    boards: boards?.length,
    tags: tags?.length,
    agents: agents?.length,
  };
  const sections = SECTIONS.map((key) => ({
    key,
    label: key,
    to: key === "entries" ? "/studio" : `/studio/${key}`,
    count: counts[key],
  }));

  return (
    <>
      <SiteHeader>
        {signedIn && [entries, boards, tags, agents].includes(null) && <LoadingWord />}
        {signedIn && (
          <button
            type="button"
            onClick={() => {
              signOwnerOut();
              setSignedIn(false);
            }}
          >
            leave
          </button>
        )}
      </SiteHeader>
      <main>
        <LabelRow rule="double" label="Studio" className="intro-row">
          <p className="display">The back room.</p>
        </LabelRow>
        {!signedIn && (
          <LabelRow rule="single" label="Owner">
            <OwnerSignInForm onSignedIn={() => setSignedIn(true)} />
          </LabelRow>
        )}
        {signedIn && (
          <>
            <SectionLine label="Show" sections={sections} current={section} />
            {{ entries, boards, tags, agents }[section] === null && <LoadingMark />}
            {section === "entries" && entries && (
              <EntryIndex
                entries={entries}
                query={query}
                onSearch={search}
                onEdit={(entry) => openEntryEdit(entry.id)}
                onChanged={reload}
              />
            )}
            {section === "boards" && boards && <BoardManager boards={boards} onChanged={reload} />}
            {section === "tags" && tags && <TagNotesEditor tags={tags} query={query} onSearch={search} />}
            {section === "agents" && agents && boards && (
              <AgentManager agents={agents} boards={boards} onChanged={reload} />
            )}
          </>
        )}
      </main>
      <SiteFooter />
    </>
  );
}
