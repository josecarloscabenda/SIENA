import { Navigate } from "react-router-dom";
import { useAuth } from "@/shared/hooks/useAuth";

export default function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        backgroundColor: "#F0F4FA",
        color: "#1A3F7A",
      }}>
        A carregar...
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}