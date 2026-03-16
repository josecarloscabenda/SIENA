import { Route, Routes } from "react-router-dom";
import AlunoLayout from "./AlunoLayout";
import DashboardAluno from "./pages/DashboardAluno";
import Boletim from "./pages/Boletim";
import MinhasFaltas from "./pages/MinhasFaltas";
import HorarioAluno from "./pages/HorarioAluno";

export default function AlunoRoutes() {
  return (
    <Routes>
      <Route element={<AlunoLayout />}>
        <Route index element={<DashboardAluno />} />
        <Route path="boletim" element={<Boletim />} />
        <Route path="faltas" element={<MinhasFaltas />} />
        <Route path="horario" element={<HorarioAluno />} />
      </Route>
    </Routes>
  );
}
