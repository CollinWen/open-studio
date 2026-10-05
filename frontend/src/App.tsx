/**
 * App: the route table (which URL shows which page), plus the site-wide
 * crosshair cursor.
 */

import { BrowserRouter, Route, Routes } from "react-router-dom";
import { CrosshairCursor } from "./components/CrosshairCursor";
import { AboutPage } from "./pages/AboutPage";
import { EntryPage } from "./pages/EntryPage";
import { HomePage } from "./pages/HomePage";
import { StudioPage } from "./pages/StudioPage";

export function App() {
  return (
    <BrowserRouter>
      <CrosshairCursor />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/entry/:id" element={<EntryPage />} />
        <Route path="/about" element={<AboutPage />} />
        <Route path="/studio" element={<StudioPage />} />
      </Routes>
    </BrowserRouter>
  );
}
