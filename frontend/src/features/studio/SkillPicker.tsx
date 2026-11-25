/**
 * SkillPicker: the line of the agent window where the owner picks an
 * agent's skills, as ovals, from the skills the studio can give (read from
 * the agent resources). Pointing at one shows what it's for. A skill the
 * agent still has but the agent resources no longer hold shows as "gone",
 * picked, so one click takes it off. The two every run gets anyway
 * (open-studio, studio-collaborator) aren't offered; a quiet note says so.
 *
 * Used by AgentForm.
 */

import { useEffect, useState } from "react";
import { fetchSkills } from "../../api/skillsApi";
import { LoadingWord } from "../../components/LoadingWord";
import { WordChoice } from "../../components/WordChoice";
import { CORE_SKILLS, type Skill } from "../../types/skill";

interface Props {
  picked: string[];
  onChange: (skills: string[]) => void;
}

export function SkillPicker({ picked, onChange }: Props) {
  const [catalog, setCatalog] = useState<Skill[] | null>(null);
  const [problem, setProblem] = useState("");

  useEffect(() => {
    fetchSkills()
      .then(setCatalog)
      .catch((error) => setProblem(error instanceof Error ? error.message : String(error)));
  }, []);

  const offered = (catalog ?? []).filter((skill) => !CORE_SKILLS.includes(skill.name));
  const gone = catalog ? picked.filter((name) => !catalog.some((skill) => skill.name === name)) : [];
  const toggle = (name: string) =>
    onChange(picked.includes(name) ? picked.filter((one) => one !== name) : [...picked, name]);

  return (
    <>
      <p className="word-list is-ovals" role="group" aria-label="skills">
        <span className="quiet">skills</span>
        {!catalog && !problem && <LoadingWord>reading</LoadingWord>}
        {problem && <span className="quiet">{problem}</span>}
        {offered.map((skill) => (
          <WordChoice
            key={skill.name}
            label={skill.name}
            look="oval"
            hint={skill.description}
            active={picked.includes(skill.name)}
            onPick={() => toggle(skill.name)}
          />
        ))}
        {gone.map((name) => (
          <WordChoice key={name} label={`${name} (gone)`} look="oval" active onPick={() => toggle(name)} />
        ))}
      </p>
      <p className="quiet">Every run also gets {CORE_SKILLS.join(" and ")}, and its task's own skills.</p>
    </>
  );
}
