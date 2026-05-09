import { useRef, useState } from "react";

type Profile = {
  id: number;
  name: string;
  workload_id: number;
  workload_name: string;
  scale_level: number;
  scale_label: string;
  created_at: string;
};

type ProfileCardProps = {
  profile: Profile;
  onRename: (id: number, newName: string) => void;
  onDelete: (id: number) => void;
};

export default function ProfileCard({ profile, onRename, onDelete }: ProfileCardProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [draftName, setDraftName] = useState(profile.name);
  const cancelledRef = useRef<boolean>(false);

  function handleSave() {
    cancelledRef.current = false;
    setIsEditing(false);
    onRename(profile.id, draftName);
  }

  function handleCancel() {
    setDraftName(profile.name);
    cancelledRef.current = true;
    setIsEditing(false);
  }

  function handleDelete() {
    if (window.confirm("Delete this profile?")) {
      onDelete(profile.id);
    }
  }

  return (
    <div className="flex items-start justify-between gap-3 rounded-2xl border border-gray-800 bg-gray-900 p-5 sm:p-6">
      <div className="min-w-0 flex-1">
        {isEditing ? (
          <input
            autoFocus
            type="text"
            value={draftName}
            onChange={(e) => setDraftName(e.target.value)}
            onBlur={() => {
              if (cancelledRef.current) {
                cancelledRef.current = false;
                return;
              }
              handleSave();
            }}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                e.preventDefault();
                handleSave();
              }
              if (e.key === "Escape") {
                e.preventDefault();
                handleCancel();
              }
            }}
            className="w-full rounded-lg border border-gray-700 bg-gray-950 px-3 py-2 text-sm text-white outline-none transition focus:border-[#0076CE] focus:ring-2 focus:ring-[#0076CE]/20 sm:text-base"
          />
        ) : (
          <h3 className="truncate text-sm font-semibold text-white sm:text-base">
            {profile.name}
          </h3>
        )}
        <p className="mt-1 truncate text-sm text-gray-400">
          {profile.workload_name} · {profile.scale_label}
        </p>
      </div>

      <div className="flex shrink-0 items-center gap-2">
        <button
          type="button"
          onClick={() => {
            setDraftName(profile.name);
            setIsEditing(true);
          }}
          className="cursor-pointer rounded-lg p-2 text-gray-300 transition hover:bg-gray-800 hover:text-white focus:outline-none focus:ring-2 focus:ring-[#0076CE]/20"
          aria-label="Rename profile"
          title="Rename"
        >
          <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 20h9" />
            <path d="m16.5 3.5 4 4L7 21H3v-4z" />
          </svg>
        </button>
        <button
          type="button"
          onClick={handleDelete}
          className="cursor-pointer rounded-lg p-2 text-red-300 transition hover:bg-gray-800 hover:text-red-200 focus:outline-none focus:ring-2 focus:ring-red-900/40"
          aria-label="Delete profile"
          title="Delete"
        >
          <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M3 6h18" />
            <path d="M8 6V4h8v2" />
            <path d="M19 6l-1 14H6L5 6" />
            <path d="M10 11v6" />
            <path d="M14 11v6" />
          </svg>
        </button>
      </div>
    </div>
  );
}