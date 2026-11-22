/**
 * linkSite: the site a link goes to ("claude.ai"), written beside a link an
 * agent left (a run's session link) so a misleading one shows itself.
 * Anything that isn't a full web address comes back as it is.
 *
 * Used by RunList.
 */

export function linkSite(address: string): string {
  try {
    return new URL(address).host;
  } catch {
    return address;
  }
}
