/**
 * Format a number with Indian digit grouping and 2 decimals.
 * The last 3 digits form one group, then every 2 digits after that.
 *
 * @example formatInr(6098455224 / 100) // "6,09,84,552.24"
 */
export function formatInr(amount: number): string {
  if (typeof amount !== "number" || !Number.isFinite(amount)) {
    throw new TypeError(`expected a finite number, got ${String(amount)}`);
  }

  // Round half away from zero on the decimal string, so 1.005 becomes 1.01
  // (plain toFixed would give 1.00 because of float precision).
  const abs = Math.abs(amount);
  const asText = String(abs);
  const rounded = asText.includes("e")
    ? Math.round(abs * 100) / 100 // exponent form (e.g. 1e-7): shift directly
    : Math.round(Number(`${asText}e2`)) / 100;
  const sign = amount < 0 && rounded !== 0 ? "-" : "";
  const [whole, fraction] = rounded.toFixed(2).split(".");

  const tail = whole.slice(-3);
  let head = whole.slice(0, -3);
  const groups: string[] = [];
  while (head.length > 0) {
    groups.unshift(head.slice(-2));
    head = head.slice(0, -2);
  }
  groups.push(tail);

  return `${sign}${groups.join(",")}.${fraction}`;
}
