/**
 * Statistical calculations for ChatGPT Wrapped
 */

import type { Distribution } from "../types";

export function calculateQuantiles(dist: Distribution[]): {
  avg: number;
  q5: number;
  q25: number;
  q75: number;
  q95: number;
  q99: number;
} {
  if (!dist || dist.length === 0) {
    return { avg: 0, q5: 0, q25: 0, q75: 0, q95: 0, q99: 0 };
  }

  // Calculate total count and weighted average
  let totalCount = 0;
  let weightedSum = 0;
  for (const bin of dist) {
    totalCount += bin.count;
    const binMidpoint = (bin.bin_start + bin.bin_end) / 2;
    weightedSum += binMidpoint * bin.count;
  }
  const avg = totalCount > 0 ? weightedSum / totalCount : 0;

  // Helper function to find quantile value with interpolation
  const findQuantile = (targetPercentile: number): number => {
    const targetCount = targetPercentile * totalCount;
    let cumulativeCount = 0;

    for (let i = 0; i < dist.length; i++) {
      const bin = dist[i];
      const prevCumulative = cumulativeCount;
      cumulativeCount += bin.count;

      // Check if the target falls within this bin
      if (cumulativeCount >= targetCount) {
        // Interpolate within the bin
        const positionInBin = (targetCount - prevCumulative) / bin.count;
        const interpolatedValue =
          bin.bin_start + positionInBin * (bin.bin_end - bin.bin_start);
        return interpolatedValue;
      }
    }

    // If we get here, return the last bin's end value
    return dist[dist.length - 1].bin_end;
  };

  return {
    avg: Number(avg.toFixed(1)),
    q5: Number(findQuantile(0.05).toFixed(1)),
    q25: Number(findQuantile(0.25).toFixed(1)),
    q75: Number(findQuantile(0.75).toFixed(1)),
    q95: Number(findQuantile(0.95).toFixed(1)),
    q99: Number(findQuantile(0.99).toFixed(1)),
  };
}

