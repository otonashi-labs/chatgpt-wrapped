/**
 * Chart generation functions for ChatGPT Wrapped
 */

import type { Distribution, NameCount } from "../types";

// Generate SVG-based horizontal distribution curve (Words on Y-axis, Count on X-axis)
export function generateBellCurveSVG(
  dist: Distribution[],
  title: string,
  yLabel: string,
  color: string = "#10a37f"
): string {
  if (!dist || dist.length === 0) return "";

  const width = 400;
  const height = 180;
  const padding = { top: 30, right: 20, bottom: 30, left: 60 };
  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;

  // Find where 99% of data lies for the y-axis range (words)
  const totalCount = dist.reduce((sum, d) => sum + d.count, 0);
  let cumulative = 0;
  let cutoffIndex = dist.length - 1;
  for (let i = 0; i < dist.length; i++) {
    cumulative += dist[i].count;
    if (cumulative >= totalCount * 0.99) {
      cutoffIndex = Math.min(i + 1, dist.length - 1);
      break;
    }
  }

  // Use focused distribution
  const focusedDist = dist.slice(0, cutoffIndex + 1);
  const maxCount = Math.max(...focusedDist.map((d) => d.count));
  const maxValue = focusedDist[focusedDist.length - 1].bin_end;
  const minValue = focusedDist[0].bin_start;

  // Create smooth points - Y axis is words (top = high words), X axis is count
  const screenPoints: { x: number; y: number; value: number; count: number }[] = [];
  const numInterpolatedPoints = 40;

  for (let i = 0; i <= numInterpolatedPoints; i++) {
    const t = i / numInterpolatedPoints;
    const binFloatIndex = t * (focusedDist.length - 1);
    const binIndex = Math.floor(binFloatIndex);
    const binFrac = binFloatIndex - binIndex;

    const currBin = focusedDist[binIndex];
    const nextBin = focusedDist[Math.min(binIndex + 1, focusedDist.length - 1)];

    // Smoothstep interpolation
    const smoothT = binFrac * binFrac * (3 - 2 * binFrac);
    const interpolatedCount = currBin.count * (1 - smoothT) + nextBin.count * smoothT;

    // Calculate value (words)
    const binWidth = currBin.bin_end - currBin.bin_start;
    const wordValue = currBin.bin_start + binFrac * binWidth;

    // X position = count (0 at left, max at right)
    const xPos =
      padding.left + (maxCount > 0 ? (interpolatedCount / maxCount) * chartWidth : 0);
    // Y position = words (low words at bottom, high at top)
    const yPos = padding.top + chartHeight - t * chartHeight;

    screenPoints.push({ x: xPos, y: yPos, value: wordValue, count: interpolatedCount });
  }

  // Create smooth curve path
  let curvePath = "";
  if (screenPoints.length > 0) {
    curvePath = "M " + screenPoints[0].x + " " + screenPoints[0].y;
    for (let i = 1; i < screenPoints.length; i++) {
      const prev = screenPoints[i - 1];
      const curr = screenPoints[i];
      const cpy1 = prev.y + (curr.y - prev.y) / 3;
      const cpy2 = prev.y + (2 * (curr.y - prev.y)) / 3;
      curvePath +=
        " C " + prev.x + " " + cpy1 + ", " + curr.x + " " + cpy2 + ", " + curr.x + " " + curr.y;
    }
  }

  // Create filled area path (fill to left edge)
  const areaPath =
    curvePath +
    " L " +
    padding.left +
    " " +
    screenPoints[screenPoints.length - 1]?.y +
    " L " +
    padding.left +
    " " +
    screenPoints[0]?.y +
    " Z";

  // Y-axis labels (words - show at bottom, middle, top)
  const yLabelData = [
    { y: padding.top + chartHeight, value: minValue },
    { y: padding.top + chartHeight / 2, value: (minValue + maxValue) / 2 },
    { y: padding.top, value: maxValue },
  ];
  const yLabels = yLabelData
    .map(
      (d) =>
        '<text x="' +
        (padding.left - 5) +
        '" y="' +
        (d.y + 3) +
        '" text-anchor="end" font-size="10" fill="#666">' +
        Math.round(d.value) +
        "</text>"
    )
    .join("");

  // X-axis labels (count)
  const xLabelData = [
    { x: padding.left, value: 0 },
    { x: padding.left + chartWidth / 2, value: Math.round(maxCount / 2) },
    { x: padding.left + chartWidth, value: Math.round(maxCount) },
  ];
  const xLabels = xLabelData
    .map(
      (d) =>
        '<text x="' +
        d.x +
        '" y="' +
        (height - 8) +
        '" text-anchor="middle" font-size="10" fill="#666">' +
        d.value +
        "</text>"
    )
    .join("");

  // Vertical grid lines
  const gridLines = [0.25, 0.5, 0.75]
    .map((pct) => {
      const x = padding.left + chartWidth * pct;
      return (
        '<line x1="' +
        x +
        '" y1="' +
        padding.top +
        '" x2="' +
        x +
        '" y2="' +
        (padding.top + chartHeight) +
        '" stroke="#eee" stroke-width="1" stroke-dasharray="4,2"/>'
      );
    })
    .join("");

  return `
    <div class="histogram-container">
      <div class="histogram-title">${title}</div>
      <svg viewBox="0 0 ${width} ${height}" class="histogram-svg">
        <!-- Grid lines -->
        <line x1="${padding.left}" y1="${padding.top}" x2="${padding.left}" y2="${padding.top + chartHeight}" stroke="#ddd" stroke-width="1"/>
        <line x1="${padding.left}" y1="${padding.top + chartHeight}" x2="${width - padding.right}" y2="${padding.top + chartHeight}" stroke="#ddd" stroke-width="1"/>
        ${gridLines}
        <!-- Filled area -->
        <path d="${areaPath}" fill="${color}" opacity="0.15"/>
        <!-- Curve line -->
        <path d="${curvePath}" fill="none" stroke="${color}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
        ${xLabels}
        ${yLabels}
        <text x="${width / 2}" y="${height - 2}" text-anchor="middle" font-size="11" fill="#888">Count</text>
        <text x="12" y="${height / 2}" text-anchor="middle" font-size="11" fill="#888" transform="rotate(-90 12 ${height / 2})">${yLabel}</text>
      </svg>
    </div>
  `;
}

// Generate bar chart for hourly/weekday with hover tooltips
export function generateBarChartSVG(
  data: { label: string; value: number; messages?: number }[],
  title: string,
  color: string = "#000",
  chartId: string = "chart"
): string {
  const maxVal = Math.max(...data.map((d) => d.value));
  const width = 500;
  const height = 180;
  const padding = { top: 30, right: 20, bottom: 50, left: 50 };
  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;
  const barWidth = chartWidth / data.length - 2;

  const bars = data
    .map((d, i) => {
      const barHeight = maxVal > 0 ? (d.value / maxVal) * chartHeight : 0;
      const x = padding.left + i * (chartWidth / data.length) + 1;
      const y = padding.top + chartHeight - barHeight;
      const messages = d.messages || Math.round(d.value);
      return `<rect x="${x}" y="${y}" width="${barWidth}" height="${barHeight}" fill="${color}" opacity="0.7" class="bar-hover" data-label="${d.label}" data-messages="${messages}"/>`;
    })
    .join("");

  const labels = data
    .map((d, i) => {
      const x = padding.left + i * (chartWidth / data.length) + barWidth / 2 + 1;
      return `<text x="${x}" y="${height - 15}" text-anchor="middle" font-size="9" fill="#666">${d.label}</text>`;
    })
    .join("");

  return `
    <div class="chart-wrapper" id="${chartId}">
      <div class="chart-title">${title}</div>
      <svg viewBox="0 0 ${width} ${height}" class="bar-chart-svg">
        <line x1="${padding.left}" y1="${padding.top + chartHeight}" x2="${width - padding.right}" y2="${padding.top + chartHeight}" stroke="#ccc" stroke-width="1"/>
        ${bars}
        ${labels}
      </svg>
    </div>
  `;
}

// Pie chart color palette - harmonious teal/green tones
const PIE_COLORS = [
  "#10a37f", // Primary teal
  "#0d8c6d", // Darker teal
  "#75e0c3", // Light teal
  "#4fcca8", // Medium teal
  "#2bb390", // Deep teal
  "#1a9176", // Forest teal
  "#c4f4e6", // Very light teal
  "#a8e6d3", // Pale teal
  "#5cd4b1", // Bright teal
  "#087d63", // Dark green teal
];

// Generate visual quantile line representation
export function generateQuantileViz(
  q: { avg: number; q5: number; q25: number; q75: number; q95: number; q99: number },
  title: string,
  options: { 
    description?: string, 
    trend?: { month: string, average: number }[],
    color?: string 
  } = {}
): string {
  const max = Math.max(q.q99, 1);
  const getPos = (val: number) => Math.min(100, (val / max) * 100);
  const color = options.color || "#10a37f";

  const points = [
    { label: "q5", val: q.q5, pos: getPos(q.q5) },
    { label: "q25", val: q.q25, pos: getPos(q.q25) },
    { label: "avg", val: q.avg, pos: getPos(q.avg), isMain: true },
    { label: "q75", val: q.q75, pos: getPos(q.q75) },
    { label: "q95", val: q.q95, pos: getPos(q.q95) },
    { label: "q99", val: q.q99, pos: getPos(q.q99) },
  ];

  const trendHtml = options.trend && options.trend.length > 0 
    ? `
      <div class="quantile-trend-container">
        <div class="trend-label">Monthly Trend</div>
        <div class="trend-chart-line">
          ${(() => {
            const trendData = options.trend;
            const width = 350;
            const height = 40;
            const pad = 5;
            const maxVal = Math.max(...trendData.map(t => t.average), 1);
            const minVal = Math.min(...trendData.map(t => t.average));
            const range = maxVal - minVal || 1;
            
            const points = trendData.length > 1 
              ? trendData.map((t, i) => {
                  const x = pad + (i / (trendData.length - 1)) * (width - 2 * pad);
                  const y = pad + (1 - (t.average - minVal) / range) * (height - 2 * pad);
                  return `${x},${y}`;
                }).join(" ")
              : `${width/2},${height/2}`;

            return `
              <svg viewBox="0 0 ${width} ${height}" preserveAspectRatio="none" style="width: 100%; height: 40px; display: block;">
                ${trendData.length > 1 ? `
                <polyline
                  fill="none"
                  stroke="${color}"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  points="${points}"
                  style="opacity: 0.8"
                />` : ""}
                ${trendData.map((t, i) => {
                  const x = trendData.length > 1 
                    ? pad + (i / (trendData.length - 1)) * (width - 2 * pad)
                    : width / 2;
                  const y = trendData.length > 1
                    ? pad + (1 - (t.average - minVal) / range) * (height - 2 * pad)
                    : height / 2;
                  return `
                    <circle cx="${x}" cy="${y}" r="2.5" fill="${color}" class="trend-marker" data-month="${t.month}" data-value="${t.average}" style="opacity: 1" />
                    <circle cx="${x}" cy="${y}" r="10" fill="transparent" class="trend-hover-area" data-month="${t.month}" data-value="${t.average}" />
                  `;
                }).join("")}
              </svg>
            `;
          })()}
        </div>
      </div>
    ` 
    : "";

  const descHtml = options.description 
    ? `<div class="quantile-desc">${options.description}</div>` 
    : "";

  return `
    <div class="quantile-card-new">
      <div class="quantile-card-header">
        <div class="quantile-card-title">${title}</div>
        ${descHtml}
      </div>
      
      <div class="quantile-line-container">
        <div class="quantile-line-base"></div>
        <div class="quantile-line-range" style="left: ${getPos(q.q25)}%; width: ${getPos(q.q75) - getPos(q.q25)}%; background: ${color}"></div>
        <div class="quantile-dot main" style="left: ${getPos(q.avg)}%; background: ${color}"></div>
      </div>

      <div class="quantile-table">
        ${points
          .map(
            (p) => `
          <div class="quantile-col ${p.isMain ? "main" : ""}">
            <div class="q-label" style="${p.isMain ? `color: ${color}` : "" }">${p.label}</div>
            <div class="q-val" style="${p.isMain ? `color: ${color}` : "" }">${p.val}</div>
          </div>
        `
          )
          .join("")}
      </div>

      ${trendHtml}
    </div>
  `;
}

export function getQuantileStyles(): string {
  return `
    .quantile-card-new {
      background: var(--bg-alt);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 24px;
      margin-bottom: 24px;
      display: flex;
      flex-direction: column;
    }
    
    .quantile-card-header {
      margin-bottom: 24px;
    }

    .quantile-card-title {
      font-size: 1rem;
      font-weight: 600;
      color: var(--text);
      margin-bottom: 4px;
      text-align: center;
    }

    .quantile-desc {
      font-size: 0.75rem;
      color: var(--text-secondary);
      line-height: 1.4;
      text-align: center;
    }
    
    .quantile-line-container {
      position: relative;
      height: 4px;
      margin: 12px 0 32px;
      background: var(--border);
      border-radius: 2px;
    }
    
    .quantile-line-range {
      position: absolute;
      top: 0;
      height: 100%;
      opacity: 0.3;
      border-radius: 2px;
    }
    
    .quantile-dot {
      position: absolute;
      top: 50%;
      width: 12px;
      height: 12px;
      border: 2px solid var(--bg);
      border-radius: 50%;
      transform: translate(-50%, -50%);
      z-index: 2;
    }
    
    .quantile-table {
      display: flex;
      justify-content: space-between;
      gap: 12px;
    }
    
    .quantile-col {
      display: flex;
      flex-direction: column;
      align-items: center;
      flex: 1;
    }
    
    .quantile-col.main .q-label {
      font-weight: 600;
    }
    
    .quantile-col.main .q-val {
      font-weight: 700;
      font-size: 1.1rem;
    }
    
    .q-label {
      font-size: 0.7rem;
      color: var(--text-secondary);
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 4px;
    }
    
    .q-val {
      font-size: 0.95rem;
      font-weight: 600;
      font-family: 'JetBrains Mono', monospace;
      color: var(--text);
    }

    .quantile-trend-container {
      margin-top: 24px;
      padding-top: 16px;
      border-top: 1px solid var(--border);
    }

    .trend-label {
      font-size: 0.7rem;
      text-transform: uppercase;
      color: var(--text-secondary);
      letter-spacing: 0.5px;
      margin-bottom: 8px;
    }

    .quantile-trend-container .mini-chart {
      display: flex;
      align-items: flex-end;
      gap: 3px;
      height: 30px;
    }
    
    .quantile-trend-container .mini-bar {
      flex: 1;
      opacity: 0.6;
      border-radius: 1px;
      min-height: 2px;
    }

    .trend-hover-area {
      cursor: pointer;
    }

    .trend-marker {
      transition: r 0.15s;
    }

    .trend-hover-area:hover + .trend-marker,
    .trend-marker:hover {
      r: 4;
    }
  `;
}

// Generate compact pie chart SVG for category data
export function generatePieChartSVG(
  data: NameCount[],
  title: string,
  chartId: string = "pie-chart"
): string {
  if (!data || data.length === 0) return "";

  const size = 140;
  const radius = 50;
  const centerX = size / 2;
  const centerY = size / 2;

  const total = data.reduce((sum, d) => sum + d.count, 0);
  let currentAngle = -Math.PI / 2; // Start from top

  const slices = data.map((item, index) => {
    const sliceAngle = (item.count / total) * 2 * Math.PI;
    const startX = centerX + radius * Math.cos(currentAngle);
    const startY = centerY + radius * Math.sin(currentAngle);
    const endX = centerX + radius * Math.cos(currentAngle + sliceAngle);
    const endY = centerY + radius * Math.sin(currentAngle + sliceAngle);
    const largeArc = sliceAngle > Math.PI ? 1 : 0;
    
    const path = `M ${centerX} ${centerY} L ${startX} ${startY} A ${radius} ${radius} 0 ${largeArc} 1 ${endX} ${endY} Z`;
    
    currentAngle += sliceAngle;
    
    return {
      path,
      color: PIE_COLORS[index % PIE_COLORS.length],
      name: item.name.replace(/_/g, " "),
      count: item.count,
      percentage: ((item.count / total) * 100).toFixed(1)
    };
  });

  const slicesSvg = slices.map((slice, i) => `
    <path 
      d="${slice.path}" 
      fill="${slice.color}" 
      stroke="var(--bg)" 
      stroke-width="1.5"
      class="pie-slice"
      data-name="${slice.name}"
      data-count="${slice.count}"
      data-percentage="${slice.percentage}"
    />`).join("");

  // Compact legend - 2 columns
  const legendItems = slices.slice(0, 6).map((slice, i) => `
    <div class="pie-legend-item">
      <span class="pie-legend-color" style="background: ${slice.color};"></span>
      <span class="pie-legend-label">${slice.name}</span>
      <span class="pie-legend-value">${slice.count}</span>
    </div>
  `).join("");

  return `
    <div class="pie-chart-wrapper" id="${chartId}">
      <div class="pie-chart-title">${title}</div>
      <div class="pie-chart-content">
        <svg viewBox="0 0 ${size} ${size}" class="pie-chart-svg">
          ${slicesSvg}
        </svg>
        <div class="pie-legend">
          ${legendItems}
        </div>
      </div>
    </div>
  `;
}

// Styles for pie charts
export function getPieChartStyles(): string {
  return `
    .pie-chart-wrapper {
      background: var(--bg-alt);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 16px;
      flex: 1;
      min-width: 0;
    }
    
    .pie-chart-title {
      font-size: 0.8rem;
      font-weight: 500;
      margin-bottom: 12px;
      color: var(--text-secondary);
      text-align: center;
    }
    
    .pie-chart-content {
      display: flex;
      align-items: center;
      gap: 16px;
    }
    
    .pie-chart-svg {
      width: 100px;
      height: 100px;
      flex-shrink: 0;
    }
    
    .pie-slice {
      cursor: pointer;
      transition: opacity 0.15s, transform 0.15s;
      transform-origin: center;
    }
    
    .pie-slice:hover {
      opacity: 0.85;
    }
    
    .pie-legend {
      display: flex;
      flex-direction: column;
      gap: 4px;
      flex: 1;
      min-width: 0;
    }
    
    .pie-legend-item {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 0.75rem;
    }
    
    .pie-legend-color {
      width: 8px;
      height: 8px;
      border-radius: 2px;
      flex-shrink: 0;
    }
    
    .pie-legend-label {
      color: var(--text-secondary);
      text-transform: lowercase;
      flex: 1;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    
    .pie-legend-value {
      font-family: 'JetBrains Mono', monospace;
      font-weight: 500;
      color: var(--text);
      font-size: 0.7rem;
    }
  `;
}

