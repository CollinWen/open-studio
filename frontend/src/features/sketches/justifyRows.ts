/**
 * justifyRows: the contact-sheet layout. Pictures keep their own shapes and
 * are laid in rows that run exactly edge to edge, like a photographer's
 * proof sheet: each row is scaled so its pictures fill the width.
 *
 * Used by ContactSheet. Takes each item's shape (width / height) and returns
 * where every item sits, in pixels.
 */

export interface Tile {
  x: number;
  y: number;
  width: number;
  height: number;
}

/** A row may stretch at most this much taller than asked, so a lone wide picture doesn't get huge. */
const MAX_STRETCH = 1.6;

export function justifyRows(shapes: number[], width: number, rowHeight: number, gap: number): { tiles: Tile[]; height: number } {
  const tiles: Tile[] = [];
  let y = 0;
  let row: number[] = [];

  const placeRow = (isLast: boolean) => {
    const shapesWidth = row.reduce((sum, i) => sum + shapes[i] * rowHeight, 0);
    const fill = (width - gap * (row.length - 1)) / shapesWidth;
    const height = rowHeight * (isLast ? Math.min(fill, 1) : Math.min(fill, MAX_STRETCH));
    let x = 0;
    for (const i of row) {
      tiles[i] = { x, y, width: shapes[i] * height, height };
      x += shapes[i] * height + gap;
    }
    y += height + gap;
    row = [];
  };

  shapes.forEach((shape, i) => {
    row.push(i);
    const rowWidth = row.reduce((sum, j) => sum + shapes[j] * rowHeight, 0) + gap * (row.length - 1);
    if (rowWidth >= width) placeRow(false);
  });
  if (row.length > 0) placeRow(true);

  return { tiles, height: Math.max(0, y - gap) };
}
