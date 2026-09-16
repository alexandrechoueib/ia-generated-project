import type {
  Debate,
  DebateCreatePayload,
  DebateCreateResponse,
} from "../types/debate";

/**
 * EXPO_PUBLIC_API_URL :
 * - iOS sim / web : http://localhost:8000
 * - Android emulator : http://10.0.2.2:8000
 * - Device physique : http://<IP-LAN-du-PC>:8000
 */
const API_URL =
  process.env.EXPO_PUBLIC_API_URL?.replace(/\/$/, "") || "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
  });

  let body: unknown = null;
  const text = await res.text();
  try {
    body = text ? JSON.parse(text) : null;
  } catch {
    body = { detail: text || res.statusText };
  }

  if (!res.ok) {
    const detail =
      typeof body === "object" &&
      body &&
      "detail" in body &&
      typeof (body as { detail: unknown }).detail === "string"
        ? (body as { detail: string }).detail
        : `Erreur HTTP ${res.status}`;
    throw new Error(detail);
  }

  return body as T;
}

export function getApiUrl(): string {
  return API_URL;
}

export function createDebate(
  payload: DebateCreatePayload
): Promise<DebateCreateResponse> {
  return request<DebateCreateResponse>("/debates", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getDebate(id: string): Promise<Debate> {
  return request<Debate>(`/debates/${id}`);
}

export function runDebate(id: string): Promise<Debate> {
  return request<Debate>(`/debates/${id}/run`, { method: "POST" });
}
