import json
import os
import random
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
WMETA_DIR = Path("data/wmeta")
WMETA_DIR.mkdir(parents=True, exist_ok=True)

DOMAINS = ["problem_solving", "creation", "learning", "work", "life_admin"]
SUB_DOMAINS = {
    "problem_solving": ["technical", "debugging", "troubleshooting"],
    "creation": ["writing", "coding", "planning"],
    "learning": ["understanding", "research", "exploration"],
    "work": ["career", "strategy", "communication"],
    "life_admin": ["health", "finance", "travel"]
}
CONV_TYPES = ["quick_lookup", "brainstorming", "coding", "learning"]
MODELS = ["gpt-4o", "gpt-4o-mini", "o1-preview", "gpt-3.5-turbo"]

def generate_mapping(user_msg_count, assistant_msg_count):
    mapping = {}
    for i in range(user_msg_count + assistant_msg_count):
        role = "user" if i % 2 == 0 else "assistant"
        node_id = f"node_{i}"
        mapping[node_id] = {
            "message": {
                "author": {"role": role},
                "content": {
                    "content_type": "text",
                    "parts": [f"Synthetic message {i} for long range test. " * 10]
                }
            }
        }
    return mapping

def generate_synthetic_conv(date):
    conv_id = f"test_long_{random.getrandbits(32)}"
    domain = random.choice(DOMAINS)
    sub_domain = random.choice(SUB_DOMAINS[domain])
    user_msgs = random.randint(1, 5)
    assistant_msgs = user_msgs
    
    conv = {
        "id": conv_id,
        "title": f"Synthetic Conv {conv_id[:8]}",
        "timestamps": {"created_at": date.strftime("%Y-%m-%dT%H:%M:%SZ")},
        "meta": {
            "total_messages": user_msgs + assistant_msgs,
            "total_tokens": random.randint(100, 1000),
            "user_tokens": random.randint(50, 500),
            "assistant_tokens": random.randint(50, 500),
            "word_count": random.randint(100, 500),
            "messages_by_role": {"user": user_msgs, "assistant": assistant_msgs},
            "primary_model": random.choice(MODELS)
        },
        "llm_meta": {
            "domain": domain, "sub_domain": sub_domain,
            "conversation_type": random.choice(CONV_TYPES),
            "keywords": ["long-range", "test"],
            "inferred_future_relevance_score": random.randint(20, 90),
            "urgency_score": random.randint(10, 80),
            "complexity_score": random.randint(20, 85),
            "information_density": random.randint(30, 95),
            "depth_of_engagement": random.randint(10, 90),
            "user_satisfaction_inferred": random.randint(40, 100),
            "user_request_quality_inferred": random.randint(50, 95),
            "ai_response_quality_score": random.randint(60, 98),
            "serendipity_vs_general_public": random.randint(10, 90),
            "serendipity_vs_power_users": random.randint(10, 80),
            "conversation_flow": "smooth", "user_mood": "focused", "conversation_tone": "technical",
            "one_line_summary": "Long range test conversation",
            "outcome_type": "task_completed", "information_direction": "collaborative"
        },
        "mapping": generate_mapping(user_msgs, assistant_msgs)
    }
    return conv

def main():
    print("🧪 Generating long-range synthetic data (June 2023 - Dec 2025)...")
    
    # Range: June 2023 to Dec 2025 (~31 months)
    start_date = datetime(2023, 6, 1)
    end_date = datetime(2025, 12, 31)
    delta_days = (end_date - start_date).days
    
    # Generate ~10 conversations per month
    for _ in range(310):
        random_days = random.randint(0, delta_days)
        date = start_date + timedelta(days=random_days)
        
        month_folder = f"{date.month:02d}-{date.year}"
        folder_path = WMETA_DIR / month_folder
        folder_path.mkdir(parents=True, exist_ok=True)
        
        conv = generate_synthetic_conv(date)
        with open(folder_path / f"{conv['id']}.json", "w", encoding="utf-8") as f:
            json.dump(conv, f, indent=2, ensure_ascii=False)

    print(f"✅ Generated 310 conversations across 31 months in {WMETA_DIR}")

if __name__ == "__main__":
    main()

