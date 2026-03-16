import { Route, Routes } from "react-router-dom";
import AdminLayout from "./AdminLayout";
import DashboardAdmin from "./pages/DashboardAdmin";
import EscolasAdmin from "./pages/EscolasAdmin";

export default function AdminRoutes() {
  return (
    <Routes>
      <Route element={<AdminLayout />}>
        <Route index element={<DashboardAdmin />} />
        <Route path="escolas" element={<EscolasAdmin />} />
      </Route>
    </Routes>
  );
}
