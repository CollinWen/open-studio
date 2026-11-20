/**
 * useGridColumns: how many columns the picture grid has right now, read
 * from its --grid-columns in styles/board.css (which changes with the
 * picture size and the screen width), so the column counts live in one
 * place: the styles.
 * Read again whenever the grid changes width. Used by EntryGrid.
 */

import { useLayoutEffect, useState, type RefObject } from "react";

export function useGridColumns(grid: RefObject<HTMLElement | null>, size: string) {
  const [columns, setColumns] = useState(1);

  // Before the first paint, so the grid never shows one column and then jumps.
  useLayoutEffect(() => {
    const element = grid.current;
    if (!element) return;
    const read = () => {
      const count = parseInt(getComputedStyle(element).getPropertyValue("--grid-columns"), 10);
      setColumns(count > 0 ? count : 1);
    };
    read();
    const watcher = new ResizeObserver(read);
    watcher.observe(element);
    return () => watcher.disconnect();
  }, [grid, size]);

  return columns;
}
