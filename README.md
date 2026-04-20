# SIENA
Backend (Python/FastAPI)
15 módulos com Clean Architecture (api/, domain/, application/, infrastructure/)
common/ com código partilhado: database base/session, event bus, schemas, auth
main.py — entrypoint FastAPI com health check
base.py — BaseModel com UUID PK, timestamps, soft delete, tenant mixin
bus.py — event bus in-process (pub/sub)
pyproject.toml — dependências e config de tooling
Dockerfile — multi-stage, non-root user
Alembic configurado para migrations
Frontend (React 18 + Vite)
10 módulos espelhando os domínios do backend
5 portais (aluno, encarregado, professor, direcao, gestao)
shared/ — components, hooks, api client, utils
Vite com proxy para o backend em dev
Infraestrutura
docker-compose.yml — PostgreSQL + Redis + Nginx + Backend
init-schemas.sql — 15 schemas criados automaticamente
nginx.conf — reverse proxy
GitHub Actions para backend e frontend
Prometheus config para observabilidade
Placeholders
frontend/admin-local/ — Tauri (Fase 3)
frontend/mobile/ — React Native (Fase 2)

COmandos para configurar o git e baixar o repostorio no meu lap top abaixo:
git 

Cabenda