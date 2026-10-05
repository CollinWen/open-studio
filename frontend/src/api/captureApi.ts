/**
 * Asks the backend to read a link (YouTube, Google Drive, GitHub, any page)
 * and return a prefilled entry draft. Owner only.
 */

import type { CapturedLink } from "../types/entry";
import { backendRequest } from "./backendRequest";

export const captureLink = (url: string) =>
  backendRequest<CapturedLink>("/api/capture/link", { method: "POST", body: JSON.stringify({ url }) });
