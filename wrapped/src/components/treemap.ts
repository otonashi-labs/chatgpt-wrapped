/**
 * Treemap visualization for domains and subdomains
 * Creates a hierarchical rectangular treemap with proper sizing and nesting
 */

import type { NameCountWithSubs } from "../types";

interface TreemapRect {
  x: number;
  y: number;
  width: number;
  height: number;
  name: string;
  count: number;
  percentage: number;
  color: string;
  children?: TreemapRect[];
}

// OpenAI brand color palette for treemap
const COLORS = [
  "#10a37f", // Primary teal
  "#0d8c6d", // Darker teal
  "#75e0c3", // Light teal
  "#4fcca8", // Medium teal
  "#2bb390", // Deep teal
  "#1a9176", // Forest teal
  "#c4f4e6", // Very light teal
  "#a8e6d3", // Pale teal
  "#7dd9c0", // Soft teal
  "#5cd4b1", // Bright teal
];

function getColor(index: number): string {
  return COLORS[index % COLORS.length];
}

/**
 * Squarify algorithm for treemap layout
 * Creates more square-like rectangles for better readability
 */
function squarify(
  items: { name: string; count: number; percentage: number; subdomains?: NameCountWithSubs["subdomains"] }[],
  x: number,
  y: number,
  width: number,
  height: number,
  colorOffset: number = 0
): TreemapRect[] {
  if (items.length === 0) return [];

  const totalValue = items.reduce((sum, item) => sum + item.count, 0);
  const rects: TreemapRect[] = [];

  let currentX = x;
  let currentY = y;
  let remainingWidth = width;
  let remainingHeight = height;

  items.forEach((item, index) => {
    const ratio = item.count / totalValue;
    let rectWidth: number;
    let rectHeight: number;

    // Alternate between horizontal and vertical splits for more balanced layout
    if (remainingWidth > remainingHeight) {
      // Horizontal split
      rectWidth = remainingWidth * ratio;
      rectHeight = remainingHeight;
      
      rects.push({
        x: currentX,
        y: currentY,
        width: rectWidth,
        height: rectHeight,
        name: item.name,
        count: item.count,
        percentage: item.percentage || 0,
        color: getColor(colorOffset + index),
        children: item.subdomains && item.subdomains.length > 0 
          ? layoutSubdomains(item.subdomains, currentX, currentY, rectWidth, rectHeight, colorOffset + index)
          : undefined
      });

      currentX += rectWidth;
      remainingWidth -= rectWidth;
    } else {
      // Vertical split
      rectWidth = remainingWidth;
      rectHeight = remainingHeight * ratio;

      rects.push({
        x: currentX,
        y: currentY,
        width: rectWidth,
        height: rectHeight,
        name: item.name,
        count: item.count,
        percentage: item.percentage || 0,
        color: getColor(colorOffset + index),
        children: item.subdomains && item.subdomains.length > 0
          ? layoutSubdomains(item.subdomains, currentX, currentY, rectWidth, rectHeight, colorOffset + index)
          : undefined
      });

      currentY += rectHeight;
      remainingHeight -= rectHeight;
    }
  });

  return rects;
}

/**
 * Layout subdomains within a parent rectangle
 * Uses padding to create visual hierarchy
 */
function layoutSubdomains(
  subdomains: NameCountWithSubs["subdomains"],
  parentX: number,
  parentY: number,
  parentWidth: number,
  parentHeight: number,
  colorOffset: number
): TreemapRect[] {
  if (!subdomains || subdomains.length === 0) return [];

  // Add padding to show hierarchy
  const padding = 4;
  const innerX = parentX + padding;
  const innerY = parentY + padding;
  const innerWidth = Math.max(0, parentWidth - padding * 2);
  const innerHeight = Math.max(0, parentHeight - padding * 2);

  // Only show subdomains if there's enough space
  if (innerWidth < 60 || innerHeight < 40) return [];

  const totalSubCount = subdomains.reduce((sum, sub) => sum + sub.count, 0);
  
  return squarify(
    subdomains.map(sub => ({
      name: sub.name,
      count: sub.count,
      percentage: (sub.count / totalSubCount) * 100
    })),
    innerX,
    innerY,
    innerWidth,
    innerHeight,
    colorOffset + 10 // Offset color for subdomains
  );
}

/**
 * Generate SVG treemap visualization
 */
export function generateTreemap(domains: NameCountWithSubs[]): string {
  const width = 900;
  const height = 500;
  const topDomains = domains.slice(0, 10); // Show top 10 domains

  const rects = squarify(topDomains, 0, 0, width, height);

  function renderRect(rect: TreemapRect, isChild: boolean = false): string {
    const minWidth = 80;
    const minHeight = 50;
    const showLabel = rect.width >= minWidth && rect.height >= minHeight;
    const showPercentage = rect.width >= 100 && rect.height >= 60;

    // Calculate text properties
    const fontSize = isChild ? 11 : 13;
    const textX = rect.x + rect.width / 2;
    const textY = rect.y + rect.height / 2;
    const displayName = rect.name.replace(/_/g, " ");
    
    // Truncate long names
    const maxChars = Math.floor(rect.width / (fontSize * 0.6));
    const truncatedName = displayName.length > maxChars 
      ? displayName.substring(0, maxChars - 3) + "..."
      : displayName;

    let svg = `
      <g class="treemap-cell" data-name="${rect.name}" data-count="${rect.count}">
        <rect 
          x="${rect.x}" 
          y="${rect.y}" 
          width="${rect.width}" 
          height="${rect.height}" 
          fill="${rect.color}" 
          opacity="${isChild ? '0.7' : '0.85'}"
          stroke="var(--bg)" 
          stroke-width="${isChild ? '1' : '2'}"
          rx="4"
          class="treemap-rect"
        />`;

    if (showLabel) {
      svg += `
        <text 
          x="${textX}" 
          y="${textY - 5}" 
          text-anchor="middle" 
          font-size="${fontSize}" 
          font-weight="${isChild ? '500' : '600'}"
          fill="${isChild ? 'var(--text)' : '#ffffff'}"
          class="treemap-label"
        >${truncatedName}</text>`;

      if (showPercentage) {
        svg += `
          <text 
            x="${textX}" 
            y="${textY + 12}" 
            text-anchor="middle" 
            font-size="${fontSize - 2}" 
            font-weight="400"
            fill="${isChild ? 'var(--text-secondary)' : '#ffffff'}"
            opacity="0.9"
            class="treemap-count"
          >${rect.count} (${rect.percentage.toFixed(1)}%)</text>`;
      }
    }

    svg += `</g>`;

    // Render children (subdomains)
    if (rect.children && rect.children.length > 0) {
      svg += rect.children.map(child => renderRect(child, true)).join("");
    }

    return svg;
  }

  const treemapSvg = `
    <div class="treemap-container">
      <svg viewBox="0 0 ${width} ${height}" class="treemap-svg">
        <defs>
          <filter id="treemap-shadow">
            <feDropShadow dx="0" dy="2" stdDeviation="3" flood-opacity="0.1"/>
          </filter>
        </defs>
        ${rects.map(rect => renderRect(rect)).join("")}
      </svg>
    </div>
  `;

  return treemapSvg;
}

/**
 * Generate treemap CSS styles
 */
export function getTreemapStyles(): string {
  return `
    /* Treemap */
    .treemap-container {
      margin: 32px 0;
      padding: 24px;
      background: var(--bg-alt);
      border: 1px solid var(--border);
      border-radius: 8px;
    }
    
    .treemap-svg {
      width: 100%;
      height: auto;
      display: block;
    }
    
    .treemap-cell {
      cursor: pointer;
      transition: opacity 0.2s;
    }
    
    .treemap-cell:hover {
      opacity: 0.9;
    }
    
    .treemap-rect {
      transition: stroke-width 0.2s;
    }
    
    .treemap-cell:hover .treemap-rect {
      stroke-width: 3;
    }
    
    .treemap-label {
      pointer-events: none;
      text-transform: capitalize;
    }
    
    .treemap-count {
      pointer-events: none;
      font-family: 'JetBrains Mono', monospace;
    }
  `;
}


