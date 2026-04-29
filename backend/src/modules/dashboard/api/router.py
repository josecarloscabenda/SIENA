"""FastAPI router for cross-module dashboard / analytics endpoints."""

import uuid
from datetime import date, timedelta
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.auth.middleware import CurrentUser, get_current_user
from src.common.database.session import get_db
from src.modules.academico.infrastructure.models import (
    Disciplina,
    HorarioAula,
    Turma,
)
from src.modules.avaliacoes.infrastructure.models import Avaliacao, Falta, Nota
from src.modules.dashboard.api.dtos import (
    AlunoDisciplinaResumo,
    AlunoStats,
    EducandoResumo,
    EncarregadoStats,
    GestaoStats,
    PautaAlunoLinha,
    PautaResponse,
    ProfessorStats,
    ProximaAulaItem,
    ProximaAvaliacaoItem,
    TurmaResumoProfessor,
)
from src.modules.directory.infrastructure.models import (
    Aluno,
    Encarregado,
    Pessoa,
    Professor,
    VinculoAlunoEncarregado,
)
from src.modules.enrollment.infrastructure.models import AlocacaoTurma, Matricula
from src.modules.escolas.infrastructure.models import AnoLetivo

router = APIRouter()


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

DIA_ORDER = ["segunda", "terca", "quarta", "quinta", "sexta", "sabado", "domingo"]


def _media(valores: list[Decimal]) -> Decimal | None:
    if not valores:
        return None
    return (sum(valores, Decimal("0")) / Decimal(len(valores))).quantize(Decimal("0.01"))


async def _get_active_ano_letivo_id(db: AsyncSession, tenant_id: uuid.UUID) -> uuid.UUID | None:
    result = await db.execute(
        select(AnoLetivo.id).where(
            AnoLetivo.tenant_id == tenant_id,
            AnoLetivo.ativo.is_(True),
            AnoLetivo.deleted_at.is_(None),
        )
    )
    return result.scalar_one_or_none()


# ──────────────────────────────────────────────
# /dashboard/gestao  (Task #38)
# ──────────────────────────────────────────────

@router.get("/dashboard/gestao", response_model=GestaoStats)
async def dashboard_gestao(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> GestaoStats:
    """Estatísticas globais da escola (totais por entidade + matrículas por estado)."""
    tenant_id = current_user.tenant_id

    async def _count(stmt):  # noqa: ANN001, ANN202
        return (await db.execute(stmt)).scalar_one()

    total_alunos = await _count(
        select(func.count(Aluno.id)).where(
            Aluno.tenant_id == tenant_id, Aluno.deleted_at.is_(None)
        )
    )
    total_alunos_ativos = await _count(
        select(func.count(Aluno.id)).where(
            Aluno.tenant_id == tenant_id,
            Aluno.deleted_at.is_(None),
            Aluno.status == "ativo",
        )
    )
    total_professores = await _count(
        select(func.count(Professor.id)).where(
            Professor.tenant_id == tenant_id, Professor.deleted_at.is_(None)
        )
    )
    total_encarregados = await _count(
        select(func.count(Encarregado.id)).where(
            Encarregado.tenant_id == tenant_id, Encarregado.deleted_at.is_(None)
        )
    )
    total_turmas = await _count(
        select(func.count(Turma.id)).where(
            Turma.tenant_id == tenant_id, Turma.deleted_at.is_(None)
        )
    )
    total_disciplinas = await _count(
        select(func.count(Disciplina.id)).where(
            Disciplina.tenant_id == tenant_id, Disciplina.deleted_at.is_(None)
        )
    )

    async def _count_matriculas(estado: str) -> int:
        return await _count(
            select(func.count(Matricula.id)).where(
                Matricula.tenant_id == tenant_id,
                Matricula.deleted_at.is_(None),
                Matricula.estado == estado,
            )
        )

    matriculas_pendentes = await _count_matriculas("pendente")
    matriculas_aprovadas = await _count_matriculas("aprovada")
    matriculas_rejeitadas = await _count_matriculas("rejeitada")

    avaliacoes_total = await _count(
        select(func.count(Avaliacao.id)).where(
            Avaliacao.tenant_id == tenant_id, Avaliacao.deleted_at.is_(None)
        )
    )
    notas_lancadas = await _count(
        select(func.count(Nota.id)).where(
            Nota.tenant_id == tenant_id, Nota.deleted_at.is_(None)
        )
    )

    # Faltas do período activo (último mês — proxy razoável sem campo "periodo activo")
    cutoff = date.today() - timedelta(days=30)
    faltas_periodo_atual = await _count(
        select(func.count(Falta.id)).where(
            Falta.tenant_id == tenant_id,
            Falta.deleted_at.is_(None),
            Falta.data >= cutoff,
        )
    )

    return GestaoStats(
        total_alunos=total_alunos,
        total_alunos_ativos=total_alunos_ativos,
        total_professores=total_professores,
        total_encarregados=total_encarregados,
        total_turmas=total_turmas,
        total_disciplinas=total_disciplinas,
        matriculas_pendentes=matriculas_pendentes,
        matriculas_aprovadas=matriculas_aprovadas,
        matriculas_rejeitadas=matriculas_rejeitadas,
        avaliacoes_total=avaliacoes_total,
        notas_lancadas=notas_lancadas,
        faltas_periodo_atual=faltas_periodo_atual,
    )


# ──────────────────────────────────────────────
# /dashboard/professor  (Task #39)
# ──────────────────────────────────────────────

@router.get("/dashboard/professor", response_model=ProfessorStats)
async def dashboard_professor(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    professor_id: uuid.UUID | None = Query(default=None, description="Sobreposição (admin/diretor)"),
) -> ProfessorStats:
    """Resumo do professor: turmas, disciplinas, próximas aulas, notas por lançar."""
    tenant_id = current_user.tenant_id

    # Resolver professor_id: parâmetro, ou lookup via Utilizador.pessoa_id
    target_professor_id = professor_id
    if target_professor_id is None:
        # Procurar pelo user logado
        from src.modules.identity.infrastructure.models import Utilizador
        result = await db.execute(
            select(Utilizador.pessoa_id).where(Utilizador.id == current_user.user_id)
        )
        pessoa_id = result.scalar_one_or_none()
        if pessoa_id is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilizador sem pessoa associada")
        prof_result = await db.execute(
            select(Professor.id).where(
                Professor.pessoa_id == pessoa_id,
                Professor.tenant_id == tenant_id,
                Professor.deleted_at.is_(None),
            )
        )
        target_professor_id = prof_result.scalar_one_or_none()
        if target_professor_id is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilizador não é professor")

    # Nome
    nome_result = await db.execute(
        select(Pessoa.nome_completo)
        .join(Professor, Professor.pessoa_id == Pessoa.id)
        .where(Professor.id == target_professor_id, Professor.tenant_id == tenant_id)
    )
    nome = nome_result.scalar_one_or_none() or "—"

    # Turmas (regente OR via HorarioAula)
    leciona_subq = (
        select(HorarioAula.turma_id)
        .where(
            HorarioAula.professor_id == target_professor_id,
            HorarioAula.tenant_id == tenant_id,
            HorarioAula.deleted_at.is_(None),
        )
        .distinct()
        .subquery()
    )
    turmas_q = (
        select(Turma.id, Turma.nome, Turma.classe, Turma.turno, Turma.professor_regente_id)
        .where(
            Turma.tenant_id == tenant_id,
            Turma.deleted_at.is_(None),
            (Turma.professor_regente_id == target_professor_id)
            | (Turma.id.in_(select(leciona_subq.c.turma_id))),
        )
        .order_by(Turma.classe, Turma.nome)
    )
    turmas_rows = (await db.execute(turmas_q)).all()
    turma_ids = [r.id for r in turmas_rows]

    # Para cada turma: nº disciplinas leccionadas + total alunos alocados
    disc_count_per_turma: dict[uuid.UUID, int] = {}
    aluno_count_per_turma: dict[uuid.UUID, int] = {}
    if turma_ids:
        d_rows = await db.execute(
            select(
                HorarioAula.turma_id,
                func.count(distinct(HorarioAula.disciplina_id)).label("n"),
            )
            .where(
                HorarioAula.turma_id.in_(turma_ids),
                HorarioAula.professor_id == target_professor_id,
                HorarioAula.tenant_id == tenant_id,
                HorarioAula.deleted_at.is_(None),
            )
            .group_by(HorarioAula.turma_id)
        )
        for row in d_rows.all():
            disc_count_per_turma[row.turma_id] = row.n

        a_rows = await db.execute(
            select(AlocacaoTurma.turma_id, func.count(AlocacaoTurma.id))
            .where(
                AlocacaoTurma.turma_id.in_(turma_ids),
                AlocacaoTurma.tenant_id == tenant_id,
                AlocacaoTurma.deleted_at.is_(None),
            )
            .group_by(AlocacaoTurma.turma_id)
        )
        for row in a_rows.all():
            aluno_count_per_turma[row.turma_id] = row[1]

    turmas_resumo = [
        TurmaResumoProfessor(
            turma_id=r.id,
            nome=r.nome,
            classe=r.classe,
            turno=r.turno,
            is_regente=(r.professor_regente_id == target_professor_id),
            leciona_disciplinas=disc_count_per_turma.get(r.id, 0),
            total_alunos=aluno_count_per_turma.get(r.id, 0),
        )
        for r in turmas_rows
    ]

    # Disciplinas leccionadas (DISTINCT)
    disc_count = (
        await db.execute(
            select(func.count(distinct(HorarioAula.disciplina_id))).where(
                HorarioAula.professor_id == target_professor_id,
                HorarioAula.tenant_id == tenant_id,
                HorarioAula.deleted_at.is_(None),
            )
        )
    ).scalar_one()

    total_alunos = sum(aluno_count_per_turma.values())

    # Notas por lançar = avaliações criadas pelo prof (i.e., das suas turmas+disciplinas)
    # cuja contagem de notas < contagem de alunos da turma. Aproximação: avaliações sem
    # qualquer nota lançada.
    avals_sem_notas_q = (
        select(func.count(Avaliacao.id))
        .where(
            Avaliacao.tenant_id == tenant_id,
            Avaliacao.deleted_at.is_(None),
            Avaliacao.turma_id.in_(turma_ids) if turma_ids else False,
            ~Avaliacao.id.in_(
                select(Nota.avaliacao_id).where(Nota.tenant_id == tenant_id, Nota.deleted_at.is_(None))
            ),
        )
    )
    notas_por_lancar = (await db.execute(avals_sem_notas_q)).scalar_one() if turma_ids else 0

    # Próximas aulas — todas as aulas ordenadas por dia da semana e hora
    proximas_q = (
        select(
            HorarioAula.id,
            HorarioAula.turma_id,
            Turma.nome.label("turma_nome"),
            HorarioAula.disciplina_id,
            Disciplina.nome.label("disciplina_nome"),
            HorarioAula.dia_semana,
            HorarioAula.hora_inicio,
            HorarioAula.hora_fim,
        )
        .join(Turma, Turma.id == HorarioAula.turma_id)
        .join(Disciplina, Disciplina.id == HorarioAula.disciplina_id)
        .where(
            HorarioAula.professor_id == target_professor_id,
            HorarioAula.tenant_id == tenant_id,
            HorarioAula.deleted_at.is_(None),
        )
    )
    proximas_rows = (await db.execute(proximas_q)).all()
    proximas_rows_sorted = sorted(
        proximas_rows,
        key=lambda r: (DIA_ORDER.index(r.dia_semana) if r.dia_semana in DIA_ORDER else 99, r.hora_inicio),
    )
    proximas_aulas = [
        ProximaAulaItem(
            horario_id=r.id,
            turma_id=r.turma_id,
            turma_nome=r.turma_nome,
            disciplina_id=r.disciplina_id,
            disciplina_nome=r.disciplina_nome,
            dia_semana=r.dia_semana,
            hora_inicio=r.hora_inicio.strftime("%H:%M"),
            hora_fim=r.hora_fim.strftime("%H:%M"),
        )
        for r in proximas_rows_sorted[:10]
    ]

    return ProfessorStats(
        professor_id=target_professor_id,
        nome=nome,
        turmas_atribuidas=len(turmas_rows),
        disciplinas_lecciona=disc_count,
        total_alunos=total_alunos,
        notas_por_lancar=notas_por_lancar,
        proximas_aulas=proximas_aulas,
        turmas=turmas_resumo,
    )


# ──────────────────────────────────────────────
# /dashboard/aluno  (Task #40)
# ──────────────────────────────────────────────

async def _aluno_stats(db: AsyncSession, tenant_id: uuid.UUID, aluno_id: uuid.UUID) -> AlunoStats:
    """Constrói AlunoStats — partilhado entre /dashboard/aluno e /dashboard/encarregado."""
    aluno_q = (
        select(Aluno.id, Aluno.n_processo, Pessoa.nome_completo)
        .select_from(Aluno)
        .join(Pessoa, Pessoa.id == Aluno.pessoa_id)
        .where(
            Aluno.id == aluno_id,
            Aluno.tenant_id == tenant_id,
            Aluno.deleted_at.is_(None),
        )
    )
    aluno_row = (await db.execute(aluno_q)).first()
    if aluno_row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aluno não encontrado")

    # Matrícula activa + alocação
    mat_q = (
        select(
            Matricula.id.label("matricula_id"),
            Matricula.classe,
            AlocacaoTurma.turma_id,
            Turma.nome.label("turma_nome"),
        )
        .outerjoin(AlocacaoTurma, AlocacaoTurma.matricula_id == Matricula.id)
        .outerjoin(Turma, Turma.id == AlocacaoTurma.turma_id)
        .where(
            Matricula.aluno_id == aluno_id,
            Matricula.tenant_id == tenant_id,
            Matricula.deleted_at.is_(None),
            Matricula.estado == "aprovada",
        )
        .order_by(Matricula.created_at.desc())
        .limit(1)
    )
    mat_row = (await db.execute(mat_q)).first()

    # Notas → médias por disciplina
    notas_q = (
        select(
            Avaliacao.disciplina_id,
            Disciplina.nome.label("disciplina_nome"),
            Nota.valor,
            Avaliacao.peso,
            Avaliacao.nota_maxima,
        )
        .join(Avaliacao, Avaliacao.id == Nota.avaliacao_id)
        .join(Disciplina, Disciplina.id == Avaliacao.disciplina_id)
        .where(
            Nota.aluno_id == aluno_id,
            Nota.tenant_id == tenant_id,
            Nota.deleted_at.is_(None),
        )
    )
    by_disc: dict[uuid.UUID, dict] = {}
    for row in (await db.execute(notas_q)).all():
        d = by_disc.setdefault(row.disciplina_id, {"nome": row.disciplina_nome, "notas": []})
        d["notas"].append((Decimal(str(row.valor)), Decimal(str(row.peso))))

    # Faltas por disciplina + totais
    faltas_q = select(Falta.disciplina_id, Falta.tipo).where(
        Falta.aluno_id == aluno_id,
        Falta.tenant_id == tenant_id,
        Falta.deleted_at.is_(None),
    )
    faltas_total = 0
    faltas_just = 0
    faltas_inj = 0
    faltas_per_disc: dict[uuid.UUID, int] = {}
    for row in (await db.execute(faltas_q)).all():
        faltas_total += 1
        if row.tipo == "justificada":
            faltas_just += 1
        elif row.tipo == "injustificada":
            faltas_inj += 1
        faltas_per_disc[row.disciplina_id] = faltas_per_disc.get(row.disciplina_id, 0) + 1

    # Disciplinas presentes em notas OU faltas
    disc_ids = set(by_disc.keys()) | set(faltas_per_disc.keys())
    disc_resumos: list[AlunoDisciplinaResumo] = []
    medias_validas: list[Decimal] = []
    if disc_ids:
        # Resolver nomes em falta
        nome_q = await db.execute(
            select(Disciplina.id, Disciplina.nome).where(Disciplina.id.in_(disc_ids))
        )
        nomes = {r.id: r.nome for r in nome_q.all()}
        for disc_id in disc_ids:
            entry = by_disc.get(disc_id, {"nome": nomes.get(disc_id, "—"), "notas": []})
            notas_data: list[tuple[Decimal, Decimal]] = entry["notas"]
            if notas_data:
                soma_pesos = sum((p for _, p in notas_data), Decimal("0"))
                if soma_pesos > 0:
                    media = sum((v * p for v, p in notas_data), Decimal("0")) / soma_pesos
                    media = media.quantize(Decimal("0.01"))
                else:
                    media = _media([v for v, _ in notas_data])
                if media is not None:
                    medias_validas.append(media)
            else:
                media = None
            disc_resumos.append(
                AlunoDisciplinaResumo(
                    disciplina_id=disc_id,
                    disciplina_nome=entry["nome"],
                    media=media,
                    faltas=faltas_per_disc.get(disc_id, 0),
                )
            )
        disc_resumos.sort(key=lambda d: d.disciplina_nome)

    media_geral = _media(medias_validas)

    # Próximas avaliações — futuro, da turma do aluno
    proximas_avaliacoes: list[ProximaAvaliacaoItem] = []
    if mat_row and mat_row.turma_id:
        prox_q = (
            select(
                Avaliacao.id,
                Avaliacao.disciplina_id,
                Disciplina.nome.label("disciplina_nome"),
                Avaliacao.tipo,
                Avaliacao.data,
                Avaliacao.nota_maxima,
            )
            .join(Disciplina, Disciplina.id == Avaliacao.disciplina_id)
            .where(
                Avaliacao.turma_id == mat_row.turma_id,
                Avaliacao.tenant_id == tenant_id,
                Avaliacao.deleted_at.is_(None),
                Avaliacao.data >= date.today(),
            )
            .order_by(Avaliacao.data)
            .limit(10)
        )
        for r in (await db.execute(prox_q)).all():
            proximas_avaliacoes.append(
                ProximaAvaliacaoItem(
                    avaliacao_id=r.id,
                    disciplina_id=r.disciplina_id,
                    disciplina_nome=r.disciplina_nome,
                    tipo=r.tipo,
                    data=r.data,
                    nota_maxima=r.nota_maxima,
                )
            )

    return AlunoStats(
        aluno_id=aluno_id,
        nome=aluno_row.nome_completo,
        n_processo=aluno_row.n_processo,
        matricula_id=mat_row.matricula_id if mat_row else None,
        classe=mat_row.classe if mat_row else None,
        turma_id=mat_row.turma_id if mat_row else None,
        turma_nome=mat_row.turma_nome if mat_row else None,
        media_geral=media_geral,
        total_faltas=faltas_total,
        faltas_justificadas=faltas_just,
        faltas_injustificadas=faltas_inj,
        proximas_avaliacoes=proximas_avaliacoes,
        disciplinas=disc_resumos,
    )


@router.get("/dashboard/aluno", response_model=AlunoStats)
async def dashboard_aluno(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    aluno_id: uuid.UUID | None = Query(default=None, description="Sobreposição (admin/encarregado)"),
) -> AlunoStats:
    """Resumo do aluno: média geral, faltas, próximas avaliações, médias por disciplina."""
    tenant_id = current_user.tenant_id

    target_aluno_id = aluno_id
    if target_aluno_id is None:
        # Resolver via user.pessoa_id → Aluno
        from src.modules.identity.infrastructure.models import Utilizador
        u = await db.execute(
            select(Utilizador.pessoa_id).where(Utilizador.id == current_user.user_id)
        )
        pessoa_id = u.scalar_one_or_none()
        if pessoa_id is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilizador sem pessoa associada")
        a_q = await db.execute(
            select(Aluno.id).where(
                Aluno.pessoa_id == pessoa_id,
                Aluno.tenant_id == tenant_id,
                Aluno.deleted_at.is_(None),
            )
        )
        target_aluno_id = a_q.scalar_one_or_none()
        if target_aluno_id is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilizador não é aluno")

    return await _aluno_stats(db, tenant_id, target_aluno_id)


# ──────────────────────────────────────────────
# /dashboard/encarregado  (Task #41)
# ──────────────────────────────────────────────

@router.get("/dashboard/encarregado", response_model=EncarregadoStats)
async def dashboard_encarregado(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> EncarregadoStats:
    """Resumo dos educandos vinculados ao encarregado logado."""
    tenant_id = current_user.tenant_id

    from src.modules.identity.infrastructure.models import Utilizador
    u = await db.execute(
        select(Utilizador.pessoa_id).where(Utilizador.id == current_user.user_id)
    )
    pessoa_id = u.scalar_one_or_none()
    if pessoa_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilizador sem pessoa associada")

    enc_q = await db.execute(
        select(Encarregado.id, Pessoa.nome_completo)
        .join(Pessoa, Pessoa.id == Encarregado.pessoa_id)
        .where(
            Encarregado.pessoa_id == pessoa_id,
            Encarregado.tenant_id == tenant_id,
            Encarregado.deleted_at.is_(None),
        )
    )
    enc_row = enc_q.first()
    if enc_row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilizador não é encarregado")

    encarregado_id = enc_row.id

    # Lista educandos vinculados
    vinc_q = await db.execute(
        select(VinculoAlunoEncarregado.aluno_id)
        .where(
            VinculoAlunoEncarregado.encarregado_id == encarregado_id,
            VinculoAlunoEncarregado.tenant_id == tenant_id,
            VinculoAlunoEncarregado.deleted_at.is_(None),
        )
    )
    aluno_ids = [r[0] for r in vinc_q.all()]

    educandos: list[EducandoResumo] = []
    for aluno_id in aluno_ids:
        try:
            stats = await _aluno_stats(db, tenant_id, aluno_id)
        except HTTPException:
            continue
        educandos.append(
            EducandoResumo(
                aluno_id=stats.aluno_id,
                nome=stats.nome,
                n_processo=stats.n_processo,
                classe=stats.classe,
                turma_nome=stats.turma_nome,
                media_geral=stats.media_geral,
                total_faltas=stats.total_faltas,
                faltas_injustificadas=stats.faltas_injustificadas,
            )
        )

    educandos.sort(key=lambda e: e.nome)
    return EncarregadoStats(
        encarregado_id=encarregado_id,
        nome=enc_row.nome_completo,
        educandos=educandos,
    )


# ──────────────────────────────────────────────
# /turmas/{id}/pauta  (Task #43)
# ──────────────────────────────────────────────

@router.get("/turmas/{turma_id}/pauta", response_model=PautaResponse)
async def get_pauta(
    turma_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    periodo: int = Query(default=1, ge=1, le=3),
) -> PautaResponse:
    """Pauta da turma: grid aluno × disciplina com médias por período."""
    tenant_id = current_user.tenant_id

    turma_q = (
        select(
            Turma.id,
            Turma.nome,
            Turma.classe,
            Turma.ano_letivo_id,
            AnoLetivo.designacao.label("ano_letivo_designacao"),
        )
        .join(AnoLetivo, AnoLetivo.id == Turma.ano_letivo_id)
        .where(
            Turma.id == turma_id,
            Turma.tenant_id == tenant_id,
            Turma.deleted_at.is_(None),
        )
    )
    turma_row = (await db.execute(turma_q)).first()
    if turma_row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Turma não encontrada")

    # Disciplinas da turma — DISTINCT via Avaliacao OR HorarioAula
    disc_q = (
        select(distinct(Disciplina.id), Disciplina.nome, Disciplina.codigo)
        .where(
            Disciplina.tenant_id == tenant_id,
            Disciplina.deleted_at.is_(None),
            Disciplina.id.in_(
                select(HorarioAula.disciplina_id).where(
                    HorarioAula.turma_id == turma_id,
                    HorarioAula.tenant_id == tenant_id,
                    HorarioAula.deleted_at.is_(None),
                )
            ),
        )
        .order_by(Disciplina.nome)
    )
    disc_rows = (await db.execute(disc_q)).all()
    disciplinas = [
        {"id": str(r[0]), "nome": r.nome, "codigo": r.codigo} for r in disc_rows
    ]

    # Alunos da turma
    alunos_q = (
        select(
            Aluno.id.label("aluno_id"),
            Matricula.id.label("matricula_id"),
            Pessoa.nome_completo,
            Aluno.n_processo,
        )
        .select_from(AlocacaoTurma)
        .join(Matricula, Matricula.id == AlocacaoTurma.matricula_id)
        .join(Aluno, Aluno.id == Matricula.aluno_id)
        .join(Pessoa, Pessoa.id == Aluno.pessoa_id)
        .where(
            AlocacaoTurma.turma_id == turma_id,
            AlocacaoTurma.tenant_id == tenant_id,
            AlocacaoTurma.deleted_at.is_(None),
            Aluno.deleted_at.is_(None),
            Pessoa.deleted_at.is_(None),
        )
        .order_by(Pessoa.nome_completo)
    )
    alunos_rows = (await db.execute(alunos_q)).all()
    aluno_ids = [r.aluno_id for r in alunos_rows]

    # Notas da turma no período
    notas_q = (
        select(
            Nota.aluno_id,
            Avaliacao.disciplina_id,
            Nota.valor,
            Avaliacao.peso,
        )
        .join(Avaliacao, Avaliacao.id == Nota.avaliacao_id)
        .where(
            Avaliacao.turma_id == turma_id,
            Avaliacao.periodo == periodo,
            Avaliacao.tenant_id == tenant_id,
            Avaliacao.deleted_at.is_(None),
            Nota.tenant_id == tenant_id,
            Nota.deleted_at.is_(None),
            Nota.aluno_id.in_(aluno_ids) if aluno_ids else False,
        )
    )
    # estrutura: {aluno_id: {disciplina_id: [(valor, peso), ...]}}
    notas_map: dict[uuid.UUID, dict[uuid.UUID, list[tuple[Decimal, Decimal]]]] = {}
    if aluno_ids:
        for row in (await db.execute(notas_q)).all():
            notas_map.setdefault(row.aluno_id, {}).setdefault(
                row.disciplina_id, []
            ).append((Decimal(str(row.valor)), Decimal(str(row.peso))))

    linhas: list[PautaAlunoLinha] = []
    for a in alunos_rows:
        medias_por_disc: dict[str, Decimal | None] = {}
        medias_validas: list[Decimal] = []
        a_notas = notas_map.get(a.aluno_id, {})
        for d in disc_rows:
            disc_id = d[0]
            pares = a_notas.get(disc_id, [])
            if not pares:
                medias_por_disc[str(disc_id)] = None
                continue
            soma_pesos = sum((p for _, p in pares), Decimal("0"))
            if soma_pesos > 0:
                m = sum((v * p for v, p in pares), Decimal("0")) / soma_pesos
            else:
                m = sum((v for v, _ in pares), Decimal("0")) / Decimal(len(pares))
            m = m.quantize(Decimal("0.01"))
            medias_por_disc[str(disc_id)] = m
            medias_validas.append(m)

        linhas.append(
            PautaAlunoLinha(
                aluno_id=a.aluno_id,
                matricula_id=a.matricula_id,
                nome=a.nome_completo,
                n_processo=a.n_processo,
                medias_por_disciplina=medias_por_disc,
                media_geral=_media(medias_validas),
            )
        )

    return PautaResponse(
        turma_id=turma_row.id,
        turma_nome=turma_row.nome,
        classe=turma_row.classe,
        ano_letivo_designacao=turma_row.ano_letivo_designacao,
        periodo=periodo,
        disciplinas=disciplinas,
        linhas=linhas,
    )
