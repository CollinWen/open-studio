/**
 * downloadText: hands some text to the browser as a file to save (e.g.
 * agents.yaml), without opening a new page.
 *
 * Used by AgentManager.
 */

export function downloadText(fileName: string, text: string): void {
  const address = URL.createObjectURL(new Blob([text], { type: "text/plain" }));
  const link = document.createElement("a");
  link.href = address;
  link.download = fileName;
  link.click();
  URL.revokeObjectURL(address);
}
