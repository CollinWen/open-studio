/**
 * Skill data shapes, matching backend/app/features/skills/schemas.py: one
 * skill the studio can give an agent, read from the agent resources
 * (AGENT_RESOURCES on the backend).
 */

export interface Skill {
  name: string;
  /** What it's for and when to use it, from its SKILL.md. */
  description: string;
  /** Where it was read from, as written in AGENT_RESOURCES. */
  source: string;
}

/** Every run gets these before its task's skills and its agent's own (backend runs/run_kit.py). */
export const CORE_SKILLS = ["open-studio", "studio-collaborator"];
