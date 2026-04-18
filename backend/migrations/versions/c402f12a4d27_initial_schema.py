"""initial_schema

Revision ID: c402f12a4d27
Revises: 
Create Date: 2026-04-18 10:24:01.998529

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c402f12a4d27'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        );
        """
    )

    op.execute(
        """
        CREATE TABLE archetypes (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            is_mobile_primary INTEGER NOT NULL DEFAULT 0
        );
        """
    )

    op.execute(
        """
        CREATE TABLE industries (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            archetype_id INTEGER NOT NULL REFERENCES archetypes(id)
        );
        """
    )

    op.execute(
        """
        CREATE TABLE verticals (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            industry_id INTEGER NOT NULL REFERENCES industries(id)
        );
        """
    )

    op.execute(
        """
        CREATE TABLE workloads (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            vertical_id INTEGER NOT NULL REFERENCES verticals(id)
        );
        """
    )

    op.execute(
        """
        CREATE TABLE scale_tiers (
            id SERIAL PRIMARY KEY,
            workload_id INTEGER NOT NULL REFERENCES workloads(id),
            scale_level INTEGER NOT NULL CHECK (scale_level IN (1, 2, 3)),
            scale_label TEXT NOT NULL CHECK (scale_label IN ('Light', 'Standard', 'Heavy')),
            threshold_unit TEXT,
            threshold_min REAL,
            threshold_max REAL,
            description TEXT
        );
        """
    )

    op.execute(
        """
        CREATE TABLE products (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            brand TEXT,
            form_factor TEXT,
            max_cpu_cores INTEGER,
            max_cpu_tdp_watts INTEGER,
            max_ram_gb INTEGER,
            ram_slots INTEGER,
            max_gpu_vram_gb INTEGER,
            gpu_vram_range TEXT,
            supports_dual_gpu INTEGER DEFAULT 0,
            max_storage_nvme_tb REAL,
            max_psu_watts INTEGER,
            isv_certified INTEGER DEFAULT 1,
            ecc_memory INTEGER DEFAULT 1,
            os_support TEXT,
            recommended_scale_min INTEGER CHECK (recommended_scale_min IN (1, 2, 3)),
            recommended_scale_max INTEGER CHECK (recommended_scale_max IN (1, 2, 3)),
            notes TEXT
        );
        """
    )

    op.execute(
        """
        CREATE TABLE scale_tier_products (
            id SERIAL PRIMARY KEY,
            scale_tier_id INTEGER NOT NULL REFERENCES scale_tiers(id),
            product_id INTEGER NOT NULL REFERENCES products(id),
            rank INTEGER NOT NULL DEFAULT 1,
            UNIQUE (scale_tier_id, product_id)
        );
        """
    )

    op.execute(
        """
        CREATE TABLE saved_profiles (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            name TEXT NOT NULL,
            workload_id INTEGER NOT NULL REFERENCES workloads(id),
            scale_level INTEGER NOT NULL CHECK (scale_level IN (1, 2, 3)),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TABLE IF EXISTS saved_profiles CASCADE;")
    op.execute("DROP TABLE IF EXISTS scale_tier_products CASCADE;")
    op.execute("DROP TABLE IF EXISTS products CASCADE;")
    op.execute("DROP TABLE IF EXISTS scale_tiers CASCADE;")
    op.execute("DROP TABLE IF EXISTS workloads CASCADE;")
    op.execute("DROP TABLE IF EXISTS verticals CASCADE;")
    op.execute("DROP TABLE IF EXISTS industries CASCADE;")
    op.execute("DROP TABLE IF EXISTS archetypes CASCADE;")
    op.execute("DROP TABLE IF EXISTS users CASCADE;")
