/**
 * Starts the frontend: loads the typeface (Inter) and the
 * global styles, then puts the App on the page. If the owner's password is
 * kept in this browser, it's checked first (api/ownerSignIn.ts), so a changed
 * one never shows owner controls; visitors skip the check.
 */

import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "@fontsource-variable/inter";
import { forgetRefusedPassword } from "./api/ownerSignIn";
import { App } from "./App";
import "./styles/global.css";

forgetRefusedPassword().finally(() =>
  createRoot(document.getElementById("root")!).render(
    <StrictMode>
      <App />
    </StrictMode>,
  ),
);
