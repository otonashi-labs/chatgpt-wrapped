"""
Configuration for the metadater_v2 module.

Taxonomy Design Principles (from dialog classification best practices):
1. MECE: Mutually Exclusive, Collectively Exhaustive
2. Each domain has clear sub-domains + "other" catch-all
3. Sub-domains at similar granularity level
4. Based on actual user conversation patterns

All scores are on a 0-100 scale for consistency.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
MODEL = "google/gemini-3-flash-preview"

# Rate limiting
# For paid models, OpenRouter doesn't enforce strict rate limits
# Google's Gemini API allows 2000 RPM for flash models
# We use minimal delay + retry logic for 429 errors
DELAY_BETWEEN_REQUESTS = 0.1  # 100ms - just to avoid hammering
MAX_RETRIES = 3
RETRY_BACKOFF = 2.0  # exponential backoff multiplier

# Paths
DEFAULT_INPUT_DIR = Path(__file__).parent.parent / "data" / "unrolled"
DEFAULT_OUTPUT_DIR = Path(__file__).parent.parent / "data" / "wmeta"
PROMPT_FILE = Path(__file__).parent / "prompt.md"

# =============================================================================
# UNIVERSAL DOMAIN & SUB-DOMAIN TAXONOMY
# =============================================================================

TAXONOMY = {
    "problem_solving": [
        "technical",           # Code, systems, infrastructure
        "analytical",          # Data, research, investigation
        "troubleshooting",     # Fixing things that broke
        "decision_support",    # Weighing options
        "optimization",        # Making something better
        "debugging",           # Finding root causes
        "other",
    ],
    
    "creation": [
        "writing",             # Text of any kind
        "coding",              # Software development
        "design",              # Visual, UI/UX, graphics
        "planning",            # Roadmaps, strategies, schedules
        "ideation",            # Brainstorming, concepts
        "prototyping",         # Building MVPs, proofs of concept
        "editing",             # Refining, improving existing work
        "other",
    ],
    
    "learning": [
        "understanding",       # Explain X to me
        "skill_building",      # How to do Y
        "research",            # Deep dive on topic
        "fact_checking",       # Is X true? What is Y?
        "exploration",         # Curious wandering
        "comparison",          # Understanding differences between X and Y
        "synthesis",           # Connecting multiple concepts
        "other",
    ],
    
    "work": [
        "career",              # Job, growth, transitions
        "business_ops",        # Running a company/project
        "communication",       # Emails, presentations, docs
        "analysis",            # Reports, insights, metrics
        "management",          # Team, projects, resources
        "strategy",            # Long-term planning, positioning
        "sales_marketing",     # Pitching, campaigns, outreach
        "hiring",              # Recruiting, interviewing
        "other",
    ],
    
    "life_admin": [
        "health",              # Medical, fitness, mental health
        "finance",             # Money, investing, budgeting
        "travel",              # Planning, booking, logistics
        "home",                # Living space, maintenance
        "legal",               # Contracts, rights, compliance
        "shopping",            # Purchase research, comparison
        "bureaucracy",         # Forms, applications, official processes
        "other",
    ],
    
    "entertainment": [
        "media",               # Movies, books, music, games
        "hobbies",             # Personal interests, crafts
        "social",              # Relationships, events
        "curiosity",           # Random fun questions
        "gaming",              # Video games, strategy, walkthroughs
        "sports",              # Following, playing, analyzing
        "other",
    ],
    
    "personal_growth": [
        "reflection",          # Self-analysis, journaling prompts
        "productivity",        # Systems, tools, workflows
        "habits",              # Building, breaking, tracking
        "mental_models",       # Frameworks for thinking
        "goal_setting",        # Defining objectives
        "self_improvement",    # Becoming better at X
        "other",
    ],
    
    "technical_deep": [
        "ai_ml",               # LLMs, models, ML concepts
        "infrastructure",      # Servers, cloud, DevOps
        "data_engineering",    # Pipelines, databases, ETL
        "security",            # Auth, encryption, vulnerabilities
        "architecture",        # System design, patterns
        "apis",                # Integration, endpoints, protocols
        "blockchain",          # Crypto, web3, DeFi
        "other",
    ],
    
    "creative_projects": [
        "storytelling",        # Narratives, plots, characters
        "visual_art",          # Drawing, graphics, aesthetics
        "music_audio",         # Composition, production, sound
        "content_creation",    # Videos, podcasts, posts
        "branding",            # Identity, positioning, naming
        "worldbuilding",       # Creating fictional universes/systems
        "other",
    ],
    
    "commerce": [
        "product_development", # Building, launching products
        "pricing",             # Monetization, packaging, tiers
        "market_research",     # Competition, positioning, TAM
        "fundraising",         # Pitching, investors, capital
        "partnerships",        # Deals, collaborations, B2B
        "customer_support",    # Helping users, resolving issues
        "other",
    ],
}

# Flatten for easy access
DOMAINS = list(TAXONOMY.keys())

def get_subdomains(domain: str) -> list[str]:
    """Get sub-domains for a domain."""
    return TAXONOMY.get(domain, ["other"])

# =============================================================================
# CONVERSATION TYPES
# =============================================================================

CONVERSATION_TYPES = [
    "quick_lookup",       # Simple factual question
    "troubleshooting",    # Fixing a problem
    "brainstorming",      # Generating ideas
    "research",           # Information gathering (shallow or deep)
    "decision_making",    # Weighing options
    "learning",           # Understanding concepts
    "creative",           # Writing, designing, generating
    "coding",             # Writing or debugging code
    "analysis",           # Breaking down data or situations
    "planning",           # Organizing future actions
]

# =============================================================================
# REQUEST TYPES
# =============================================================================

REQUEST_TYPES = [
    "question",           # Asking for information or explanation
    "task",               # Asking to perform a specific action
    "review",             # Asking for feedback on something provided
    "comparison",         # Asking to compare options or alternatives
    "explanation",        # Asking for a concept to be broken down
    "recommendation",     # Asking for suggestions or advice
    "validation",         # Checking if understanding/approach is correct
    "translation",        # Converting between languages or formats
    "summarization",      # Condensing content
    "generation",         # Creating new content from scratch
]

# =============================================================================
# OUTCOME TYPES
# =============================================================================

OUTCOME_TYPES = [
    "answer_found",
    "options_generated",
    "decision_made",
    "understanding_gained",
    "nothing_concrete",
    "task_completed",
    "ongoing",
]

# =============================================================================
# INFORMATION DIRECTIONS
# =============================================================================

INFORMATION_DIRECTIONS = [
    "user_learning",
    "user_validating",
    "collaborative",
    "user_teaching",
]

# =============================================================================
# USER MOODS (expanded)
# =============================================================================

USER_MOODS = [
    "curious",            # Exploring, interested, open-ended inquiry
    "frustrated",         # Struggling, upset, things not working
    "excited",            # Enthusiastic, eager, positive energy
    "neutral",            # No strong emotion, matter-of-fact
    "confused",           # Lost, uncertain, seeking clarity
    "focused",            # Determined, task-oriented, efficient
    "anxious",            # Worried, stressed about outcome
    "playful",            # Light-hearted, experimenting for fun
    "impatient",          # Wanting quick answers, time-pressed
    "skeptical",          # Questioning, needs convincing
    "overwhelmed",        # Too much to handle, needs simplification
    "satisfied",          # Happy with progress/results
]

# =============================================================================
# CONVERSATION TONES (expanded)
# =============================================================================

CONVERSATION_TONES = [
    "formal",             # Professional, structured, business-like
    "casual",             # Relaxed, conversational, friendly
    "technical",          # Jargon-heavy, precise, domain-specific
    "playful",            # Light, humorous, experimental
    "urgent",             # Time-sensitive, high-stakes, pressing
    "educational",        # Teaching/learning mode, explanatory
    "collaborative",      # Working together, back-and-forth
    "inquisitive",        # Probing, questioning, exploratory
    "direct",             # Straight to the point, minimal filler
    "creative",           # Imaginative, brainstorming, blue-sky
    "analytical",         # Data-driven, methodical, logical
]

# =============================================================================
# CONVERSATION FLOWS (expanded)
# =============================================================================

CONVERSATION_FLOWS = [
    "smooth",             # Clear progression, no confusion
    "iterative",          # Back-and-forth refinement, building on previous
    "confused",           # Misunderstandings, restarts, clarifications needed
    "exploratory",        # Open-ended, meandering through ideas
    "focused",            # Direct, efficient, straight to the point
    "branching",          # Multiple threads/topics, divergent
    "deepening",          # Starting shallow, going progressively deeper
    "scattered",          # Jumping between unrelated topics
    "circular",           # Returning to same points, not progressing
    "escalating",         # Building urgency or complexity over time
]
