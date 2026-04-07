import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/useAuth";

export default function NavBar() {
  const { user, loading, logout } = useAuth();
  const navigate = useNavigate();

  async function handleLogout() {
    await logout();
    navigate("/login");
  }

  return (
    <nav className="bg-gray-900 text-white px-6 py-4 flex justify-between items-center">
      <Link to="/" className="font-semibold text-lg hover:text-gray-300">
        Workstation Advisor
      </Link>
      <div className="flex items-center gap-4">
        {!loading && user === null && (
          <>
            <Link to="/login" className="hover:text-gray-300">
              Login
            </Link>
            <Link to="/register" className="hover:text-gray-300">
              Register
            </Link>
          </>
        )}
        {!loading && user !== null && (
          <>
            <span className="text-gray-300">{user.email}</span>
            <button
              onClick={handleLogout}
              className="hover:text-gray-300 cursor-pointer"
            >
              Logout
            </button>
          </>
        )}
      </div>
    </nav>
  );
}
