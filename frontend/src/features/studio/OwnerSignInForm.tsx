/**
 * OwnerSignInForm: how the owner signs in on the studio page. Today a single
 * line asking for the admin password (the OWNER_TOKEN from backend/.env).
 * It's checked with the backend first and kept in this browser only if it's
 * right (api/ownerSignIn.ts); a wrong one says so and the form stays. For
 * Google sign-in this becomes one "sign in with Google" word.
 */

import { useState } from "react";
import { signInWithPassword } from "../../api/ownerSignIn";
import { LoadingWord } from "../../components/LoadingWord";

export function OwnerSignInForm({ onSignedIn }: { onSignedIn: () => void }) {
  const [password, setPassword] = useState("");
  const [checking, setChecking] = useState(false);
  const [problem, setProblem] = useState("");

  const signIn = async () => {
    setChecking(true);
    setProblem("");
    try {
      if ((await signInWithPassword(password.trim())) === "signed-in") return onSignedIn();
      setProblem("That isn't the owner password.");
    } catch {
      setProblem("Couldn't reach the studio. Try again in a moment.");
    } finally {
      setChecking(false);
    }
  };

  return (
    <form
      onSubmit={(event) => {
        event.preventDefault();
        if (!checking) signIn();
      }}
    >
      <input
        type="password"
        autoFocus
        placeholder="owner password, then enter"
        value={password}
        onChange={(event) => setPassword(event.target.value)}
      />
      {checking && <LoadingWord>checking</LoadingWord>}
      {problem && <p className="quiet">{problem}</p>}
    </form>
  );
}
