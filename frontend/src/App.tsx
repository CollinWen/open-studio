/**
 * App: the route table (which URL shows which page), plus the owner's entry
 * form, which opens over any page.
 */

import { BrowserRouter, Route, Routes } from "react-router-dom";
import { EntryFormModal } from "./features/studio/EntryFormModal";
import { AboutPage } from "./pages/AboutPage";
import { EntryPage } from "./pages/EntryPage";
import { BoardPage } from "./pages/BoardPage";
import { SketchPage } from "./pages/SketchPage";
import { StudioPage } from "./pages/StudioPage";

export function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<BoardPage />} />
        <Route path="/b/:board" element={<BoardPage />} />
        <Route path="/entry/:id" element={<EntryPage />} />
        <Route path="/about" element={<AboutPage />} />
        <Route path="/studio" element={<StudioPage />} />
        <Route path="/sketch" element={<SketchPage />} />
      </Routes>
      <EntryFormModal />
    </BrowserRouter>
  );
}
