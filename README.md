# ChatGPT Wrapped 2025 - DS grade

Analyze your ChatGPT history with industrial-grade LLM metadata extraction and generate a feature rich, interactive dashboard.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![Frontend](https://img.shields.io/badge/frontend-Bun%2BTypeScript-green.svg)

## 🚀 Quick Start

1.  **Export Data**: Go to ChatGPT Settings → Data Controls → Export Data. You'll receive an email with a zip file with images, voices and a lot of stuff there. You need to locate `conversations.json`
2.  **Prepare Folder**: Place the extracted `conversations.json` into `data/conversations/`.
3.  **Configure AI**: Copy `env.example` to `.env` and add your [OpenRouter API Key](https://openrouter.ai/keys).
4.  **Install Dependencies**:
    ```bash
    # Install Python tools
    pip install -r unroller/requirements.txt -r metadater/requirements.txt
    
    # Install Dashboard generator (requires Bun)
    cd wrapped && bun install && cd ..
    ```
5.  **Run Pipeline**:
    ```bash
    python run.py
    ```
6.  **View Dashboard**:
    *   Open `wrapped/wrapped.html` directly in your browser.
    *   **Or** run a local dev server for live viewing:
        ```bash
        cd wrapped && bun run dev
        ```
        Then open `http://localhost:9876`.

---

## 🏗️ How it Works

The pipeline is designed to handle thousands of conversations with high precision.

### 1. Unroll (`unroller/`)
Splits your monolithic `conversations.json` (often hundreds of MBs) into manageable, monthly-organized files. It also performs initial enrichment:
*   **Command**: `python unroller/unroll.py data/conversations/conversations.json`
*   Calculates token counts and word counts.
*   Extracts message duration and primary model used.
*   Identifies voice-mode conversations and media attachments.

### 2. Infuse Metadata (`metadater/`)
The "brain" of the project. It uses **Gemini 3 Flash** to analyze every conversation against a custom 10-domain taxonomy:
*   **Command**: `python metadater/metadate.py`
*   **Taxonomy**: Categorizes conversations into domains like `problem_solving`, `creation`, `learning`, `technical_deep`, etc.
*   **Scores (0-100)**: Extracts metrics for Future Relevance, Complexity, Urgency, and even your "Alignment Score" (how polite you are to the AI).
*   **Entities**: Identifies people, companies, technologies, and concepts discussed.
*   **Mood & Tone**: Detects your emotional state and the conversation's flow pattern.

### 3. Generate Wrapped (`wrapped/`)
Aggregates all metadata into a unified statistics engine and produces a standalone, interactive HTML dashboard using TypeScript and modern web components.
*   **Commands**:
    ```bash
    python wrapped/aggregate.py
    cd wrapped && bun run generate
    ```

---

## 🫦 Motivation (hooman written)
So it's always a struggle to find something in ChatGPT chats.

Imagine you need a formula from research you have done months ago. Or banger GTM idea you have written to chat at 2 am random Thursday. You know that it is there, but oh man it takes time and grind to find it. Especially if you have thousands of chats. That is why an idea of building a good search over the chats has been around with me; you know - proper SOTA agentic search. 

For a good search you need to build the metadata layer over chats. I've decided to do it two fold:
1) deterministic - unroll/ module
2) LLM infused - metadater/prompt.md & Gemini 3 Flash 

It ended up being good metadata. And once it was sorted I've realized that it's a "Wrapped season" going right now. So here it goes - nice side quest.

---

## 📊 Technical Details

### Metadata Fields
Each analyzed conversation is enriched with an `llm_meta` section containing:
*   **Classification**: Domain, sub-domain, conversation type, and request types.
*   **Context**: User intent, specific keywords, and entity extraction.
*   **Quality Metrics**: 8+ numerical scores measuring engagement and response quality.
*   **Dynamics**: Tone, mood, and flow patterns.

### Pipeline Performance
*   **Gemini 3 Flash**: Chosen for its massive 1M token context window and low cost.
*   **Cost Estimate**: Processing ~1,500 conversations typically costs between $5-7 USD via OpenRouter. 

---

## 🛡️ Privacy First

*   **Local Processing**: Your raw data never leaves your machine except for the metadata extraction request sent to the LLM.
*   **No Tracking**: This tool has no analytics or external reporting.
*   **Protected**: The `.gitignore` is pre-configured to ensure no JSON exports or `.env` files are ever committed.

## 📄 License

MIT

