/**
 * Owner sign-in: the one place that knows how the owner proves who they are.
 * Today that's the admin password (OWNER_TOKEN in backend/.env), typed once
 * and kept in this browser. Visitors never sign in.
 *
 * Everything else asks only isOwnerSignedIn() and ownerAuthorization(), so
 * moving to Google sign-in (Firebase Auth) means changing this file and
 * OwnerSignInForm: sign in with Firebase's signInWithPopup, return
 * `Bearer <currentUser.getIdToken()>` from ownerAuthorization (it's async for
 * this reason), and sign out with Firebase's signOut. The backend side is
 * is_owner in backend/app/auth/owner_auth.py.
 */

const STORAGE_KEY = "open-studio-owner-token";

export function isOwnerSignedIn(): boolean {
  return Boolean(readPassword());
}

/** The Authorization header for the owner's requests; empty for visitors. */
export async function ownerAuthorization(): Promise<string> {
  const password = readPassword();
  return password ? `Bearer ${password}` : "";
}

export function signInWithPassword(password: string): void {
  try {
    localStorage.setItem(STORAGE_KEY, password);
  } catch {
    // Storage blocked (e.g. private window): the sign-in lasts until reload.
  }
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
