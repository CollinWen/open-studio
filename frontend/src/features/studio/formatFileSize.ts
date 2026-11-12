/**
 * formatFileSize: a file's size in the words the entry form shows beside an
 * upload ("840 KB", "14.2 MB"), so the owner can see when something is heavy
 * enough to link to instead.
 *
 * Used by MediaListEditor.
 */

const UNITS = ["bytes", "KB", "MB", "GB"];

export function formatFileSize(bytes: number): string {
  let size = bytes;
  let unit = 0;
  while (size >= 1000 && unit < UNITS.length - 1) {
    size /= 1000;
    unit += 1;
  }
  const rounded = unit === 0 || size >= 100 ? Math.round(size) : Math.round(size * 10) / 10;
  return `${rounded} ${UNITS[unit]}`;
}
