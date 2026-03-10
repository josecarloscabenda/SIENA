import { useEffect, useState } from "react";

function App() {
  const [apiStatus, setApiStatus] = useState<string>("a verificar...");

  useEffect(() => {
    fetch("/api/health")
      .then((res) => res.json())
      .then((data) => setApiStatus(data.status === "ok" ? "Conectado" : "Erro"))
      .catch(() => setApiStatus("Offline"));
  }, []);

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        fontFamily: "Inter, Roboto, Arial, sans-serif",
        backgroundColor: "#F0F4FA",
        color: "#1A3F7A",
      }}
    >
      <h1 style={{ fontSize: "2.5rem", marginBottom: "0.5rem" }}>SIENA</h1>
      <p style={{ fontSize: "1.1rem", opacity: 0.8, marginBottom: "2rem" }}>
        Sistema de Integração Educacional Nacional de Angola
      </p>
      <div
        style={{
          padding: "1.5rem 2rem",
          backgroundColor: "#fff",
          borderRadius: "8px",
          boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
        }}
      >
        <p style={{ margin: 0 }}>
          Backend API:{" "}
          <strong
            style={{
              color: apiStatus === "Conectado" ? "#00A878" : "#E53E3E",
            }}
          >
            {apiStatus}
          </strong>
        </p>
      </div>
      <p
        style={{
          marginTop: "2rem",
          fontSize: "0.85rem",
          opacity: 0.5,
        }}
      >
        Educar é transformar o futuro de Angola
      </p>
    </div>
  );
}

export default App;
