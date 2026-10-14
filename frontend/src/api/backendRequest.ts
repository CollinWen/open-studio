/**
 * The one function every API file uses to call the backend. Attaches the
 * owner token when there is one and turns error replies into thrown errors.
 *
 * In development requests go to /api on the Vite server (passed through to the
 * backend). In production VITE_API_URL (set by deploy.py) gives the backend's
 * own address, e.g. https://api.yourdomain.com.
 */

import { readOwnerToken } from "./ownerToken";

const API_URL = import.meta.env.VITE_API_URL ?? "";

export async function backendRequest<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  const token = readOwnerToken();
  if (token) headers.set("Authorization", `Bearer ${token}`);
  if (init.body && !(init.body instanceof FormData)) headers.set("Content-Type", "application/json");

  const response = await fetch(`${API_URL}${path}`, { ...init, headers });
  if (!response.ok) {
    throw new Error(await readErrorMessage(response));
  }
  return response.status === 204 ? (undefined as T) : response.json();
}

/** The backend's own explanation when it gives one ({"detail": "..."}), otherwise the status code. */
async function readErrorMessage(response: Response): Promise<string> {
  const text = await response.text();
  try {
    const { detail } = JSON.parse(text);
    if (typeof detail === "string") return detail;
  } catch {
    // Not JSON: fall through.
  }
  return `${response.status} ${text}`;
}
