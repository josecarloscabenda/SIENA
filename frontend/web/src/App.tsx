import { Route, Routes } from "react-router-dom";
import ProtectedRoute from "@/shared/components/ProtectedRoute";
import RoleRoute from "@/shared/components/RoleRoute";
import PortalRedirect from "@/shared/components/PortalRedirect";
import Login from "@/pages/Login";
import Forbidden from "@/pages/Forbidden";

import AdminRoutes from "@/portals/admin/AdminRoutes";
import GestaoRoutes from "@/portals/gestao/GestaoRoutes";
import ProfessorRoutes from "@/portals/professor/ProfessorRoutes";
import AlunoRoutes from "@/portals/aluno/AlunoRoutes";
import EncarregadoRoutes from "@/portals/encarregado/EncarregadoRoutes";

const GESTAO = ["super_admin", "diretor", "secretaria"];

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      {/* Pre-filled login URL per-school (shareable link) */}
      <Route path="/escola/:slug/login" element={<Login />} />
      <Route path="/escola/:slug" element={<Login />} />

      {/* Redirect root to the correct portal */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <PortalRedirect />
          </ProtectedRoute>
        }
      />

      {/* 403 */}
      <Route
        path="/403"
        element={
          <ProtectedRoute>
            <Forbidden />
          </ProtectedRoute>
        }
      />

      {/* Portal: Admin (platform management) */}
      <Route
        path="/admin/*"
        element={
          <ProtectedRoute>
            <RoleRoute roles={["super_admin"]}>
              <AdminRoutes />
            </RoleRoute>
          </ProtectedRoute>
        }
      />

      {/* Portal: Gestao Escolar */}
      <Route
        path="/gestao/*"
        element={
          <ProtectedRoute>
            <RoleRoute roles={GESTAO}>
              <GestaoRoutes />
            </RoleRoute>
          </ProtectedRoute>
        }
      />

      {/* Portal: Professor */}
      <Route
        path="/professor/*"
        element={
          <ProtectedRoute>
            <RoleRoute roles={["professor"]}>
              <ProfessorRoutes />
            </RoleRoute>
          </ProtectedRoute>
        }
      />

      {/* Portal: Aluno */}
      <Route
        path="/aluno/*"
        element={
          <ProtectedRoute>
            <RoleRoute roles={["aluno"]}>
              <AlunoRoutes />
            </RoleRoute>
          </ProtectedRoute>
        }
      />

      {/* Portal: Encarregado */}
      <Route
        path="/encarregado/*"
        element={
          <ProtectedRoute>
            <RoleRoute roles={["encarregado"]}>
              <EncarregadoRoutes />
            </RoleRoute>
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}
