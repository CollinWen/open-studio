/**
 * tokenLengths: how long a token can be picked to last, from a quick single
 * task to a harness that keeps working, and the one picked unless you choose.
 * The longest the backend allows is RUN_MINUTES_MAX (90 days, config.py).
 *
 * Used by TokenForm.
 */

const HOUR = 60;
const DAY = 24 * HOUR;

export const TOKEN_LENGTHS = [
  { label: "20 min", minutes: 20 },
  { label: "4 h", minutes: 4 * HOUR },
  { label: "1 day", minutes: DAY },
  { label: "30 days", minutes: 30 * DAY },
  { label: "90 days", minutes: 90 * DAY },
];

export const DEFAULT_TOKEN_LENGTH = TOKEN_LENGTHS[1];
