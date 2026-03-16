import { Navigate } from "react-router-dom";
import { useAuth } from "@/shared/hooks/useAuth";

interface Props {
  roles: string[];
  children: React.ReactNode;
}

export default function RoleRoute({ roles, children }: Props) {
  const { hasRole, loading } = useAuth();

  if (loading) return null;

  if (!hasRole(...roles)) {
    return <Navigate to="/403" replace />;
  }

  return <>{children}</>;
}
