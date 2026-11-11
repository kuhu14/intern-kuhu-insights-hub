import { describe, expect, it } from "vitest";

import { formatInr } from "./formatInr";

describe("formatInr", () => {
  it("formats the acceptance example with Indian grouping", () => {
    expect(formatInr(6098455224 / 100)).toBe("6,09,84,552.24");
  });

  it.each([
    [0, "0.00"],
    [999, "999.00"],
    [1000, "1,000.00"],
    [100000, "1,00,000.00"],
    [12345678.9, "1,23,45,678.90"],
  ])("groups %d as %s", (amount, expected) => {
    expect(formatInr(amount)).toBe(expected);
  });

  it("rounds to 2 decimals, half away from zero", () => {
    expect(formatInr(1.005)).toBe("1.01");
    expect(formatInr(2.345)).toBe("2.35");
    expect(formatInr(-0.001)).toBe("0.00");
    expect(formatInr(1e-7)).toBe("0.00");
  });

  it("keeps the minus sign for negative amounts", () => {
    expect(formatInr(-150000.5)).toBe("-1,50,000.50");
  });

  it("throws on NaN and Infinity", () => {
    expect(() => formatInr(Number.NaN)).toThrow(TypeError);
    expect(() => formatInr(Number.POSITIVE_INFINITY)).toThrow(TypeError);
  });
});
