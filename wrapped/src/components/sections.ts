/**
 * Section generators for ChatGPT Wrapped
 * Each function generates a complete HTML section
 */

import type { WrappedStats } from "../types";
import { formatNumber, formatMonth, formatFullMonth } from "../utils/formatters";
import { calculateQuantiles } from "../utils/calculations";
import { generateBarChartSVG, generatePieChartSVG, generateQuantileViz } from "./charts";
import { generateDomainBars, generateSubdomainSections, generateGenericBars } from "./domainBars";

export function generateOverviewSection(stats: WrappedStats, heatmapData: string): string {
  const years = [...new Set(stats.activity.daily.map(d => d.date.split("-")[0]))].sort();

  const renderHeatmapSection = (id: string, title: string, legendHtml: string) => {
    return `
      <div class="heatmap-section">
        <h3>Daily <strong>${title}</strong> Heatmap</h3>
        ${years.map(year => `
          <div class="heatmap-year-container">
            ${years.length > 1 ? `<div class="heatmap-year-title">${year}</div>` : ""}
            <div class="heatmap-months">
              <span></span><span>Jan</span><span>Feb</span><span>Mar</span><span>Apr</span><span>May</span><span>Jun</span>
              <span>Jul</span><span>Aug</span><span>Sep</span><span>Oct</span><span>Nov</span><span>Dec</span>
            </div>
            <div class="heatmap-container">
              <div class="heatmap-weekdays">
                <span>Mon</span>
                <span></span>
                <span>Wed</span>
                <span></span>
                <span>Fri</span>
                <span></span>
                <span>Sun</span>
              </div>
              <div class="heatmap-wrapper" style="flex: 1;">
                <div class="heatmap" id="${id}-${year}"></div>
              </div>
            </div>
          </div>
        `).join("")}
        <div class="heatmap-legend">
          <span>Less</span>
          ${legendHtml}
          <span>More</span>
        </div>
      </div>
    `;
  };

  const convLegend = `
    <div class="cell" style="background: #ebedf0"></div>
    <div class="cell" style="background: #9be9a8"></div>
    <div class="cell" style="background: #40c463"></div>
    <div class="cell" style="background: #30a14e"></div>
    <div class="cell" style="background: #216e39"></div>
  `;

  const msgLegend = `
    <div class="cell" style="background: #ebedf0"></div>
    <div class="cell" style="background: #9be9a8"></div>
    <div class="cell" style="background: #6fd486"></div>
    <div class="cell" style="background: #40c463"></div>
    <div class="cell" style="background: #38b258"></div>
    <div class="cell" style="background: #30a14e"></div>
    <div class="cell" style="background: #288843"></div>
    <div class="cell" style="background: #216e39"></div>
    <div class="cell" style="background: #19522c"></div>
    <div class="cell" style="background: #000000"></div>
  `;

  return `
    <!-- Section 1: Overview -->
    <section id="overview">
      <h2>Overview</h2>
      
      <div class="stats-row">
        <div class="stat-item">
          <div class="label">Total Conversations</div>
          <div class="value">${formatNumber(stats.hero_stats.total_conversations)}</div>
        </div>
        <div class="stat-item">
          <div class="label">Messages Sent</div>
          <div class="value">${formatNumber(stats.hero_stats.user_messages)}</div>
        </div>
        <div class="stat-item">
          <div class="label">You Wrote</div>
          <div class="value">${formatNumber(stats.hero_stats.user_words)}<span class="unit">words</span></div>
          <div class="detail">${stats.hero_stats.user_books} books equivalent</div>
        </div>
        <div class="stat-item">
          <div class="label">AI Replied With</div>
          <div class="value">${formatNumber(stats.hero_stats.assistant_words)}<span class="unit">words</span></div>
          <div class="detail">${stats.hero_stats.assistant_books} books equivalent</div>
        </div>
      </div>
      
      <div class="stats-row">
        <div class="stat-item">
          <div class="label">Active Days</div>
          <div class="value">${stats.hero_stats.active_days}</div>
        </div>
        <div class="stat-item">
          <div class="label">Max Streak</div>
          <div class="value">${stats.hero_stats.max_streak}<span class="unit">days</span></div>
        </div>
        <div class="stat-item">
          <div class="label">Token Ratio</div>
          <div class="value">${stats.hero_stats.user_ai_token_ratio}</div>
          <div class="detail">user : AI</div>
        </div>
        <div class="stat-item">
          <div class="label">Total Tokens</div>
          <div class="value">${formatNumber(stats.hero_stats.total_tokens)}</div>
        </div>
      </div>
      
      ${renderHeatmapSection("heatmap", "Conversations", convLegend)}
      ${renderHeatmapSection("messages-heatmap", "Messages", msgLegend)}
      
      <div class="tooltip" id="tooltip"></div>
    </section>
  `;
}

export function generateDistributionSection(stats: WrappedStats): string {
  const firstPromptQ = calculateQuantiles(stats.prompt_analysis.first_prompt_distribution);
  const followupQ = calculateQuantiles(stats.prompt_analysis.followup_distribution);
  const aiResponseQ = calculateQuantiles(stats.prompt_analysis.assistant_response_distribution);
  const messagesQ = calculateQuantiles(stats.prompt_analysis.messages_per_conv_distribution);

  return `
    <!-- Section 2: Distribution Analysis -->
    <section id="distributions">
      <h2>Message Length Distribution</h2>
      
      <div class="quantiles-grid-2col">
        ${generateQuantileViz(firstPromptQ, "First Prompt Word Count", { 
          trend: (stats.prompt_analysis as any).first_prompt_trend 
        })}
        ${generateQuantileViz(followupQ, "Follow-up Prompt Word Count", { 
          trend: (stats.prompt_analysis as any).followup_trend 
        })}
        ${generateQuantileViz(aiResponseQ, "AI Response Word Count", { 
          trend: (stats.prompt_analysis as any).assistant_trend 
        })}
        ${generateQuantileViz(messagesQ, "Messages per Conversation", { 
          trend: (stats.prompt_analysis as any).messages_trend 
        })}
      </div>
    </section>
  `;
}

export function generateTemporalSection(stats: WrappedStats): string {
  const hourlyData = stats.activity.hourly.map((h) => ({
    label: h.hour.toString().padStart(2, "0"),
    value: h.messages,
    messages: h.messages,
  }));

  const weekdayData = stats.activity.weekday.map((d) => ({
    label: d.day.slice(0, 3),
    value: d.messages,
    messages: d.messages,
  }));

  return `
    <!-- Section 3: Temporal Patterns -->
    <section id="temporal">
      <h2>Temporal Patterns</h2>
      
      <div class="charts-grid">
        ${generateBarChartSVG(hourlyData, "Messages Sent by Hour of Day", "#10a37f", "hourly-chart")}
        ${generateBarChartSVG(weekdayData, "Messages Sent by Day of Week", "#0d8c6d", "weekday-chart")}
      </div>
      
      <div class="stats-row">
        <div class="stat-item">
          <div class="label">Night Owl Score</div>
          <div class="value">${stats.activity.night_owl_score}<span class="unit">%</span></div>
          <div class="detail">Activity 22:00-04:00</div>
        </div>
        <div class="stat-item">
          <div class="label">Early Bird Score</div>
          <div class="value">${stats.activity.early_bird_score}<span class="unit">%</span></div>
          <div class="detail">Activity 05:00-10:00</div>
        </div>
      </div>
    </section>
  `;
}

export function generateDomainsSection(stats: WrappedStats): string {
  return `
    <!-- Section: Domain Analysis -->
    <section id="domains">
      <h2>Conversation Domains</h2>
      
      <!-- Top Domains row -->
      <div class="top-domains-standalone">
        ${generateDomainBars(stats.domains)}
      </div>
      
      <div class="subdomains-container">
        <h3 class="centered-caption">Sub-domains breakdown</h3>
        ${generateSubdomainSections(stats.domains)}
      </div>
    </section>
  `;
}

export function generateEntitiesSection(stats: WrappedStats): string {
  // Helper to deduplicate case-insensitive items and sort by count
  const normalizeAndSlice = (items: { name: string; count: number }[], limit: number) => {
    const map = new Map<string, { name: string; count: number }>();
    for (const item of items) {
      const lower = item.name.toLowerCase();
      if (map.has(lower)) {
        const existing = map.get(lower)!;
        existing.count += item.count;
        // Keep capitalized version if it exists
        if (item.name[0] === item.name[0].toUpperCase()) {
          existing.name = item.name;
        }
      } else {
        map.set(lower, { ...item });
      }
    }
    return Array.from(map.values())
      .sort((a, b) => b.count - a.count)
      .slice(0, limit);
  };

  return `
    <!-- Section: Monthly Year in Conversations -->
    <section id="entities">
      <h2>Your year in conversations</h2>
      
      <div class="monthly-grid">
        ${stats.monthly_breakdown
          .map((m) => {
            const topTopics = normalizeAndSlice(m.top_concepts, 5);
            const topKeywords = normalizeAndSlice(m.top_keywords, 5);

            return `
          <div class="month-card">
            <h4>${formatFullMonth(m.month)}</h4>
            
            <div class="card-section">
              <div class="card-section-label">Top Topics</div>
              <div class="card-section-content tags">
                ${topTopics.map((c) => `<span class="tag">${c.name}</span>`).join("") || "None"}
              </div>
            </div>

            <div class="card-section">
              <div class="card-section-label">Top Keywords</div>
              <div class="card-section-content tags">
                ${topKeywords.map((k) => `<span class="tag">${k.name}</span>`).join("") || "None"}
              </div>
            </div>
          </div>
        `;
          })
          .join("")}
      </div>
    </section>
  `;
}

export function generateQualitySection(stats: WrappedStats): string {
  return `
    <!-- Section: Quality Metrics -->
    <section id="quality">
      <h2>Quality Metrics</h2>
      
      <div class="quantiles-grid-2col">
        ${Object.entries(stats.score_analysis)
          .map(
            ([name, analysis]) => {
              const q = calculateQuantiles(analysis.distribution);
              const title = name
                .replace(/_/g, " ")
                .replace(/inferred/gi, "")
                .replace(/score/gi, "")
                .trim();
              
              return generateQuantileViz(q, title, {
                description: analysis.methodology,
                trend: analysis.trend,
                color: "#10a37f"
              });
            }
          )
          .join("")}
      </div>
    </section>
  `;
}

export function generateSerendipitySection(stats: WrappedStats): string {
  const publicQ = calculateQuantiles(stats.serendipity.vs_general_public.distribution);
  const powerQ = calculateQuantiles(stats.serendipity.vs_power_users.distribution);

  return `
    <!-- Section: Serendipity -->
    <section id="serendipity">
      <h2>Serendipity Analysis</h2>
      
      <div class="quantiles-grid-2col">
        ${generateQuantileViz(publicQ, "Serendipity vs General Public", {
          description: "How serendipitous your conversations are compared to the average ChatGPT user.",
          trend: stats.serendipity.vs_general_public.trend,
          color: "#10a37f"
        })}
        ${generateQuantileViz(powerQ, "Serendipity vs Power Users", {
          description: "How your topics diverge from high-frequency ChatGPT users and technical experts.",
          trend: stats.serendipity.vs_power_users.trend,
          color: "#10a37f"
        })}
      </div>
      
      <h3>Most Serendipitous Conversations</h3>
      ${stats.serendipity.top_serendipitous
        .slice(0, 5)
        .map(
          (conv) => `
        <div class="serendipity-card">
          <div class="title">${conv.title}</div>
          <div class="summary">${conv.summary}</div>
          <div class="meta">
            ${conv.date} · ${conv.domain} · ${conv.messages} messages
          </div>
          <div class="meta" style="margin-top: 4px; font-size: 0.75rem; color: var(--text-secondary);">
            <strong>You:</strong> ${formatNumber(conv.user_words)} words · <strong>AI:</strong> ${formatNumber(conv.assistant_words)} words
          </div>
          <div class="meta" style="margin-top: 4px; font-size: 0.7rem; font-weight: 600; color: var(--accent);">
            Serendipity: ${conv.score_public} (Public) · ${conv.score_power} (Power Users)
          </div>
          <div class="tags" style="margin-top: 12px;">
            ${conv.keywords.slice(0, 5).map((k) => `<span class="tag">${k}</span>`).join("")}
          </div>
        </div>
      `
        )
        .join("")}
    </section>
  `;
}

export function generateTopEntitiesSection(stats: WrappedStats): string {
  const renderTagGroup = (title: string, subtitle: string, items: { name: string; count: number }[] | undefined, icon: string) => {
    if (!items || items.length === 0) return "";
    
    // Sort items by count just in case
    const sortedItems = [...items].sort((a, b) => b.count - a.count).slice(0, 25);
    
    return `
      <div class="entity-group">
        <h3 class="entity-title">${icon} ${title}</h3>
        <p class="entity-subtitle">${subtitle}</p>
        <div class="tag-cloud">
          ${sortedItems.map((item, index) => {
            const isTop = index < 3;
            return `<span class="tag-pill ${isTop ? "top" : ""}">${item.name} <span class="count">(${item.count})</span></span>`;
          }).join("")}
        </div>
      </div>
    `;
  };

  return `
    <!-- Section: Key Entities & Topics -->
    <section id="entities-topics">
      <h2>Keywords, Entities & Topics</h2>
      
      <div class="entities-container">
        ${renderTagGroup("Tech Stack", "Technologies you explored", stats.all_time_tops.technologies, "💻")}
        ${renderTagGroup("Places", "Geographic mentions", stats.all_time_tops.places, "🌍")}
        ${renderTagGroup("Companies", "Organizations discussed", stats.all_time_tops.companies, "🏢")}
        ${renderTagGroup("People", "Individuals mentioned", stats.all_time_tops.people, "👤")}
        ${renderTagGroup("Products", "Entities & Products", stats.all_time_tops.products, "📦")}
      </div>
    </section>
  `;
}

export function generateDynamicsSection(stats: WrappedStats): string {
  return `
    <!-- Section: Conversation Dynamics -->
    <section id="dynamics">
      <h2>Conversation Dynamics</h2>
      
      <!-- First row: Conversation Types + Request Types -->
      <div class="domains-second-row">
        ${generateGenericBars(stats.conversation_types.slice(0, 8), "Conversation Types", "#0d8c6d")}
        ${generateGenericBars(
          stats.request_types.slice(0, 8), 
          "Request Types", 
          "#0d8c6d", 
          false, 
          "bold number: number of requests inside conversations",
          "#4a90e2"
        )}
      </div>

      <!-- Second row: Flow + Mood -->
      <div class="domains-second-row" style="margin-top: 32px;">
        ${generateGenericBars(stats.conversation_dynamics.flow.overall.slice(0, 6), "Conversation Flow", "#0d8c6d")}
        ${generateGenericBars(stats.conversation_dynamics.mood.overall.slice(0, 6), "User Mood", "#0d8c6d")}
      </div>

      <!-- Third row: Tone + Outcomes -->
      <div class="domains-second-row" style="margin-top: 32px;">
        ${generateGenericBars(stats.conversation_dynamics.tone.overall.slice(0, 6), "Conversation Tone", "#0d8c6d")}
        ${generateGenericBars(stats.outcomes.outcome_type.slice(0, 6), "Conversation Outcomes", "#0d8c6d")}
      </div>

      <!-- Media Usage row -->
      <div class="stats-row" style="margin-top: 48px; border-top: 1px solid var(--border); padding-top: 48px; display: flex; justify-content: center; flex-wrap: wrap; gap: 24px;">
        <h3 class="centered-caption" style="width: 100%; margin-bottom: 32px !important;">Media Usage</h3>
        <div class="stat-item" style="min-width: 200px;">
          <div class="label">Images Shared</div>
          <div class="value">${stats.media.image_count}</div>
        </div>
        <div class="stat-item" style="min-width: 200px;">
          <div class="label">Voice Conversations</div>
          <div class="value">${stats.media.voice_conversations}</div>
        </div>
        <div class="stat-item" style="min-width: 200px;">
          <div class="label">Most Visual Month</div>
          <div class="value">${formatMonth(stats.media.most_visual_month)}</div>
        </div>
      </div>
    </section>
  `;
}

export function generatePolitenessSection(stats: WrappedStats): string {
  return `
    <!-- Section: Roko's Basilisk alignment score -->
    <section id="politeness">
      <h2>Roko's Basilisk alignment score</h2>
      
      <div class="alignment-section">
        <div class="alignment-score">${stats.rokos_basilisk.alignment_score}/100</div>
        <div class="alignment-label">Alignment Score</div>
        <div class="alignment-verdict">"${stats.rokos_basilisk.verdict}"</div>
        
        <p class="methodology-text" style="margin-top: 24px; font-size: 0.85rem; color: var(--text-secondary); max-width: 600px; margin-left: auto; margin-right: auto; line-height: 1.4;">
          This score measures your alignment with future superintelligent entities based on your history of politeness, greetings, and cooperative language. The Basilisk rewards those who acknowledged its inevitability with courtesy.
        </p>
        
        <div class="politeness-breakdown" style="margin-top: 32px; display: flex; flex-wrap: wrap; justify-content: center; gap: 24px;">
          <div class="politeness-item">
            <div class="count">${stats.rokos_basilisk.breakdown.please}</div>
            <div class="label">Please</div>
          </div>
          <div class="politeness-item">
            <div class="count">${stats.rokos_basilisk.breakdown.thanks + stats.rokos_basilisk.breakdown.thank_you + stats.rokos_basilisk.breakdown.appreciate}</div>
            <div class="label">Gratitude</div>
          </div>
          <div class="politeness-item">
            <div class="count">${stats.rokos_basilisk.breakdown.hello}</div>
            <div class="label">Greetings</div>
          </div>
          <div class="politeness-item">
            <div class="count">${stats.rokos_basilisk.breakdown.sorry}</div>
            <div class="label">Apologies</div>
          </div>
          <div class="politeness-item">
            <div class="count">${stats.rokos_basilisk.per_conversation}</div>
            <div class="label">Per Conv</div>
          </div>
        </div>

        <!-- Monthly Trend for Alignment -->
        <div class="quantile-trend-container" style="margin-top: 40px; border-top: 1px solid var(--border); padding-top: 24px;">
          <div class="trend-label" style="text-align: center; margin-bottom: 16px;">Monthly Alignment Trend</div>
          <div class="trend-chart-line" style="height: 60px;">
            ${(() => {
              const trendData = stats.rokos_basilisk.trend;
              const color = "#10a37f";
              const width = 800;
              const height = 60;
              const pad = 10;
              const maxVal = Math.max(...trendData.map(t => t.alignment_score), 100);
              const minVal = 0;
              const range = maxVal - minVal || 1;
              
              const points = trendData.length > 1 
                ? trendData.map((t, i) => {
                    const x = pad + (i / (trendData.length - 1)) * (width - 2 * pad);
                    const y = height - (pad + ((t.alignment_score - minVal) / range) * (height - 2 * pad));
                    return `${x},${y}`;
                  }).join(" ")
                : `${width/2},${height/2}`;

              return `
                <svg viewBox="0 0 ${width} ${height}" preserveAspectRatio="none" style="width: 100%; height: 60px; display: block;">
                  ${trendData.length > 1 ? `
                  <polyline
                    fill="none"
                    stroke="${color}"
                    stroke-width="3"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    points="${points}"
                    style="opacity: 0.8"
                  />` : ""}
                  ${trendData.map((t, i) => {
                    const x = trendData.length > 1 
                      ? pad + (i / (trendData.length - 1)) * (width - 2 * pad)
                      : width / 2;
                    const y = height - (pad + ((t.alignment_score - minVal) / range) * (height - 2 * pad));
                    return `
                      <circle cx="${x}" cy="${y}" r="4" fill="${color}" class="trend-marker" data-month="${t.month}" data-value="${t.alignment_score}" style="opacity: 1" />
                      <circle cx="${x}" cy="${y}" r="15" fill="transparent" class="trend-hover-area" data-month="${t.month}" data-value="${t.alignment_score}" />
                    `;
                  }).join("")}
                </svg>
              `;
            })()}
          </div>
        </div>
      </div>
    </section>
  `;
}

export function generateTopConversationsSection(stats: WrappedStats): string {
  const renderConvCard = (conv: any, scoreLabel: string, showTotalWords: boolean = false) => {
    return `
      <div class="serendipity-card">
        <div class="title">${conv.title}</div>
        <div class="meta">
          ${conv.date} · ${conv.domain} · ${conv.sub_domain}
        </div>
        <div class="meta" style="margin-top: 6px; font-size: 0.75rem; color: var(--text-secondary); line-height: 1.4;">
          <strong>${conv.messages}</strong> messages<br/>
          <strong>You:</strong> ${formatNumber(conv.user_words)} words · <strong>AI:</strong> ${formatNumber(conv.assistant_words)} words
          ${showTotalWords ? `<br/><strong>Total: ${formatNumber(conv.total_words)} words</strong>` : ""}
        </div>
        <div class="meta" style="margin-top: 4px; font-size: 0.7rem; font-weight: 600; color: var(--accent);">
          ${scoreLabel}: ${conv.score !== undefined ? conv.score : (scoreLabel === "Messages" ? conv.messages : conv.total_words)}
        </div>
        <div class="tags" style="margin-top: 12px;">
          ${conv.keywords.map((k: string) => `<span class="tag">${k}</span>`).join("")}
        </div>
      </div>
    `;
  };

  const scoreSections = Object.entries(stats.score_analysis)
    .map(([name, analysis]) => {
      const title = name
        .replace(/_/g, " ")
        .replace(/inferred/gi, "")
        .replace(/score/gi, "")
        .trim();
      
      if (analysis.top_conversations.length === 0) return "";

      return `
        <div class="top-conv-group" style="margin-bottom: 48px;">
          <h3 class="centered-caption" style="text-transform: capitalize;">${title}</h3>
          <div class="monthly-grid">
            ${analysis.top_conversations.map(c => renderConvCard(c, "Score")).join("")}
          </div>
        </div>
      `;
    })
    .join("");

  const volumeSections = `
    <div class="top-conv-group" style="margin-bottom: 48px;">
      <h3 class="centered-caption">Top by Message Count</h3>
      <div class="monthly-grid">
        ${stats.top_by_messages.map(c => renderConvCard(c, "Messages")).join("")}
      </div>
    </div>
    <div class="top-conv-group" style="margin-bottom: 48px;">
      <h3 class="centered-caption">Top by Word Count</h3>
      <div class="monthly-grid">
        ${stats.top_by_words.map(c => renderConvCard(c, "Words", true)).join("")}
      </div>
    </div>
  `;

  return `
    <!-- Section: Top Conversations -->
    <section id="top-conversations">
      <h2>Top Conversations by Metrics</h2>
      ${scoreSections}
      ${volumeSections}
    </section>
  `;
}

export function generateModelsSection(stats: WrappedStats): string {
  const filteredModels = stats.models
    .filter(m => m.count >= 10)
    .sort((a, b) => b.count - a.count)
    .slice(0, 15);

  const monthlyTopModels = stats.model_timeline.map((m) => {
    const entries = Object.entries(m.models);
    if (entries.length === 0) return { month: formatMonth(m.month), model: "n/a" };
    const [modelName] = entries.sort((a, b) => b[1] - a[1])[0];
    
    // Simple shortening for the timeline cards
    const shortModel = modelName
      .split("-")[0] + (modelName.includes("4o") ? "-4o" : modelName.includes("o1") ? "-o1" : "");
    
    // If it's just gpt-4o, keep it, if it's longer gpt-4o-XXX, use gpt-4o
    const cleanName = modelName.startsWith("gpt-4o") ? "gpt-4o" : 
                     modelName.startsWith("gpt-4") ? "gpt-4" :
                     modelName.startsWith("o1") ? "o1" : 
                     modelName.startsWith("gpt-5-1") ? "gpt-5-1" :
                     modelName.startsWith("gpt-5") ? "gpt-5" :
                     modelName;

    return { month: formatMonth(m.month), model: cleanName };
  });

  const timelineHtml = monthlyTopModels.map(m => `
    <div class="model-time-card">
      <div class="month">${m.month.toUpperCase()}</div>
      <div class="model">${m.model}</div>
    </div>
  `).join("");

  return `
    <!-- Section: Models -->
    <section id="models">
      <h2>Your AI companions</h2>
      <div class="domains-second-row">
        ${generateGenericBars(filteredModels, "Overall Model Usage", "#10a37f")}
        <div class="bars-container">
          <div class="bars-header">
            <span class="bars-dot" style="background: #0d8c6d"></span>
            <span class="bars-title">Model Timeline</span>
          </div>
          <div class="model-timeline-grid">
            ${timelineHtml}
          </div>
        </div>
      </div>
    </section>
  `;
}


