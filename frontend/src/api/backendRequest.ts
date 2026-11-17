/**
 * The one function every API file uses to call the backend. Attaches the
 * owner's sign-in (api/ownerSignIn.ts) when there is one and turns error replies into thrown errors.
 *
 * In development requests go to /api on the Vite server (passed through to the
 * backend). In production VITE_API_URL (set by deploy.py) gives the backend's
 * own address, e.g. https://api.yourdomain.com.
 */

import { ownerAuthorization } from "./ownerSignIn";

export const API_URL = import.meta.env.VITE_API_URL ?? "";

export async function backendRequest<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  const authorization = await ownerAuthorization();
  if (authorization) headers.set("Authorization", authorization);
  if (init.body && !(init.body instanceof FormData)) headers.set("Content-Type", "application/json");

  const response = await fetch(`${API_URL}${path}`, { ...init, headers });
  if (!response.ok) {
    throw new Error(await readErrorMessage(response));
  }
  return response.status === 204 ? (undefined as T) : response.json();
}

/**
 * The backend's own explanation when it gives one, otherwise the status code:
 * {"detail": "..."} as it is, or a list of field problems (a 422) as their
 * plain messages, one after another.
 */
async function readErrorMessage(response: Response): Promise<string> {
  const text = await response.text();
  try {
    const { detail } = JSON.parse(text);
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail) && detail.every((problem) => typeof problem?.msg === "string")) {
      return detail.map((problem) => problem.msg.replace(/^Value error, /, "")).join(" ");
    }
  } catch {
    // Not JSON: fall through.
  }
  return `${response.status} ${text}`;
}
