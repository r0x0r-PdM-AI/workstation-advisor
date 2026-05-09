import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { apiFetch } from "../api/client";
import ProductCard from "../components/ProductCard";
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
      <div className="flex min-h-screen items-center justify-center bg-gray-950 px-4">
        <p className="text-sm text-gray-400">Loading recommendations…</p>
      </div>
    );
  }

  if (recommendations) {
    return (
      <div className="min-h-screen bg-gray-950 px-4 py-10 sm:py-12">
        <div className="mx-auto max-w-2xl">
          <button
            onClick={handleBack}
            className="mb-6 cursor-pointer text-sm text-gray-400 transition hover:text-white"
          >
            ← Start Over
          </button>
          <h2 className="mb-6 text-2xl font-semibold tracking-tight text-white">
            Recommended Workstations
          </h2>
          {matchedWorkload && (
            <div className="mb-4 inline-flex max-w-full flex-wrap items-center gap-x-2 gap-y-1 rounded-lg border border-gray-800 bg-gray-900 px-3 py-2 text-sm text-gray-400">
              <span>Matched to:</span>
              <span className="font-medium text-white">{matchedWorkload}</span>
              <span className="text-gray-600">·</span>
              <span>{SCALE_LABELS[nlScaleLevel ?? 0] ?? ""}</span>
            </div>
          )}
          {recommendations.length === 0 ? (
            <div className="rounded-2xl border border-gray-800 bg-gray-900 px-5 py-6 text-sm leading-6 text-gray-300">
              {responseMessage}
            </div>
          ) : (
            <div className="flex flex-col gap-4">
              {recommendations.map((rec, i) => (
                <ProductCard
                  key={i}
                  product={rec.product}
                  brand={rec.brand}
                  form_factor={rec.form_factor}
                  notes={rec.notes}
                  rank={rec.rank}
                  explanation={rec.explanation}
                />
              ))}
            </div>
          )}
          <div className="mt-6 border-t border-gray-800 pt-6">
            {user ? (
              <div className="flex flex-col gap-3">
                <input
                  type="text"
                  value={profileName}
                  onChange={(e) => setProfileName(e.target.value)}
                  className="w-full rounded-lg border border-gray-700 bg-gray-950 px-3 py-2 text-sm text-white outline-none transition focus:border-[#0076CE] focus:ring-2 focus:ring-[#0076CE]/20"
                />
                <button
                  onClick={handleSaveProfile}
                  disabled={saveStatus === "saving" || saveStatus === "saved"}
                  className="w-fit cursor-pointer rounded-lg bg-[#0076CE] px-4 py-2 text-sm font-semibold text-white transition hover:bg-[#0067B3] disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {saveStatus === "saving" ? "Saving..." : "Save Profile"}
                </button>
                {saveStatus === "saved" && (
                  <p className="w-fit rounded-lg border border-green-900/60 bg-green-950/30 px-3 py-2 text-sm text-green-300">
                    Profile saved!
                  </p>
                )}
                {saveStatus === "error" && (
                  <div className="rounded-lg border border-red-900/60 bg-red-950/30 px-3 py-3">
                    <p className="text-sm leading-5 text-red-300">
                      Failed to save. Try again.
                    </p>
                  </div>
                )}
              </div>
            ) : (
              <p className="text-sm text-gray-400">
                <Link
                  to="/login"
                  className="font-medium text-gray-200 underline decoration-gray-600 underline-offset-4 transition hover:text-white hover:decoration-gray-300"
                >
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
    <div className="min-h-screen bg-gray-950 px-4 py-10 sm:py-12">
      <div className="mx-auto max-w-xl">
        {mode === "nl" ? (
          <div>
            <h1 className="text-2xl font-semibold tracking-tight text-white">
              Workstation Advisor
            </h1>
            <p className="mb-6 mt-2 text-sm text-gray-400">
              Describe your work. We'll find the right fit.
            </p>
            <textarea
              value={nlDescription}
              onChange={(e) => setNlDescription(e.target.value)}
              placeholder="e.g. I'm a mechanical engineer running FEA simulations for a mid-sized automotive team..."
              rows={4}
              className="w-full resize-none rounded-xl border border-gray-700 bg-gray-950 px-4 py-3 text-sm text-white placeholder:text-gray-600 outline-none transition focus:border-[#0076CE] focus:ring-2 focus:ring-[#0076CE]/20"
            />
            <button
              onClick={handleNLSubmit}
              disabled={!nlDescription.trim() || nlLoading}
              className="mt-4 h-11 cursor-pointer rounded-lg bg-[#0076CE] px-6 text-sm font-semibold text-white transition hover:bg-[#0067B3] disabled:cursor-not-allowed disabled:opacity-50"
            >
              {nlLoading ? "Finding..." : "Find My Workstation"}
            </button>
            {nlError && (
              <div className="mt-3 rounded-lg border border-red-900/60 bg-red-950/30 px-3 py-3">
                <p className="text-sm leading-5 text-red-300">{nlError}</p>
              </div>
            )}
            <button
              onClick={() => setMode("stepper")}
              className="mt-4 flex w-full cursor-pointer items-center justify-between rounded-xl border border-gray-800 bg-gray-900 px-4 py-3 text-left transition hover:border-gray-700 hover:bg-gray-800"
            >
              <span className="text-sm text-gray-300">
                Prefer to browse by category? Use the step-by-step guide
              </span>
              <span className="shrink-0 pl-3 text-lg text-[#0076CE]">→</span>
            </button>
          </div>
        ) : (
          <div>
            <button
              onClick={() => setMode("nl")}
              className="mb-4 flex w-full cursor-pointer items-center justify-between rounded-xl border border-gray-800 bg-gray-900 px-4 py-3 text-left transition hover:border-gray-700 hover:bg-gray-800"
            >
              <span className="text-sm text-gray-300">
                Prefer to describe your needs instead? Switch to free-text input
              </span>
              <span className="shrink-0 pl-3 text-lg text-[#0076CE]">→</span>
            </button>
            <p className="mb-3 text-xs uppercase tracking-wide text-gray-500">
              Step {step} of 5 — {STEP_NAMES[step - 1]}
            </p>
            <div className="mb-6 h-1 w-full rounded-full bg-gray-800">
              <div
                className="h-1 rounded-full bg-[#0076CE] transition-all"
                style={{ width: `${(step / 5) * 100}%` }}
              />
            </div>

            {error && (
              <div className="mb-4 rounded-lg border border-red-900/60 bg-red-950/30 px-3 py-3">
                <p className="text-sm leading-5 text-red-300">{error}</p>
              </div>
            )}

            <div className="flex flex-col gap-3">
              {getStepOptions().map((option) => (
                <button
                  key={option.id}
                  onClick={() => handleCardClick(option)}
                  className={`w-full cursor-pointer rounded-xl border border-gray-800 bg-gray-900 p-4 text-left text-sm text-white transition-colors hover:border-gray-700 hover:bg-gray-800 ${
                    selectedId === option.id ? "border-[#0076CE] ring-2 ring-[#0076CE]" : ""
                  }`}
                >
                  {option.name}
                </button>
              ))}
            </div>

            {step > 1 && (
              <button
                onClick={handleBack}
                className="mt-6 cursor-pointer text-sm text-gray-400 transition hover:text-white"
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