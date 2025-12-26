/**
 * Horizontal bar chart for top domains and their subdomains
 * Domains and subdomains are shown in separate sections
 */

import type { NameCount, NameCountWithSubs } from "../types";
import { formatNumber } from "../utils/formatters";

/**
 * Generic horizontal bar chart for various metrics
 */
export function generateGenericBars(
  data: NameCount[],
  title: string,
  color: string = "#10a37f",
  showLabelAnnotation: boolean = false,
  annotationOverride?: string,
  countColor?: string
): string {
  if (data.length === 0) return "";

  const maxCount = Math.max(...data.map((d) => d.count));

  const bars = data
    .map((item) => {
      const percentage = (item.count / maxCount) * 100;
      const displayName = item.name.replace(/_/g, " ");
      const countStyle = countColor ? `style="color: ${countColor};"` : "";

      return `
      <div class="bar-row">
        <div class="bar-label">${displayName}</div>
        <div class="bar-track">
          <div class="bar-fill" style="width: ${percentage}%; background: ${color};"></div>
        </div>
        <div class="bar-count" ${countStyle}>${item.count}</div>
      </div>
    `;
    })
    .join("");

  const annotation = annotationOverride 
    ? `<div class="bar-annotation">${annotationOverride}</div>`
    : (showLabelAnnotation ? `<div class="bar-annotation">bold number: amount of conversations</div>` : "");

  return `
    <div class="bars-container">
      <div class="bars-header">
        <span class="bars-dot" style="background: ${color}"></span>
        <span class="bars-title">${title}</span>
      </div>
      <div class="bars-list">
        ${bars}
      </div>
      ${annotation}
    </div>
  `;
}

export function generateDomainBars(domains: NameCountWithSubs[]): string {
  return generateGenericBars(domains.slice(0, 8), "Top Domains", "#10a37f", true);
}

export function generateSubdomainSections(domains: NameCountWithSubs[]): string {
  const domainsWithSubs = domains.filter((d) => d.subdomains && d.subdomains.length > 0).slice(0, 9);

  if (domainsWithSubs.length === 0) return "";

  const sections = domainsWithSubs
    .map((domain) => {
      const displayName = domain.name.replace(/_/g, " ");
      let topSubs: NameCount[];
      
      if (domain.subdomains!.length <= 4) {
        topSubs = domain.subdomains!;
      } else {
        topSubs = domain.subdomains!.slice(0, 4);
        const otherCount = domain.subdomains!.slice(4).reduce((sum, s) => sum + s.count, 0);
        topSubs.push({ name: "other", count: otherCount });
      }

      return generateGenericBars(topSubs, displayName, "#0d8c6d", false);
    })
    .join("");

  return `
    <div class="subdomains-grid">
      ${sections}
    </div>
  `;
}

export function getDomainBarsStyles(): string {
  return `
    /* Domain and Generic Bars */
    .bars-container {
      padding: 16px;
      background: var(--bg-alt);
      border: 1px solid var(--border);
      border-radius: 8px;
      height: 100%;
    }
    
    .bars-header {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 12px;
    }
    
    .bars-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      display: inline-block;
    }
    
    .bars-title {
      font-size: 0.85rem;
      font-weight: 600;
      color: var(--text-secondary);
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }
    
    .bars-list {
      display: flex;
      flex-direction: column;
      gap: 6px;
    }
    
    .bar-row {
      display: grid;
      grid-template-columns: 140px 1fr 50px;
      align-items: center;
      gap: 12px;
      height: 22px;
    }
    
    .bar-label {
      font-size: 0.8rem;
      font-weight: 500;
      color: var(--text);
      text-transform: lowercase;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    
    .bar-track {
      height: 6px;
      background: var(--bg);
      border: 1px solid var(--border);
      border-radius: 3px;
      overflow: hidden;
    }
    
    .bar-fill {
      height: 100%;
      border-radius: 3px;
      transition: width 0.6s ease-out;
    }
    
    .bar-count {
      font-size: 0.9rem;
      font-weight: 700;
      font-family: 'JetBrains Mono', monospace;
      color: var(--text);
      text-align: right;
    }

    .bar-annotation {
      margin-top: 12px;
      font-size: 0.7rem;
      color: var(--text-secondary);
      font-style: italic;
      text-align: right;
    }
    
    .subdomains-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 16px;
      margin-top: 24px;
    }
    
    @media (max-width: 1000px) {
      .subdomains-grid {
        grid-template-columns: repeat(2, 1fr);
      }
    }
    
    @media (max-width: 600px) {
      .subdomains-grid {
        grid-template-columns: 1fr;
      }
      .bar-row {
        grid-template-columns: 80px 1fr 40px;
      }
      .bar-row:has(.bar-words) {
        grid-template-columns: 80px 1fr 40px;
      }
      .bar-words {
        display: none;
      }
    }
  `;
}
