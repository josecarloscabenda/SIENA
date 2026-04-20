import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import api from "@/shared/api/client";
import type { UserResponse } from "@/shared/api/types";

interface AuthState {
  user: UserResponse | null;
  loading: boolean;
  isAuthenticated: boolean;
}

interface LoginOptions {
  tenantId?: string;
  tenantSlug?: string;
}

interface AuthContextType extends AuthState {
  login: (username: string, password: string, opts: LoginOptions) => Promise<void>;
  logout: () => void;
  hasRole: (...roles: string[]) => boolean;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>({
    user: null,
    loading: true,
    isAuthenticated: false,
  });

  const fetchUser = useCallback(async () => {
    try {
      const { data } = await api.get<UserResponse>("/auth/me");
      setState({ user: data, loading: false, isAuthenticated: true });
    } catch {
      setState({ user: null, loading: false, isAuthenticated: false });
    }
  }, []);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
      fetchUser();
    } else {
      setState({ user: null, loading: false, isAuthenticated: false });
    }
  }, [fetchUser]);

  const login = async (username: string, password: string, opts: LoginOptions) => {
    const body: Record<string, string> = { username, password };
    if (opts.tenantId) body.tenant_id = opts.tenantId;
    if (opts.tenantSlug) body.tenant_slug = opts.tenantSlug;
    const { data } = await api.post("/auth/login", body);
    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("refresh_token", data.refresh_token);
    if (opts.tenantSlug) {
      localStorage.setItem("tenant_slug", opts.tenantSlug);
    }
    await fetchUser();
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("tenant_slug");
    setState({ user: null, loading: false, isAuthenticated: false });
  };

  const hasRole = (...roles: string[]) => {
    if (!state.user) return false;
    return state.user.papeis.some((p) => roles.includes(p));
  };

  return (
    <AuthContext.Provider value={{ ...state, login, logout, hasRole }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}

export function getDefaultPortal(user: UserResponse): string {
  const p = user.papeis;
  if (p.includes("super_admin")) return "/admin";
  if (p.includes("diretor") || p.includes("secretaria")) return "/gestao";
  if (p.includes("professor")) return "/professor";
  if (p.includes("aluno")) return "/aluno";
  if (p.includes("encarregado")) return "/encarregado";
  return "/login";
}