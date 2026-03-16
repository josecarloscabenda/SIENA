import { Route, Routes } from "react-router-dom";
import EncarregadoLayout from "./EncarregadoLayout";
import EncarregadoView from "./pages/EncarregadoView";

export default function EncarregadoRoutes() {
  return (
    <Routes>
      <Route element={<EncarregadoLayout />}>
        <Route index element={<EncarregadoView />} />
        <Route path="filhos" element={<EncarregadoView />} />
      </Route>
    </Routes>
  );
}
