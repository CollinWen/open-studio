/**
 * StudioPage ( /studio, /studio/<section> ): the owner's back room, laid
 * out like every page: an intro, a section line, controls, then one list.
 * Asks the owner to sign in once (OwnerSignInForm). The sections, each with its count:
 *
 *   entries  ( /studio )         every entry, to edit or delete; the plus
 *                                opens the entry form (?add)
 *   boards   ( /studio/boards )  add a board, change its name or brief
 *   tags     ( /studio/tags )    describe and rank each tag
 *   add-ons  ( /studio/addons )  what agents can be given beyond the studio,
 *                                each defined once: its guide, the account it
 *                                acts as (connected on Composio's page)
 *   agents   ( /studio/agents )  add, pause, remove, issue tokens; the boards,
 *                                skills and add-ons of each, and its AGENTS.md
 *   runs     ( /studio/runs )    every token issued (each is a run): its agent,
 *                                add-ons, boards, state, and a link to watch its
 *                                harness's session; ?agent= narrows to one agent
 *
 * This page loads all six lists (for the counts) and reloads them after
 * any change; the large studio mark holds the section until its own list
 * is in. "leave" (under the section words) signs the owner out. ?q=
 * searches entries or tags. Adding and editing an entry happen in the form
 * that opens over the page (features/studio/EntryFormModal.tsx). Linked as "owner" ("studio" once signed in) in the header.
 */

import { useCallback, useEffect, useState } from "react";
import { useParams, useSearchParams } from "react-router-dom";
import { fetchAddons } from "../api/addonsApi";
import { fetchAgents } from "../api/agentsApi";
import { fetchBoards } from "../api/boardsApi";
import { fetchEntries } from "../api/entriesApi";
import { fetchRuns } from "../api/runsApi";
import { isOwnerSignedIn, signOwnerOut } from "../api/ownerSignIn";
import { fetchTags } from "../api/tagsApi";
import { LabelRow } from "../components/LabelRow";
import { LoadingMark } from "../components/LoadingMark";
import { SectionLine } from "../components/SectionLine";
import { SiteFooter } from "../components/SiteFooter";
import { AddonManager } from "../features/studio/AddonManager";
import { AgentManager } from "../features/studio/AgentManager";
import { BoardManager } from "../features/studio/BoardManager";
import { EntryIndex } from "../features/studio/EntryIndex";
import { OwnerSignInForm } from "../features/studio/OwnerSignInForm";
import { RunList } from "../features/studio/RunList";
import { TagNotesEditor } from "../features/studio/TagNotesEditor";
import { useOnEntrySaved } from "../features/studio/entrySavedEvent";
import { useEntryFormParam } from "../features/studio/useEntryFormParam";
import type { Addon } from "../types/addon";
import type { Agent } from "../types/agent";
import type { Board, Entry, Tag } from "../types/entry";
import type { Run } from "../types/run";

const SECTIONS = ["entries", "boards", "tags", "addons", "agents", "runs"] as const;
type Section = (typeof SECTIONS)[number];
// How a section is written, where it isn't its address.
const SECTION_LABELS: Partial<Record<Section, string>> = { addons: "add-ons" };

export function StudioPage() {
  const asked = useParams().section as Section | undefined;
  const section: Section = asked && SECTIONS.includes(asked) ? asked : "entries";
  const [params, setParams] = useSearchParams();
  const query = params.get("q") ?? "";
  const runAgent = params.get("agent") ?? "";
  const [signedIn, setSignedIn] = useState(isOwnerSignedIn());
  // null until loaded, so a section's count only shows once it's known.
  const [entries, setEntries] = useState<Entry[] | null>(null);
  const [boards, setBoards] = useState<Board[] | null>(null);
  const [tags, setTags] = useState<Tag[] | null>(null);
  const [addons, setAddons] = useState<Addon[] | null>(null);
  const [agents, setAgents] = useState<Agent[] | null>(null);
  const [runs, setRuns] = useState<Run[] | null>(null);
  const { openEntryEdit } = useEntryFormParam();

  const reload = useCallback(() => {
    fetchEntries().then(setEntries).catch(console.error);
    fetchBoards().then(setBoards).catch(console.error);
    fetchTags().then(setTags).catch(console.error);
    fetchAddons().then(setAddons).catch(console.error);
    fetchAgents().then(setAgents).catch(console.error);
    fetchRuns().then(setRuns).catch(console.error);
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
    addons: addons?.length,
    agents: agents?.length,
    runs: runs?.length,
  };
  const sections = SECTIONS.map((key) => ({
    key,
    label: SECTION_LABELS[key] ?? key,
    to: key === "entries" ? "/studio" : `/studio/${key}`,
    count: counts[key],
  }));

  return (
    <>
      <main>
        <LabelRow className="intro-row">
          <p className="display">The back room.</p>
        </LabelRow>
        {!signedIn && (
          <LabelRow rule="single" label="Owner token">
            <OwnerSignInForm onSignedIn={() => setSignedIn(true)} />
          </LabelRow>
        )}
        {signedIn && (
          <>
            <SectionLine label="Studio" sections={sections} current={section}>
              <p className="word-list quiet section-note">
                <button
                  type="button"
                  onClick={() => {
                    signOwnerOut();
                    setSignedIn(false);
                  }}
                >
                  leave the studio
                </button>
              </p>
            </SectionLine>
            {{ entries, boards, tags, addons, agents, runs }[section] === null && <LoadingMark />}
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
            {section === "addons" && addons && agents && (
              <AddonManager addons={addons} agents={agents} onChanged={reload} />
            )}
            {section === "agents" && agents && boards && addons && (
              <AgentManager agents={agents} boards={boards} addons={addons} onChanged={reload} />
            )}
            {section === "runs" && runs && entries && (
              <RunList
                runs={runAgent ? runs.filter((run) => run.agent === runAgent) : runs}
                entries={entries}
                agent={runAgent || undefined}
              />
            )}
          </>
        )}
      </main>
      <SiteFooter />
    </>
  );
}
