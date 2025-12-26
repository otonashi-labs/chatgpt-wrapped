# 🤖 AI Agent Guide: ChatGPT Wrapped

This document provides instructions for AI coding agents (Cursor, Claude Code, etc.) on how to run, navigate, and customize this project.

## 🏗 Project Architecture

The pipeline consists of four main stages:

1.  **Unroll (`unroller/`)**: Splits `conversations.json` into monthly folders (`data/unrolled/YYYY-MM/`).
    *   *Key file*: `unroller/unroll.py` - Core logic for splitting and initial enrichment.
2.  **Metadate (`metadater/`)**: The "AI layer" that uses Gemini 3 Flash via OpenRouter.
    *   *Key file*: `metadater/config.py` - Defines the taxonomy (domains/sub-domains).
    *   *Key file*: `metadater/prompt.md` - The system prompt used for extraction.
3.  **Aggregate (`wrapped/aggregate.py`)**: Processes all enriched files in `data/wmeta/` and generates a single `data/stats/stats.json`.
    *   *Note*: This script is year-agnostic and handles multi-year data.
4.  **Generate (`wrapped/src/generate.ts`)**: A Bun/TypeScript script that transforms `stats.json` into a standalone `wrapped.html`.
    *   *Components*: Located in `wrapped/src/components/` (sections, charts, etc.).

## 🚀 How to Run (for Agents)

Ensure the user has provided an `OPENROUTER_API_KEY` in `.env`.

```bash
# Run the entire pipeline
python3 run.py --concurrency 10

# Run frontend dev server (with hot reload for component development)
cd wrapped && bun run dev
```

## 🛠 Customization Guide

### 1. Changing the Taxonomy
If you want to add or modify domains/sub-domains:
1.  Update `metadater/config.py`.
2.  Update `metadater/prompt.md` to reflect the changes in the instructions.
3.  Update `wrapped/src/types.ts` if the JSON structure changes.

### 2. Modifying the Dashboard
*   **Styles**: Global styles are in `wrapped/src/generate.ts` (the `getStyles()` function).
*   **Sections**: Each dashboard section is a function in `wrapped/src/components/sections.ts`.
*   **Charts**: Custom SVG chart logic is in `wrapped/src/components/charts.ts`.

### 3. Testing Changes
To test pipeline changes without waiting for LLM calls:
1.  Use a small sample of real conversations in `data/conversations/`.
2.  Or create a synthetic data generator script (e.g., `test_data_generator.py`) that mocks the `llm_meta` field in the JSON files within `data/wmeta/`.

## 📍 Data Flow Summary
`conversations.json` -> `data/unrolled/` -> `data/wmeta/` (AI Enriched) -> `data/stats/stats.json` -> `wrapped.html`

