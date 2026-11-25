/**
 * Calls to the backend's skill endpoint (backend/app/features/skills/routes.py):
 * the skills the owner can give an agent, read from the agent resources.
 * An agent's picks are saved with the agent (agentsApi.ts).
 */

import type { Skill } from "../types/skill";
import { backendRequest } from "./backendRequest";

export const fetchSkills = () => backendRequest<Skill[]>("/api/skills");
