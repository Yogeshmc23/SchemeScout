import { validResponse } from "./contracts";

export class ApiError extends Error {
  constructor(message: string, public readonly status?: number) { super(message); this.name = "ApiError"; }
}
export async function api<T>(path: string, body?: unknown, signal?: AbortSignal): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`/api/v1/${path}`, {
      method: body === undefined ? "GET" : "POST",
      headers: { "Content-Type": "application/json" },
      ...(body === undefined ? {} : { body: JSON.stringify(body) }),
      signal: signal ? AbortSignal.any([signal, AbortSignal.timeout(390000)]) : AbortSignal.timeout(390000),
    });
  } catch (error) {
    if (signal?.aborted) throw new ApiError("Request cancelled.");
    if (error instanceof Error && ["TimeoutError", "AbortError"].includes(error.name)) {
      throw new ApiError("The request timed out. Some scholarship records may already have been saved; check stored results before retrying.");
    }
    throw new ApiError("Could not reach SchemeRadar. Check your connection and backend service, then retry.");
  }
  const data: unknown = await response.json().catch(() => null);
  if (!response.ok) {
    const detail = typeof data === "object" && data !== null && "detail" in data ? data.detail : null;
    const message = typeof detail === "string" ? detail :
      Array.isArray(detail) ? detail.map(e => typeof e?.msg === "string" ? e.msg : "Invalid request").join("; ") :
      `Request failed (${response.status}). Check backend connectivity.`;
    throw new ApiError(message, response.status);
  }
  if (!validResponse(path, data)) throw new ApiError("The server returned an invalid response. No results were accepted; check the API contract.", 502);
  return data as T;
}
