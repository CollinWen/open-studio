/**
 * Owner token: remembers the admin password in this browser, so the owner
 * only types it once. Visitors never have one.
 */

const STORAGE_KEY = "open-studio-owner-token";

export function readOwnerToken(): string {
  try {
    return localStorage.getItem(STORAGE_KEY) ?? "";
  } catch {
    return "";
  }
}

export function saveOwnerToken(token: string): void {
  try {
    localStorage.setItem(STORAGE_KEY, token);
  } catch {
    // Storage blocked (e.g. private window): the token lasts until reload.
  }
}

export function forgetOwnerToken(): void {
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch {
    // Nothing stored, nothing to forget.
  }
}
