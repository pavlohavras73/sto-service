"""
Migration Job — applies all pending Alembic migrations to the database.

This is a standalone console application that runs `alembic upgrade head`.
It is intended to run as a one-shot Docker container before the main service starts.
"""
import logging
import sys
import os

# Allow importing project modules from the project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from alembic.config import Config
from alembic import command

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def run_migrations():
    logger.info("Starting database migration job...")

    alembic_cfg = Config(os.path.join(os.path.dirname(__file__), "..", "alembic.ini"))
    # Set the script location to the alembic directory relative to project root
    alembic_cfg.set_main_option(
        "script_location",
        os.path.join(os.path.dirname(__file__), "..", "alembic"),
    )

    try:
        command.upgrade(alembic_cfg, "head")
        logger.info("Migration job completed successfully.")
    except Exception as e:
        logger.error(f"Migration job failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_migrations()
