import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { apiFetch } from "../api/client";

export default function RegisterPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      const res = await apiFetch("/api/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      if (res.status === 201) {
        navigate("/login");
      } else {
        const data = await res.json().catch(() => ({}));
        setError(data.error ?? "Registration failed");
      }
    } catch {
      setError("Registration failed");
    }
  }

  return (
    <div className="overflow-x-hidden bg-gray-950 px-4 text-white sm:px-6">
      <div className="mx-auto flex min-h-screen w-full max-w-md flex-col justify-center py-10 sm:py-12">
        <div className="mb-8 flex flex-col items-center text-center">
          <div className="mb-5 flex h-12 w-12 shrink-0 items-center justify-center rounded-xl border border-gray-800 bg-gray-900">
            <div className="flex items-end gap-1.5">
              <div className="h-5 w-7 rounded-sm border border-gray-600 bg-gray-800" />
              <div className="h-8 w-3 rounded-sm border border-[#0076CE] bg-[#0076CE]/20" />
            </div>
          </div>

          <h1 className="text-2xl font-semibold tracking-tight text-white">
            Workstation Advisor
          </h1>
          <p className="mt-2 max-w-sm text-sm leading-6 text-gray-400">
            Match workstation configurations to workload needs.
          </p>
        </div>

        <div className="w-full rounded-2xl border border-gray-800 bg-gray-900/80 shadow-2xl">
          <div className="border-b border-gray-800 px-5 py-5 sm:px-6">
            <h2 className="text-lg font-semibold tracking-tight text-white">
              Create account
            </h2>
            <p className="mt-1 text-sm leading-6 text-gray-400">
              Set up access to your advisor workspace.
            </p>
          </div>

          <form
            onSubmit={handleSubmit}
            className="flex flex-col gap-5 px-5 py-6 sm:px-6"
          >
            <div className="flex flex-col gap-2">
              <label htmlFor="email" className="text-sm font-medium text-gray-300">
                Email
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                placeholder="you@example.com"
                className="h-11 w-full rounded-lg border border-gray-700 bg-gray-950 px-3 text-sm text-white placeholder:text-gray-600 outline-none transition focus:border-[#0076CE] focus:ring-2 focus:ring-[#0076CE]/20"
              />
            </div>

            <div className="flex flex-col gap-2">
              <label
                htmlFor="password"
                className="text-sm font-medium text-gray-300"
              >
                Password
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                placeholder="Create a password"
                className="h-11 w-full rounded-lg border border-gray-700 bg-gray-950 px-3 text-sm text-white placeholder:text-gray-600 outline-none transition focus:border-[#0076CE] focus:ring-2 focus:ring-[#0076CE]/20"
              />
            </div>

            {error && (
              <div className="rounded-lg border border-red-900/60 bg-red-950/30 px-3 py-2">
                <p className="text-sm leading-5 text-red-300">{error}</p>
              </div>
            )}

            <button
              type="submit"
              className="mt-1 h-11 w-full cursor-pointer rounded-lg bg-[#0076CE] px-4 text-sm font-semibold text-white transition hover:bg-[#0067B3] focus:outline-none focus:ring-2 focus:ring-[#0076CE]/30 focus:ring-offset-2 focus:ring-offset-gray-900"
            >
              Create account
            </button>
          </form>

          <div className="border-t border-gray-800 px-5 py-5 sm:px-6">
            <p className="text-center text-sm leading-6 text-gray-400">
              Already have an account?{" "}
              <Link
                to="/login"
                className="font-medium text-gray-200 underline decoration-gray-600 underline-offset-4 transition hover:text-white hover:decoration-gray-300"
              >
                Sign in
              </Link>
            </p>
          </div>
        </div>

        <p className="mt-6 text-center text-xs leading-5 text-gray-500">
          Personal learning project — not an official Dell product
        </p>
      </div>
    </div>
  );
}