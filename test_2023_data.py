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
                    "parts": [f"This is some dummy {role} content for node {i}. " * random.randint(5, 20)]
                },
                "create_time": 1682899200 + i * 100 # May 1st 2023
            }
        }
    return mapping

def generate_synthetic_conv(date):
    conv_id = f"test_{random.getrandbits(32)}"
    domain = random.choice(DOMAINS)
    sub_domain = random.choice(SUB_DOMAINS[domain])
    user_msgs = random.randint(1, 10)
    assistant_msgs = user_msgs + random.randint(-1, 1)
    if assistant_msgs < 1: assistant_msgs = 1
    
    conv = {
        "id": conv_id,
        "title": f"Synthetic Conv {conv_id[:8]}",
        "timestamps": {
            "created_at": date.strftime("%Y-%m-%dT%H:%M:%SZ")
        },
        "meta": {
            "total_messages": user_msgs + assistant_msgs,
            "total_tokens": random.randint(100, 5000),
            "user_tokens": random.randint(50, 2000),
            "assistant_tokens": random.randint(50, 3000),
            "word_count": random.randint(100, 2000),
            "messages_by_role": {"user": user_msgs, "assistant": assistant_msgs},
            "image_count": random.randint(0, 2),
            "audio_count": 0,
            "is_voice_conversation": random.choice([True, False, False, False]),
            "primary_model": random.choice(MODELS)
        },
        "llm_meta": {
            "domain": domain,
            "sub_domain": sub_domain,
            "conversation_type": random.choice(CONV_TYPES),
            "user_intent": "Testing the pipeline with 2023 data",
            "request_types": ["question", "task"],
            "keywords": ["synthetic", "2023", "test"],
            "entities_people": [],
            "entities_companies": ["OpenAI"],
            "entities_products": [],
            "entities_places": ["London"],
            "technologies": ["Python"],
            "concepts": ["Time Travel"],
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
            "conversation_flow": "smooth",
            "user_mood": "focused",
            "conversation_tone": "technical",
            "one_line_summary": "Synthetic 2023 test conversation",
            "outcome_type": "task_completed",
            "information_direction": "collaborative",
            "topic_tags": ["2023_testing"]
        },
        "mapping": generate_mapping(user_msgs, assistant_msgs)
    }
    return conv

def main():
    print("🧪 Generating synthetic data starting May 2023...")
    
    # Generate data starting May 2023 through end of 2023
    start_date = datetime(2023, 5, 1)
    end_date = datetime(2023, 12, 31)
    delta = end_date - start_date
    
    for _ in range(100):
        random_days = random.randint(0, delta.days)
        date = start_date + timedelta(days=random_days)
        
        month_folder = f"{date.month:02d}-{date.year}"
        folder_path = WMETA_DIR / month_folder
        folder_path.mkdir(parents=True, exist_ok=True)
        
        conv = generate_synthetic_conv(date)
        file_path = folder_path / f"{conv['id']}.json"
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(conv, f, indent=2, ensure_ascii=False)

    print(f"✅ Generated 100 synthetic 2023 conversations in {WMETA_DIR}")

if __name__ == "__main__":
    main()

