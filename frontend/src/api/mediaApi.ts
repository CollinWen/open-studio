/**
 * Uploads an image or video file and returns the URL it's served from.
 */

import { backendRequest } from "./backendRequest";

export async function uploadMedia(file: File): Promise<string> {
  const form = new FormData();
  form.append("file", file);
  const { url } = await backendRequest<{ url: string }>("/api/media", { method: "POST", body: form });
  return url;
}
