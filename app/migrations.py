from alembic import command
from alembic.config import Config as AlembicConfig


def run_migrations() -> None:
    alembic_cfg = AlembicConfig("alembic.ini")
    command.upgrade(alembic_cfg, "head")
