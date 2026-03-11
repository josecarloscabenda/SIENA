import { Route, Routes } from "react-router-dom";
import Layout from "@/shared/components/Layout";
import ProtectedRoute from "@/shared/components/ProtectedRoute";
import Dashboard from "@/pages/Dashboard";
import Escolas from "@/pages/Escolas";
import Login from "@/pages/Login";
import UsersPage from "@/pages/Users";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route path="/" element={<Dashboard />} />
        <Route path="/escolas" element={<Escolas />} />
        <Route path="/users" element={<UsersPage />} />
      </Route>
    </Routes>
  );
}