"""
Seed MVP — Popula a base de dados SIENA com dados realistas para o piloto angolano.

Fase 1.5.1: Escala os dados base para nivel MVP:
  - 100 alunos, 15 professores, 80 encarregados
  - 6 turmas (7.ª-A/B, 8.ª-A/B, 9.ª-A/B)
  - Curriculos completos para 7.ª, 8.ª e 9.ª classes
  - Horarios semanais completos para todas as turmas
  - Matriculas aprovadas + alocacoes em turmas
  - Avaliacoes do 1.o periodo (testes + trabalhos)
  - Notas e faltas realistas

Uso:
    cd backend
    python -m scripts.seed_mvp
"""

import asyncio
import os
import random
from datetime import date, time, datetime, timedelta
from decimal import Decimal

from sqlalchemy import select, text, func
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.modules.directory.infrastructure.models import (
    Pessoa,
    Aluno,
    Professor,
    Encarregado,
    VinculoAlunoEncarregado,
)
from src.modules.enrollment.infrastructure.models import Matricula, AlocacaoTurma
from src.modules.academico.infrastructure.models import (
    Curriculo,
    Disciplina,
    Turma,
    HorarioAula,
)
from src.modules.avaliacoes.infrastructure.models import Avaliacao, Nota, Falta
from src.modules.escolas.infrastructure.models import AnoLetivo

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+psycopg://siena:siena@localhost:5432/siena"
)

# ---------------------------------------------------------------------------
# Reproducibility
# ---------------------------------------------------------------------------
random.seed(42)

# ---------------------------------------------------------------------------
# Name pools — realistic Angolan names
# ---------------------------------------------------------------------------
ANGOLAN_FIRST_NAMES_M = [
    "Manuel", "Jose", "Antonio", "Pedro", "Carlos", "Francisco", "Joao",
    "Paulo", "Fernando", "Alberto", "Domingos", "Miguel", "Rafael", "Tiago",
    "Ricardo", "Luis", "Andre", "Daniel", "Eduardo", "Gabriel", "Bernardo",
    "Helder", "Isaias", "Jorge", "Mateus", "Nelson", "Osvaldo", "Quintino",
    "Roberto", "Samuel", "Tomás", "Valentim", "Wilson", "Xavier", "Zacarias",
    "Afonso", "Bento", "Celestino", "Dario", "Evaristo", "Feliciano",
    "Gaspar", "Henrique", "Inácio", "Januário", "Kizua", "Lázaro",
    "Marcelino", "Narciso", "Orlando",
]

ANGOLAN_FIRST_NAMES_F = [
    "Ana", "Maria", "Teresa", "Rosa", "Joana", "Helena", "Luisa",
    "Fernanda", "Catarina", "Isabel", "Beatriz", "Sofia", "Clara",
    "Francisca", "Margarida", "Esperanca", "Graca", "Patricia", "Sandra",
    "Raquel", "Celeste", "Dulce", "Eugenia", "Filomena", "Gloria",
    "Ines", "Judite", "Leonor", "Marta", "Natalia", "Olinda", "Paula",
    "Rita", "Sara", "Telma", "Ursula", "Vera", "Zulmira", "Adelia",
    "Branca", "Carla", "Diana", "Elisa", "Fatima", "Guiomar",
    "Herminia", "Ivone", "Josefina", "Kieza", "Luciana",
]

ANGOLAN_LAST_NAMES = [
    "da Silva", "Santos", "Neto", "Joao", "Domingos", "Costa", "Ferreira",
    "Pereira", "Sousa", "Gomes", "Rodrigues", "Martins", "Fernandes",
    "Teixeira", "Lopes", "Almeida", "Oliveira", "Mendes", "Ribeiro",
    "Cardoso", "Nunes", "Monteiro", "Vieira", "Carvalho", "Moreira",
    "Baptista", "Pinto", "Gaspar", "Sebastiao", "Kiala", "Kambuengo",
    "Mangueira", "Bumba", "Lutonda", "Cassule", "Cahombo", "Quiala",
    "Mussungo", "Tchimbali", "Ngola",
]

PROFISSOES = [
    "Engenheiro Civil", "Professor", "Enfermeira", "Comerciante", "Motorista",
    "Medico", "Advogado", "Contabilista", "Funcionario Publico", "Agricultor",
    "Mecanico", "Electricista", "Pedreiro", "Cozinheira", "Vendedora",
    "Policia", "Militar", "Pescador", "Carpinteiro", "Costureira",
    "Informatico", "Jornalista", "Economista", "Arquitecto", "Farmaceutico",
]

ESCOLARIDADES = [
    "6.ª Classe", "9.ª Classe", "12.ª Classe",
    "Bacharelato", "Licenciatura", "Mestrado",
]

ESPECIALIDADES_PROF = [
    "Matematica", "Lingua Portuguesa", "Ciencias Naturais", "Historia",
    "Geografia", "Educacao Fisica", "Educacao Visual", "Ingles",
]

NIVEIS_ACADEMICOS_PROF = [
    "Licenciatura em Matematica", "Licenciatura em Letras",
    "Bacharelato em Biologia", "Licenciatura em Historia",
    "Licenciatura em Geografia", "Licenciatura em Educacao Fisica",
    "Licenciatura em Artes Visuais", "Licenciatura em Ingles",
    "Mestrado em Pedagogia", "Bacharelato em Ciencias da Educacao",
    "Licenciatura em Ciencias da Educacao", "Bacharelato em Matematica",
]

# Discipline definitions per class (nome, codigo_suffix, carga_horaria)
DISCIPLINAS_TEMPLATE = [
    ("Lingua Portuguesa", "LP", 5),
    ("Matematica", "MAT", 5),
    ("Ciencias Naturais", "CN", 3),
    ("Historia", "HIST", 3),
    ("Geografia", "GEO", 3),
    ("Educacao Fisica", "EF", 2),
    ("Educacao Visual", "EV", 2),
    ("Ingles", "ING", 3),
]

DIAS_SEMANA = ["segunda", "terca", "quarta", "quinta", "sexta"]

# Time slots for matutino
SLOTS_MATUTINO = [
    (time(7, 30), time(8, 15)),
    (time(8, 20), time(9, 5)),
    (time(9, 20), time(10, 5)),
    (time(10, 10), time(10, 55)),
    (time(11, 0), time(11, 45)),
]

# Time slots for vespertino
SLOTS_VESPERTINO = [
    (time(13, 0), time(13, 45)),
    (time(13, 50), time(14, 35)),
    (time(14, 50), time(15, 35)),
    (time(15, 40), time(16, 25)),
    (time(16, 30), time(17, 15)),
]

VINCULO_TIPOS = ["pai", "mae", "tutor", "outro"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _random_name(sexo: str) -> str:
    """Generate a random full name (first + 1-2 last names)."""
    pool = ANGOLAN_FIRST_NAMES_M if sexo == "M" else ANGOLAN_FIRST_NAMES_F
    first = random.choice(pool)
    n_last = random.choice([1, 2])
    lasts = random.sample(ANGOLAN_LAST_NAMES, n_last)
    return f"{first} {' '.join(lasts)}"


def _random_bi() -> str:
    """Generate BI in format 00XXXXXXLA0YY."""
    digits = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    suffix = ''.join([str(random.randint(0, 9)) for _ in range(2)])
    return f"00{digits}LA0{suffix}"


def _random_date(start_year: int, end_year: int) -> date:
    """Random date between Jan 1 start_year and Dec 31 end_year."""
    start = date(start_year, 1, 1)
    end = date(end_year, 12, 31)
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


def _random_date_in_range(start: date, end: date) -> date:
    """Random date within a specific date range."""
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


# ---------------------------------------------------------------------------
# Main seed
# ---------------------------------------------------------------------------
async def seed_mvp() -> None:
    engine = create_async_engine(DATABASE_URL)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    # ------------------------------------------------------------------
    # Step 0: Run existing module seeds to ensure base data
    # ------------------------------------------------------------------
    print("=" * 60)
    print("SIENA MVP Seed — Fase 1.5.1")
    print("=" * 60)

    print("\n[0/10] Running base module seeds...")

    # Identity seed creates its own engine/session
    from src.modules.identity.application.seed import seed as seed_identity_main

    await seed_identity_main()

    async with session_factory() as session:
        from src.modules.escolas.application.seed import seed_escolas
        from src.modules.directory.application.seed import seed_directory
        from src.modules.enrollment.application.seed import seed_enrollment
        from src.modules.academico.application.seed import seed_academico
        from src.modules.avaliacoes.application.seed import seed_avaliacoes

        await seed_escolas(session)
        await seed_directory(session)
        await seed_enrollment(session)
        await seed_academico(session)
        await seed_avaliacoes(session)

    print("  Base seeds complete.")

    # ------------------------------------------------------------------
    # Step 1: Fetch references (tenant, ano_letivo, existing data)
    # ------------------------------------------------------------------
    async with session_factory() as session:
        print("\n[1/10] Fetching tenant and ano_letivo...")

        tenant_row = await session.execute(
            text("SELECT id FROM identity.tenant WHERE nome = 'Escola Piloto SIENA'")
        )
        tenant_id = tenant_row.scalar_one()
        print(f"  tenant_id = {tenant_id}")

        ano_result = await session.execute(
            select(AnoLetivo).where(
                AnoLetivo.tenant_id == tenant_id,
                AnoLetivo.ativo.is_(True),
                AnoLetivo.deleted_at.is_(None),
            )
        )
        ano_letivo = ano_result.scalar_one()
        print(f"  ano_letivo = {ano_letivo.designacao} (id: {ano_letivo.id})")

        # Existing counts
        existing_alunos_r = await session.execute(
            select(func.count(Aluno.id)).where(
                Aluno.tenant_id == tenant_id, Aluno.deleted_at.is_(None)
            )
        )
        existing_alunos_count = existing_alunos_r.scalar()

        existing_profs_r = await session.execute(
            select(func.count(Professor.id)).where(
                Professor.tenant_id == tenant_id, Professor.deleted_at.is_(None)
            )
        )
        existing_profs_count = existing_profs_r.scalar()

        existing_encs_r = await session.execute(
            select(func.count(Encarregado.id)).where(
                Encarregado.tenant_id == tenant_id, Encarregado.deleted_at.is_(None)
            )
        )
        existing_encs_count = existing_encs_r.scalar()

        existing_turmas_r = await session.execute(
            select(func.count(Turma.id)).where(
                Turma.tenant_id == tenant_id, Turma.deleted_at.is_(None)
            )
        )
        existing_turmas_count = existing_turmas_r.scalar()

        print(
            f"  Existing: {existing_alunos_count} alunos, "
            f"{existing_profs_count} profs, {existing_encs_count} encarregados, "
            f"{existing_turmas_count} turmas"
        )

        # Check idempotency — if we already have MVP-level data, skip
        if existing_alunos_count >= 100:
            print("\n  MVP data already present (>=100 alunos). Nothing to do.")
            await engine.dispose()
            return

        # Fetch all existing professors (we will need them for turma assignments)
        all_profs_r = await session.execute(
            select(Professor).where(
                Professor.tenant_id == tenant_id, Professor.deleted_at.is_(None)
            )
        )
        existing_professors = list(all_profs_r.scalars().all())

        # Fetch existing alunos
        all_alunos_r = await session.execute(
            select(Aluno).where(
                Aluno.tenant_id == tenant_id, Aluno.deleted_at.is_(None)
            )
        )
        existing_alunos = list(all_alunos_r.scalars().all())

        # Fetch existing turmas
        all_turmas_r = await session.execute(
            select(Turma).where(
                Turma.tenant_id == tenant_id, Turma.deleted_at.is_(None)
            )
        )
        existing_turmas = list(all_turmas_r.scalars().all())

        # Fetch existing curriculos
        all_curriculos_r = await session.execute(
            select(Curriculo).where(
                Curriculo.tenant_id == tenant_id, Curriculo.deleted_at.is_(None)
            )
        )
        existing_curriculos = list(all_curriculos_r.scalars().all())
        existing_classe_set = {c.classe for c in existing_curriculos}

        # Fetch existing disciplinas (for all curriculos)
        all_disc_r = await session.execute(
            select(Disciplina).where(
                Disciplina.tenant_id == tenant_id, Disciplina.deleted_at.is_(None)
            )
        )
        existing_disciplinas = list(all_disc_r.scalars().all())

        # Fetch existing matriculas
        all_matr_r = await session.execute(
            select(Matricula).where(
                Matricula.tenant_id == tenant_id, Matricula.deleted_at.is_(None)
            )
        )
        existing_matriculas = list(all_matr_r.scalars().all())
        matriculated_aluno_ids = {m.aluno_id for m in existing_matriculas}

        # ------------------------------------------------------------------
        # Step 2: Create additional professors (12 new -> total 15)
        # ------------------------------------------------------------------
        print("\n[2/10] Creating additional professores...")
        new_profs_needed = 15 - existing_profs_count
        new_professors = []
        for i in range(new_profs_needed):
            sexo = random.choice(["M", "F"])
            nome = _random_name(sexo)
            bi = _random_bi()
            nascimento = _random_date(1975, 1995)
            esp_idx = (existing_profs_count + i) % len(ESPECIALIDADES_PROF)

            pessoa = Pessoa(
                tenant_id=tenant_id,
                nome_completo=nome,
                bi_identificacao=bi,
                dt_nascimento=nascimento,
                sexo=sexo,
                nacionalidade="Angolana",
                telefone=f"+244 9{random.randint(10, 99)} {random.randint(100, 999)} {random.randint(100, 999)}",
            )
            session.add(pessoa)
            await session.flush()

            prof = Professor(
                tenant_id=tenant_id,
                pessoa_id=pessoa.id,
                codigo_funcional=f"PROF-{existing_profs_count + i + 1:03d}",
                especialidade=ESPECIALIDADES_PROF[esp_idx],
                carga_horaria_semanal=random.choice([20, 22, 24]),
                tipo_contrato=random.choice(["efetivo", "contrato"]),
                nivel_academico=random.choice(NIVEIS_ACADEMICOS_PROF),
            )
            session.add(prof)
            await session.flush()
            new_professors.append(prof)

        all_professors = existing_professors + new_professors
        print(f"  Created {len(new_professors)} new professors (total: {len(all_professors)})")

        # ------------------------------------------------------------------
        # Step 3: Create additional encarregados (75 new -> total 80)
        # ------------------------------------------------------------------
        print("\n[3/10] Creating additional encarregados...")
        # Fetch existing encarregados
        all_enc_r = await session.execute(
            select(Encarregado).where(
                Encarregado.tenant_id == tenant_id, Encarregado.deleted_at.is_(None)
            )
        )
        existing_encarregados = list(all_enc_r.scalars().all())

        new_encs_needed = 80 - existing_encs_count
        new_encarregados = []
        for i in range(new_encs_needed):
            sexo = random.choice(["M", "F"])
            nome = _random_name(sexo)
            bi = _random_bi()
            nascimento = _random_date(1970, 1990)

            pessoa = Pessoa(
                tenant_id=tenant_id,
                nome_completo=nome,
                bi_identificacao=bi,
                dt_nascimento=nascimento,
                sexo=sexo,
                nacionalidade="Angolana",
                telefone=f"+244 9{random.randint(10, 99)} {random.randint(100, 999)} {random.randint(100, 999)}",
            )
            session.add(pessoa)
            await session.flush()

            enc = Encarregado(
                tenant_id=tenant_id,
                pessoa_id=pessoa.id,
                profissao=random.choice(PROFISSOES),
                escolaridade=random.choice(ESCOLARIDADES),
            )
            session.add(enc)
            await session.flush()
            new_encarregados.append(enc)

        all_encarregados = existing_encarregados + new_encarregados
        print(f"  Created {len(new_encarregados)} new encarregados (total: {len(all_encarregados)})")

        # ------------------------------------------------------------------
        # Step 4: Create additional alunos (95 new -> total 100)
        # ------------------------------------------------------------------
        print("\n[4/10] Creating additional alunos...")
        new_alunos_needed = 100 - existing_alunos_count
        new_alunos = []
        for i in range(new_alunos_needed):
            sexo = random.choice(["M", "F"])
            nome = _random_name(sexo)
            bi = _random_bi()
            nascimento = _random_date(2010, 2013)
            n_proc = f"ALU-2026-{existing_alunos_count + i + 1:03d}"

            pessoa = Pessoa(
                tenant_id=tenant_id,
                nome_completo=nome,
                bi_identificacao=bi,
                dt_nascimento=nascimento,
                sexo=sexo,
                nacionalidade="Angolana",
            )
            session.add(pessoa)
            await session.flush()

            aluno = Aluno(
                tenant_id=tenant_id,
                pessoa_id=pessoa.id,
                n_processo=n_proc,
                ano_ingresso=2026,
                necessidades_especiais=(random.random() < 0.05),
            )
            session.add(aluno)
            await session.flush()
            new_alunos.append(aluno)

        all_alunos = existing_alunos + new_alunos
        print(f"  Created {len(new_alunos)} new alunos (total: {len(all_alunos)})")

        # ------------------------------------------------------------------
        # Step 5: Create vinculos aluno <-> encarregado
        # ------------------------------------------------------------------
        print("\n[5/10] Creating vinculos aluno-encarregado...")
        # Check existing vinculos
        existing_vinculos_r = await session.execute(
            select(VinculoAlunoEncarregado.aluno_id).where(
                VinculoAlunoEncarregado.tenant_id == tenant_id,
                VinculoAlunoEncarregado.deleted_at.is_(None),
            ).distinct()
        )
        alunos_with_vinculos = {row[0] for row in existing_vinculos_r.fetchall()}

        vinculo_count = 0
        enc_idx = 0
        for aluno in all_alunos:
            if aluno.id in alunos_with_vinculos:
                continue

            # Each aluno gets 1-2 encarregados
            n_encs = random.choice([1, 1, 1, 2])  # 75% get 1, 25% get 2
            for j in range(n_encs):
                enc = all_encarregados[enc_idx % len(all_encarregados)]
                enc_idx += 1
                tipo = random.choice(VINCULO_TIPOS)
                session.add(
                    VinculoAlunoEncarregado(
                        tenant_id=tenant_id,
                        aluno_id=aluno.id,
                        encarregado_id=enc.id,
                        tipo=tipo,
                        principal=(j == 0),
                    )
                )
                vinculo_count += 1

        await session.flush()
        print(f"  Created {vinculo_count} new vinculos")

        # ------------------------------------------------------------------
        # Step 6: Create curriculos for 8.ª and 9.ª classes
        # ------------------------------------------------------------------
        print("\n[6/10] Creating curriculos for 8.ª and 9.ª classes...")
        all_curriculos = {c.classe: c for c in existing_curriculos}
        all_disciplinas_by_classe: dict[str, list[Disciplina]] = {}

        # Group existing disciplinas by curriculo
        for d in existing_disciplinas:
            for c in existing_curriculos:
                if d.curriculo_id == c.id:
                    all_disciplinas_by_classe.setdefault(c.classe, []).append(d)

        for classe_label, classe_num in [("8.ª", "8"), ("9.ª", "9")]:
            if classe_label in existing_classe_set:
                print(f"  Curriculo {classe_label} already exists, skipping.")
                continue

            curriculo = Curriculo(
                tenant_id=tenant_id,
                nivel="secundario_1ciclo",
                classe=classe_label,
                ano_letivo_id=ano_letivo.id,
                carga_horaria_total=30,
            )
            session.add(curriculo)
            await session.flush()
            all_curriculos[classe_label] = curriculo

            disc_list = []
            for nome, codigo_pfx, carga in DISCIPLINAS_TEMPLATE:
                disc = Disciplina(
                    tenant_id=tenant_id,
                    nome=nome,
                    codigo=f"{codigo_pfx}-{classe_num}",
                    curriculo_id=curriculo.id,
                    carga_horaria_semanal=carga,
                )
                session.add(disc)
                await session.flush()
                disc_list.append(disc)

            all_disciplinas_by_classe[classe_label] = disc_list
            print(f"  Created curriculo {classe_label} with {len(disc_list)} disciplinas")

        # Make sure 7.ª is in the dict
        if "7.ª" not in all_disciplinas_by_classe:
            # Reload from DB
            for c in existing_curriculos:
                if c.classe == "7.ª":
                    disc_r = await session.execute(
                        select(Disciplina).where(
                            Disciplina.curriculo_id == c.id,
                            Disciplina.deleted_at.is_(None),
                        )
                    )
                    all_disciplinas_by_classe["7.ª"] = list(disc_r.scalars().all())

        # ------------------------------------------------------------------
        # Step 7: Create 4 additional turmas (total 6)
        # ------------------------------------------------------------------
        print("\n[7/10] Creating additional turmas...")
        existing_turma_names = {t.nome for t in existing_turmas}

        # Turma definitions: (nome, classe, turno, sala)
        all_turma_defs = [
            ("7.ª-A", "7.ª", "matutino", "Sala 1A"),
            ("7.ª-B", "7.ª", "matutino", "Sala 1B"),
            ("8.ª-A", "8.ª", "vespertino", "Sala 2A"),
            ("8.ª-B", "8.ª", "vespertino", "Sala 1A"),
            ("9.ª-A", "9.ª", "matutino", "Sala 2A"),
            ("9.ª-B", "9.ª", "matutino", "Sala 1B"),
        ]

        new_turma_count = 0
        all_turmas_dict: dict[str, Turma] = {t.nome: t for t in existing_turmas}

        for idx, (t_nome, t_classe, t_turno, t_sala) in enumerate(all_turma_defs):
            if t_nome in existing_turma_names:
                continue

            # Distribute regentes among professors
            regente = all_professors[idx % len(all_professors)]
            turma = Turma(
                tenant_id=tenant_id,
                nome=t_nome,
                classe=t_classe,
                turno=t_turno,
                ano_letivo_id=ano_letivo.id,
                capacidade_max=35,
                professor_regente_id=regente.id,
                sala=t_sala,
            )
            session.add(turma)
            await session.flush()
            all_turmas_dict[t_nome] = turma
            new_turma_count += 1

        print(f"  Created {new_turma_count} new turmas (total: {len(all_turmas_dict)})")

        # ------------------------------------------------------------------
        # Step 8: Create horarios for all 6 turmas
        # ------------------------------------------------------------------
        print("\n[8/10] Creating horarios for all turmas...")

        # Check existing horarios
        existing_horarios_r = await session.execute(
            select(HorarioAula.turma_id).where(
                HorarioAula.tenant_id == tenant_id,
                HorarioAula.deleted_at.is_(None),
            ).distinct()
        )
        turmas_with_horarios = {row[0] for row in existing_horarios_r.fetchall()}

        # Build a professor-schedule tracker to avoid conflicts:
        # prof_schedule[(prof_id, dia, slot_index)] = turma_nome
        prof_schedule: dict[tuple, str] = {}

        # Map each professor to the disciplines they can teach (by especialidade)
        especialidade_to_disc_idx = {
            "Lingua Portuguesa": 0,
            "Matematica": 1,
            "Ciencias Naturais": 2,
            "Historia": 3,
            "Geografia": 4,
            "Educacao Fisica": 5,
            "Educacao Visual": 6,
            "Ingles": 7,
        }

        # Build a pool of professors per discipline index
        profs_by_disc_idx: dict[int, list[Professor]] = {i: [] for i in range(8)}
        for p in all_professors:
            idx = especialidade_to_disc_idx.get(p.especialidade)
            if idx is not None:
                profs_by_disc_idx[idx].append(p)
        # Fill gaps: if no professor for a discipline, assign from any pool
        for d_idx in range(8):
            if not profs_by_disc_idx[d_idx]:
                profs_by_disc_idx[d_idx] = list(all_professors)

        horario_total = 0
        for t_nome, t_classe, t_turno, _ in all_turma_defs:
            turma_obj = all_turmas_dict.get(t_nome)
            if turma_obj is None:
                continue
            if turma_obj.id in turmas_with_horarios:
                print(f"    Horarios for {t_nome} already exist, skipping.")
                continue

            slots = SLOTS_MATUTINO if t_turno == "matutino" else SLOTS_VESPERTINO
            disc_list = all_disciplinas_by_classe.get(t_classe, [])
            if not disc_list:
                print(f"    No disciplinas for classe {t_classe}, skipping horarios.")
                continue

            # Distribute disciplines across the week.
            # Each discipline needs `carga` slots per week.
            disc_slots: list[int] = []  # list of disc indices to fill weekly slots
            for d_i, d in enumerate(disc_list):
                disc_slots.extend([d_i] * d.carga_horaria_semanal)

            # Shuffle to spread them across the week
            random.shuffle(disc_slots)

            slot_cursor = 0
            for dia in DIAS_SEMANA:
                for s_idx, (h_inicio, h_fim) in enumerate(slots):
                    if slot_cursor >= len(disc_slots):
                        break
                    d_i = disc_slots[slot_cursor]
                    disc = disc_list[d_i]

                    # Find a professor for this discipline that is free at this slot
                    candidates = profs_by_disc_idx.get(d_i, all_professors)
                    assigned_prof = None
                    for cand in candidates:
                        sched_key = (cand.id, dia, s_idx, t_turno)
                        if sched_key not in prof_schedule:
                            assigned_prof = cand
                            prof_schedule[sched_key] = t_nome
                            break

                    if assigned_prof is None:
                        # Fallback: pick any available professor
                        for p in all_professors:
                            sched_key = (p.id, dia, s_idx, t_turno)
                            if sched_key not in prof_schedule:
                                assigned_prof = p
                                prof_schedule[sched_key] = t_nome
                                break

                    if assigned_prof is None:
                        # Last resort — just use any professor (conflict accepted)
                        assigned_prof = random.choice(all_professors)

                    session.add(
                        HorarioAula(
                            tenant_id=tenant_id,
                            turma_id=turma_obj.id,
                            disciplina_id=disc.id,
                            professor_id=assigned_prof.id,
                            dia_semana=dia,
                            hora_inicio=h_inicio,
                            hora_fim=h_fim,
                        )
                    )
                    slot_cursor += 1
                    horario_total += 1

        await session.flush()
        print(f"  Created {horario_total} new horario entries")

        # ------------------------------------------------------------------
        # Step 9: Create matriculas + alocacoes for all alunos
        # ------------------------------------------------------------------
        print("\n[9/10] Creating matriculas and alocacoes...")

        # Distribute 100 alunos across 6 turmas (~16-17 each)
        turma_order = [
            "7.ª-A", "7.ª-B", "8.ª-A", "8.ª-B", "9.ª-A", "9.ª-B",
        ]
        turma_classe_map = {
            "7.ª-A": "7.ª", "7.ª-B": "7.ª",
            "8.ª-A": "8.ª", "8.ª-B": "8.ª",
            "9.ª-A": "9.ª", "9.ª-B": "9.ª",
        }
        turma_turno_map = {
            "7.ª-A": "matutino", "7.ª-B": "matutino",
            "8.ª-A": "vespertino", "8.ª-B": "vespertino",
            "9.ª-A": "matutino", "9.ª-B": "matutino",
        }

        # Build assignment: round-robin alunos into turmas
        aluno_turma_assignments: dict[str, list[Aluno]] = {t: [] for t in turma_order}
        for idx, aluno in enumerate(all_alunos):
            turma_name = turma_order[idx % len(turma_order)]
            aluno_turma_assignments[turma_name].append(aluno)

        matricula_count = 0
        alocacao_count = 0

        for turma_name, alunos_in_turma in aluno_turma_assignments.items():
            turma_obj = all_turmas_dict.get(turma_name)
            if turma_obj is None:
                continue

            classe = turma_classe_map[turma_name]
            turno = turma_turno_map[turma_name]

            for aluno in alunos_in_turma:
                if aluno.id in matriculated_aluno_ids:
                    # Already has a matricula — just ensure alocacao exists
                    # Find the existing matricula
                    existing_m_r = await session.execute(
                        select(Matricula).where(
                            Matricula.tenant_id == tenant_id,
                            Matricula.aluno_id == aluno.id,
                            Matricula.ano_letivo_id == ano_letivo.id,
                            Matricula.deleted_at.is_(None),
                        )
                    )
                    existing_m = existing_m_r.scalar_one_or_none()
                    if existing_m:
                        # Check if alocacao already exists
                        aloc_r = await session.execute(
                            select(AlocacaoTurma).where(
                                AlocacaoTurma.tenant_id == tenant_id,
                                AlocacaoTurma.matricula_id == existing_m.id,
                                AlocacaoTurma.deleted_at.is_(None),
                            )
                        )
                        if aloc_r.scalar_one_or_none() is None:
                            session.add(
                                AlocacaoTurma(
                                    tenant_id=tenant_id,
                                    matricula_id=existing_m.id,
                                    turma_id=turma_obj.id,
                                    data_alocacao=date(2026, 2, 3),
                                )
                            )
                            alocacao_count += 1
                    continue

                matricula = Matricula(
                    tenant_id=tenant_id,
                    aluno_id=aluno.id,
                    ano_letivo_id=ano_letivo.id,
                    classe=classe,
                    turno=turno,
                    estado="aprovada",
                    data_pedido=date(2026, 1, 15),
                    data_aprovacao=date(2026, 2, 1),
                )
                session.add(matricula)
                await session.flush()
                matricula_count += 1

                session.add(
                    AlocacaoTurma(
                        tenant_id=tenant_id,
                        matricula_id=matricula.id,
                        turma_id=turma_obj.id,
                        data_alocacao=date(2026, 2, 3),
                    )
                )
                alocacao_count += 1

        await session.flush()
        print(f"  Created {matricula_count} matriculas + {alocacao_count} alocacoes")

        # ------------------------------------------------------------------
        # Step 10: Create avaliacoes, notas and faltas (1st period)
        # ------------------------------------------------------------------
        print("\n[10/10] Creating avaliacoes, notas and faltas (periodo 1)...")

        # Check existing avaliacoes
        existing_aval_r = await session.execute(
            select(func.count(Avaliacao.id)).where(
                Avaliacao.tenant_id == tenant_id,
                Avaliacao.deleted_at.is_(None),
            )
        )
        existing_aval_count = existing_aval_r.scalar()
        if existing_aval_count > 0:
            print(f"  Avaliacoes already exist ({existing_aval_count}), skipping.")
        else:
            # For each turma x disciplina: 1 teste (peso 0.4) + 1 trabalho (peso 0.3)
            aval_count = 0
            nota_count = 0
            falta_count = 0

            # Pick a professor to be the "lancador" for notas
            # Use the first available professor as default
            default_lancador_id = all_professors[0].id

            for turma_name in turma_order:
                turma_obj = all_turmas_dict.get(turma_name)
                if turma_obj is None:
                    continue

                classe = turma_classe_map[turma_name]
                disc_list = all_disciplinas_by_classe.get(classe, [])
                alunos_in_turma = aluno_turma_assignments.get(turma_name, [])

                for disc in disc_list:
                    # Teste — February
                    teste_date = _random_date_in_range(date(2026, 2, 10), date(2026, 2, 28))
                    teste = Avaliacao(
                        tenant_id=tenant_id,
                        turma_id=turma_obj.id,
                        disciplina_id=disc.id,
                        tipo="teste",
                        periodo=1,
                        data=teste_date,
                        peso=0.4,
                        nota_maxima=20,
                    )
                    session.add(teste)
                    await session.flush()
                    aval_count += 1

                    # Trabalho — March
                    trabalho_date = _random_date_in_range(date(2026, 3, 2), date(2026, 3, 20))
                    trabalho = Avaliacao(
                        tenant_id=tenant_id,
                        turma_id=turma_obj.id,
                        disciplina_id=disc.id,
                        tipo="trabalho",
                        periodo=1,
                        data=trabalho_date,
                        peso=0.3,
                        nota_maxima=20,
                    )
                    session.add(trabalho)
                    await session.flush()
                    aval_count += 1

                    # Notas for each aluno
                    for aluno in alunos_in_turma:
                        # Teste nota: 5-20 with realistic distribution
                        # Most students score 8-16, a few lower or higher
                        teste_val = _generate_realistic_nota()
                        session.add(
                            Nota(
                                tenant_id=tenant_id,
                                avaliacao_id=teste.id,
                                aluno_id=aluno.id,
                                valor=Decimal(str(teste_val)),
                                lancado_por=default_lancador_id,
                            )
                        )
                        nota_count += 1

                        # Trabalho nota: generally a bit higher
                        trab_val = _generate_realistic_nota(bias=1.5)
                        session.add(
                            Nota(
                                tenant_id=tenant_id,
                                avaliacao_id=trabalho.id,
                                aluno_id=aluno.id,
                                valor=Decimal(str(trab_val)),
                                lancado_por=default_lancador_id,
                            )
                        )
                        nota_count += 1

                    # Faltas: 0-3 per aluno per discipline
                    for aluno in alunos_in_turma:
                        n_faltas = random.choices(
                            [0, 1, 2, 3], weights=[40, 30, 20, 10]
                        )[0]
                        for _ in range(n_faltas):
                            falta_date = _random_date_in_range(
                                date(2026, 2, 5), date(2026, 3, 25)
                            )
                            # ~70% injustificada, ~30% justificada
                            tipo_falta = random.choices(
                                ["injustificada", "justificada"],
                                weights=[70, 30],
                            )[0]
                            justificativa = None
                            if tipo_falta == "justificada":
                                justificativa = random.choice([
                                    "Doenca comprovada",
                                    "Consulta medica",
                                    "Problema familiar",
                                    "Motivo de forca maior",
                                ])
                            session.add(
                                Falta(
                                    tenant_id=tenant_id,
                                    aluno_id=aluno.id,
                                    turma_id=turma_obj.id,
                                    disciplina_id=disc.id,
                                    data=falta_date,
                                    tipo=tipo_falta,
                                    justificativa=justificativa,
                                )
                            )
                            falta_count += 1

            await session.flush()
            print(
                f"  Created {aval_count} avaliacoes, "
                f"{nota_count} notas, {falta_count} faltas"
            )

        # ------------------------------------------------------------------
        # Commit everything
        # ------------------------------------------------------------------
        await session.commit()
        print("\n" + "=" * 60)
        print("MVP Seed complete!")
        print("=" * 60)
        print(f"  Professores: {len(all_professors)}")
        print(f"  Encarregados: {len(all_encarregados)}")
        print(f"  Alunos: {len(all_alunos)}")
        print(f"  Turmas: {len(all_turmas_dict)}")
        print(f"  Turma distribution:")
        for t_name, a_list in aluno_turma_assignments.items():
            print(f"    {t_name}: {len(a_list)} alunos")

    await engine.dispose()


def _generate_realistic_nota(bias: float = 0.0) -> float:
    """Generate a realistic grade between 5 and 20.

    Most grades cluster around 10-14 with tails on both ends.
    bias shifts the distribution upward (useful for trabalhos).
    """
    # Use a truncated normal-ish distribution via triangular
    val = random.triangular(4, 20, 12 + bias)
    val = max(5, min(20, round(val, 1)))
    return val


if __name__ == "__main__":
    asyncio.run(seed_mvp())
