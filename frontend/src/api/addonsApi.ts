/**
 * Calls to the backend's add-on endpoints (backend/app/features/addons/routes.py),
 * all for the owner: every add-on, defining one (its guide starts from a
 * template), changing its guide, removing one, a Composio add-on's tools,
 * and connecting one to its account on Composio's own sign-in page. Which
 * agents use an add-on, and how, is saved with the agent (agentsApi.ts).
 */

import type { Addon, AddonKind, CatalogTool } from "../types/addon";
import { backendRequest } from "./backendRequest";

const addonPath = (name: string) => `/api/addons/${encodeURIComponent(name)}`;

export const fetchAddons = () => backendRequest<Addon[]>("/api/addons");

export const addAddon = (addon: { name: string; kind: AddonKind; service: string }) =>
  backendRequest<Addon>("/api/addons", { method: "POST", body: JSON.stringify(addon) });

export const updateAddonGuide = (name: string, guide: string) =>
  backendRequest<Addon>(addonPath(name), { method: "PATCH", body: JSON.stringify({ guide }) });

export const removeAddon = (name: string) => backendRequest<void>(addonPath(name), { method: "DELETE" });

export const fetchAddonCatalog = (name: string, words = "") =>
  backendRequest<CatalogTool[]>(`${addonPath(name)}/catalog${words ? `?q=${encodeURIComponent(words)}` : ""}`);

/** The address of Composio's sign-in page for this add-on, which sends the owner back to returnUrl. */
export const startAddonConnection = (name: string, returnUrl: string) =>
  backendRequest<{ url: string }>(`${addonPath(name)}/connect`, {
    method: "POST",
    body: JSON.stringify({ return_url: returnUrl }),
  });

/** Keep the account Composio sent the owner back with; the backend checks it first. */
export const saveAddonConnection = (name: string, connectedAccountId: string) =>
  backendRequest<Addon>(`${addonPath(name)}/connection`, {
    method: "POST",
    body: JSON.stringify({ connected_account_id: connectedAccountId }),
  });
