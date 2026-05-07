import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { apiFetch } from "../api/client";
import { naturalLanguageRecommend } from "../api/recommend";
import { useAuth } from "../context/useAuth";

type Workload = { id: number; name: string };
type Vertical = { id: number; name: string; workloads: Workload[] };
type Industry = { id: number; name: string; verticals: Vertical[] };
type Archetype = { id: number; name: string; industries: Industry[] };

type Selections = {
  archetype?: Archetype;
  industry?: Industry;
  vertical?: Vertical;
  workload?: Workload;
  scale_level?: number;
};

type Recommendation = {
  product: string;
  brand: string;
  form_factor: string;
  notes: string;
  rank: number;
  explanation?: string;
};

type RecommendationResponse = {
  recommendations: Recommendation[];
  message: string;
  scale_label: string;
  workload: string;
};

type NLRecommendationResponse = {
  recommendations: Recommendation[];
  matched_workload: string;
  workload_id: number;
  scale_level: number;
};

const SCALE_OPTIONS = [
  { id: 1, name: "Starter" },
  { id: 2, name: "Professional" },
  { id: 3, name: "Enterprise" },
];

const SCALE_LABELS: Record<number, string> = {
  1: "Starter",
  2: "Professional",
  3: "Enterprise",
};

const STEP_NAMES = ["Archetype", "Industry", "Vertical", "Workload", "Scale"];

export default function AdvisorPage() {
  const { user } = useAuth();

  const [taxonomy, setTaxonomy] = useState<Archetype[]>([]);
  const [step, setStep] = useState(1);
  const [selections, setSelections] = useState<Selections>({});
  const [recommendations, setRecommendations] = useState<Recommendation[] | null>(null);
  const [responseMessage, setResponseMessage] = useState<string | null>(null);
  const [profileName, setProfileName] = useState("");
  const [saveStatus, setSaveStatus] = useState<"idle" | "saving" | "saved" | "error">("idle");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [mode, setMode] = useState<"nl" | "stepper">("nl");
  const [nlDescription, setNlDescription] = useState("");
  const [nlLoading, setNlLoading] = useState(false);
  const [nlError, setNlError] = useState<string | null>(null);
  const [matchedWorkload, setMatchedWorkload] = useState<string | null>(null);
  const [nlWorkloadId, setNlWorkloadId] = useState<number | null>(null);
  const [nlScaleLevel, setNlScaleLevel] = useState<number | null>(null);

  useEffect(() => {
    apiFetch("/api/taxonomy")
      .then((res) => res.json())
      .then((data) => setTaxonomy(data))
      .catch(() => setError("Failed to load taxonomy"));
  }, []);

  async function handleNLSubmit() {
    if (!nlDescription.trim()) return;
    setNlLoading(true);
    setNlError(null);
    try {
      const data: NLRecommendationResponse =
        await naturalLanguageRecommend(nlDescription);
      setRecommendations(data.recommendations);
      setMatchedWorkload(data.matched_workload);
      setNlWorkloadId(data.workload_id);
      setNlScaleLevel(data.scale_level);
      setProfileName(
        `${data.matched_workload} — ${SCALE_LABELS[data.scale_level] ?? data.scale_level}`
      );
      setSaveStatus("idle");
      setResponseMessage(null);
    } catch (err) {
      setNlError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setNlLoading(false);
    }
  }

  async function fetchRecommendations(scaleLevel: number) {
    if (!selections.workload) return;
    setLoading(true);
    setError(null);
    try {
      const res = await apiFetch("/api/recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          workload_id: selections.workload.id,
          scale_level: scaleLevel,
        }),
      });
      const data: RecommendationResponse = await res.json();
      setRecommendations(data.recommendations);
      setResponseMessage(data.message ?? null);
      setProfileName(`${data.workload} — ${data.scale_label}`);
      setSaveStatus("idle");
    } catch {
      setError("Failed to fetch recommendations");
    } finally {
      setLoading(false);
    }
  }

  async function handleSaveProfile() {
    const workloadId = selections.workload?.id ?? nlWorkloadId;
    const scaleLevel = selections.scale_level ?? nlScaleLevel;
    if (!workloadId || scaleLevel === undefined || scaleLevel === null) return;
    setSaveStatus("saving");
    try {
      const res = await apiFetch("/api/profiles", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: profileName,
          workload_id: workloadId,
          scale_level: scaleLevel,
        }),
      });
      setSaveStatus(res.ok ? "saved" : "error");
    } catch {
      setSaveStatus("error");
    }
  }

  function handleSelectArchetype(archetype: Archetype) {
    setSelections({ archetype });
    setStep(2);
  }

  function handleSelectIndustry(industry: Industry) {
    setSelections((s) => ({ archetype: s.archetype, industry }));
    setStep(3);
  }

  function handleSelectVertical(vertical: Vertical) {
    setSelections((s) => ({ archetype: s.archetype, industry: s.industry, vertical }));
    setStep(4);
  }

  function handleSelectWorkload(workload: Workload) {
    setSelections((s) => ({
      archetype: s.archetype,
      industry: s.industry,
      vertical: s.vertical,
      workload,
    }));
    setStep(5);
  }

  function handleSelectScale(scale: { id: number; name: string }) {
    setSelections((s) => ({ ...s, scale_level: scale.id }));
    fetchRecommendations(scale.id);
  }

  function handleBack() {
    if (recommendations) {
      setRecommendations(null);
      setResponseMessage(null);
      setSelections({});
      setStep(1);
      setMatchedWorkload(null);
      setNlWorkloadId(null);
      setNlScaleLevel(null);
      setNlDescription("");
      setNlError(null);
      setMode("nl");
    } else {
      setStep((s) => s - 1);
    }
  }

  function getStepOptions(): { id: number; name: string }[] {
    if (step === 1) return taxonomy;
    if (step === 2) return selections.archetype?.industries ?? [];
    if (step === 3) return selections.industry?.verticals ?? [];
    if (step === 4) return selections.vertical?.workloads ?? [];
    return SCALE_OPTIONS;
  }

  function getSelectedId(): number | undefined {
    if (step === 1) return selections.archetype?.id;
    if (step === 2) return selections.industry?.id;
    if (step === 3) return selections.vertical?.id;
    if (step === 4) return selections.workload?.id;
    return selections.scale_level;
  }

  function handleCardClick(option: { id: number; name: string }) {
    if (step === 1) handleSelectArchetype(option as Archetype);
    else if (step === 2) handleSelectIndustry(option as Industry);
    else if (step === 3) handleSelectVertical(option as Vertical);
    else if (step === 4) handleSelectWorkload(option as Workload);
    else handleSelectScale(option);
  }

  const selectedId = getSelectedId();

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center">
        <p className="text-white text-lg">Loading recommendations...</p>
      </div>
    );
  }

  if (recommendations) {
    return (
      <div className="min-h-screen bg-gray-950 px-4 py-10">
        <div className="max-w-2xl mx-auto">
          <button
            onClick={handleBack}
            className="text-gray-400 hover:text-white mb-6 text-sm cursor-pointer"
          >
            ← Start Over
          </button>
          <h2 className="text-white text-2xl font-semibold mb-6">
            Recommended Workstations
          </h2>
          {matchedWorkload && (
            <p className="text-gray-400 text-sm mb-2">
              Matched to:{" "}
              <span className="text-blue-400 font-medium">{matchedWorkload}</span>
              {" · "}
              <span className="text-gray-400">
                {SCALE_LABELS[nlScaleLevel ?? 0] ?? ""}
              </span>
            </p>
          )}
          {recommendations.length === 0 ? (
            <div className="bg-gray-800 text-gray-300 rounded p-4">
              {responseMessage}
            </div>
          ) : (
          <div className="flex flex-col gap-4">
            {recommendations.map((rec, i) => (
              <div key={i} className="bg-gray-900 rounded-lg p-6 text-white">
                <div className="flex items-center gap-3 mb-1">
                  <h3 className="text-xl font-semibold">
                    {rec.product} — {rec.brand}
                  </h3>
                  <span className="text-xs bg-blue-600 text-white px-2 py-0.5 rounded-full">
                    Match #{rec.rank}
                  </span>
                </div>
                <p className="text-gray-400 text-sm mb-2">{rec.form_factor}</p>
                <p className="text-gray-300">{rec.notes}</p>
                {rec.explanation && (
                  <p className="text-blue-300 text-sm mt-3 italic">{rec.explanation}</p>
                )}
              </div>
            ))}
          </div>
          )}
          <div className="mt-6 pt-6 border-t border-gray-800">
            {user ? (
              <div className="flex flex-col gap-3">
                <input
                  type="text"
                  value={profileName}
                  onChange={(e) => setProfileName(e.target.value)}
                  className="bg-gray-800 border border-gray-600 rounded px-3 py-2 text-white focus:outline-none focus:border-blue-500"
                />
                <button
                  onClick={handleSaveProfile}
                  disabled={saveStatus === "saving" || saveStatus === "saved"}
                  className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium py-2 px-4 rounded cursor-pointer w-fit"
                >
                  {saveStatus === "saving" ? "Saving..." : "Save Profile"}
                </button>
                {saveStatus === "saved" && (
                  <p className="text-green-400 text-sm">Profile saved!</p>
                )}
                {saveStatus === "error" && (
                  <p className="text-red-400 text-sm">Failed to save. Try again.</p>
                )}
              </div>
            ) : (
              <p className="text-gray-400 text-sm">
                <Link to="/login" className="text-blue-400 hover:text-blue-300">
                  Log in
                </Link>{" "}
                to save this profile
              </p>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-950 px-4 py-10">
      <div className="max-w-xl mx-auto">
        {mode === "nl" ? (
          <div>
            <h1 className="text-white text-3xl font-bold mb-2">
              Dell Workstation Advisor
            </h1>
            <p className="text-gray-400 text-lg mb-6">
              Describe your work and we'll recommend the right workstation
            </p>
            <textarea
              value={nlDescription}
              onChange={(e) => setNlDescription(e.target.value)}
              placeholder="e.g. I'm a mechanical engineer running FEA simulations for a mid-sized automotive team..."
              rows={4}
              className="w-full bg-gray-800 border border-gray-600 rounded px-4 py-3 text-white focus:outline-none focus:border-blue-500 resize-none"
            />
            <button
              onClick={handleNLSubmit}
              disabled={!nlDescription.trim() || nlLoading}
              className="mt-4 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium py-2 px-6 rounded cursor-pointer"
            >
              {nlLoading ? "Finding..." : "Find My Workstation"}
            </button>
            {nlError && <p className="text-red-400 text-sm mt-3">{nlError}</p>}
            <p className="text-gray-400 text-sm mt-6">
              Prefer to browse by category?{" "}
              <button
                onClick={() => setMode("stepper")}
                className="text-blue-400 hover:text-blue-300 cursor-pointer"
              >
                Use the step-by-step guide →
              </button>
            </p>
          </div>
        ) : (
          <div>
            <p className="text-gray-400 text-sm mb-3">
              <button
                onClick={() => setMode("nl")}
                className="text-blue-400 hover:text-blue-300 cursor-pointer"
              >
                ← Describe your needs instead
              </button>
            </p>
            <p className="text-gray-400 text-sm mb-2">
              Step {step} of 5 — {STEP_NAMES[step - 1]}
            </p>
            <div className="w-full bg-gray-800 rounded-full h-1.5 mb-6">
              <div
                className="bg-blue-500 h-1.5 rounded-full transition-all"
                style={{ width: `${(step / 5) * 100}%` }}
              />
            </div>

            {error && <p className="text-red-400 text-sm mb-4">{error}</p>}

            <div className="flex flex-col gap-3">
              {getStepOptions().map((option) => (
                <button
                  key={option.id}
                  onClick={() => handleCardClick(option)}
                  className={`bg-gray-800 hover:bg-gray-700 text-white rounded p-4 w-full text-left cursor-pointer transition-colors ${
                    selectedId === option.id ? "ring-2 ring-blue-500" : ""
                  }`}
                >
                  {option.name}
                </button>
              ))}
            </div>

            {step > 1 && (
              <button
                onClick={handleBack}
                className="mt-6 text-gray-400 hover:text-white text-sm cursor-pointer"
              >
                ← Back
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
