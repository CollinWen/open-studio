/**
 * Starts the frontend: loads the typeface (Inter) and the
 * global styles, then puts the App on the page straight away. If the
 * owner's password is kept in this browser, it's checked alongside
 * (api/ownerSignIn.ts); one that was changed since is forgotten and the page
 * reloads as a visitor's, so stale owner controls never stay. Visitors skip
 * the check.
 */

import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "@fontsource-variable/inter";
import { forgetRefusedPassword } from "./api/ownerSignIn";
import { App } from "./App";
import "./styles/global.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);

forgetRefusedPassword().then((forgotten) => {
  if (forgotten) window.location.reload();
});
