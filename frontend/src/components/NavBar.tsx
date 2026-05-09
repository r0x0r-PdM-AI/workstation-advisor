import { useState } from "react";
import { Link, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/useAuth";

export default function NavBar() {
  const { user, loading, logout } = useAuth();
  const navigate = useNavigate();
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  async function handleLogout() {
    await logout();
    setIsMenuOpen(false);
    navigate("/login");
  }

  const navLinkClass = ({ isActive }: { isActive: boolean }) =>
    `text-sm font-medium transition ${
      isActive
        ? "text-white"
        : "text-gray-400 hover:text-gray-200"
    }`;

  return (
    <nav className="sticky top-0 z-50 border-b border-gray-800 bg-gray-950 text-white">
      <div className="mx-auto flex h-16 w-full max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <Link
          to="/"
          onClick={() => setIsMenuOpen(false)}
          className="flex min-w-0 items-center gap-3"
        >
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border border-gray-800 bg-gray-900">
            <div className="flex items-end gap-1">
              <div className="h-4 w-6 rounded-sm border border-gray-600 bg-gray-800" />
              <div className="h-6 w-2.5 rounded-sm border border-[#0076CE] bg-[#0076CE]/20" />
            </div>
          </div>

          <span className="truncate text-sm font-semibold tracking-tight text-white sm:text-base">
            Workstation Advisor
          </span>
        </Link>

        <div className="hidden items-center gap-5 md:flex">
          {!loading && user === null && (
            <>
              <NavLink to="/login" className={navLinkClass}>
                Sign in
              </NavLink>
              <NavLink to="/register" className={navLinkClass}>
                Register
              </NavLink>
            </>
          )}

          {!loading && user !== null && (
            <>
              <NavLink to="/dashboard" className={navLinkClass}>
                Dashboard
              </NavLink>
              <span className="max-w-56 truncate text-sm text-gray-500">
                {user.email}
              </span>
              <button
                onClick={handleLogout}
                className="cursor-pointer text-sm font-medium text-gray-400 transition hover:text-gray-200"
              >
                Logout
              </button>
            </>
          )}
        </div>

        <button
          type="button"
          onClick={() => setIsMenuOpen((open) => !open)}
          className="flex h-10 w-10 cursor-pointer items-center justify-center rounded-lg border border-gray-800 bg-gray-900 text-gray-300 transition hover:border-gray-700 hover:text-white md:hidden"
          aria-label="Toggle navigation menu"
          aria-expanded={isMenuOpen}
        >
          <span className="flex flex-col gap-1.5">
            <span className="h-0.5 w-4 rounded-full bg-current" />
            <span className="h-0.5 w-4 rounded-full bg-current" />
            <span className="h-0.5 w-4 rounded-full bg-current" />
          </span>
        </button>
      </div>

      {isMenuOpen && (
        <div className="border-t border-gray-800 bg-gray-950 px-4 py-4 md:hidden">
          <div className="flex flex-col gap-4">
            {!loading && user === null && (
              <>
                <NavLink
                  to="/login"
                  onClick={() => setIsMenuOpen(false)}
                  className={navLinkClass}
                >
                  Sign in
                </NavLink>
                <NavLink
                  to="/register"
                  onClick={() => setIsMenuOpen(false)}
                  className={navLinkClass}
                >
                  Register
                </NavLink>
              </>
            )}

            {!loading && user !== null && (
              <>
                <NavLink
                  to="/dashboard"
                  onClick={() => setIsMenuOpen(false)}
                  className={navLinkClass}
                >
                  Dashboard
                </NavLink>
                <span className="break-all text-sm text-gray-500">
                  {user.email}
                </span>
                <button
                  onClick={handleLogout}
                  className="w-fit cursor-pointer text-sm font-medium text-gray-400 transition hover:text-gray-200"
                >
                  Logout
                </button>
              </>
            )}
          </div>
        </div>
      )}
    </nav>
  );
}