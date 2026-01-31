"""
Migration script to add actor_thinking column to turns table.

Run this script to update your existing database without losing data.
Usage: python backend/migrate_add_actor_thinking.py
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text
from app.database import async_session_maker, engine


async def migrate():
    """Add actor_thinking column to turns table."""

    print("Starting migration: Adding actor_thinking column to turns table...")

    async with async_session_maker() as session:
        # Check if column already exists
        check_query = text("""
            SELECT COUNT(*) as count
            FROM pragma_table_info('turns')
            WHERE name = 'actor_thinking'
        """)

        result = await session.execute(check_query)
        row = result.fetchone()

        if row[0] > 0:
            print("✓ Column 'actor_thinking' already exists. No migration needed.")
            return

        # Add the column
        alter_query = text("""
            ALTER TABLE turns
            ADD COLUMN actor_thinking TEXT NULL
        """)

        await session.execute(alter_query)
        await session.commit()

        print("✓ Successfully added 'actor_thinking' column to turns table.")
        print("✓ Migration complete!")


async def verify():
    """Verify the migration was successful."""
    async with async_session_maker() as session:
        # Check the table structure
        query = text("SELECT name, type FROM pragma_table_info('turns')")
        result = await session.execute(query)
        columns = result.fetchall()

        print("\nCurrent 'turns' table structure:")
        for col in columns:
            print(f"  - {col[0]}: {col[1]}")


if __name__ == "__main__":
    print("=" * 60)
    print("Database Migration: Add actor_thinking column")
    print("=" * 60)

    try:
        asyncio.run(migrate())
        asyncio.run(verify())
        print("\n" + "=" * 60)
        print("Migration successful!")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        print("\nIf you prefer to start fresh, you can delete the database:")
        print("  rm backend/redteam_simulator.db")
        sys.exit(1)
