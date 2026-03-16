"""Router for CSV import endpoints — directory module."""

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.auth.middleware import CurrentUser, get_current_user
from src.common.auth.rbac import require_role
from src.common.database.session import get_db
from src.modules.directory.application.import_service import import_alunos_csv

router = APIRouter()


@router.post(
    "/import/alunos",
    status_code=status.HTTP_200_OK,
    summary="Importar alunos via CSV",
    dependencies=[Depends(require_role("super_admin", "diretor", "secretaria"))],
)
async def import_alunos(
    file: UploadFile = File(..., description="Ficheiro CSV com dados de alunos"),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Import alunos from a CSV file.

    Expected columns: nome_completo, bi_identificacao, dt_nascimento (YYYY-MM-DD),
    sexo (M/F), n_processo, ano_ingresso, nacionalidade (optional),
    telefone (optional), email (optional).

    Returns a report with the number of created, skipped, and errored rows.
    """
    if file.content_type and file.content_type not in (
        "text/csv",
        "application/vnd.ms-excel",
        "application/octet-stream",
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de ficheiro não suportado: {file.content_type}. Envie um ficheiro CSV.",
        )

    raw = await file.read()
    try:
        content = raw.decode("utf-8-sig")  # utf-8-sig handles BOM from Excel
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não foi possível ler o ficheiro. Verifique que está codificado em UTF-8.",
        )

    result = await import_alunos_csv(db, current_user.tenant_id, content)
    return result.to_dict()
