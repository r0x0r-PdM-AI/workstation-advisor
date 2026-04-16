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
    return <div className="p-6 text-white">Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-950 px-4 py-8">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-2xl text-white font-semibold mb-6">Dashboard</h1>

        {error && <p className="text-sm text-red-400 mb-4">{error}</p>}

        {profiles.length === 0 ? (
          <p className="text-gray-300">
            No saved profiles yet. <Link to="/" className="text-blue-400 hover:text-blue-300">Go to Advisor</Link>
          </p>
        ) : (
          <div className="space-y-3">
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
