import { apiFetch } from "./client";

export type SavedProfile = {
  id: number;
  name: string;
  workload_id: number;
  workload_name: string;
  scale_level: number;
  scale_label: string;
  created_at: string;
};

type SaveProfileInput = {
  name: string;
  workload_id: number;
  scale_level: number;
};

export async function saveProfile(payload: SaveProfileInput): Promise<SavedProfile> {
  const res = await apiFetch("/api/profiles", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    throw new Error("Failed to save profile");
  }

  return res.json();
}

export async function updateProfile(id: number, name: string): Promise<void> {
  const res = await apiFetch(`/api/profiles/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  });

  if (!res.ok) {
    throw new Error("Failed to update profile");
  }
}

export async function deleteProfile(id: number): Promise<void> {
  const res = await apiFetch(`/api/profiles/${id}`, {
    method: "DELETE",
  });

  if (!res.ok) {
    throw new Error("Failed to delete profile");
  }
}
