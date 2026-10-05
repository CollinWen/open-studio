/**
 * AboutPage ( /about ): the welcome text from the project brief.
 * Edit the words here directly.
 */

import { SiteFooter } from "../components/SiteFooter";
import { SiteHeader } from "../components/SiteHeader";

export function AboutPage() {
  return (
    <>
      <SiteHeader />
      <main className="column">
        <p>
          Welcome. This is a working collection of things I make and things I'm curious about. You'll find
          computer science, cooking experiments, art, and everything in between. Part portfolio, part sketchbook.
        </p>
        <p>
          I've never been great at showing the things I find meaningful, so this is partly an experiment in doing
          that, and partly a look at how I organize my own life. It's always in progress.
        </p>
        <p>
          Each piece links to others related in meaning, whatever they're made of: a coding project can lead to a
          recipe.
        </p>
        <p>If something here catches your eye, I'd love to talk about it. Send me a note.</p>
      </main>
      <SiteFooter />
    </>
  );
}
