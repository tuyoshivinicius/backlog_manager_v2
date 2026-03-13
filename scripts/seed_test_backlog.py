"""Seed script for test backlog generation.

Generates a realistic backlog with developers, features, stories, and dependencies
for testing the allocation engine.
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import random
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import aiosqlite

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from backlog_manager.infrastructure.database.sqlite_connection import (
    create_connection,
    init_database,
)

if TYPE_CHECKING:
    pass

# =============================================================================
# Constants (T003)
# =============================================================================

DEVELOPERS: list[str] = [
    "Ana",
    "Bruno",
    "Carlos",
    "Diana",
    "Eduardo",
    "Fernanda",
    "Gabriel",
]

WAVES: dict[int, tuple[str, list[str], list[str]]] = {
    # wave: (domain_name, components, feature_names)
    1: (
        "Autenticacao",
        ["AUTH"],
        ["Login", "Registro", "Recuperacao Senha", "OAuth", "2FA"],
    ),
    2: (
        "Usuarios",
        ["USER"],
        ["Perfil", "Preferencias", "Avatar", "Enderecos"],
    ),
    3: (
        "Produtos",
        ["PROD"],
        ["Catalogo", "Busca", "Detalhes", "Favoritos", "Comparacao"],
    ),
    4: (
        "Carrinho",
        ["CART"],
        ["Adicionar Item", "Remover Item", "Atualizar Qtd", "Cupons"],
    ),
    5: (
        "Pagamentos",
        ["PAY"],
        ["Checkout", "Cartao Credito", "Pix", "Boleto", "Historico"],
    ),
    6: (
        "Relatorios",
        ["REPORT"],
        ["Dashboard", "Vendas", "Usuarios", "Produtos"],
    ),
    7: (
        "Comunicacao",
        ["NOTIF", "API"],
        ["Push", "Email", "Webhooks", "REST API", "GraphQL"],
    ),
}

# Story Points distribution: (value, weight%)
SP_WEIGHTS: list[tuple[int, int]] = [(3, 30), (5, 35), (8, 25), (13, 10)]

# Random seed for reproducibility (T022)
RANDOM_SEED: int = 42

# =============================================================================
# Logging Setup (T005)
# =============================================================================

logger = logging.getLogger(__name__)


def setup_logging() -> None:
    """Configure logging with Portuguese messages at INFO level."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


# =============================================================================
# CLI Argument Parsing (T002)
# =============================================================================


def parse_args() -> argparse.Namespace:
    """Parse command line arguments.

    Returns:
        Namespace with parsed arguments (clean, db_path).
    """
    parser = argparse.ArgumentParser(
        description="Seed test backlog for allocation engine testing.",
        prog="seed_test_backlog.py",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Remove existing data before seeding",
    )
    parser.add_argument(
        "--db-path",
        type=Path,
        default=None,
        metavar="PATH",
        help="Custom database path (default: app default)",
    )
    return parser.parse_args()


# =============================================================================
# Database Utilities (T004, T015, T016)
# =============================================================================


async def check_existing_data(conn: aiosqlite.Connection) -> bool:
    """Check if database already contains data.

    Args:
        conn: Database connection.

    Returns:
        True if any data exists in Story table.
    """
    cursor = await conn.execute("SELECT COUNT(*) FROM Story")
    row = await cursor.fetchone()
    return row[0] > 0 if row else False


async def clean_data(conn: aiosqlite.Connection) -> None:
    """Delete all existing data respecting FK order.

    Deletes in order: Story_Dependency -> Story -> Feature -> Developer

    Args:
        conn: Database connection.
    """
    logger.info("Limpando dados existentes...")
    await conn.execute("DELETE FROM Story_Dependency")
    await conn.execute("DELETE FROM Story")
    await conn.execute("DELETE FROM Feature")
    await conn.execute("DELETE FROM Developer")
    logger.info("Dados existentes removidos")


# =============================================================================
# Generation Functions (T007-T014)
# =============================================================================


def get_weighted_sp() -> int:
    """Get a story point value based on weighted distribution.

    Returns:
        Story point value (3, 5, 8, or 13).
    """
    values, weights = zip(*SP_WEIGHTS)
    result: int = random.choices(list(values), weights=list(weights), k=1)[0]
    return result


async def generate_developers(conn: aiosqlite.Connection) -> list[int]:
    """Generate 7 fixed developers.

    Args:
        conn: Database connection.

    Returns:
        List of created developer IDs.
    """
    developer_ids: list[int] = []
    for name in DEVELOPERS:
        cursor = await conn.execute(
            "INSERT INTO Developer (name) VALUES (?)",
            (name,),
        )
        if cursor.lastrowid is not None:
            developer_ids.append(cursor.lastrowid)
    logger.info("Criados %d desenvolvedores", len(developer_ids))
    return developer_ids


async def generate_features(conn: aiosqlite.Connection) -> dict[int, int]:
    """Generate features distributed across 7 waves.

    Args:
        conn: Database connection.

    Returns:
        Dict mapping wave number to feature_id.
    """
    wave_to_feature: dict[int, int] = {}
    feature_count = 0

    for wave_num, (domain_name, _, feature_names) in WAVES.items():
        # Create one feature per wave with the domain name
        feature_name = f"{domain_name} - Wave {wave_num}"
        cursor = await conn.execute(
            "INSERT INTO Feature (name, wave) VALUES (?, ?)",
            (feature_name, wave_num),
        )
        if cursor.lastrowid is not None:
            wave_to_feature[wave_num] = cursor.lastrowid
            feature_count += 1

    logger.info("Criadas %d features em %d ondas", feature_count, len(WAVES))
    return wave_to_feature


async def generate_stories(
    conn: aiosqlite.Connection,
    wave_to_feature: dict[int, int],
) -> list[tuple[str, int, int]]:
    """Generate 150-200 stories with proper distribution.

    Args:
        conn: Database connection.
        wave_to_feature: Mapping of wave number to feature_id.

    Returns:
        List of (story_id, wave, priority) tuples in topological order.
    """
    stories: list[tuple[str, int, int]] = []
    component_counters: dict[str, int] = {}

    # Target ~180 stories, distributed across waves
    # Earlier waves (core) have more stories, later waves have fewer
    stories_per_wave = {
        1: 25,  # AUTH - foundation
        2: 30,  # USER - heavy
        3: 35,  # PROD - densest
        4: 25,  # CART
        5: 30,  # PAY
        6: 20,  # REPORT - lightest
        7: 25,  # NOTIF/API
    }

    story_names_by_component = {
        "AUTH": [
            "Implementar login",
            "Validar credenciais",
            "Criar sessao",
            "Logout",
            "Token refresh",
            "Forgot password",
            "Reset password",
            "Email verification",
            "OAuth Google",
            "OAuth Facebook",
            "2FA setup",
            "2FA validation",
            "Remember me",
            "Session timeout",
            "Login attempts limit",
            "IP whitelist",
            "Login audit",
            "SSO integration",
            "LDAP auth",
            "API key auth",
            "JWT generation",
            "Token blacklist",
            "Auth middleware",
            "Permission check",
            "Role validation",
        ],
        "USER": [
            "Criar perfil",
            "Editar perfil",
            "Upload avatar",
            "Resize avatar",
            "Delete avatar",
            "Preferencias email",
            "Preferencias notif",
            "Tema escuro",
            "Idioma",
            "Timezone",
            "Adicionar endereco",
            "Editar endereco",
            "Remover endereco",
            "Endereco padrao",
            "Validar CEP",
            "Historico login",
            "Devices conectados",
            "Encerrar sessoes",
            "Export dados",
            "Delete conta",
            "Bloquear usuario",
            "Desbloquear usuario",
            "Merge contas",
            "User search",
            "User list admin",
            "User stats",
            "User segments",
            "Bulk update",
            "User import",
            "User export",
        ],
        "PROD": [
            "Listar produtos",
            "Filtrar categoria",
            "Ordenar preco",
            "Ordenar rating",
            "Busca texto",
            "Busca avancada",
            "Autocomplete busca",
            "Detalhes produto",
            "Galeria imagens",
            "Zoom imagem",
            "Video produto",
            "Reviews",
            "Rating",
            "Perguntas",
            "Respostas",
            "Produtos relacionados",
            "Historico visto",
            "Favoritar",
            "Lista favoritos",
            "Compartilhar",
            "Comparar produtos",
            "Tabela comparacao",
            "Alerta preco",
            "Disponibilidade",
            "Estoque",
            "SKU variants",
            "Bundle produtos",
            "Kit produtos",
            "Produto personalizado",
            "Pre-order",
            "Waitlist",
            "Product feed",
            "SEO produto",
            "Schema markup",
            "Breadcrumbs",
        ],
        "CART": [
            "Adicionar item",
            "Remover item",
            "Atualizar quantidade",
            "Limpar carrinho",
            "Salvar carrinho",
            "Recuperar carrinho",
            "Merge carrinhos",
            "Mini cart",
            "Cart drawer",
            "Cart page",
            "Subtotal",
            "Frete estimado",
            "Aplicar cupom",
            "Remover cupom",
            "Validar cupom",
            "Cupom unico",
            "Cupom percentual",
            "Cupom fixo",
            "Frete gratis",
            "Gift card",
            "Checkout rapido",
            "Buy now",
            "Wishlist",
            "Save for later",
            "Cart expiry",
        ],
        "PAY": [
            "Checkout flow",
            "Resumo pedido",
            "Selecionar endereco",
            "Selecionar frete",
            "Cartao credito",
            "Validar cartao",
            "CVV check",
            "3DS",
            "Pix QR",
            "Pix copia cola",
            "Boleto gerar",
            "Boleto validar",
            "Split payment",
            "Parcelamento",
            "Recorrencia",
            "Reembolso",
            "Cancelamento",
            "Chargeback",
            "Fraud check",
            "Risk score",
            "Order created",
            "Order confirmed",
            "Order history",
            "Invoice",
            "Receipt",
            "Payment retry",
            "Pending payment",
            "Failed payment",
            "Webhook payment",
            "Payment notify",
        ],
        "REPORT": [
            "Dashboard home",
            "KPIs",
            "Graficos vendas",
            "Vendas periodo",
            "Vendas produto",
            "Vendas categoria",
            "Top produtos",
            "Conversao",
            "Ticket medio",
            "Usuarios ativos",
            "Novos usuarios",
            "Churn rate",
            "Retention",
            "Cohort analysis",
            "Funnel",
            "Export CSV",
            "Export PDF",
            "Schedule report",
            "Email report",
            "Custom report",
        ],
        "NOTIF": [
            "Push setup",
            "Push send",
            "Push template",
            "Push schedule",
            "Push segment",
            "Email setup",
            "Email template",
            "Email send",
            "Email track",
            "SMS setup",
            "SMS send",
            "In-app notif",
            "Notif center",
            "Notif preferences",
            "Unsubscribe",
        ],
        "API": [
            "REST endpoints",
            "GraphQL schema",
            "API versioning",
            "Rate limiting",
            "API auth",
            "API docs",
            "Webhook setup",
            "Webhook retry",
            "API monitoring",
            "API logs",
        ],
    }

    for wave_num in range(1, 8):
        _, components, _ = WAVES[wave_num]
        feature_id = wave_to_feature[wave_num]
        num_stories = stories_per_wave[wave_num]

        for priority in range(num_stories):
            # Pick component (for waves with multiple components, distribute)
            component = random.choice(components)

            # Initialize counter for component
            if component not in component_counters:
                component_counters[component] = 0
            component_counters[component] += 1

            # Generate story ID: COMPONENT-NNN
            story_id = f"{component}-{component_counters[component]:03d}"

            # Get story name from predefined list or generate
            name_list = story_names_by_component.get(component, [])
            if name_list and component_counters[component] <= len(name_list):
                name = name_list[component_counters[component] - 1]
            else:
                name = f"{component} Story {component_counters[component]}"

            story_points = get_weighted_sp()

            await conn.execute(
                """
                INSERT INTO Story
                (id, component, name, story_points, priority, status, developer_id, feature_id)
                VALUES (?, ?, ?, ?, ?, 'BACKLOG', NULL, ?)
                """,
                (story_id, component, name, story_points, priority, feature_id),
            )
            stories.append((story_id, wave_num, priority))

    logger.info("Criadas %d historias", len(stories))
    return stories


async def generate_dependencies(
    conn: aiosqlite.Connection,
    stories: list[tuple[str, int, int]],
) -> int:
    """Generate 80-120 dependencies without cycles.

    Dependencies follow topological ordering:
    - Story can only depend on earlier stories (lower index in list)
    - 60% intra-wave, 40% inter-wave
    - Max 3 dependencies per story
    - Wave 1 stories have no dependencies

    Args:
        conn: Database connection.
        stories: List of (story_id, wave, priority) in topological order.

    Returns:
        Number of dependencies created.
    """
    # Build index for efficient lookup
    story_by_wave: dict[int, list[tuple[str, int]]] = {}
    for idx, (story_id, wave, priority) in enumerate(stories):
        if wave not in story_by_wave:
            story_by_wave[wave] = []
        story_by_wave[wave].append((story_id, idx))

    target_deps = random.randint(80, 120)
    intra_wave_target = int(target_deps * 0.6)
    inter_wave_target = target_deps - intra_wave_target

    dependencies: list[tuple[str, str]] = []
    story_dep_count: dict[str, int] = {}

    def add_dependency(story_id: str, depends_on_id: str) -> bool:
        """Add dependency if valid."""
        if story_id == depends_on_id:
            return False
        if story_dep_count.get(story_id, 0) >= 3:
            return False
        if (story_id, depends_on_id) in dependencies:
            return False
        dependencies.append((story_id, depends_on_id))
        story_dep_count[story_id] = story_dep_count.get(story_id, 0) + 1
        return True

    # Generate intra-wave dependencies (within same wave)
    intra_count = 0
    for wave in range(2, 8):  # Skip wave 1
        wave_stories = story_by_wave.get(wave, [])
        for story_id, story_idx in wave_stories:
            if intra_count >= intra_wave_target:
                break
            # Can depend on earlier stories in same wave
            earlier_in_wave = [
                (sid, idx) for sid, idx in wave_stories if idx < story_idx
            ]
            if earlier_in_wave and random.random() < 0.4:
                depends_on = random.choice(earlier_in_wave)
                if add_dependency(story_id, depends_on[0]):
                    intra_count += 1
        if intra_count >= intra_wave_target:
            break

    # Generate inter-wave dependencies (across waves)
    inter_count = 0
    for wave in range(2, 8):  # Skip wave 1
        wave_stories = story_by_wave.get(wave, [])
        for story_id, story_idx in wave_stories:
            if inter_count >= inter_wave_target:
                break
            # Can depend on stories from earlier waves
            earlier_waves = []
            for earlier_wave in range(1, wave):
                earlier_waves.extend(story_by_wave.get(earlier_wave, []))
            if earlier_waves and random.random() < 0.3:
                depends_on = random.choice(earlier_waves)
                if add_dependency(story_id, depends_on[0]):
                    inter_count += 1
        if inter_count >= inter_wave_target:
            break

    # Ensure critical scenarios per FR-014
    # 1. Dependency chain crossing 3+ waves
    if len(stories) >= 100:
        # Create chain: wave1 -> wave3 -> wave5 -> wave7
        wave1_stories = story_by_wave.get(1, [])
        wave3_stories = story_by_wave.get(3, [])
        wave5_stories = story_by_wave.get(5, [])
        wave7_stories = story_by_wave.get(7, [])

        if wave1_stories and wave3_stories:
            add_dependency(wave3_stories[-1][0], wave1_stories[0][0])
        if wave3_stories and wave5_stories:
            add_dependency(wave5_stories[-1][0], wave3_stories[-1][0])
        if wave5_stories and wave7_stories:
            add_dependency(wave7_stories[-1][0], wave5_stories[-1][0])

    # 2. At least one story with 3 dependencies
    wave6_stories = story_by_wave.get(6, [])
    if wave6_stories and len(stories) >= 50:
        target_story = wave6_stories[-1][0]
        # Reset count for this story to add more deps
        current_count = story_dep_count.get(target_story, 0)
        for earlier_wave in [1, 2, 3]:
            if current_count >= 3:
                break
            earlier = story_by_wave.get(earlier_wave, [])
            if earlier:
                dep = earlier[0][0]
                if (target_story, dep) not in dependencies:
                    dependencies.append((target_story, dep))
                    current_count += 1
        story_dep_count[target_story] = current_count

    # Insert all dependencies
    for story_id, depends_on_id in dependencies:
        await conn.execute(
            "INSERT INTO Story_Dependency (story_id, depends_on_id) VALUES (?, ?)",
            (story_id, depends_on_id),
        )

    logger.info("Criadas %d dependencias", len(dependencies))
    return len(dependencies)


# =============================================================================
# Main Orchestration (T010, T011)
# =============================================================================


async def seed_database(
    db_path: Path | None = None,
    clean: bool = False,
) -> dict[str, int]:
    """Main seed function orchestrating all data generation.

    Args:
        db_path: Optional custom database path.
        clean: Whether to clean existing data first.

    Returns:
        Dict with counts of created entities.

    Raises:
        RuntimeError: If data exists and --clean not specified.
    """
    # Initialize random seed for reproducibility (T022, T023)
    random.seed(RANDOM_SEED)

    # Initialize database schema (T004)
    logger.info("Inicializando banco de dados...")
    await init_database(db_path)

    conn = await create_connection(db_path)
    try:
        # Check for existing data (T015, T017)
        has_data = await check_existing_data(conn)
        if has_data:
            if clean:
                await clean_data(conn)
            else:
                raise RuntimeError(
                    "Banco de dados ja contem dados. Use --clean para substituir."
                )

        logger.info("Iniciando seed do backlog de teste...")

        # Transaction management (T006)
        try:
            # Generate all entities (T007-T014)
            developer_ids = await generate_developers(conn)
            wave_to_feature = await generate_features(conn)
            stories = await generate_stories(conn, wave_to_feature)
            dep_count = await generate_dependencies(conn, stories)

            await conn.commit()

            # Final summary (T021)
            result = {
                "developers": len(developer_ids),
                "features": len(wave_to_feature),
                "stories": len(stories),
                "dependencies": dep_count,
            }

            logger.info(
                "Seed concluido com sucesso! "
                "Desenvolvedores: %d, Features: %d, Historias: %d, Dependencias: %d",
                result["developers"],
                result["features"],
                result["stories"],
                result["dependencies"],
            )

            return result

        except Exception:
            await conn.rollback()
            raise

    finally:
        await conn.close()


def validate_db_path(db_path: Path | None) -> None:
    """Validate that db_path directory exists.

    Args:
        db_path: Database path to validate.

    Raises:
        ValueError: If directory does not exist.
    """
    if db_path is not None:
        parent = db_path.parent
        if not parent.exists():
            raise ValueError(
                f"Diretorio nao existe: {parent}. Crie o diretorio primeiro."
            )


def main() -> None:
    """Entry point for the seed script."""
    setup_logging()
    args = parse_args()

    # Validate --db-path (T019)
    try:
        validate_db_path(args.db_path)
    except ValueError as e:
        logger.error(str(e))
        sys.exit(1)

    # Run async seed
    try:
        asyncio.run(seed_database(db_path=args.db_path, clean=args.clean))
    except RuntimeError as e:
        logger.error(str(e))
        sys.exit(1)
    except Exception as e:
        logger.exception("Erro durante seed: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
