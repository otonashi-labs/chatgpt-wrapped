/**
 * Formatting utilities for ChatGPT Wrapped
 */

export function formatNumber(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return n.toLocaleString();
}

export function formatMonth(month: string): string {
  const [year, m] = month.split("-");
  const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  return months[parseInt(m) - 1] || month;
}

export function formatFullMonth(month: string): string {
  const [year, m] = month.split("-");
  const months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
  return `${months[parseInt(m) - 1]} ${year}`;
}

export function generateHeatmapData(daily: { date: string; count: number }[]): string {
  return JSON.stringify(daily.map(d => ({
    date: d.date,
    count: d.count
  })));
}

export function generateMessagesHeatmapData(daily: { date: string; messages: number }[]): string {
  return JSON.stringify(daily.map(d => ({
    date: d.date,
    count: d.messages
  })));
}

export function generateWordsHeatmapData(daily: { date: string; tokens: number }[]): string {
  // Convert tokens to approximate words (1 token ≈ 0.75 words)
  return JSON.stringify(daily.map(d => ({
    date: d.date,
    count: Math.round(d.tokens * 0.75)
  })));
}
