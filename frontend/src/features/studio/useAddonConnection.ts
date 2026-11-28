/**
 * useAddonConnection: connecting a Composio add-on to the account it acts
 * as, without handling a key. `connect` asks the backend for Composio's
 * sign-in page for the add-on and goes there; Composio sends the owner back
 * to /studio/addons?connected=<name>, with status=success and the new
 * account's connected_account_id added. This hook then hands that account
 * to the backend (which checks it with Composio before keeping it), takes
 * the three words back out of the address, and reports how it went.
 *
 * Used by AddonManager.
 */

import { useEffect, useRef, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { saveAddonConnection, startAddonConnection } from "../../api/addonsApi";

// The words Composio adds to the address it sends the owner back to.
const COMPOSIO_STATUS = "status";
const COMPOSIO_ACCOUNT = "connected_account_id";
const CONNECTED = "connected";

export function useAddonConnection(onChanged: () => void) {
  const [params, setParams] = useSearchParams();
  const [message, setMessage] = useState("");
  const returned = params.get(CONNECTED);
  const status = params.get(COMPOSIO_STATUS);
  const account = params.get(COMPOSIO_ACCOUNT);
  // The return already handled: effects can run twice (React's strict mode), a save should not.
  const handled = useRef("");

  useEffect(() => {
    if (!returned || handled.current === `${returned} ${account}`) return;
    handled.current = `${returned} ${account}`;
    setParams(
      (current) => {
        const next = new URLSearchParams(current);
        [CONNECTED, COMPOSIO_STATUS, COMPOSIO_ACCOUNT].forEach((word) => next.delete(word));
        return next;
      },
      { replace: true },
    );
    if (status !== "success" || !account) {
      setMessage(`${returned} wasn't connected: Composio said ${status ?? "nothing"}.`);
      return;
    }
    setMessage(`connecting ${returned}`);
    saveAddonConnection(returned, account)
      .then(() => setMessage(`${returned} is connected, as ${account}.`))
      .catch((error) => setMessage(error instanceof Error ? error.message : String(error)))
      .finally(onChanged);
  }, [returned, status, account, setParams, onChanged]);

  const connect = (name: string) => {
    setMessage(`opening Composio for ${name}`);
    const back = `${window.location.origin}/studio/addons?${CONNECTED}=${encodeURIComponent(name)}`;
    startAddonConnection(name, back)
      .then(({ url }) => window.location.assign(url))
      .catch((error) => setMessage(error instanceof Error ? error.message : String(error)));
  };

  return { connect, message };
}
