from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="SIENA",
    description="Sistema de Integração Educacional Nacional de Angola",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: restringir em produção
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "siena"}


# --- Registar routers dos módulos ---
# from src.modules.identity.api.router import router as identity_router
# from src.modules.escolas.api.router import router as escolas_router
# app.include_router(identity_router, prefix="/api/v1", tags=["Identity"])
# app.include_router(escolas_router, prefix="/api/v1", tags=["Escolas"])