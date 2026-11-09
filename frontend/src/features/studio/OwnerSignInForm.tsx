/**
 * OwnerSignInForm: how the owner signs in on the studio page. Today a single
 * line asking for the admin password (the OWNER_TOKEN from backend/.env),
 * kept in this browser so it's only asked once (api/ownerSignIn.ts). For
 * Google sign-in this becomes one "sign in with Google" word.
 */

import { useState } from "react";
import { signInWithPassword } from "../../api/ownerSignIn";

export function OwnerSignInForm({ onSignedIn }: { onSignedIn: () => void }) {
  const [password, setPassword] = useState("");

  return (
    <form
      onSubmit={(event) => {
        event.preventDefault();
        signInWithPassword(password.trim());
        onSignedIn();
      }}
    >
      <input
        type="password"
        autoFocus
        placeholder="owner password, then enter"
        value={password}
        onChange={(event) => setPassword(event.target.value)}
      />
    </form>
  );
}
