/**
 * App: the route table (which URL shows which page; anything else gets the
 * not-found page), under the one site header, which stays put (and stays
 * up while a page loads), plus the owner's entry form, which opens over any page.
 * A newly opened page starts at the top (ScrollToTopOnNewPage).
 */

import { BrowserRouter, Route, Routes } from "react-router-dom";
import { ScrollToTopOnNewPage } from "./components/ScrollToTopOnNewPage";
import { SiteHeader } from "./components/SiteHeader";
import { EntryFormModal } from "./features/studio/EntryFormModal";
import { AboutPage } from "./pages/AboutPage";
import { AgentsPage } from "./pages/AgentsPage";
import { EntryPage } from "./pages/EntryPage";
import { NotFoundPage } from "./pages/NotFoundPage";
import { BoardPage } from "./pages/BoardPage";
import { SketchPage } from "./pages/SketchPage";
import { StudioPage } from "./pages/StudioPage";

export function App() {
  return (
    <BrowserRouter>
      <ScrollToTopOnNewPage />
      <SiteHeader />
      <Routes>
        <Route path="/" element={<BoardPage />} />
        <Route path="/b/:board" element={<BoardPage />} />
        <Route path="/entry/:id" element={<EntryPage />} />
        <Route path="/about" element={<AboutPage />} />
        <Route path="/agents" element={<AgentsPage />} />
        <Route path="/agents/:section" element={<AgentsPage />} />
        <Route path="/studio" element={<StudioPage />} />
        <Route path="/studio/:section" element={<StudioPage />} />
        <Route path="/sketch" element={<SketchPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
      <EntryFormModal />
    </BrowserRouter>
  );
}
