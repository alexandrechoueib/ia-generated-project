export type Complexity = "tout_public" | "intermediaire" | "expert";

export type Speaker = "grok" | "gpt" | "summary";

export type DebateStatus = "created" | "running" | "completed" | "failed";

export interface Message {
  index: number;
  speaker: Speaker;
  content: string;
  side?: "pour" | "contre" | "neutre" | null;
}

export interface Debate {
  id: string;
  topic: string;
  total_messages: number;
  complexity: Complexity;
  status: DebateStatus;
  messages: Message[];
  summary?: string | null;
  remaining_turns: number;
  error?: string | null;
}

export interface DebateCreatePayload {
  topic: string;
  total_messages: number;
  complexity: Complexity;
}

export interface DebateCreateResponse {
  id: string;
  topic: string;
  total_messages: number;
  complexity: Complexity;
  status: DebateStatus;
}
