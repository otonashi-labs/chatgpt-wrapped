# ChatGPT Wrapped — Metadata Field Reference

This document catalogs every metadata field available in the ChatGPT Wrapped pipeline. Fields are organized by source (deterministic vs. LLM-extracted) and grouped by technical category.

---

## 📊 DATA STRUCTURE OVERVIEW

Each conversation JSON follows this structure:

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

*Computed from raw data during the `unroll` step. 100% reliable.*

## Core Identifiers

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique conversation UUID (Primary Key) |
| `title` | string | User-visible title (auto-generated or user-set) |
| `gizmo_id` | string? | Custom GPT ID if the conversation used one |

## Timestamps

**Path:** `timestamps.*`

| Field | Type | Description |
|-------|------|-------------|
| `created_at` | ISO string | Human-readable creation time |
| `updated_at` | ISO string | Last message time |
| `created_unix` | float | Unix epoch (seconds) |
| `updated_unix` | float | Unix epoch (seconds) |

## Conversation Statistics

**Path:** `meta.*`

| Field | Type | Description |
|-------|------|-------------|
| `total_messages` | int | Total number of messages in the exchange |
| `messages_by_role` | dict | Count breakdown: `{user: N, assistant: M}` |
| `total_tokens` | int | Estimated total tokens (~4 chars/token) |
| `user_tokens` | int | Estimated tokens from user messages |
| `assistant_tokens` | int | Estimated tokens from assistant responses |
| `tokens_by_role` | dict | Token breakdown by message role |
| `word_count` | int | Total words in the conversation |
| `duration_seconds` | float | Time from first to last message in seconds |
| `duration_human` | string | Formatted duration (e.g., "5m 23s") |

## Model Usage

**Path:** `meta.*`

| Field | Type | Description |
|-------|------|-------------|
| `models_used` | string[] | List of all models active in the session |
| `primary_model` | string | The default/start model for the conversation |

## Media Content

**Path:** `meta.*`

| Field | Type | Description |
|-------|------|-------------|
| `has_images` | bool | Indicates if image uploads are present |
| `has_audio` | bool | Indicates if audio/transcriptions are present |
| `image_count` | int | Number of images shared |
| `audio_count` | int | Number of audio clips shared |
| `is_voice_conversation` | bool | Flag for Voice Mode interactions |
| `voice_name` | string? | Name of the voice assistant used |

## Flags

| Field | Type | Description |
|-------|------|-------------|
| `is_archived` | bool | Whether the conversation was archived by the user |
| `is_starred` | bool? | Whether the conversation was favorited/starred |

---

# PART 2: LLM-EXTRACTED METADATA

*Enriched during the `metadater` step using semantic analysis.*

**Path:** `llm_meta.*`

## Classification

| Field | Type | Description |
|-------|------|-------------|
| `domain` | string | Primary topic category (10 domains) |
| `sub_domain` | string | Granular sub-category |
| `conversation_type` | string | Nature of interaction (Research, Coding, etc.) |

### Domain Taxonomy

| Domain | Description |
|--------|-------------|
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

### Conversation Types

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

## Intent & Requests

| Field | Type | Description |
|-------|------|-------------|
| `user_intent` | string | One-sentence summary of the user's primary goal |
| `request_types` | string[] | Categories of requests (Question, Task, Review, etc.) |
| `one_line_summary` | string | Searchable 100-character summary |

## Keywords & Tags

| Field | Type | Description |
|-------|------|-------------|
| `keywords` | string[] | Specific, searchable terms (max 10) |
| `topic_tags` | string[] | Abstract themes or tags (max 5) |

## Entity Extraction

| Field | Type | Description |
|-------|------|-------------|
| `entities_people` | string[] | Names of individuals mentioned |
| `entities_companies` | string[] | Organizations and brands discussed |
| `entities_products` | string[] | Specific products, tools, or services |
| `entities_places` | string[] | Geographic locations |
| `technologies` | string[] | Programming languages, frameworks, hardware |
| `concepts` | string[] | Abstract ideas or scientific theories |

## Quality & Engagement Scores (0-100)

| Field | Range | Description |
|-------|-------|-------------|
| `inferred_future_relevance_score` | 0-100 | Probability of being useful for future reference |
| `urgency_score` | 0-100 | Implied time-sensitivity or user stress level |
| `complexity_score` | 0-100 | Technical depth or reasoning required |
| `information_density` | 0-100 | Signal-to-noise ratio of the information exchanged |
| `depth_of_engagement` | 0-100 | User's cognitive effort and investment in the session |
| `user_satisfaction_inferred` | 0-100 | How successful the outcome seemed for the user |
| `user_request_quality_inferred` | 0-100 | Clarity and precision of user prompts |
| `ai_response_quality_score` | 0-100 | Technical accuracy and helpfulness of AI responses |

## Serendipity Scores (0-100)

| Field | Range | Description |
|-------|-------|-------------|
| `serendipity_vs_general_public` | 0-100 | How unusual the topic is compared to average global usage |
| `serendipity_vs_power_users` | 0-100 | How unique the interaction is vs other technical experts |

## Conversation Dynamics

| Field | Type | Description |
|-------|------|-------------|
| `conversation_flow` | string | Structural progression (Smooth, Iterative, Scattered, etc.) |
| `user_mood` | string | Apparent emotional state (Curious, Frustrated, Focused, etc.) |
| `conversation_tone` | string | Communication style (Technical, Casual, formal, etc.) |

## Outcomes

| Field | Type | Description |
|-------|------|-------------|
| `outcome_type` | string | Result classification (Answer Found, Task Completed, etc.) |
| `information_direction` | string | Knowledge flow (User Learning, Collaborative, User Teaching) |
