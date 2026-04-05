import { useEffect, useState, type ReactNode } from "react";
import { apiFetch } from "../api/client";
import { AuthContext, type User } from "./AuthContext";

type AuthProviderProps = {
  children: ReactNode;
};

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    async function fetchCurrentUser() {
      try {
        const response = await apiFetch("/api/auth/me");

        if (!isMounted) {
          return;
        }

        if (response.ok) {
          const data: User = await response.json();
          setUser(data);
          return;
        }

        setUser(null);
      } catch {
        if (isMounted) {
          setUser(null);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    void fetchCurrentUser();

    return () => {
      isMounted = false;
    };
  }, []);

  async function login(email: string, password: string) {
    const response = await apiFetch("/api/auth/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      const data = await response.json().catch(() => ({}));
      throw new Error(data.error ?? "Login failed");
    }

    const data = await response.json();
    setUser(data.user);
  }

  async function logout() {
    await apiFetch("/api/auth/logout", {
      method: "POST",
    });

    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
