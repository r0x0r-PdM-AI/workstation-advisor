import { apiFetch } from "./client";

export async function naturalLanguageRecommend(description: string) {
  const res = await apiFetch("/api/recommend/natural", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ description }),
  });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.error || "Request failed");
  }
  return data;
}
