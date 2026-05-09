import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { apiFetch } from "../api/client";
import { deleteProfile, updateProfile } from "../api/profiles";
import ProfileCard from "../components/ProfileCard";

type Profile = {
  id: number;
  name: string;
  workload_id: number;
  workload_name: string;
  scale_level: number;
  scale_label: string;
  created_at: string;
};

export default function DashboardPage() {
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadProfiles() {
      setLoading(true);
      setError(null);
      try {
        const res = await apiFetch("/api/profiles");
        if (!res.ok) {
          throw new Error("Failed to load profiles");
        }
        const data: Profile[] = await res.json();
        setProfiles(data);
      } catch {
        setError("Failed to load profiles");
      } finally {
        setLoading(false);
      }
    }

    void loadProfiles();
  }, []);

  async function handleRename(id: number, newName: string) {
    const original = profiles.find((profile) => profile.id === id);
    if (!original) {
      return;
    }

    setError(null);
    setProfiles((prev) =>
      prev.map((profile) =>
        profile.id === id ? { ...profile, name: newName } : profile,
      ),
    );

    try {
      await updateProfile(id, newName);
      setError(null);
    } catch {
      setProfiles((prev) =>
        prev.map((profile) =>
          profile.id === id ? { ...profile, name: original.name } : profile,
        ),
      );
      setError("Failed to rename profile");
    }
  }

  async function handleDelete(id: number) {
    const originalIndex = profiles.findIndex((profile) => profile.id === id);
    if (originalIndex === -1) {
      return;
    }

    const original = profiles[originalIndex];

    setError(null);
    setProfiles((prev) => prev.filter((profile) => profile.id !== id));

    try {
      await deleteProfile(id);
      setError(null);
    } catch {
      setProfiles((prev) => {
        const next = [...prev];
        next.splice(originalIndex, 0, original);
        return next;
      });
      setError("Failed to delete profile");
    }
  }

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-950 px-4">
        <p className="text-sm text-gray-400">Loading saved profiles…</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-950 px-4 py-10 sm:py-12">
      <div className="mx-auto max-w-2xl">
        <header className="mb-6">
          <h1 className="text-2xl font-semibold tracking-tight text-white">
            Dashboard
          </h1>
          <p className="mt-2 text-sm text-gray-400">
            Your saved workload profiles
          </p>
        </header>

        {error && (
          <div className="mb-4 rounded-lg border border-red-900/60 bg-red-950/30 px-3 py-3">
            <p className="text-sm leading-5 text-red-300">{error}</p>
          </div>
        )}

        {profiles.length === 0 ? (
          <div className="rounded-2xl border border-gray-800 bg-gray-900 px-5 py-10 text-center sm:px-6">
            <h2 className="text-base font-semibold text-white">
              No saved profiles yet
            </h2>
            <p className="mx-auto mt-2 max-w-sm text-sm leading-6 text-gray-400">
              Save a workload recommendation from the advisor to see it here.
            </p>
            <Link
              to="/"
              className="mt-5 inline-flex text-sm font-medium text-gray-200 underline decoration-gray-600 underline-offset-4 transition hover:text-white hover:decoration-gray-300"
            >
              Go to Advisor
            </Link>
          </div>
        ) : (
          <div className="flex flex-col gap-4">
            {profiles.map((profile) => (
              <ProfileCard
                key={profile.id}
                profile={profile}
                onRename={handleRename}
                onDelete={handleDelete}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}