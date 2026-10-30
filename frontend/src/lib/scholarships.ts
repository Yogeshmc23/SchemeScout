import { api } from "./api";
import type { AgentResult, ExtractionSnapshot, ResearchRun, Scholarship } from "./types";

export const scholarships = {
  list: (signal?: AbortSignal) => api<Scholarship[]>("scholarships", undefined, signal),
  detail: (id: number, signal?: AbortSignal) => api<Scholarship>(`scholarships/${id}`, undefined, signal),
  history: (id: number, signal?: AbortSignal) => api<ExtractionSnapshot[]>(`scholarships/${id}/history`, undefined, signal),
};
export const researchHistory = {
  list: (signal?: AbortSignal) => api<ResearchRun[]>("research/history", undefined, signal),
  detail: (id: string, signal?: AbortSignal) => api<AgentResult>(`research/history/${encodeURIComponent(id)}`, undefined, signal),
};
