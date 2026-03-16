"""Router for CSV import endpoints — avaliacoes module."""

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.auth.middleware import CurrentUser, get_current_user
from src.common.auth.rbac import require_role
from src.common.database.session import get_db
from src.modules.avaliacoes.application.import_service import import_notas_csv

router = APIRouter()


@router.post(
    "/import/notas",
    status_code=status.HTTP_200_OK,
    summary="Importar notas históricas via CSV",
    dependencies=[Depends(require_role("super_admin", "diretor", "professor"))],
)
async def import_notas(
    file: UploadFile = File(..., description="Ficheiro CSV com notas"),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Import historical notas from a CSV file.

    Expected columns: n_processo, avaliacao_id (UUID), valor (numeric),
    observacoes (optional).

    If a nota already exists for the same (avaliacao, aluno), it is updated.
    Returns a report with the number of created, skipped (updated), and errored rows.
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
        content = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não foi possível ler o ficheiro. Verifique que está codificado em UTF-8.",
        )

    result = await import_notas_csv(
        db, current_user.tenant_id, current_user.user_id, content
    )
    return result.to_dict()
