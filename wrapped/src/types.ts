/**
 * TypeScript interfaces for ChatGPT Wrapped 2025
 * Matches the output structure from aggregate.py
 */

export interface Distribution {
  bin_start: number;
  bin_end: number;
  count: number;
  percentage: number;
}

export interface NameCount {
  name: string;
  count: number;
  percentage?: number;
}

export interface NameCountWithSubs extends NameCount {
  subdomains?: NameCount[];
  top_domains?: Record<string, number>;
}

export interface DailyActivity {
  date: string;
  count: number;
  tokens: number;
  messages: number;
}

export interface HourlyActivity {
  hour: number;
  conversations: number;
  messages: number;
  weighted_score: number;
}

export interface WeekdayActivity {
  day: string;
  day_index: number;
  conversations: number;
  messages: number;
  weighted_score: number;
}

export interface MonthlyTrend {
  month: string;
  conversations: number;
  tokens: number;
  messages: number;
  peak_hour: number;
  peak_weekday: string;
  hourly_breakdown: Record<number, number>;
  weekday_breakdown: Record<string, number>;
}

export interface MonthlyBreakdown {
  month: string;
  conversations: number;
  messages: number;
  words: number;
  top_keywords: NameCount[];
  top_people: NameCount[];
  top_companies: NameCount[];
  top_products: NameCount[];
  top_places: NameCount[];
  top_technologies: NameCount[];
  top_concepts: NameCount[];
}

export interface GeographicPlace {
  place: string;
  count: number;
  months: string[];
  first_mentioned: string;
  top_domain: string;
}

export interface ScoreTrend {
  month: string;
  average: number;
  count?: number;
}

export interface HighScoreConv {
  id: string;
  title: string;
  score: number;
  domain: string;
  sub_domain: string;
  keywords: string[];
  date: string;
  messages: number;
  user_words: number;
  assistant_words: number;
}

export interface VolumeConv {
  id: string;
  title: string;
  domain: string;
  sub_domain: string;
  keywords: string[];
  date: string;
  messages: number;
  user_words: number;
  assistant_words: number;
  total_words: number;
}

export interface ScoreAnalysis {
  methodology: string;
  average: number;
  median: number;
  stdev: number;
  min: number;
  max: number;
  trend: ScoreTrend[];
  distribution: Distribution[];
  high_score_count: number;
  high_score_top_domains: NameCount[];
  high_score_top_subdomains: NameCount[];
  high_score_top_keywords: NameCount[];
  top_conversations: HighScoreConv[];
}

export interface SerendipitousConv {
  id: string;
  title: string;
  score_public: number;
  score_power: number;
  domain: string;
  sub_domain: string;
  keywords: string[];
  summary: string;
  date: string;
  messages: number;
  user_words: number;
  assistant_words: number;
}

export interface SerendipitySection {
  average: number;
  median: number;
  distribution: Distribution[];
  trend: ScoreTrend[];
}

export interface SerendipityAnalysis {
  vs_general_public: SerendipitySection;
  vs_power_users: SerendipitySection;
  top_serendipitous: SerendipitousConv[];
  serendipitous_domains: NameCount[];
  serendipitous_keywords: NameCount[];
}

export interface DynamicsSection {
  overall: NameCount[];
  monthly: Record<string, Record<string, number>>;
}

export interface ConversationDynamics {
  flow: DynamicsSection;
  mood: DynamicsSection;
  tone: DynamicsSection;
}

export interface PolitenessBreakdown {
  please: number;
  thanks: number;
  thank_you: number;
  sorry: number;
  appreciate: number;
  grateful: number;
  pardon: number;
  excuse_me: number;
  hello: number;
}

export interface PolitenessTrend {
  month: string;
  total: number;
  per_conversation: number;
  alignment_score: number;
  breakdown: PolitenessBreakdown;
}

export interface RokosBasilisk {
  total_polite_phrases: number;
  breakdown: PolitenessBreakdown;
  per_conversation: number;
  alignment_score: number;
  trend: PolitenessTrend[];
  verdict: string;
}

export interface TopCombination {
  combination: string;
  domain: string;
  type: string;
  request: string;
  count: number;
}

export interface ModelTimeline {
  month: string;
  models: Record<string, number>;
}

export interface WrappedStats {
  hero_stats: {
    total_conversations: number;
    total_messages: number;
    user_messages: number;
    assistant_messages: number;
    total_tokens: number;
    user_tokens: number;
    assistant_tokens: number;
    user_words: number;
    assistant_words: number;
    user_books: number;
    assistant_books: number;
    active_days: number;
    max_streak: number;
    user_ai_token_ratio: number;
  };

  prompt_analysis: {
    avg_first_prompt_words: number;
    avg_followup_words: number;
    avg_assistant_words: number;
    avg_messages_per_conv: number;
    first_prompt_distribution: Distribution[];
    followup_distribution: Distribution[];
    assistant_response_distribution: Distribution[];
    messages_per_conv_distribution: Distribution[];
  };

  activity: {
    daily: DailyActivity[];
    hourly: HourlyActivity[];
    weekday: WeekdayActivity[];
    night_owl_score: number;
    early_bird_score: number;
    monthly_trends: MonthlyTrend[];
  };

  media: {
    image_count: number;
    audio_count: number;
    voice_conversations: number;
    most_visual_month: string;
  };

  domains: NameCountWithSubs[];
  conversation_types: NameCount[];
  domain_type_synthesis: Record<string, Record<string, number>>;
  request_types: NameCountWithSubs[];
  top_combinations: TopCombination[];
  monthly_breakdown: MonthlyBreakdown[];

  all_time_tops: {
    keywords: NameCount[];
    people: NameCount[];
    companies: NameCount[];
    products: NameCount[];
    places: NameCount[];
    technologies: NameCount[];
    concepts: NameCount[];
  };

  geographic_data: GeographicPlace[];

  score_analysis: Record<string, ScoreAnalysis>;
  model_scores: Record<string, Record<string, { average: number; count: number }>>;

  top_by_messages: VolumeConv[];
  top_by_words: VolumeConv[];

  serendipity: SerendipityAnalysis;

  conversation_dynamics: ConversationDynamics;
  outcomes: {
    outcome_type: NameCount[];
    information_direction: NameCount[];
  };

  rokos_basilisk: RokosBasilisk;

  models: NameCount[];
  model_timeline: ModelTimeline[];

  insights: Record<string, string>;

  generated_at: string;
  year: number;
}

