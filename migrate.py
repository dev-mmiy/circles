#!/usr/bin/env python3
"""
Database migration script for the healthcare community platform.
Provides easy-to-use commands for database management.
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from migration_manager import MigrationManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_database():
    """Setup database with initial migration and seeding."""
    print("🚀 Setting up database...")
    
    manager = MigrationManager()
    
    try:
        # Check if database is already initialized
        if manager.is_database_initialized():
            print("✅ Database already initialized")
            return
        
        # Create tables
        print("📋 Creating tables...")
        manager.create_tables()
        
        # Initialize migrations
        print("🔄 Initializing migrations...")
        manager.init_migrations()
        
        # Create initial migration
        print("📝 Creating initial migration...")
        manager.create_initial_migration("Initial migration with internationalization support")
        
        # Seed database
        print("🌱 Seeding database...")
        manager.seed_database()
        
        print("✅ Database setup completed successfully!")
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        sys.exit(1)


def upgrade_database():
    """Upgrade database to latest version."""
    print("⬆️ Upgrading database...")
    
    manager = MigrationManager()
    
    try:
        current = manager.get_current_revision()
        head = manager.get_head_revision()
        
        print(f"Current revision: {current}")
        print(f"Head revision: {head}")
        
        if current == head:
            print("✅ Database is already up to date")
            return
        
        manager.upgrade_database()
        print("✅ Database upgraded successfully!")
        
    except Exception as e:
        print(f"❌ Error upgrading database: {e}")
        sys.exit(1)


def downgrade_database(revision: str):
    """Downgrade database to specified revision."""
    print(f"⬇️ Downgrading database to {revision}...")
    
    manager = MigrationManager()
    
    try:
        manager.downgrade_database(revision)
        print(f"✅ Database downgraded to {revision}")
        
    except Exception as e:
        print(f"❌ Error downgrading database: {e}")
        sys.exit(1)


def reset_database():
    """Reset database (WARNING: This will delete all data)."""
    print("⚠️  WARNING: This will delete all data!")
    response = input("Are you sure you want to continue? (yes/no): ")
    
    if response.lower() != 'yes':
        print("❌ Operation cancelled")
        return
    
    print("🔄 Resetting database...")
    
    manager = MigrationManager()
    
    try:
        manager.reset_database()
        print("✅ Database reset successfully!")
        
    except Exception as e:
        print(f"❌ Error resetting database: {e}")
        sys.exit(1)


def show_status():
    """Show database migration status."""
    print("📊 Database migration status:")
    
    manager = MigrationManager()
    
    try:
        current = manager.get_current_revision()
        head = manager.get_head_revision()
        
        print(f"Current revision: {current}")
        print(f"Head revision: {head}")
        print(f"Up to date: {'✅' if current == head else '❌'}")
        
        if current != head:
            print("💡 Run 'python migrate.py upgrade' to update")
        
    except Exception as e:
        print(f"❌ Error getting status: {e}")
        sys.exit(1)


def show_history():
    """Show migration history."""
    print("📚 Migration history:")
    
    manager = MigrationManager()
    
    try:
        history = manager.get_migration_history()
        
        if not history:
            print("No migrations found")
            return
        
        for migration in history:
            print(f"  {migration['revision']}: {migration['doc']}")
        
    except Exception as e:
        print(f"❌ Error getting history: {e}")
        sys.exit(1)


def create_migration(message: str):
    """Create a new migration."""
    print(f"📝 Creating migration: {message}")
    
    manager = MigrationManager()
    
    try:
        manager.create_initial_migration(message)
        print("✅ Migration created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating migration: {e}")
        sys.exit(1)


def seed_database():
    """Seed database with initial data."""
    print("🌱 Seeding database...")
    
    manager = MigrationManager()
    
    try:
        manager.seed_database()
        print("✅ Database seeded successfully!")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        sys.exit(1)


def backup_database(backup_path: str):
    """Backup database."""
    print(f"💾 Backing up database to {backup_path}...")
    
    manager = MigrationManager()
    
    try:
        manager.backup_database(backup_path)
        print("✅ Database backed up successfully!")
        
    except Exception as e:
        print(f"❌ Error backing up database: {e}")
        sys.exit(1)


def restore_database(backup_path: str):
    """Restore database from backup."""
    print(f"🔄 Restoring database from {backup_path}...")
    
    manager = MigrationManager()
    
    try:
        manager.restore_database(backup_path)
        print("✅ Database restored successfully!")
        
    except Exception as e:
        print(f"❌ Error restoring database: {e}")
        sys.exit(1)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Database migration tool for healthcare community platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python migrate.py setup          # Setup database with initial migration
  python migrate.py upgrade       # Upgrade to latest version
  python migrate.py status        # Show current status
  python migrate.py history      # Show migration history
  python migrate.py create "Add new feature"  # Create new migration
  python migrate.py reset         # Reset database (WARNING: deletes data)
  python migrate.py seed          # Seed database with initial data
  python migrate.py backup backup.db  # Backup database
  python migrate.py restore backup.db # Restore database
        """
    )
    
    parser.add_argument(
        "command",
        choices=[
            "setup", "upgrade", "downgrade", "reset", "status", "history",
            "create", "seed", "backup", "restore"
        ],
        help="Migration command to execute"
    )
    
    parser.add_argument(
        "args",
        nargs="*",
        help="Additional arguments for the command"
    )
    
    parser.add_argument(
        "--database-url",
        help="Database URL (default: sqlite:///./app_i18n.db)"
    )
    
    args = parser.parse_args()
    
    # Set database URL if provided
    if args.database_url:
        os.environ["DATABASE_URL"] = args.database_url
    
    # Execute command
    if args.command == "setup":
        setup_database()
        
    elif args.command == "upgrade":
        upgrade_database()
        
    elif args.command == "downgrade":
        if not args.args:
            print("❌ Error: revision required for downgrade")
            sys.exit(1)
        downgrade_database(args.args[0])
        
    elif args.command == "reset":
        reset_database()
        
    elif args.command == "status":
        show_status()
        
    elif args.command == "history":
        show_history()
        
    elif args.command == "create":
        if not args.args:
            print("❌ Error: message required for create")
            sys.exit(1)
        create_migration(args.args[0])
        
    elif args.command == "seed":
        seed_database()
        
    elif args.command == "backup":
        if not args.args:
            print("❌ Error: backup path required")
            sys.exit(1)
        backup_database(args.args[0])
        
    elif args.command == "restore":
        if not args.args:
            print("❌ Error: backup path required")
            sys.exit(1)
        restore_database(args.args[0])


if __name__ == "__main__":
    main()
