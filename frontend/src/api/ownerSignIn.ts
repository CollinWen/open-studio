/**
 * Owner sign-in: the one place that knows how the owner proves who they are.
 * Today that's the admin password (OWNER_TOKEN in backend/.env), typed once,
 * checked with the backend (GET /api/auth/owner) and kept in this browser only
 * if it's right. A kept password is checked again when the site starts
 * (main.tsx), so one that was changed since is forgotten instead of leaving
 * owner controls that would fail. Visitors never sign in.
 *
 * Everything else asks only isOwnerSignedIn() and ownerAuthorization(), so
 * moving to Google sign-in (Firebase Auth) means changing this file and
 * OwnerSignInForm: sign in with Firebase's signInWithPopup, return
 * `Bearer <currentUser.getIdToken()>` from ownerAuthorization (it's async for
 * this reason), and sign out with Firebase's signOut. The backend side is
 * is_owner in backend/app/auth/owner_auth.py.
 */

import { API_URL } from "./backendRequest";

const STORAGE_KEY = "open-studio-owner-token";
// How long the start-up check may take before the site shows anyway, still signed in.
const START_CHECK_TIMEOUT_MS = 3000;

export function isOwnerSignedIn(): boolean {
  return Boolean(readPassword());
}

/** The Authorization header for the owner's requests; empty for visitors. */
export async function ownerAuthorization(): Promise<string> {
  const password = readPassword();
  return password ? `Bearer ${password}` : "";
}

/**
 * Asks the backend whether this is the owner's password and keeps it only if
 * so. Throws when the backend can't be reached, so a network problem is never
 * mistaken for a wrong password.
 */
export async function signInWithPassword(password: string): Promise<"signed-in" | "wrong-password"> {
  const response = await askIfOwner(password);
  if (response.status === 401) return "wrong-password";
  if (!response.ok) throw new Error(`The studio didn't answer (${response.status})`);
  try {
    localStorage.setItem(STORAGE_KEY, password);
  } catch {
    // Storage blocked (e.g. private window): the sign-in lasts until reload.
  }
  return "signed-in";
}

/**
 * Forgets the kept password if the backend now refuses it (it was changed).
 * A slow or unreachable backend keeps it: an outage never signs the owner out.
 */
export async function forgetRefusedPassword(): Promise<void> {
  const password = readPassword();
  if (!password) return;
  try {
    const response = await askIfOwner(password, AbortSignal.timeout(START_CHECK_TIMEOUT_MS));
    if (response.status === 401) signOwnerOut();
  } catch {
    // Unreachable or too slow: stay signed in; a save will say what's wrong.
  }
}

function askIfOwner(password: string, signal?: AbortSignal): Promise<Response> {
  return fetch(`${API_URL}/api/auth/owner`, { headers: { Authorization: `Bearer ${password}` }, signal });
}

export function signOwnerOut(): void {
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch {
    // Nothing stored, nothing to forget.
  }
}

function readPassword(): string {
  try {
    return localStorage.getItem(STORAGE_KEY) ?? "";
  } catch {
    return "";
  }
}
