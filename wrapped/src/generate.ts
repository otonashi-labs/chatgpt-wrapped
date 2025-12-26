/**
 * ChatGPT Wrapped 2025 - HTML Generator
 * Clean, scientific research-style design following OpenAI brand guidelines
 */

import { readFile, writeFile } from "fs/promises";
import { join } from "path";
import type { WrappedStats } from "./types";
import { formatNumber, generateHeatmapData, generateMessagesHeatmapData } from "./utils/formatters";
import {
  generateOverviewSection,
  generateDistributionSection,
  generateTemporalSection,
  generateDomainsSection,
  generateEntitiesSection,
  generateEntitiesSection,
  generateQualitySection,
  generateSerendipitySection,
  generateTopEntitiesSection,
  generateDynamicsSection,
  generatePolitenessSection,
  generateModelsSection,
  generateTopConversationsSection,
} from "./components/sections";
import { getDomainBarsStyles } from "./components/domainBars";
import { getPieChartStyles, getQuantileStyles } from "./components/charts";

const STATS_FILE = join(import.meta.dir, "../../data/stats/stats.json");
const OUTPUT_FILE = join(import.meta.dir, "../wrapped.html");

function getStyles(): string {
  return `
    :root {
      --bg: #ffffff;
      --bg-alt: #f8f9fa;
      --text: #1a1a1a;
      --text-secondary: #6b7280;
      --border: #e5e7eb;
      --accent: #000000;
      --accent-light: #374151;
    }
    
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }
    
    body {
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.6;
      font-size: 15px;
    }
    
    .container {
      max-width: 900px;
      margin: 0 auto;
      padding: 0 24px;
    }
    
    /* Header */
    header {
      padding: 60px 0 40px;
      border-bottom: 1px solid var(--border);
      text-align: center;
    }
    
    header h1 {
      font-size: 2rem;
      font-weight: 600;
      margin-bottom: 8px;
      letter-spacing: -0.5px;
    }
    
    header .subtitle {
      color: var(--text-secondary);
      font-size: 1rem;
    }
    
    header .meta {
      margin-top: 16px;
      font-size: 0.85rem;
      color: var(--text-secondary);
    }
    
    /* Sections */
    section {
      padding: 48px 0;
      border-bottom: 1px solid var(--border);
    }
    
    section:last-child {
      border-bottom: none;
    }
    
    h2 {
      font-size: 1.25rem;
      font-weight: 600;
      margin-bottom: 24px;
      letter-spacing: -0.3px;
      text-align: center;
    }
    
    h3 {
      font-size: 1rem;
      font-weight: 500;
      margin-bottom: 16px;
      color: var(--text-secondary);
    }
    
    .heatmap-scale-note {
      font-size: 0.75rem;
      font-weight: 400;
      color: var(--text-secondary);
      font-style: italic;
      margin-left: 8px;
    }
    
    /* Stats Grid */
    .stats-row {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 24px;
      margin-bottom: 32px;
    }
    
    .stat-item {
      padding: 20px;
      background: var(--bg-alt);
      border: 1px solid var(--border);
      border-radius: 8px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      text-align: center;
      min-height: 100px;
    }
    
    .stat-item .label {
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: var(--text-secondary);
      margin-bottom: 6px;
    }
    
    .stat-item .value {
      font-size: 1.75rem;
      font-weight: 600;
      font-family: 'JetBrains Mono', monospace;
    }
    
    .stat-item .unit {
      font-size: 0.9rem;
      font-weight: 400;
      color: var(--text-secondary);
      margin-left: 4px;
    }
    
    .stat-item .detail {
      font-size: 0.8rem;
      color: var(--text-secondary);
      margin-top: 4px;
    }

    .centered-caption {
      text-align: center;
      margin-bottom: 24px !important;
    }
    
    /* Heatmap */
    .heatmap-section {
      margin: 32px 0;
    }
    
    .heatmap-months {
      display: flex;
      margin-bottom: 8px;
      padding-left: 0;
    }
    
    .heatmap-months span {
      flex: 1;
      font-size: 0.7rem;
      color: var(--text-secondary);
      text-align: center;
    }
    
    .heatmap-wrapper {
      position: relative;
    }
    
    .heatmap {
      display: grid;
      grid-template-rows: repeat(7, 1fr);
      grid-auto-flow: column;
      grid-auto-columns: 1fr;
      gap: 2px;
    }
    
    .heatmap-weekdays {
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      padding: 2px 0;
      margin-right: 4px;
      font-size: 0.65rem;
      color: var(--text-secondary);
    }
    
    .heatmap-weekdays span {
      height: calc(100% / 7);
      display: flex;
      align-items: center;
    }
    
    .heatmap-row {
      display: flex;
      align-items: center;
    }
    
    .heatmap-container {
      display: flex;
    }
    
    .heatmap-cell {
      aspect-ratio: 1;
      background: #ebedf0;
      border-radius: 2px;
      cursor: pointer;
      transition: transform 0.15s;
    }
    
    .heatmap-cell:hover {
      transform: scale(1.8);
      z-index: 10;
      position: relative;
    }
    
    /* GitHub-style Heatmap Colors */
    .gh-level-0 { background: #ebedf0 !important; }
    .gh-level-1 { background: #9be9a8 !important; }
    .gh-level-2 { background: #40c463 !important; }
    .gh-level-3 { background: #30a14e !important; }
    .gh-level-4 { background: #216e39 !important; }

    /* GitHub-style Messages (Extended) */
    .gh-msg-level-1 { background: #9be9a8 !important; }
    .gh-msg-level-2 { background: #6fd486 !important; }
    .gh-msg-level-3 { background: #40c463 !important; }
    .gh-msg-level-4 { background: #38b258 !important; }
    .gh-msg-level-5 { background: #30a14e !important; }
    .gh-msg-level-6 { background: #288843 !important; }
    .gh-msg-level-7 { background: #216e39 !important; }
    .gh-msg-level-8 { background: #19522c !important; }
    .gh-msg-level-9 { background: #000000 !important; }
    
    .heatmap-legend {
      display: flex;
      align-items: center;
      justify-content: flex-end;
      gap: 4px;
      margin-top: 8px;
      font-size: 0.7rem;
      color: var(--text-secondary);
    }
    
    .heatmap-legend .cell {
      width: 10px;
      height: 10px;
      border-radius: 2px;
    }
    
    .tooltip {
      position: fixed;
      background: var(--text);
      color: var(--bg);
      padding: 6px 10px;
      border-radius: 4px;
      font-size: 0.75rem;
      pointer-events: none;
      z-index: 1000;
      display: none;
      white-space: nowrap;
    }
    
    /* Charts */
    .charts-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 24px;
      margin: 24px 0;
    }
    
    .charts-vertical {
      display: flex;
      flex-direction: column;
      gap: 24px;
      margin: 24px 0;
    }
    
    @media (max-width: 700px) {
      .charts-grid {
        grid-template-columns: 1fr;
      }
    }
    
    .chart-wrapper {
      background: var(--bg-alt);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 16px;
    }
    
    .chart-title {
      font-size: 0.8rem;
      font-weight: 500;
      margin-bottom: 12px;
      color: var(--text-secondary);
    }
    
    .bar-chart-svg, .histogram-svg {
      width: 100%;
      height: auto;
    }
    
    .bar-hover {
      cursor: pointer;
      transition: opacity 0.15s;
    }
    
    .bar-hover:hover {
      opacity: 1 !important;
    }
    
    /* Histograms */
    .histograms-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 20px;
      margin: 24px 0;
    }
    
    @media (max-width: 700px) {
      .histograms-grid {
        grid-template-columns: 1fr;
      }
    }
    
    .histogram-container {
      background: var(--bg-alt);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 16px;
    }
    
    /* Quantile Cards */
    .quantiles-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 24px;
      margin: 24px 0;
    }
    
    @media (max-width: 700px) {
      .quantiles-grid {
        grid-template-columns: 1fr;
      }
    }
    
    .quantile-card {
      background: var(--bg-alt);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 20px;
    }
    
    .quantile-card h3 {
      font-size: 1rem;
      font-weight: 600;
      margin: 0 0 16px 0;
      color: var(--text);
    }
    
    .quantile-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 8px 0;
      border-bottom: 1px solid var(--border);
    }
    
    .quantile-row:last-child {
      border-bottom: none;
    }
    
    .quantile-row.main {
      padding: 12px 0 16px 0;
      margin-bottom: 8px;
      border-bottom: 2px solid #10a37f;
    }
    
    .quantile-row.main .quantile-label {
      font-size: 0.95rem;
      font-weight: 600;
      color: var(--text);
    }
    
    .quantile-row.main .quantile-value {
      font-size: 1.5rem;
      font-weight: 700;
      font-family: 'JetBrains Mono', monospace;
      color: #10a37f;
    }
    
    .quantile-label {
      font-size: 0.85rem;
      color: var(--text-secondary);
    }
    
    .quantile-value {
      font-size: 1.1rem;
      font-weight: 600;
      font-family: 'JetBrains Mono', monospace;
      color: var(--text);
    }
    
    .histogram-title {
      font-size: 0.8rem;
      font-weight: 500;
      margin-bottom: 12px;
      color: var(--text-secondary);
    }
    
    /* Quantiles Grid */
    .quantiles-grid-2col {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 16px;
      margin: 24px 0;
    }
    
    @media (max-width: 800px) {
      .quantiles-grid-2col {
        grid-template-columns: 1fr;
      }
    }
    
    /* Tags */
    .tags {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin: 12px 0;
    }
    
    .tag {
      font-size: 0.75rem;
      padding: 4px 10px;
      background: var(--bg-alt);
      border: 1px solid var(--border);
      border-radius: 4px;
      font-family: 'JetBrains Mono', monospace;
    }

    .month-card .tags {
      margin: 4px 0 0 0;
      gap: 4px;
    }

    .month-card .tag {
      font-size: 0.7rem;
      padding: 2px 6px;
    }
    
    /* Table */
    .data-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.85rem;
      margin: 16px 0;
    }
    
    .data-table th,
    .data-table td {
      padding: 10px 12px;
      text-align: left;
      border-bottom: 1px solid var(--border);
    }
    
    .data-table th {
      font-weight: 500;
      color: var(--text-secondary);
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }
    
    .data-table tbody tr:hover {
      background: var(--bg-alt);
    }
    
    /* Score Cards */
    .scores-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 16px;
    }
    
    .score-card {
      padding: 16px;
      background: var(--bg-alt);
      border: 1px solid var(--border);
      border-radius: 8px;
    }
    
    .score-card .header {
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      margin-bottom: 8px;
    }
    
    .score-card .name {
      font-size: 0.8rem;
      font-weight: 500;
      text-transform: capitalize;
    }
    
    .score-card .value {
      font-size: 1.5rem;
      font-weight: 600;
      font-family: 'JetBrains Mono', monospace;
    }
    
    .score-card .desc {
      font-size: 0.75rem;
      color: var(--text-secondary);
      margin-bottom: 12px;
    }
    
    .score-card .mini-chart {
      display: flex;
      align-items: flex-end;
      gap: 2px;
      height: 40px;
    }
    
    .score-card .mini-bar {
      flex: 1;
      background: var(--accent);
      opacity: 0.6;
      border-radius: 1px;
      min-height: 2px;
    }
    
    /* Serendipity */
    .serendipity-card {
      padding: 16px;
      background: var(--bg-alt);
      border: 1px solid var(--border);
      border-radius: 8px;
      margin: 12px 0;
    }
    
    .serendipity-card .title {
      font-weight: 500;
      margin-bottom: 6px;
    }
    
    .serendipity-card .summary {
      font-size: 0.85rem;
      color: var(--text-secondary);
      margin-bottom: 8px;
    }
    
    .serendipity-card .meta {
      font-size: 0.75rem;
      color: var(--text-secondary);
      font-family: 'JetBrains Mono', monospace;
    }
    
    /* Alignment Score */
    .alignment-section {
      text-align: center;
      padding: 32px;
      background: var(--bg-alt);
      border: 1px solid var(--border);
      border-radius: 8px;
      margin: 24px 0;
    }
    
    .alignment-score {
      font-size: 4rem;
      font-weight: 700;
      font-family: 'JetBrains Mono', monospace;
    }
    
    .alignment-label {
      font-size: 1rem;
      color: var(--text-secondary);
    }
    
    .alignment-verdict {
      margin-top: 16px;
      font-style: italic;
      color: var(--text-secondary);
    }
    
    .politeness-breakdown {
      display: flex;
      justify-content: center;
      gap: 32px;
      margin-top: 24px;
    }
    
    .politeness-item {
      text-align: center;
    }
    
    .politeness-item .count {
      font-size: 1.5rem;
      font-weight: 600;
      font-family: 'JetBrains Mono', monospace;
    }
    
    .politeness-item .label {
      font-size: 0.75rem;
      color: var(--text-secondary);
      text-transform: uppercase;
    }

    /* Key Entities & Topics */
    .entities-container {
      display: flex;
      flex-direction: column;
      gap: 32px;
    }
    
    .entity-group {
      border-top: 1px solid var(--border);
      padding-top: 24px;
    }
    
    .entity-group:first-child {
      border-top: none;
      padding-top: 0;
    }
    
    .entity-title {
      font-size: 1.1rem;
      font-weight: 600;
      margin-bottom: 4px;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
    }
    
    .entity-subtitle {
      font-size: 0.85rem;
      color: var(--text-secondary);
      margin-bottom: 16px;
      text-align: center;
    }
    
    .tag-cloud {
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
      gap: 8px;
    }
    
    .tag-pill {
      font-size: 0.8rem;
      padding: 6px 12px;
      background: var(--bg);
      border: 1px solid var(--border);
      border-radius: 20px;
      color: var(--text);
      font-family: 'Inter', sans-serif;
      transition: all 0.2s;
    }
    
    .tag-pill .count {
      color: var(--text-secondary);
      font-size: 0.75rem;
      margin-left: 4px;
      font-weight: 400;
    }
    
    .tag-pill.top {
      border-color: #10a37f;
      background: rgba(16, 163, 127, 0.05);
      font-weight: 500;
    }
    
    .tag-pill.top .count {
      color: #10a37f;
      font-weight: 600;
    }
    
    /* Footer */
    footer {
      padding: 40px 0;
      text-align: center;
      color: var(--text-secondary);
      font-size: 0.85rem;
    }
    
    /* Places Grid */
    .places-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 12px;
    }
    
    .place-item {
      padding: 12px;
      background: var(--bg-alt);
      border: 1px solid var(--border);
      border-radius: 6px;
    }
    
    .place-item .name {
      font-weight: 500;
      font-size: 0.9rem;
    }
    
    .place-item .info {
      font-size: 0.75rem;
      color: var(--text-secondary);
    }
    
    /* Monthly Grid */
    .monthly-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 16px;
      margin-top: 24px;
    }
    
    .month-card {
      padding: 16px;
      background: var(--bg-alt);
      border: 1px solid var(--border);
      border-radius: 8px;
      text-align: left;
      height: 100%;
    }
    
    .month-card h4 {
      font-size: 0.95rem;
      font-weight: 600;
      margin-bottom: 12px;
      border-bottom: 1px solid var(--border);
      padding-bottom: 4px;
      color: var(--accent);
    }
    
    .month-card .card-section {
      margin-bottom: 10px;
    }
    
    .month-card .card-section:last-child {
      margin-bottom: 0;
    }
    
    .month-card .card-section-label {
      font-size: 0.65rem;
      text-transform: uppercase;
      color: var(--text-secondary);
      letter-spacing: 0.5px;
      margin-bottom: 2px;
      font-weight: 600;
    }
    
    .month-card .card-section-content {
      font-size: 0.8rem;
      color: var(--text);
      line-height: 1.4;
    }
    
    @media (max-width: 850px) {
      .monthly-grid {
        grid-template-columns: repeat(2, 1fr);
      }
    }
    
    @media (max-width: 550px) {
      .monthly-grid {
        grid-template-columns: 1fr;
      }
    }
    
    /* Responsive */
    @media (max-width: 600px) {
      header h1 {
        font-size: 1.5rem;
      }
      
      .stat-item .value {
        font-size: 1.4rem;
      }
      
      .stats-row {
        grid-template-columns: repeat(2, 1fr);
        gap: 12px;
      }
      
      .stat-item {
        padding: 14px;
      }
    }
    
    ${getDomainBarsStyles()}
    
    ${getPieChartStyles()}

    ${getQuantileStyles()}
    
    /* Domains Layout */
    .top-domains-standalone {
      display: block;
      margin-bottom: 32px;
    }
    
    @media (max-width: 900px) {
      .top-domains-standalone {
        display: block;
      }
    }
    
    .domains-second-row {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 16px;
      margin-bottom: 32px;
    }
    
    @media (max-width: 800px) {
      .domains-second-row {
        grid-template-columns: 1fr;
      }
    }

    /* Model Timeline */
    .model-timeline-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(70px, 1fr));
      gap: 8px;
      margin-top: 8px;
    }
    
    .model-time-card {
      background: var(--bg);
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 8px 4px;
      text-align: center;
      display: flex;
      flex-direction: column;
      justify-content: center;
      min-height: 60px;
    }
    
    .model-time-card .month {
      font-size: 0.6rem;
      color: var(--text-secondary);
      font-weight: 600;
      margin-bottom: 4px;
      text-transform: uppercase;
    }
    
    .model-time-card .model {
      font-size: 0.75rem;
      font-weight: 600;
      color: #10a37f;
      font-family: 'JetBrains Mono', monospace;
      line-height: 1.2;
    }
  `;
}

function getScripts(year: number, heatmapData: string, messagesHeatmapData: string): string {
  return `
    const tooltip = document.getElementById('tooltip');
    const year = ${year};
    
    // Helper function to create a heatmap
    function createHeatmap(containerId, data, tooltipLabel) {
      const container = document.getElementById(containerId);
      if (!container) return;
      
      const dataMap = new Map(data.map(d => [d.date, d.count]));
      const maxCount = Math.max(...data.map(d => d.count));
      
      const startDate = new Date(year, 0, 1);
      const endDate = new Date(year, 11, 31);
      let currentDate = new Date(startDate);
      
      // Add placeholder cells for days before Jan 1
      const startDayOfWeek = (currentDate.getDay() + 6) % 7;
      for (let i = 0; i < startDayOfWeek; i++) {
        const placeholder = document.createElement('div');
        placeholder.className = 'heatmap-cell';
        placeholder.style.visibility = 'hidden';
        container.appendChild(placeholder);
      }
      
      // Add cells for each day
      while (currentDate <= endDate) {
        const dateStr = currentDate.toISOString().split('T')[0];
        const count = dataMap.get(dateStr) || 0;
        
        let level = 0;
        if (count > 0) {
          // GitHub style: 4 levels of activity
          level = Math.min(4, Math.ceil((count / maxCount) * 4));
        }
        
        const cell = document.createElement('div');
        cell.className = 'heatmap-cell gh-level-' + level;
        cell.dataset.date = dateStr;
        cell.dataset.count = count;
        
        cell.addEventListener('mouseenter', (e) => {
          const date = new Date(e.target.dataset.date);
          const options = { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' };
          const formattedDate = date.toLocaleDateString('en-US', options);
          const countVal = parseInt(e.target.dataset.count).toLocaleString();
          tooltip.textContent = formattedDate + ' — ' + countVal + ' ' + tooltipLabel;
          tooltip.style.display = 'block';
        });
        
        cell.addEventListener('mousemove', (e) => {
          tooltip.style.left = e.clientX + 12 + 'px';
          tooltip.style.top = e.clientY - 10 + 'px';
        });
        
        cell.addEventListener('mouseleave', () => {
          tooltip.style.display = 'none';
        });
        
        container.appendChild(cell);
        currentDate.setDate(currentDate.getDate() + 1);
      }
    }
    
    // Initialize conversations heatmap
    const conversationData = ${heatmapData};
    createHeatmap('heatmap', conversationData, 'conversations');
    
    // Initialize messages heatmap with clipping for better visuals
    const messagesData = ${messagesHeatmapData};
    createHeatmapWithClipping('messages-heatmap', messagesData, 'messages');
    
    // Helper function to create heatmap with linear scale and clipping
    function createHeatmapWithClipping(containerId, data, tooltipLabel) {
      const container = document.getElementById(containerId);
      if (!container) return;
      
      const counts = data.map(d => d.count).filter(c => c > 0).sort((a, b) => a - b);
      // Determine threshold for black (level 8) - only top 4 days
      const blackThreshold = counts.length > 4 ? counts[counts.length - 4] : Infinity;
      // Clip for green levels at 90th percentile to differentiate the bulk of data
      const clipValue = counts.length > 0 ? counts[Math.floor(counts.length * 0.9)] : 0;
      const maxForScale = clipValue || 1;
      
      const dataMap = new Map(data.map(d => [d.date, d.count]));
      
      const startDate = new Date(year, 0, 1);
      const endDate = new Date(year, 11, 31);
      let currentDate = new Date(startDate);
      
      // Add placeholder cells for days before Jan 1
      const startDayOfWeek = (currentDate.getDay() + 6) % 7;
      for (let i = 0; i < startDayOfWeek; i++) {
        const placeholder = document.createElement('div');
        placeholder.className = 'heatmap-cell';
        placeholder.style.visibility = 'hidden';
        container.appendChild(placeholder);
      }
      
      // Add cells for each day
      while (currentDate <= endDate) {
        const dateStr = currentDate.toISOString().split('T')[0];
        const count = dataMap.get(dateStr) || 0;
        
        let level = 0;
        if (count > 0) {
          if (count >= blackThreshold) {
            level = 9;
          } else {
            // Linear scale across 8 shades of green
            level = Math.min(8, Math.ceil((count / maxForScale) * 8));
          }
        }
        
        const cell = document.createElement('div');
        cell.className = 'heatmap-cell gh-msg-level-' + level;
        cell.dataset.date = dateStr;
        cell.dataset.count = count;
        
        cell.addEventListener('mouseenter', (e) => {
          const date = new Date(e.target.dataset.date);
          const options = { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' };
          const formattedDate = date.toLocaleDateString('en-US', options);
          const countVal = parseInt(e.target.dataset.count).toLocaleString();
          tooltip.textContent = formattedDate + ' — ' + countVal + ' ' + tooltipLabel;
          tooltip.style.display = 'block';
        });
        
        cell.addEventListener('mousemove', (e) => {
          tooltip.style.left = e.clientX + 12 + 'px';
          tooltip.style.top = e.clientY - 10 + 'px';
        });
        
        cell.addEventListener('mouseleave', () => {
          tooltip.style.display = 'none';
        });
        
        container.appendChild(cell);
        currentDate.setDate(currentDate.getDate() + 1);
      }
    }
    
    // Add hover tooltips for bar charts
    document.querySelectorAll('.bar-hover').forEach(bar => {
      bar.addEventListener('mouseenter', (e) => {
        const label = e.target.dataset.label;
        const messages = parseInt(e.target.dataset.messages).toLocaleString();
        tooltip.textContent = label + ' — ' + messages + ' messages';
        tooltip.style.display = 'block';
      });
      
      bar.addEventListener('mousemove', (e) => {
        tooltip.style.left = e.clientX + 12 + 'px';
        tooltip.style.top = e.clientY - 10 + 'px';
      });
      
      bar.addEventListener('mouseleave', () => {
        tooltip.style.display = 'none';
      });
    });
    
    // Add hover tooltips for treemap
    document.querySelectorAll('.treemap-cell').forEach(cell => {
      cell.addEventListener('mouseenter', (e) => {
        const name = e.currentTarget.dataset.name.replace(/_/g, ' ');
        const count = parseInt(e.currentTarget.dataset.count).toLocaleString();
        tooltip.textContent = name + ' — ' + count + ' conversations';
        tooltip.style.display = 'block';
      });
      
      cell.addEventListener('mousemove', (e) => {
        tooltip.style.left = e.clientX + 12 + 'px';
        tooltip.style.top = e.clientY - 10 + 'px';
      });
      
      cell.addEventListener('mouseleave', () => {
        tooltip.style.display = 'none';
      });
    });

    // Add hover tooltips for trend charts
    document.querySelectorAll('.trend-hover-area').forEach(hitArea => {
      hitArea.addEventListener('mouseenter', (e) => {
        const month = e.target.dataset.month;
        const value = e.target.dataset.value;
        tooltip.textContent = month + ' — ' + value;
        tooltip.style.display = 'block';
      });
      
      hitArea.addEventListener('mousemove', (e) => {
        tooltip.style.left = e.clientX + 12 + 'px';
        tooltip.style.top = e.clientY - 10 + 'px';
      });
      
      hitArea.addEventListener('mouseleave', () => {
        tooltip.style.display = 'none';
      });
    });
  `;
}

async function generate(): Promise<void> {
  const statsRaw = await readFile(STATS_FILE, "utf-8");
  const stats: WrappedStats = JSON.parse(statsRaw);

  const heatmapData = generateHeatmapData(stats.activity.daily);
  const messagesHeatmapData = generateMessagesHeatmapData(stats.activity.daily);

  const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ChatGPT Wrapped ${stats.year}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    ${getStyles()}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>ChatGPT Wrapped</h1>
      <p class="meta">${stats.activity.daily[0]?.date || "N/A"} — ${stats.activity.daily[stats.activity.daily.length - 1]?.date || "N/A"}</p>
    </header>
    
    ${generateOverviewSection(stats, heatmapData)}
    ${generateDistributionSection(stats)}
    ${generateTemporalSection(stats)}
    ${generateModelsSection(stats)}
    ${generateDomainsSection(stats)}
    ${generateDynamicsSection(stats)}
    ${generateEntitiesSection(stats)}
    ${generateTopEntitiesSection(stats)}
    ${generateQualitySection(stats)}
    ${generateTopConversationsSection(stats)}
    ${generateSerendipitySection(stats)}
    ${generatePolitenessSection(stats)}
    
    <footer>
      <p>ChatGPT Wrapped · ${stats.year}</p>
    </footer>
  </div>
  
  <script>
    ${getScripts(stats.year, heatmapData, messagesHeatmapData)}
  </script>
</body>
</html>`;

  await writeFile(OUTPUT_FILE, html);
  console.log(`\n📊 Wrapped HTML generated: ${OUTPUT_FILE}`);
}

// Main
generate().catch(console.error);
