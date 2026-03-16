import { Route, Routes } from "react-router-dom";
import GestaoLayout from "./GestaoLayout";
import DashboardDirecao from "./pages/DashboardDirecao";
import Alunos from "./pages/Alunos";
import Professores from "./pages/Professores";
import Encarregados from "./pages/Encarregados";
import Matriculas from "./pages/Matriculas";
import Turmas from "./pages/Turmas";
import Curriculos from "./pages/Curriculos";
import Horarios from "./pages/Horarios";
import Pauta from "./pages/Pauta";
import Escolas from "./pages/Escolas";
import UsersPage from "./pages/Users";

export default function GestaoRoutes() {
  return (
    <Routes>
      <Route element={<GestaoLayout />}>
        <Route index element={<DashboardDirecao />} />
        <Route path="alunos" element={<Alunos />} />
        <Route path="professores" element={<Professores />} />
        <Route path="encarregados" element={<Encarregados />} />
        <Route path="matriculas" element={<Matriculas />} />
        <Route path="turmas" element={<Turmas />} />
        <Route path="curriculos" element={<Curriculos />} />
        <Route path="horarios" element={<Horarios />} />
        <Route path="pauta" element={<Pauta />} />
        <Route path="escola" element={<Escolas />} />
        <Route path="utilizadores" element={<UsersPage />} />
      </Route>
    </Routes>
  );
}
