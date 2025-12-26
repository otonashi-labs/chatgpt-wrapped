# ChatGPT Wrapped — Metadata Field Reference

**~1400 conversations · 2025**

This document catalogs every metadata field available for building the wrapped experience. Fields are organized by source (deterministic vs. LLM-extracted) and grouped by use case.

---

## 📊 DATA STRUCTURE OVERVIEW

Each conversation JSON has this structure:

```json
{
  "id": "uuid",
  "title": "string",
  "timestamps": { ... },
  "meta": { ... },              // Deterministic stats
  "is_archived": bool,
  "is_starred": bool,
  "mapping": { ... },           // Raw messages (tree structure)
  "llm_meta": { ... },          // LLM-extracted semantic metadata
  "safe_urls": [...],
  "gizmo_id": "..."             // Custom GPT ID if used
}
```

---

# PART 1: DETERMINISTIC METADATA

*Added during unroll step — computed from raw data, 100% reliable*

## Core Identifiers

| Field | Type | Description | Wrapped Use Case |
|-------|------|-------------|------------------|
| `id` | string | Unique conversation UUID | Primary key, deduplication |
| `title` | string | User-visible title (often auto-generated) | Display, word clouds, search |
| `gizmo_id` | string? | Custom GPT ID if conversation used one | "Top Custom GPTs used" |

## Timestamps

**Path:** `timestamps.*`

| Field | Type | Description | Wrapped Use Case |
|-------|------|-------------|------------------|
| `created_at` | ISO string | Human-readable creation time | Timeline, "busiest day" |
| `updated_at` | ISO string | Last message time | Session length calc |
| `created_unix` | float | Unix epoch (seconds) | Sorting, grouping by date |
| `updated_unix` | float | Unix epoch (seconds) | Duration calculations |

**Wrapped Ideas:**
- 📅 Busiest day/week/month
- 🌙 Late night vs morning usage patterns
- 📈 Usage trend over the year
- 🏃 Longest streak of daily usage

## Conversation Statistics

**Path:** `meta.*`

| Field | Type | Description | Wrapped Use Case |
|-------|------|-------------|------------------|
| `total_messages` | int | Total message count | "You sent X messages" |
| `messages_by_role` | dict | `{user: N, assistant: M}` | Turn ratio, chattiness |
| `total_tokens` | int | Estimated total tokens (~4 chars/token) | "You used ~X million tokens" |
| `user_tokens` | int | Tokens from user messages | How much YOU wrote |
| `assistant_tokens` | int | Tokens from assistant | How much AI wrote |
| `tokens_by_role` | dict | Breakdown by role | User:AI ratio |
| `word_count` | int | Total words in conversation | Readability metric |
| `duration_seconds` | float | Time from first to last message | Session length |
| `duration_human` | string | "5m 23s" or "2h 15m" | Display-ready duration |

**Wrapped Ideas:**
- 📝 "You wrote X words — that's Y novels worth"
- ⏱️ "Longest conversation: 4 hours 23 minutes"
- 💬 "Average conversation: 8 turns"
- 📊 User:AI token ratio (are you verbose or terse?)

## Model Usage

**Path:** `meta.*`

| Field | Type | Description | Wrapped Use Case |
|-------|------|-------------|------------------|
| `models_used` | string[] | All models used in conversation | Model diversity |
| `primary_model` | string | Default model for conversation | "Your favorite model" |

**Wrapped Ideas:**
- 🤖 "Your most-used model: GPT-4o"
- 📊 Model distribution pie chart
- 🆕 "You tried X new models this year"
- 🧠 "You used GPT-5-thinking for 23% of conversations"

## Media Content

**Path:** `meta.*`

| Field | Type | Description | Wrapped Use Case |
|-------|------|-------------|------------------|
| `has_images` | bool | Contains image uploads | Filter multimodal |
| `has_audio` | bool | Contains audio/transcriptions | Voice usage |
| `image_count` | int | Number of images | "You shared X images" |
| `audio_count` | int | Number of audio clips | Voice message count |
| `is_voice_conversation` | bool | Voice mode conversation | Voice vs text ratio |
| `voice_name` | string? | Voice assistant name used | Voice preference |

**Wrapped Ideas:**
- 🖼️ "You shared 847 images with AI"
- 🎤 "You used voice mode 156 times"
- 📸 "Your most visual month: July"

## Flags

| Field | Type | Description | Wrapped Use Case |
|-------|------|-------------|------------------|
| `is_archived` | bool | User archived this conversation | Filter "important" convos |
| `is_starred` | bool? | User starred/favorited | High-signal content |

---

# PART 2: LLM-EXTRACTED METADATA

*Added during metadater step — semantic understanding of content*

**Path:** `llm_meta.*`

## Classification

| Field | Type | Description | Wrapped Use Case |
|-------|------|-------------|------------------|
| `domain` | string | Primary topic category (10 domains) | Domain breakdown chart |
| `sub_domain` | string | More specific category | Drill-down analysis |
| `conversation_type` | string | Nature of interaction (10 types) | "You did X% coding" |

### Domain Values

| Domain | What it covers |
|--------|---------------|
| `problem_solving` | Technical, analytical, troubleshooting, debugging |
| `creation` | Writing, coding, design, planning, ideation |
| `learning` | Understanding, research, fact-checking, exploration |
| `work` | Career, business ops, communication, strategy |
| `life_admin` | Health, finance, travel, home, legal, shopping |
| `entertainment` | Media, hobbies, social, gaming, sports |
| `personal_growth` | Reflection, productivity, habits, goals |
| `technical_deep` | AI/ML, infrastructure, data engineering, security |
| `creative_projects` | Storytelling, visual art, music, content creation |
| `commerce` | Product dev, pricing, market research, fundraising |

### Conversation Type Values

| Type | Description |
|------|-------------|
| `quick_lookup` | Simple factual question |
| `troubleshooting` | Fixing a problem |
| `brainstorming` | Generating ideas |
| `research` | Information gathering |
| `decision_making` | Weighing options |
| `learning` | Understanding concepts |
| `creative` | Writing, designing, generating |
| `coding` | Writing or debugging code |
| `analysis` | Breaking down data/situations |
| `planning` | Organizing future actions |

**Wrapped Ideas:**
- 🎯 "Your top domain: technical_deep (34%)"
- 💡 "You brainstormed 89 times this year"
- 🔧 "42 troubleshooting sessions — you fixed a lot of bugs"
- 📚 Domain sunburst/treemap visualization

## Intent & Requests

| Field | Type | Description | Wrapped Use Case |
|-------|------|-------------|------------------|
| `user_intent` | string | One-sentence summary of user's goal | Search, clustering |
| `request_types` | string[] | Types of requests made (1-3) | Request pattern analysis |
| `one_line_summary` | string | Searchable 100-char summary | Display, search index |

### Request Type Values

| Type | Description |
|------|-------------|
| `question` | Asking for information |
| `task` | Asking to perform action |
| `review` | Asking for feedback |
| `comparison` | Comparing alternatives |
| `explanation` | Concept breakdown |
| `recommendation` | Suggestions/advice |
| `validation` | Checking correctness |
| `translation` | Converting formats |
| `summarization` | Condensing content |
| `generation` | Creating from scratch |

**Wrapped Ideas:**
- 📋 "You asked for recommendations 234 times"
- ✅ "67% of your requests were task-based"
- 🔄 "Translation requests: 45 (mostly code to pseudocode)"

## Keywords & Tags

| Field | Type | Description | Wrapped Use Case |
|-------|------|-------------|------------------|
| `keywords` | string[] | Specific, searchable terms (max 10) | Word cloud, search |
| `topic_tags` | string[] | Abstract themes (max 5) | Topic clustering |

**Wrapped Ideas:**
- ☁️ Keyword word cloud visualization
- 🏷️ "Your top tags: ai_models, automation, career"
- 📈 Topic trends over time

## Entity Extraction

| Field | Type | Description | Wrapped Use Case |
|-------|------|-------------|------------------|
| `entities_people` | string[] | Names mentioned | "You talked about Elon 47 times" |
| `entities_companies` | string[] | Companies/orgs | "Top companies: OpenAI, Google, Apple" |
| `entities_products` | string[] | Products/tools/services | "You asked about X product 89 times" |
| `entities_places` | string[] | Locations | "Cities you researched: Tokyo, Berlin" |
| `technologies` | string[] | Languages, frameworks, tools | "Your stack: TypeScript, React, Python" |
| `concepts` | string[] | Abstract ideas discussed | "Big concepts: RAG, embeddings, agents" |

**Wrapped Ideas:**
- 🏢 Top 10 companies you discussed
- 🛠️ Your technology stack breakdown
- 🌍 Geographic interests map
- 💡 Concept frequency over time
- 👤 People you researched/discussed most

## Quality & Engagement Scores (0-100)

| Field | Range | Description | Wrapped Use Case |
|-------|-------|-------------|------------------|
| `inferred_future_relevance_score` | 0-100 | How useful for future reference? | Find "important" convos |
| `urgency_score` | 0-100 | How time-sensitive was query? | Stress patterns |
| `complexity_score` | 0-100 | Technical depth required | "Expert mode" usage |
| `information_density` | 0-100 | Signal vs noise ratio | Quality filter |
| `depth_of_engagement` | 0-100 | User effort/investment | Deep work sessions |
| `user_satisfaction_inferred` | 0-100 | Did user seem happy? | Success rate |
| `user_request_quality_inferred` | 0-100 | How clear was user's ask? | Prompting skill over time |
| `ai_response_quality_score` | 0-100 | How good were AI responses? | AI performance tracking |

**Wrapped Ideas:**
- 📈 "Your average prompt quality improved from 54 → 72 over the year"
- 🎯 "Your most complex conversation scored 94 — true expert level"
- ✨ "142 high-value conversations (relevance > 75)"
- 😊 "Average satisfaction: 68 — pretty good!"
- 📊 Engagement score distribution histogram

## Serendipity Scores (0-100)

| Field | Range | Description | Wrapped Use Case |
|-------|-------|-------------|------------------|
| `serendipity_vs_general_public` | 0-100 | How unusual vs average user? | "You're weird" score |
| `serendipity_vs_power_users` | 0-100 | How unusual vs power users? | "You're unique even among power users" |

**Wrapped Ideas:**
- 🦄 "Weirdness score: 73 — you ask things most people don't"
- 🌟 "Your most unique conversation" (highest serendipity)
- 📊 Distribution of how "normal" vs "unique" your usage is

## Conversation Dynamics

| Field | Type | Description | Wrapped Use Case |
|-------|------|-------------|------------------|
| `conversation_flow` | string | How did convo progress? | Flow pattern analysis |
| `user_mood` | string | User's apparent emotional state | Mood tracking |
| `conversation_tone` | string | Overall style of exchange | Communication style |

### Flow Values

| Flow | Description |
|------|-------------|
| `smooth` | Clear progression |
| `iterative` | Back-and-forth refinement |
| `confused` | Misunderstandings, restarts |
| `exploratory` | Open-ended, meandering |
| `focused` | Direct, efficient |
| `branching` | Multiple threads |
| `deepening` | Shallow → deep progression |
| `scattered` | Jumping between topics |
| `circular` | Returning to same points |
| `escalating` | Building urgency/complexity |

### Mood Values

| Mood | Description |
|------|-------------|
| `curious` | Exploring, interested |
| `frustrated` | Struggling, upset |
| `excited` | Enthusiastic, eager |
| `neutral` | Matter-of-fact |
| `confused` | Lost, uncertain |
| `focused` | Task-oriented |
| `anxious` | Worried, stressed |
| `playful` | Light-hearted |
| `impatient` | Time-pressed |
| `skeptical` | Questioning |
| `overwhelmed` | Needs simplification |
| `satisfied` | Happy with results |

### Tone Values

| Tone | Description |
|------|-------------|
| `formal` | Professional, business |
| `casual` | Relaxed, friendly |
| `technical` | Jargon-heavy, precise |
| `playful` | Humorous, experimental |
| `urgent` | Time-sensitive |
| `educational` | Teaching mode |
| `collaborative` | Working together |
| `inquisitive` | Probing, exploratory |
| `direct` | Straight to point |
| `creative` | Imaginative |
| `analytical` | Data-driven, logical |

**Wrapped Ideas:**
- 😤 "You were frustrated 34 times — we've all been there"
- 🧘 "Your most common mood: focused (45%)"
- 💬 "Your signature tone: technical (38%)"
- 📈 Mood distribution pie chart
- 🔄 Flow pattern analysis — are you iterative or direct?

## Outcomes

| Field | Type | Description | Wrapped Use Case |
|-------|------|-------------|------------------|
| `outcome_type` | string | What was achieved? | Success categorization |
| `information_direction` | string | Who held knowledge? | Learning style analysis |

### Outcome Values

| Outcome | Description |
|---------|-------------|
| `answer_found` | Got a clear answer |
| `options_generated` | Got possibilities to consider |
| `decision_made` | Reached a conclusion |
| `understanding_gained` | Learned/clarified something |
| `nothing_concrete` | No clear outcome |
| `task_completed` | Specific task was done |
| `ongoing` | Part of larger effort |

### Information Direction Values

| Direction | Description |
|-----------|-------------|
| `user_learning` | User asking, AI teaching |
| `user_validating` | User checking knowledge |
| `collaborative` | Both contributing |
| `user_teaching` | User providing context/corrections |

**Wrapped Ideas:**
- ✅ "You completed 892 tasks with AI help"
- 📚 "67% of conversations were learning-focused"
- 🤝 "You collaborated on 145 conversations — true partnership"
- 🎓 "You taught the AI something 23 times"

---

# PART 3: WRAPPED FEATURE IDEAS

## Hero Stats (Big Numbers)

- **Total conversations:** 1,400
- **Total tokens:** ~X million
- **Total words written:** X
- **Total time spent:** X hours
- **Days with ChatGPT:** X/365

## Top Lists

- Top 5 domains by conversation count
- Top 10 keywords
- Top 5 models used
- Top companies discussed
- Top technologies in your stack
- Most complex conversations
- Highest relevance conversations
- Longest conversations
- Most iterative conversations

## Time Analysis

- Heatmap: day of week × hour of day
- Monthly conversation trend
- Busiest week
- Longest streak
- "Night owl" vs "early bird" score
- Weekend vs weekday split

## Personality Profile

- **Communication style:** (technical/casual/formal %)
- **Typical mood:** (mood distribution)
- **Learning style:** (user_learning vs collaborative %)
- **Weirdness score:** (average serendipity)
- **Prompt quality trend:** (over time)

## Year in Review Slides

1. **Opener:** Total conversations, total tokens
2. **Time:** When you chatted most
3. **Domains:** What you talked about (treemap)
4. **Models:** Your AI preferences
5. **Entities:** Companies, people, tech you discussed
6. **Keywords:** Word cloud
7. **Quality:** Your prompting skill evolution
8. **Unique:** Your weirdest conversation
9. **Mood:** Emotional journey through the year
10. **Summary:** Personality archetype based on data

---

# APPENDIX: AGGREGATION QUERIES

## Count by Domain
```typescript
conversations.reduce((acc, c) => {
  const domain = c.llm_meta?.domain || 'unknown';
  acc[domain] = (acc[domain] || 0) + 1;
  return acc;
}, {});
```

## Average Scores
```typescript
const scores = conversations
  .filter(c => c.llm_meta)
  .map(c => c.llm_meta.complexity_score);
const avg = scores.reduce((a, b) => a + b, 0) / scores.length;
```

## Entity Frequency
```typescript
const techFreq = {};
conversations.forEach(c => {
  (c.llm_meta?.technologies || []).forEach(tech => {
    techFreq[tech] = (techFreq[tech] || 0) + 1;
  });
});
```

## Time-Based Grouping
```typescript
const byMonth = {};
conversations.forEach(c => {
  const date = new Date(c.timestamps.created_at);
  const key = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
  byMonth[key] = (byMonth[key] || []).concat(c);
});
```

---

**Ready to build the wrapped!** 🚀

