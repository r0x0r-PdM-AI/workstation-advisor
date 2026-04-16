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
    <div className="bg-gray-900 rounded-lg border border-gray-800 p-4 flex items-start justify-between gap-3">
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
            className="w-full bg-gray-800 border border-gray-700 rounded px-2 py-1 text-white focus:outline-none focus:border-blue-500"
          />
        ) : (
          <h3 className="font-semibold text-white truncate">{profile.name}</h3>
        )}
        <p className="text-sm text-gray-400 mt-1 truncate">
          {profile.workload_name} · {profile.scale_label}
        </p>
      </div>

      <div className="flex items-center gap-2 shrink-0">
        <button
          type="button"
          onClick={() => {
            setDraftName(profile.name);
            setIsEditing(true);
          }}
          className="p-2 text-gray-300 hover:text-white hover:bg-gray-800 rounded cursor-pointer"
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
          className="p-2 text-red-300 hover:text-red-200 hover:bg-gray-800 rounded cursor-pointer"
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
