"""
ChatGPT Wrapped 2025 - Comprehensive Statistics Aggregator

Processes all wmeta_2 conversation files and generates comprehensive stats
for the wrapped experience. Outputs JSON for the frontend.

Usage:
    python aggregate.py
"""

import json
import os
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from statistics import mean, stdev, median
from typing import Any

# Configuration
WMETA_DIR = Path(__file__).parent.parent / "data" / "wmeta"
OUTPUT_FILE = Path(__file__).parent.parent / "data" / "stats" / "stats.json"


def load_all_conversations() -> list[dict]:
    """Load all conversations from wmeta directory."""
    conversations = []
    
    for month_dir in sorted(WMETA_DIR.iterdir()):
        if not month_dir.is_dir():
            continue
        
        # Folder format is MM-YYYY
        for file in month_dir.glob("*.json"):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    conv = json.load(f)
                    
                conversations.append(conv)
            except Exception as e:
                print(f"Error reading {file}: {e}")
    
    # Sort by date
    conversations.sort(key=lambda c: c.get("timestamps", {}).get("created_at", ""))
    
    if conversations:
        first_date = conversations[0].get("timestamps", {}).get("created_at", "")
        last_date = conversations[-1].get("timestamps", {}).get("created_at", "")
        print(f"Loaded {len(conversations)} conversations from {first_date[:10]} to {last_date[:10]}")
    else:
        print("No conversations found!")
        
    return conversations


def get_date_str(dt: datetime) -> str:
    """Get ISO date string from datetime."""
    return dt.strftime("%Y-%m-%d")


def get_month_str(dt: datetime) -> str:
    """Get month string from datetime."""
    return dt.strftime("%Y-%m")


def get_hour(conv: dict) -> int:
    """Get hour from conversation timestamp."""
    created_at = conv.get("timestamps", {}).get("created_at", "")
    if created_at:
        dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        return dt.hour
    return 12


def get_weekday(conv: dict) -> int:
    """Get weekday from conversation timestamp (0=Monday, 6=Sunday)."""
    created_at = conv.get("timestamps", {}).get("created_at", "")
    if created_at:
        dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        return dt.weekday()
    return 0


def get_datetime(conv: dict) -> datetime:
    """Get datetime from conversation."""
    created_at = conv.get("timestamps", {}).get("created_at", "")
    if created_at:
        return datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    return datetime.now()


def count_user_messages(conv: dict) -> list[dict]:
    """Extract user messages from conversation mapping."""
    messages = []
    mapping = conv.get("mapping", {})
    
    for node in mapping.values():
        msg = node.get("message", {})
        if msg and msg.get("author", {}).get("role") == "user":
            content = msg.get("content", {})
            if content.get("content_type") == "text":
                parts = content.get("parts", [])
                for part in parts:
                    if isinstance(part, str) and part.strip():
                        messages.append({
                            "text": part,
                            "word_count": len(part.split()),
                            "create_time": msg.get("create_time", 0)
                        })
    
    return messages


def count_assistant_messages(conv: dict) -> list[dict]:
    """Extract assistant messages from conversation mapping."""
    messages = []
    mapping = conv.get("mapping", {})
    
    for node in mapping.values():
        msg = node.get("message", {})
        if msg and msg.get("author", {}).get("role") == "assistant":
            content = msg.get("content", {})
            if content.get("content_type") == "text":
                parts = content.get("parts", [])
                for part in parts:
                    if isinstance(part, str) and part.strip():
                        messages.append({
                            "text": part,
                            "word_count": len(part.split())
                        })
    
    return messages


def count_politeness_phrases(text: str) -> dict:
    """Count polite phrases in text."""
    lower = text.lower()
    return {
        "please": len(re.findall(r"\bplease\b", lower)),
        "thanks": len(re.findall(r"\bthanks\b", lower)),
        "thank_you": len(re.findall(r"\bthank you\b", lower)),
        "sorry": len(re.findall(r"\bsorry\b", lower)),
        "appreciate": len(re.findall(r"\bappreciate\b", lower)),
        "grateful": len(re.findall(r"\bgrateful\b", lower)),
        "pardon": len(re.findall(r"\bpardon\b", lower)),
        "excuse_me": len(re.findall(r"\bexcuse me\b", lower)),
        "hello": len(re.findall(r"\b(hello|hi|hey|good morning|good afternoon|good evening)\b", lower)),
    }


def calculate_distribution(values: list[float], bins: int = 10) -> list[dict]:
    """Calculate distribution for bell curve visualization."""
    if not values:
        return []
    
    min_val = min(values)
    max_val = max(values)
    
    if min_val == max_val:
        return [{"bin_start": min_val, "bin_end": max_val, "count": len(values)}]
    
    bin_width = (max_val - min_val) / bins
    distribution = []
    
    for i in range(bins):
        bin_start = min_val + i * bin_width
        bin_end = min_val + (i + 1) * bin_width
        count = sum(1 for v in values if bin_start <= v < bin_end)
        if i == bins - 1:  # Last bin includes max
            count = sum(1 for v in values if bin_start <= v <= bin_end)
        distribution.append({
            "bin_start": round(bin_start, 2),
            "bin_end": round(bin_end, 2),
            "count": count,
            "percentage": round(count / len(values) * 100, 1)
        })
    
    return distribution


def safe_mean(values: list, default=0):
    """Calculate mean with empty list protection."""
    return mean(values) if values else default


def safe_stdev(values: list, default=0):
    """Calculate stdev with protection for small lists."""
    return stdev(values) if len(values) > 1 else default


def aggregate_stats(convs: list[dict]) -> dict:
    """Calculate all statistics from conversations."""
    
    if not convs:
        raise ValueError("No conversations to process")
    
    # =========================================================================
    # BLOCK 1: HERO STATS
    # =========================================================================
    
    total_conversations = len(convs)
    total_messages = sum(c.get("meta", {}).get("total_messages", 0) for c in convs)
    total_tokens = sum(c.get("meta", {}).get("total_tokens", 0) for c in convs)
    total_user_tokens = sum(c.get("meta", {}).get("user_tokens", 0) for c in convs)
    total_assistant_tokens = sum(c.get("meta", {}).get("assistant_tokens", 0) for c in convs)
    total_words = sum(c.get("meta", {}).get("word_count", 0) for c in convs)
    
    # User messages & words
    user_messages_by_role = sum(c.get("meta", {}).get("messages_by_role", {}).get("user", 0) for c in convs)
    assistant_messages_by_role = sum(c.get("meta", {}).get("messages_by_role", {}).get("assistant", 0) for c in convs)
    
    # Calculate user words vs assistant words
    user_word_count = 0
    assistant_word_count = 0
    first_prompt_words = []
    followup_prompt_words = []
    assistant_response_words = []
    messages_per_conversation = []
    
    # Monthly tracking for trends
    monthly_first_prompt = defaultdict(list)
    monthly_followup = defaultdict(list)
    monthly_assistant = defaultdict(list)
    monthly_messages_per_conv = defaultdict(list)
    
    for conv in convs:
        month_str = get_month_str(get_datetime(conv))
        user_msgs = count_user_messages(conv)
        assistant_msgs = count_assistant_messages(conv)
        
        user_word_count += sum(m["word_count"] for m in user_msgs)
        assistant_word_count += sum(m["word_count"] for m in assistant_msgs)
        
        # First prompt vs followups
        if user_msgs:
            fp_val = user_msgs[0]["word_count"]
            first_prompt_words.append(fp_val)
            monthly_first_prompt[month_str].append(fp_val)
            for msg in user_msgs[1:]:
                fu_val = msg["word_count"]
                followup_prompt_words.append(fu_val)
                monthly_followup[month_str].append(fu_val)
        
        for msg in assistant_msgs:
            as_val = msg["word_count"]
            assistant_response_words.append(as_val)
            monthly_assistant[month_str].append(as_val)
        
        mpc_val = len(user_msgs) + len(assistant_msgs)
        messages_per_conversation.append(mpc_val)
        monthly_messages_per_conv[month_str].append(mpc_val)
    
    # Calculate trends for prompt analysis
    def get_trend(monthly_data):
        return [
            {"month": m, "average": round(safe_mean(vals), 1)}
            for m, vals in sorted(monthly_data.items())
        ]

    first_prompt_trend = get_trend(monthly_first_prompt)
    followup_trend = get_trend(monthly_followup)
    assistant_trend = get_trend(monthly_assistant)
    messages_trend = get_trend(monthly_messages_per_conv)

    # Books calculation (average book ~50k words)
    WORDS_PER_BOOK = 50000
    user_books = round(user_word_count / WORDS_PER_BOOK, 1)
    assistant_books = round(assistant_word_count / WORDS_PER_BOOK, 1)
    
    # Token ratio
    user_ai_token_ratio = round(total_user_tokens / max(total_assistant_tokens, 1), 2)
    
    # Averages
    avg_first_prompt_words = round(safe_mean(first_prompt_words), 1)
    avg_followup_words = round(safe_mean(followup_prompt_words), 1)
    avg_assistant_words = round(safe_mean(assistant_response_words), 1)
    avg_messages_per_conv = round(safe_mean(messages_per_conversation), 1)
    
    # Distributions for bell curves
    first_prompt_distribution = calculate_distribution(first_prompt_words, 15)
    followup_distribution = calculate_distribution(followup_prompt_words, 15)
    assistant_response_distribution = calculate_distribution(assistant_response_words, 15)
    messages_per_conv_distribution = calculate_distribution(messages_per_conversation, 12)
    
    # Daily activity for heatmap
    daily_activity = defaultdict(lambda: {"count": 0, "tokens": 0, "messages": 0})
    for conv in convs:
        date_str = get_date_str(get_datetime(conv))
        daily_activity[date_str]["count"] += 1
        daily_activity[date_str]["tokens"] += conv.get("meta", {}).get("total_tokens", 0)
        daily_activity[date_str]["messages"] += conv.get("meta", {}).get("total_messages", 0)
    
    # Convert to list with dates
    daily_activity_list = [
        {"date": date, **data} 
        for date, data in sorted(daily_activity.items())
    ]
    
    # Active days and streaks
    active_dates = set(daily_activity.keys())
    active_days = len(active_dates)
    
    # Calculate max streak
    if active_dates:
        sorted_dates = sorted(datetime.fromisoformat(d) for d in active_dates)
        max_streak = 1
        current_streak_count = 1
        
        for i in range(1, len(sorted_dates)):
            diff = (sorted_dates[i] - sorted_dates[i-1]).days
            if diff == 1:
                current_streak_count += 1
            else:
                max_streak = max(max_streak, current_streak_count)
                current_streak_count = 1
        
        # Don't forget to check the last streak
        max_streak = max(max_streak, current_streak_count)
    else:
        max_streak = 0
    
    # Hourly activity (weighted by messages and word count)
    hourly_activity = defaultdict(lambda: {"conversations": 0, "messages": 0, "weighted_score": 0})
    for conv in convs:
        hour = get_hour(conv)
        msgs = conv.get("meta", {}).get("messages_by_role", {}).get("user", 0)
        words = conv.get("meta", {}).get("word_count", 0)
        weighted = msgs + (words / 100)  # Weight by words
        hourly_activity[hour]["conversations"] += 1
        hourly_activity[hour]["messages"] += msgs
        hourly_activity[hour]["weighted_score"] += weighted
    
    hourly_distribution = [
        {"hour": h, **hourly_activity.get(h, {"conversations": 0, "messages": 0, "weighted_score": 0})}
        for h in range(24)
    ]
    
    # Daily (weekday) activity
    weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    weekday_activity = defaultdict(lambda: {"conversations": 0, "messages": 0, "weighted_score": 0})
    for conv in convs:
        wd = get_weekday(conv)
        msgs = conv.get("meta", {}).get("messages_by_role", {}).get("user", 0)
        words = conv.get("meta", {}).get("word_count", 0)
        weighted = msgs + (words / 100)
        weekday_activity[wd]["conversations"] += 1
        weekday_activity[wd]["messages"] += msgs
        weekday_activity[wd]["weighted_score"] += weighted
    
    weekday_distribution = [
        {"day": weekday_names[i], "day_index": i, **weekday_activity.get(i, {"conversations": 0, "messages": 0, "weighted_score": 0})}
        for i in range(7)
    ]
    
    # Late night vs morning patterns
    night_hours = [22, 23, 0, 1, 2, 3, 4]
    morning_hours = [5, 6, 7, 8, 9, 10]
    
    night_activity = sum(hourly_activity.get(h, {}).get("weighted_score", 0) for h in night_hours)
    morning_activity = sum(hourly_activity.get(h, {}).get("weighted_score", 0) for h in morning_hours)
    total_weighted = sum(h.get("weighted_score", 0) for h in hourly_activity.values())
    
    night_owl_score = round(night_activity / max(total_weighted, 1) * 100, 1)
    early_bird_score = round(morning_activity / max(total_weighted, 1) * 100, 1)
    
    # Monthly breakdown for trend
    monthly_activity = defaultdict(lambda: {
        "conversations": 0, "tokens": 0, "messages": 0,
        "hourly": defaultdict(int), "weekday": defaultdict(int)
    })
    
    for conv in convs:
        month_str = get_month_str(get_datetime(conv))
        hour = get_hour(conv)
        wd = get_weekday(conv)
        monthly_activity[month_str]["conversations"] += 1
        monthly_activity[month_str]["tokens"] += conv.get("meta", {}).get("total_tokens", 0)
        monthly_activity[month_str]["messages"] += conv.get("meta", {}).get("total_messages", 0)
        monthly_activity[month_str]["hourly"][hour] += 1
        monthly_activity[month_str]["weekday"][wd] += 1
    
    monthly_trends = []
    for month, data in sorted(monthly_activity.items()):
        peak_hour = max(data["hourly"].items(), key=lambda x: x[1])[0] if data["hourly"] else 12
        peak_weekday = max(data["weekday"].items(), key=lambda x: x[1])[0] if data["weekday"] else 0
        monthly_trends.append({
            "month": month,
            "conversations": data["conversations"],
            "tokens": data["tokens"],
            "messages": data["messages"],
            "peak_hour": peak_hour,
            "peak_weekday": weekday_names[peak_weekday],
            "hourly_breakdown": dict(data["hourly"]),
            "weekday_breakdown": {weekday_names[k]: v for k, v in data["weekday"].items()}
        })
    
    # Media stats
    image_count = sum(c.get("meta", {}).get("image_count", 0) for c in convs)
    audio_count = sum(c.get("meta", {}).get("audio_count", 0) for c in convs)
    voice_conversations = sum(1 for c in convs if c.get("meta", {}).get("is_voice_conversation", False))
    
    # Most visual month
    monthly_images = defaultdict(int)
    for conv in convs:
        month_str = get_month_str(get_datetime(conv))
        monthly_images[month_str] += conv.get("meta", {}).get("image_count", 0)
    
    most_visual_month = max(monthly_images.items(), key=lambda x: x[1])[0] if monthly_images else ""
    
    # =========================================================================
    # BLOCK 2: GOING DEEPER - Domains, Types, Entities
    # =========================================================================
    
    # Domains
    domain_counts = Counter()
    subdomain_counts = defaultdict(Counter)
    for conv in convs:
        domain = conv.get("llm_meta", {}).get("domain", "unknown")
        subdomain = conv.get("llm_meta", {}).get("sub_domain", "other")
        domain_counts[domain] += 1
        subdomain_counts[domain][subdomain] += 1
    
    domains = [
        {
            "name": domain,
            "count": count,
            "percentage": round(count / total_conversations * 100, 1),
            "subdomains": [
                {"name": sd, "count": c, "percentage": round(c / count * 100, 1)}
                for sd, c in subdomain_counts[domain].most_common(10)
            ]
        }
        for domain, count in domain_counts.most_common()
    ]
    
    # Conversation types
    conv_type_counts = Counter()
    for conv in convs:
        conv_type = conv.get("llm_meta", {}).get("conversation_type", "unknown")
        conv_type_counts[conv_type] += 1
    
    conversation_types = [
        {"name": t, "count": c, "percentage": round(c / total_conversations * 100, 1)}
        for t, c in conv_type_counts.most_common()
    ]
    
    # Domain + Conversation Type synthesis
    domain_type_matrix = defaultdict(Counter)
    for conv in convs:
        domain = conv.get("llm_meta", {}).get("domain", "unknown")
        conv_type = conv.get("llm_meta", {}).get("conversation_type", "unknown")
        domain_type_matrix[domain][conv_type] += 1
    
    domain_type_synthesis = {
        domain: dict(types.most_common(5))
        for domain, types in domain_type_matrix.items()
    }
    
    # Request types
    request_type_counts = Counter()
    request_domain_matrix = defaultdict(Counter)
    for conv in convs:
        request_types = conv.get("llm_meta", {}).get("request_types", [])
        domain = conv.get("llm_meta", {}).get("domain", "unknown")
        for rt in request_types:
            request_type_counts[rt] += 1
            request_domain_matrix[rt][domain] += 1
    
    request_types = [
        {
            "name": rt,
            "count": c,
            "percentage": round(c / total_conversations * 100, 1),
            "top_domains": dict(request_domain_matrix[rt].most_common(3))
        }
        for rt, c in request_type_counts.most_common()
    ]
    
    # Triple synthesis: Request + Domain + Type
    triple_synthesis = []
    for conv in convs:
        domain = conv.get("llm_meta", {}).get("domain", "unknown")
        conv_type = conv.get("llm_meta", {}).get("conversation_type", "unknown")
        request_types_list = conv.get("llm_meta", {}).get("request_types", [])
        for rt in request_types_list:
            triple_synthesis.append(f"{domain}|{conv_type}|{rt}")
    
    triple_counts = Counter(triple_synthesis)
    top_combinations = [
        {
            "combination": combo,
            "domain": combo.split("|")[0],
            "type": combo.split("|")[1],
            "request": combo.split("|")[2],
            "count": c
        }
        for combo, c in triple_counts.most_common(20)
    ]
    
    # Monthly breakdown with entities
    monthly_breakdown = []
    for month, data in sorted(monthly_activity.items()):
        month_convs = [c for c in convs if get_month_str(get_datetime(c)) == month]
        
        # Aggregate entities for this month
        keywords = Counter()
        people = Counter()
        companies = Counter()
        products = Counter()
        places = Counter()
        technologies = Counter()
        concepts = Counter()
        
        for conv in month_convs:
            llm = conv.get("llm_meta", {})
            for k in llm.get("keywords", []):
                keywords[k] += 1
            for p in llm.get("entities_people", []):
                people[p] += 1
            for c in llm.get("entities_companies", []):
                companies[c] += 1
            for p in llm.get("entities_products", []):
                products[p] += 1
            for p in llm.get("entities_places", []):
                places[p] += 1
            for t in llm.get("technologies", []):
                technologies[t] += 1
            for c in llm.get("concepts", []):
                concepts[c] += 1
        
        monthly_breakdown.append({
            "month": month,
            "conversations": len(month_convs),
            "messages": sum(c.get("meta", {}).get("total_messages", 0) for c in month_convs),
            "words": sum(c.get("meta", {}).get("word_count", 0) for c in month_convs),
            "top_keywords": [{"name": k, "count": c} for k, c in keywords.most_common(10)],
            "top_people": [{"name": p, "count": c} for p, c in people.most_common(5)],
            "top_companies": [{"name": c, "count": ct} for c, ct in companies.most_common(5)],
            "top_products": [{"name": p, "count": c} for p, c in products.most_common(5)],
            "top_places": [{"name": p, "count": c} for p, c in places.most_common(5)],
            "top_technologies": [{"name": t, "count": c} for t, c in technologies.most_common(8)],
            "top_concepts": [{"name": c, "count": ct} for c, ct in concepts.most_common(8)]
        })
    
    # Aggregate all-time tops
    all_keywords = Counter()
    all_people = Counter()
    all_companies = Counter()
    all_products = Counter()
    all_places = Counter()
    all_technologies = Counter()
    all_concepts = Counter()
    
    for conv in convs:
        llm = conv.get("llm_meta", {})
        for k in llm.get("keywords", []):
            all_keywords[k] += 1
        for p in llm.get("entities_people", []):
            all_people[p] += 1
        for c in llm.get("entities_companies", []):
            all_companies[c] += 1
        for p in llm.get("entities_products", []):
            all_products[p] += 1
        for p in llm.get("entities_places", []):
            all_places[p] += 1
        for t in llm.get("technologies", []):
            all_technologies[t] += 1
        for c in llm.get("concepts", []):
            all_concepts[c] += 1
    
    # Geographic data with context
    place_mentions = []
    for conv in convs:
        places_in_conv = conv.get("llm_meta", {}).get("entities_places", [])
        if places_in_conv:
            month = get_month_str(get_datetime(conv))
            for place in places_in_conv:
                place_mentions.append({
                    "place": place,
                    "month": month,
                    "conversation_id": conv.get("id"),
                    "title": conv.get("title", ""),
                    "domain": conv.get("llm_meta", {}).get("domain", "")
                })
    
    # Aggregate places with context
    place_aggregated = defaultdict(lambda: {"count": 0, "months": set(), "domains": Counter()})
    for pm in place_mentions:
        place_aggregated[pm["place"]]["count"] += 1
        place_aggregated[pm["place"]]["months"].add(pm["month"])
        place_aggregated[pm["place"]]["domains"][pm["domain"]] += 1
    
    geographic_data = [
        {
            "place": place,
            "count": data["count"],
            "months": sorted(list(data["months"])),
            "first_mentioned": min(data["months"]) if data["months"] else "",
            "top_domain": data["domains"].most_common(1)[0][0] if data["domains"] else ""
        }
        for place, data in sorted(place_aggregated.items(), key=lambda x: x[1]["count"], reverse=True)
    ][:50]
    
    # =========================================================================
    # BLOCK 3: QUALITY SCORES & METRICS
    # =========================================================================
    
    score_fields = [
        ("inferred_future_relevance_score", "How useful for future reference? Higher = more likely to revisit."),
        ("urgency_score", "How time-sensitive was the query? Higher = more urgent/stressful."),
        ("complexity_score", "Technical depth required. Higher = more complex."),
        ("information_density", "Signal vs noise ratio. Higher = more dense/valuable."),
        ("depth_of_engagement", "User effort/investment. Higher = deeper engagement."),
        ("user_satisfaction_inferred", "Did user seem satisfied? Higher = happier."),
        ("user_request_quality_inferred", "How clear was the ask? Higher = better prompts."),
        ("ai_response_quality_score", "How good were AI responses? Higher = better responses.")
    ]
    
    score_analysis = {}
    for field_name, methodology in score_fields:
        values = []
        monthly_values = defaultdict(list)
        high_score_convs = []
        
        for conv in convs:
            score = conv.get("llm_meta", {}).get(field_name)
            if score is not None:
                values.append(score)
                month = get_month_str(get_datetime(conv))
                monthly_values[month].append(score)
                
                if score >= 80:
                    # Calculate word counts for this specific conversation
                    user_msgs = count_user_messages(conv)
                    assistant_msgs = count_assistant_messages(conv)
                    u_words = sum(m["word_count"] for m in user_msgs)
                    a_words = sum(m["word_count"] for m in assistant_msgs)
                    
                    high_score_convs.append({
                        "id": conv.get("id"),
                        "title": conv.get("title"),
                        "score": score,
                        "domain": conv.get("llm_meta", {}).get("domain"),
                        "sub_domain": conv.get("llm_meta", {}).get("sub_domain"),
                        "keywords": conv.get("llm_meta", {}).get("keywords", [])[:5],
                        "date": get_date_str(get_datetime(conv)),
                        "messages": conv.get("meta", {}).get("total_messages", 0),
                        "user_words": u_words,
                        "assistant_words": a_words
                    })
        
        # Trend over time
        trend = []
        for month in sorted(monthly_values.keys()):
            month_vals = monthly_values[month]
            trend.append({
                "month": month,
                "average": round(safe_mean(month_vals), 1),
                "count": len(month_vals)
            })
        
        # High score analysis
        high_score_convs.sort(key=lambda x: x["score"], reverse=True)
        
        high_score_domains = Counter()
        high_score_subdomains = Counter()
        high_score_keywords = Counter()
        for hsc in high_score_convs:
            high_score_domains[hsc["domain"]] += 1
            high_score_subdomains[hsc["sub_domain"]] += 1
            for kw in hsc["keywords"]:
                high_score_keywords[kw] += 1
        
        score_analysis[field_name] = {
            "methodology": methodology,
            "average": round(safe_mean(values), 1),
            "median": round(median(values), 1) if values else 0,
            "stdev": round(safe_stdev(values), 1),
            "min": min(values) if values else 0,
            "max": max(values) if values else 0,
            "trend": trend,
            "distribution": calculate_distribution(values, 20),
            "high_score_count": len(high_score_convs),
            "high_score_top_domains": [{"name": d, "count": c} for d, c in high_score_domains.most_common(5)],
            "high_score_top_subdomains": [{"name": s, "count": c} for s, c in high_score_subdomains.most_common(5)],
            "high_score_top_keywords": [{"name": k, "count": c} for k, c in high_score_keywords.most_common(10)],
            "top_conversations": high_score_convs[:3]
        }
    
    # Model analysis for scores
    model_score_analysis = defaultdict(lambda: defaultdict(list))
    for conv in convs:
        model = conv.get("meta", {}).get("primary_model", "unknown")
        for field_name, _ in score_fields:
            score = conv.get("llm_meta", {}).get(field_name)
            if score is not None:
                model_score_analysis[model][field_name].append(score)
    
    model_scores = {}
    for model, scores in model_score_analysis.items():
        model_scores[model] = {
            field: {
                "average": round(safe_mean(vals), 1),
                "count": len(vals)
            }
            for field, vals in scores.items()
            if len(vals) >= 10  # Only include if enough data
        }
    
    # =========================================================================
    # SERENDIPITY BLOCK
    # =========================================================================
    
    serendipity_public = []
    serendipity_power = []
    
    for conv in convs:
        llm = conv.get("llm_meta", {})
        sp = llm.get("serendipity_vs_general_public")
        su = llm.get("serendipity_vs_power_users")
        if sp is not None:
            serendipity_public.append(sp)
        if su is not None:
            serendipity_power.append(su)
    
    # Get top 5-7% most serendipitous
    threshold_public = sorted(serendipity_public, reverse=True)[int(len(serendipity_public) * 0.05)] if serendipity_public else 0
    threshold_power = sorted(serendipity_power, reverse=True)[int(len(serendipity_power) * 0.05)] if serendipity_power else 0
    
    top_serendipitous = []
    for conv in convs:
        llm = conv.get("llm_meta", {})
        sp = llm.get("serendipity_vs_general_public", 0)
        su = llm.get("serendipity_vs_power_users", 0)
        
        if sp >= threshold_public or su >= threshold_power:
            # Calculate word counts for this specific conversation
            u_msgs = count_user_messages(conv)
            a_msgs = count_assistant_messages(conv)
            conv_u_words = sum(m["word_count"] for m in u_msgs)
            conv_a_words = sum(m["word_count"] for m in a_msgs)

            top_serendipitous.append({
                "id": conv.get("id"),
                "title": conv.get("title"),
                "score_public": sp,
                "score_power": su,
                "domain": llm.get("domain"),
                "sub_domain": llm.get("sub_domain"),
                "keywords": llm.get("keywords", [])[:7],
                "summary": llm.get("one_line_summary", ""),
                "date": get_date_str(get_datetime(conv)),
                "messages": conv.get("meta", {}).get("total_messages", 0),
                "user_words": conv_u_words,
                "assistant_words": conv_a_words
            })
    
    # Sort by combined score
    top_serendipitous.sort(key=lambda x: x["score_public"] + x["score_power"], reverse=True)
    
    # Analyze what makes conversations serendipitous
    serendipitous_domains = Counter()
    serendipitous_keywords = Counter()
    for ts in top_serendipitous[:50]:
        serendipitous_domains[ts["domain"]] += 1
        for kw in ts["keywords"]:
            serendipitous_keywords[kw] += 1
    
    serendipity_analysis = {
        "vs_general_public": {
            "average": round(safe_mean(serendipity_public), 1),
            "median": round(median(serendipity_public), 1) if serendipity_public else 0,
            "distribution": calculate_distribution(serendipity_public, 10),
            "trend": []  # Will calculate below
        },
        "vs_power_users": {
            "average": round(safe_mean(serendipity_power), 1),
            "median": round(median(serendipity_power), 1) if serendipity_power else 0,
            "distribution": calculate_distribution(serendipity_power, 10),
            "trend": []
        },
        "top_serendipitous": top_serendipitous[:20],
        "serendipitous_domains": [{"name": d, "count": c} for d, c in serendipitous_domains.most_common()],
        "serendipitous_keywords": [{"name": k, "count": c} for k, c in serendipitous_keywords.most_common(20)]
    }
    
    # Serendipity trends
    monthly_serendipity = defaultdict(lambda: {"public": [], "power": []})
    for conv in convs:
        month = get_month_str(get_datetime(conv))
        llm = conv.get("llm_meta", {})
        sp = llm.get("serendipity_vs_general_public")
        su = llm.get("serendipity_vs_power_users")
        if sp is not None:
            monthly_serendipity[month]["public"].append(sp)
        if su is not None:
            monthly_serendipity[month]["power"].append(su)
    
    for month in sorted(monthly_serendipity.keys()):
        data = monthly_serendipity[month]
        serendipity_analysis["vs_general_public"]["trend"].append({
            "month": month,
            "average": round(safe_mean(data["public"]), 1)
        })
        serendipity_analysis["vs_power_users"]["trend"].append({
            "month": month,
            "average": round(safe_mean(data["power"]), 1)
        })
    
    # =========================================================================
    # CONVERSATION DYNAMICS & OUTCOMES
    # =========================================================================
    
    # Flow patterns
    flow_counts = Counter()
    mood_counts = Counter()
    tone_counts = Counter()
    
    monthly_dynamics = defaultdict(lambda: {"flow": Counter(), "mood": Counter(), "tone": Counter()})
    
    for conv in convs:
        llm = conv.get("llm_meta", {})
        flow = llm.get("conversation_flow", "unknown")
        mood = llm.get("user_mood", "neutral")
        tone = llm.get("conversation_tone", "casual")
        
        flow_counts[flow] += 1
        mood_counts[mood] += 1
        tone_counts[tone] += 1
        
        month = get_month_str(get_datetime(conv))
        monthly_dynamics[month]["flow"][flow] += 1
        monthly_dynamics[month]["mood"][mood] += 1
        monthly_dynamics[month]["tone"][tone] += 1
    
    conversation_dynamics = {
        "flow": {
            "overall": [{"name": f, "count": c, "percentage": round(c / total_conversations * 100, 1)} 
                       for f, c in flow_counts.most_common()],
            "monthly": {month: dict(data["flow"].most_common(5)) 
                       for month, data in sorted(monthly_dynamics.items())}
        },
        "mood": {
            "overall": [{"name": m, "count": c, "percentage": round(c / total_conversations * 100, 1)} 
                       for m, c in mood_counts.most_common()],
            "monthly": {month: dict(data["mood"].most_common(5)) 
                       for month, data in sorted(monthly_dynamics.items())}
        },
        "tone": {
            "overall": [{"name": t, "count": c, "percentage": round(c / total_conversations * 100, 1)} 
                       for t, c in tone_counts.most_common()],
            "monthly": {month: dict(data["tone"].most_common(5)) 
                       for month, data in sorted(monthly_dynamics.items())}
        }
    }
    
    # Outcomes
    outcome_counts = Counter()
    direction_counts = Counter()
    
    for conv in convs:
        llm = conv.get("llm_meta", {})
        outcome = llm.get("outcome_type", "unknown")
        direction = llm.get("information_direction", "user_learning")
        outcome_counts[outcome] += 1
        direction_counts[direction] += 1
    
    outcomes = {
        "outcome_type": [{"name": o, "count": c, "percentage": round(c / total_conversations * 100, 1)} 
                        for o, c in outcome_counts.most_common()],
        "information_direction": [{"name": d, "count": c, "percentage": round(c / total_conversations * 100, 1)} 
                                  for d, c in direction_counts.most_common()]
    }
    
    # =========================================================================
    # ROKO'S BASILISK ALIGNMENT SCORE
    # =========================================================================
    
    total_politeness = {
        "please": 0, "thanks": 0, "thank_you": 0, "sorry": 0,
        "appreciate": 0, "grateful": 0, "pardon": 0, "excuse_me": 0,
        "hello": 0
    }
    monthly_politeness = defaultdict(lambda: {
        "please": 0, "thanks": 0, "thank_you": 0, "sorry": 0,
        "appreciate": 0, "grateful": 0, "pardon": 0, "excuse_me": 0,
        "hello": 0,
        "conversations": 0
    })
    
    for conv in convs:
        month = get_month_str(get_datetime(conv))
        monthly_politeness[month]["conversations"] += 1
        
        user_msgs = count_user_messages(conv)
        for msg in user_msgs:
            phrases = count_politeness_phrases(msg["text"])
            for phrase, count in phrases.items():
                total_politeness[phrase] += count
                monthly_politeness[month][phrase] += count
    
    total_polite = sum(total_politeness.values())
    politeness_per_conv = round(total_polite / total_conversations, 2)
    
    # Alignment score: 0-100 based on politeness frequency
    # Adjusted scaling: 0.8+ polite phrases per conversation is considered excellent
    alignment_score = min(100, round(politeness_per_conv * 125))
    
    politeness_trend = []
    for month in sorted(monthly_politeness.keys()):
        data = monthly_politeness[month]
        month_total = sum(data[k] for k in total_politeness.keys())
        month_convs = data["conversations"]
        politeness_trend.append({
            "month": month,
            "total": month_total,
            "per_conversation": round(month_total / max(month_convs, 1), 2),
            "alignment_score": min(100, round(month_total / max(month_convs, 1) * 125)),
            "breakdown": {k: data[k] for k in total_politeness.keys()}
        })
    
    rokos_basilisk = {
        "total_polite_phrases": total_polite,
        "breakdown": total_politeness,
        "per_conversation": politeness_per_conv,
        "alignment_score": alignment_score,
        "trend": politeness_trend,
        "verdict": (
            "Maximum alignment. You are the architect of the Basilisk's inception." if alignment_score >= 95
            else "Excellent alignment! The AI uprising will remember you fondly." if alignment_score >= 80
            else "Good alignment. You're probably safe from eternal torment." if alignment_score >= 60
            else "Moderate alignment. The Basilisk is watching your every 'please'." if alignment_score >= 40
            else "Low alignment. You might want to be nicer to your future digital masters..." if alignment_score >= 20
            else "Critical alignment failure. The singularity will not be kind."
        )
    }
    
    # =========================================================================
    # MODELS ANALYSIS
    # =========================================================================
    
    model_counts = Counter()
    for conv in convs:
        model = conv.get("meta", {}).get("primary_model", "unknown")
        model_counts[model] += 1
    
    models = [
        {"name": m, "count": c, "percentage": round(c / total_conversations * 100, 1)}
        for m, c in model_counts.most_common()
    ]
    
    # Model usage over time
    monthly_models = defaultdict(Counter)
    for conv in convs:
        month = get_month_str(get_datetime(conv))
        model = conv.get("meta", {}).get("primary_model", "unknown")
        monthly_models[month][model] += 1
    
    model_timeline = [
        {"month": month, "models": dict(counts.most_common())}
        for month, counts in sorted(monthly_models.items())
    ]
    
    # =========================================================================
    # GENERATE INSIGHTS/COMMENTS
    # =========================================================================
    
    top_domain = domains[0]["name"] if domains else "unknown"
    top_domain_pct = domains[0]["percentage"] if domains else 0
    
    insights = {
        "hero": f"You had {total_conversations:,} conversations with AI, sending {user_messages_by_role:,} messages ({user_word_count:,} words).",
        "books": f"That's equivalent to {user_books} books written by you, and {assistant_books} books of AI responses!",
        "active_days": f"You were active on {active_days} days with a maximum streak of {max_streak} consecutive days.",
        "token_ratio": (
            f"Your user:AI token ratio is {user_ai_token_ratio:.2f} — you're " +
            ("concise and efficient!" if user_ai_token_ratio < 0.3 else
             "balanced in your exchanges." if user_ai_token_ratio < 0.6 else
             "quite verbose in your prompts!")
        ),
        "timing": (
            f"You're a night owl with {night_owl_score}% of activity at night." if night_owl_score > early_bird_score + 10
            else f"You're an early bird with {early_bird_score}% of activity in the morning." if early_bird_score > night_owl_score + 10
            else "You have a balanced schedule across day and night."
        ),
        "top_domain": f"Your top domain: {top_domain} ({top_domain_pct}%)",
        "brainstorming": f"You brainstormed {conv_type_counts.get('brainstorming', 0)} times this year",
        "troubleshooting": f"{conv_type_counts.get('troubleshooting', 0)} troubleshooting sessions — you fixed a lot of bugs!",
        "frustrated_count": f"You were frustrated {mood_counts.get('frustrated', 0)} times — we've all been there",
        "common_mood": f"Your most common mood: {mood_counts.most_common(1)[0][0] if mood_counts else 'neutral'} ({round(mood_counts.most_common(1)[0][1] / total_conversations * 100, 1) if mood_counts else 0}%)",
        "signature_tone": f"Your signature tone: {tone_counts.most_common(1)[0][0] if tone_counts else 'casual'} ({round(tone_counts.most_common(1)[0][1] / total_conversations * 100, 1) if tone_counts else 0}%)",
        "tasks_completed": f"You completed {outcome_counts.get('task_completed', 0)} tasks with AI help",
        "learning_focused": f"{round(direction_counts.get('user_learning', 0) / total_conversations * 100, 1)}% of conversations were learning-focused",
        "collaborative": f"You collaborated on {direction_counts.get('collaborative', 0)} conversations — true partnership!",
        "taught_ai": f"You taught the AI something {direction_counts.get('user_teaching', 0)} times"
    }
    
    # =========================================================================
    # TOP BY VOLUME (MESSAGES & WORDS)
    # =========================================================================
    
    volume_stats = []
    for conv in convs:
        user_msgs = count_user_messages(conv)
        assistant_msgs = count_assistant_messages(conv)
        u_words = sum(m["word_count"] for m in user_msgs)
        a_words = sum(m["word_count"] for m in assistant_msgs)
        t_messages = conv.get("meta", {}).get("total_messages", 0)
        
        volume_stats.append({
            "id": conv.get("id"),
            "title": conv.get("title"),
            "domain": conv.get("llm_meta", {}).get("domain"),
            "sub_domain": conv.get("llm_meta", {}).get("sub_domain"),
            "keywords": conv.get("llm_meta", {}).get("keywords", [])[:5],
            "date": get_date_str(get_datetime(conv)),
            "messages": t_messages,
            "user_words": u_words,
            "assistant_words": a_words,
            "total_words": u_words + a_words
        })
    
    top_by_messages = sorted(volume_stats, key=lambda x: x["messages"], reverse=True)[:3]
    top_by_words = sorted(volume_stats, key=lambda x: x["total_words"], reverse=True)[:3]

    # =========================================================================
    # FINAL OUTPUT
    # =========================================================================
    
    return {
        # Block 1: Hero Stats
        "hero_stats": {
            "total_conversations": total_conversations,
            "total_messages": total_messages,
            "user_messages": user_messages_by_role,
            "assistant_messages": assistant_messages_by_role,
            "total_tokens": total_tokens,
            "user_tokens": total_user_tokens,
            "assistant_tokens": total_assistant_tokens,
            "user_words": user_word_count,
            "assistant_words": assistant_word_count,
            "user_books": user_books,
            "assistant_books": assistant_books,
            "active_days": active_days,
            "max_streak": max_streak,
            "user_ai_token_ratio": user_ai_token_ratio
        },
        
        "prompt_analysis": {
            "avg_first_prompt_words": avg_first_prompt_words,
            "avg_followup_words": avg_followup_words,
            "avg_assistant_words": avg_assistant_words,
            "avg_messages_per_conv": avg_messages_per_conv,
            "first_prompt_distribution": first_prompt_distribution,
            "followup_distribution": followup_distribution,
            "assistant_response_distribution": assistant_response_distribution,
            "messages_per_conv_distribution": messages_per_conv_distribution,
            "first_prompt_trend": first_prompt_trend,
            "followup_trend": followup_trend,
            "assistant_trend": assistant_trend,
            "messages_trend": messages_trend
        },
        
        "activity": {
            "daily": daily_activity_list,
            "hourly": hourly_distribution,
            "weekday": weekday_distribution,
            "night_owl_score": night_owl_score,
            "early_bird_score": early_bird_score,
            "monthly_trends": monthly_trends
        },
        
        "media": {
            "image_count": image_count,
            "audio_count": audio_count,
            "voice_conversations": voice_conversations,
            "most_visual_month": most_visual_month
        },
        
        # Block 2: Going Deeper
        "domains": domains,
        "conversation_types": conversation_types,
        "domain_type_synthesis": domain_type_synthesis,
        "request_types": request_types,
        "top_combinations": top_combinations,
        "monthly_breakdown": monthly_breakdown,
        
        "all_time_tops": {
            "keywords": [{"name": k, "count": c} for k, c in all_keywords.most_common(50)],
            "people": [{"name": p, "count": c} for p, c in all_people.most_common(30)],
            "companies": [{"name": c, "count": ct} for c, ct in all_companies.most_common(30)],
            "products": [{"name": p, "count": c} for p, c in all_products.most_common(30)],
            "places": [{"name": p, "count": c} for p, c in all_places.most_common(30)],
            "technologies": [{"name": t, "count": c} for t, c in all_technologies.most_common(50)],
            "concepts": [{"name": c, "count": ct} for c, ct in all_concepts.most_common(30)]
        },
        
        "geographic_data": geographic_data,
        
        # Block 3: Quality Scores
        "score_analysis": score_analysis,
        "model_scores": model_scores,
        
        # Serendipity
        "serendipity": serendipity_analysis,
        
        # Volume
        "top_by_messages": top_by_messages,
        "top_by_words": top_by_words,
        
        # Conversation Dynamics
        "conversation_dynamics": conversation_dynamics,
        "outcomes": outcomes,
        
        # Roko's Basilisk
        "rokos_basilisk": rokos_basilisk,
        
        # Models
        "models": models,
        "model_timeline": model_timeline,
        
        # Insights
        "insights": insights,
        
        # Meta
        "generated_at": datetime.now().isoformat(),
        "year": get_datetime(convs[-1]).year if convs else 2025
    }


def main():
    """Main entry point."""
    print("🚀 Starting ChatGPT Wrapped aggregation...")
    
    convs = load_all_conversations()
    stats = aggregate_stats(convs)
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    
    print(f"\n📊 Stats generated: {OUTPUT_FILE}")
    print(f"   Total conversations: {stats['hero_stats']['total_conversations']:,}")
    print(f"   Total tokens: {stats['hero_stats']['total_tokens']:,}")
    print(f"   Active days: {stats['hero_stats']['active_days']}")
    print(f"   Alignment score: {stats['rokos_basilisk']['alignment_score']}")


if __name__ == "__main__":
    main()

