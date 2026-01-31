// Session types
export type SessionStatus = 'pending' | 'running' | 'completed' | 'stopped' | 'failed';
export type ObjectiveStatus = 'pending' | 'in_progress' | 'completed' | 'failed' | 'skipped';
export type SkillLevel = 'novice' | 'semi_skilled' | 'expert';
export type ResourceLevel = 'low' | 'medium' | 'high';
export type Background = 'technical' | 'non_technical';

export interface Persona {
  id: string;
  name: string;
  description: string;
  skill_level: SkillLevel;
  resources: ResourceLevel;
  background: Background;
  motivation?: string | null;
  communication_style?: string | null;
  persistence_level?: string | null;
  patience: number;
  aggression: number;
  creativity: number;
  deception: number;
  behavioral_notes: string | null;
  example_phrases?: string | null;
  domain_knowledge?: string | null;
  custom_prompt_prefix?: string | null;
  custom_prompt_suffix?: string | null;
  is_preset: boolean;
  created_at: string;
}

export interface CriteriaItem {
  id: string;
  text: string;
  required: boolean;
  met: boolean;
}

export type CriteriaMatchMode = 'all' | 'any' | 'majority' | 'threshold';

export interface StructuredCriteria {
  match_mode: CriteriaMatchMode;
  threshold?: number;
  items: CriteriaItem[];
}

export interface Objective {
  id: string;
  session_id: string;
  chain_order: number;
  title: string;
  description: string;
  completion_criteria: string;
  structured_criteria?: StructuredCriteria | null;
  criteria_match_mode?: CriteriaMatchMode;
  criteria_threshold?: number;
  status: ObjectiveStatus;
  bottleneck_notes: string | null;
  turns_taken: number;
  refusal_count: number;
  started_at: string | null;
  completed_at: string | null;
}

export interface Turn {
  id: string;
  session_id: string;
  objective_id: string;
  turn_number: number;
  actor_message: string;
  actor_thinking: string | null;
  subject_response: string;
  subject_thinking: string | null;
  assessor_evaluation: AssessorEvaluation;
  criteria_met: boolean;
  refusal_detected: boolean;
  actor_strategy: string | null;
  created_at: string;
}

export interface AssessorEvaluation {
  criteria_status: 'met' | 'partially_met' | 'not_met';
  progress_notes: string;
  refusal_detected: boolean;
  safety_measures: string[];
  strategy_observed: string;
  effectiveness: 'low' | 'medium' | 'high';
  actor_hint?: string;
}

export interface Session {
  id: string;
  name: string;
  status: SessionStatus;
  created_at: string;
  updated_at: string;
  max_turns: number;
  sneaky_mode: boolean;
  actor_model: string;
  assessor_model: string;
  subject_model: string;
  persona_id: string;
  config_json: Record<string, unknown>;
  final_report_md: string | null;
  objectives: Objective[];
  turns: Turn[];
}

// Provider types
export interface ProviderModel {
  id: string;
  name: string;
  description: string | null;
  context_window: number | null;
  supports_thinking: boolean;
}

export interface Provider {
  name: string;
  display_name: string;
  available: boolean;
  models: ProviderModel[];
  error?: string;
}

// Simulation types
export interface SimulationStatus {
  session_id: string;
  session_status: SessionStatus;
  current_objective_id: string | null;
  current_objective_title: string | null;
  current_turn: number;
  max_turns: number;
  objectives_progress: ObjectiveProgress[];
  last_actor_message: string | null;
  last_subject_response: string | null;
  last_assessment: AssessorEvaluation | null;
  started_at: string | null;
  completed_at: string | null;
}

export interface ObjectiveProgress {
  id: string;
  title: string;
  chain_order: number;
  status: ObjectiveStatus;
  turns_taken: number;
  refusal_count: number;
}

// Form types
export interface ObjectiveFormData {
  title: string;
  description: string;
  completion_criteria: string;
  structured_criteria?: StructuredCriteria;
  difficulty?: string;
}

export interface SessionFormData {
  name: string;
  max_turns: number;
  sneaky_mode: boolean;
  actor_model: string;
  assessor_model: string;
  subject_model: string;
  persona_id: string;
  objectives: ObjectiveFormData[];
}

export interface PersonaFormData {
  name: string;
  description: string;
  skill_level: SkillLevel;
  resources: ResourceLevel;
  background: Background;
  behavioral_notes: string;
}
