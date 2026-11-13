/**
 * Media calls: upload an image, video or write-up (.html) file, and read a
 * write-up's HTML back so it can be shown in its frame.
 * A write-up's upload also says what the backend removed to make it safe.
 */

import { backendRequest } from "./backendRequest";

export interface UploadedMedia {
  url: string;
  /** For a write-up: what was taken out (styles, scripts, outside pictures...). */
  removed?: string[];
}

export async function uploadMedia(file: File): Promise<UploadedMedia> {
  const form = new FormData();
  form.append("file", file);
  return backendRequest<UploadedMedia>("/api/media", { method: "POST", body: form });
}

/** A write-up is served as a file from where media lives (R2, or /media locally). */
export async function fetchWriteup(url: string): Promise<string> {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`${response.status}`);
  return response.text();
}
