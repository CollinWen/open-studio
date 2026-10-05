/**
 * OwnerTokenForm: a single line asking for the owner token (the OWNER_TOKEN
 * from backend/.env). Saved in this browser so it's only asked once.
 */

import { useState } from "react";
import { saveOwnerToken } from "../../api/ownerToken";

export function OwnerTokenForm({ onSaved }: { onSaved: () => void }) {
  const [token, setToken] = useState("");

  return (
    <form
      onSubmit={(event) => {
        event.preventDefault();
        saveOwnerToken(token.trim());
        onSaved();
      }}
    >
      <input
        type="password"
        autoFocus
        placeholder="owner token, then enter"
        value={token}
        onChange={(event) => setToken(event.target.value)}
      />
    </form>
  );
}
