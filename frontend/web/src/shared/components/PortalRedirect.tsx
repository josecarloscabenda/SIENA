import { Navigate } from "react-router-dom";
import { useAuth } from "@/shared/hooks/useAuth";
import { getDefaultPortal } from "@/shared/hooks/useAuth";

export default function PortalRedirect() {
  const { user, loading } = useAuth();

  if (loading) return null;

  const target = user ? getDefaultPortal(user) : "/login";
  return <Navigate to={target} replace />;
}
