"""
Database migration manager for the healthcare community platform.
Handles database migrations, seeding, and internationalization setup.
"""

import os
import sys
from pathlib import Path
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

from sqlalchemy import create_engine, text
from sqlmodel import SQLModel, Session
from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory

from models_i18n import *
from i18n_config import (
    DEFAULT_LANGUAGES, DEFAULT_COUNTRIES, COMMON_TRANSLATION_KEYS,
    get_supported_languages, get_supported_countries
)

logger = logging.getLogger(__name__)


class MigrationManager:
    """Manages database migrations and seeding."""
    
    def __init__(self, database_url: str = None):
        self.database_url = database_url or os.getenv("DATABASE_URL", "sqlite:///./app_i18n.db")
        self.alembic_cfg = Config("alembic.ini")
        self.alembic_cfg.set_main_option("sqlalchemy.url", self.database_url)
        
    def create_engine(self):
        """Create database engine."""
        return create_engine(self.database_url, echo=False)
    
    def get_current_revision(self) -> Optional[str]:
        """Get current database revision."""
        try:
            engine = self.create_engine()
            with engine.connect() as connection:
                context = MigrationContext.configure(connection)
                return context.get_current_revision()
        except Exception as e:
            logger.warning(f"Could not get current revision: {e}")
            return None
    
    def get_head_revision(self) -> Optional[str]:
        """Get head revision."""
        try:
            script = ScriptDirectory.from_config(self.alembic_cfg)
            return script.get_current_head()
        except Exception as e:
            logger.warning(f"Could not get head revision: {e}")
            return None
    
    def is_database_initialized(self) -> bool:
        """Check if database is initialized."""
        try:
            engine = self.create_engine()
            with engine.connect() as connection:
                # Check if alembic_version table exists
                result = connection.execute(text("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='alembic_version'
                """))
                return result.fetchone() is not None
        except Exception:
            return False
    
    def create_tables(self):
        """Create all tables using SQLModel."""
        try:
            engine = self.create_engine()
            SQLModel.metadata.create_all(engine)
            logger.info("Tables created successfully")
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            raise
    
    def init_migrations(self):
        """Initialize Alembic migrations."""
        try:
            # Create migrations directory if it doesn't exist
            migrations_dir = Path("migrations")
            migrations_dir.mkdir(exist_ok=True)
            
            # Initialize alembic
            command.init(self.alembic_cfg, "migrations")
            logger.info("Migrations initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing migrations: {e}")
            raise
    
    def create_initial_migration(self, message: str = "Initial migration with internationalization"):
        """Create initial migration."""
        try:
            command.revision(
                self.alembic_cfg,
                message=message,
                autogenerate=True
            )
            logger.info("Initial migration created successfully")
        except Exception as e:
            logger.error(f"Error creating initial migration: {e}")
            raise
    
    def upgrade_database(self, revision: str = "head"):
        """Upgrade database to specified revision."""
        try:
            command.upgrade(self.alembic_cfg, revision)
            logger.info(f"Database upgraded to {revision}")
        except Exception as e:
            logger.error(f"Error upgrading database: {e}")
            raise
    
    def downgrade_database(self, revision: str):
        """Downgrade database to specified revision."""
        try:
            command.downgrade(self.alembic_cfg, revision)
            logger.info(f"Database downgraded to {revision}")
        except Exception as e:
            logger.error(f"Error downgrading database: {e}")
            raise
    
    def get_migration_history(self) -> List[Dict[str, Any]]:
        """Get migration history."""
        try:
            script = ScriptDirectory.from_config(self.alembic_cfg)
            revisions = []
            
            for revision in script.walk_revisions():
                revisions.append({
                    "revision": revision.revision,
                    "down_revision": revision.down_revision,
                    "branch_labels": revision.branch_labels,
                    "depends_on": revision.depends_on,
                    "doc": revision.doc,
                    "module_path": revision.module_path
                })
            
            return revisions
        except Exception as e:
            logger.error(f"Error getting migration history: {e}")
            return []
    
    def seed_database(self):
        """Seed database with initial data."""
        try:
            engine = self.create_engine()
            with Session(engine) as session:
                self._seed_languages(session)
                self._seed_countries(session)
                self._seed_translation_namespaces(session)
                self._seed_roles(session)
                self._seed_consent_scopes(session)
                self._seed_default_account(session)
                session.commit()
                logger.info("Database seeded successfully")
        except Exception as e:
            logger.error(f"Error seeding database: {e}")
            raise
    
    def _seed_languages(self, session: Session):
        """Seed supported languages."""
        from models_i18n import Language
        
        for lang_info in DEFAULT_LANGUAGES:
            existing = session.query(Language).filter(Language.code == lang_info.code.value).first()
            if not existing:
                language = Language(
                    code=lang_info.code.value,
                    name=lang_info.name,
                    native_name=lang_info.native_name,
                    is_rtl=lang_info.is_rtl,
                    is_active=lang_info.is_active,
                    sort_order=lang_info.sort_order
                )
                session.add(language)
    
    def _seed_countries(self, session: Session):
        """Seed supported countries."""
        from models_i18n import Country
        
        for country_info in DEFAULT_COUNTRIES:
            existing = session.query(Country).filter(Country.code == country_info.code.value).first()
            if not existing:
                country = Country(
                    code=country_info.code.value,
                    name=country_info.name,
                    native_name=country_info.native_name,
                    language=country_info.language.value,
                    timezone=country_info.timezone.value,
                    currency=country_info.currency.value,
                    date_format=country_info.date_format.value,
                    time_format=country_info.time_format.value,
                    measurement_unit=country_info.measurement_unit.value,
                    is_active=country_info.is_active
                )
                session.add(country)
    
    def _seed_translation_namespaces(self, session: Session):
        """Seed translation namespaces."""
        from models_i18n import TranslationNamespace
        
        namespaces = [
            ("ui", "User Interface", "UI elements and navigation"),
            ("medical", "Medical Terms", "Medical terminology and concepts"),
            ("community", "Community", "Community features and interactions"),
            ("research", "Research", "Research and clinical trial terms"),
            ("validation", "Validation", "Form validation messages"),
            ("error", "Error Messages", "Error messages and notifications")
        ]
        
        for code, name, description in namespaces:
            existing = session.query(TranslationNamespace).filter(TranslationNamespace.code == code).first()
            if not existing:
                namespace = TranslationNamespace(
                    code=code,
                    name=name,
                    description=description,
                    is_active=True
                )
                session.add(namespace)
    
    def _seed_roles(self, session: Session):
        """Seed user roles."""
        from models_i18n import Role
        
        roles = [
            ("member", "Patient or caregiver"),
            ("clinician", "Healthcare professional"),
            ("coordinator", "Trial coordinator"),
            ("moderator", "Community moderator"),
            ("admin", "Tenant admin")
        ]
        
        for code, description in roles:
            existing = session.query(Role).filter(Role.code == code).first()
            if not existing:
                role = Role(code=code, description=description)
                session.add(role)
    
    def _seed_consent_scopes(self, session: Session):
        """Seed consent scopes."""
        from models_i18n import ConsentScope
        
        scopes = [
            ("research", "Use pseudonymized data for research/analytics"),
            ("trial_referral", "Allow referral to trial coordinators"),
            ("community_share", "Allow sharing selected content in community"),
            ("data_export", "Allow data export to third-party apps")
        ]
        
        for code, description in scopes:
            existing = session.query(ConsentScope).filter(ConsentScope.code == code).first()
            if not existing:
                scope = ConsentScope(code=code, description=description)
                session.add(scope)
    
    def _seed_default_account(self, session: Session):
        """Seed default account."""
        from models_i18n import Account
        
        existing = session.query(Account).filter(Account.name == "Default Tenant").first()
        if not existing:
            account = Account(
                name="Default Tenant",
                plan="pro",
                country="US",
                timezone="UTC",
                is_active=True
            )
            session.add(account)
    
    def reset_database(self):
        """Reset database (drop all tables and recreate)."""
        try:
            engine = self.create_engine()
            
            # Drop all tables
            SQLModel.metadata.drop_all(engine)
            logger.info("All tables dropped")
            
            # Recreate tables
            SQLModel.metadata.create_all(engine)
            logger.info("All tables recreated")
            
            # Seed database
            self.seed_database()
            
        except Exception as e:
            logger.error(f"Error resetting database: {e}")
            raise
    
    def backup_database(self, backup_path: str):
        """Backup database."""
        try:
            import shutil
            if self.database_url.startswith("sqlite"):
                db_path = self.database_url.replace("sqlite:///", "")
                shutil.copy2(db_path, backup_path)
                logger.info(f"Database backed up to {backup_path}")
            else:
                logger.warning("Backup not implemented for non-SQLite databases")
        except Exception as e:
            logger.error(f"Error backing up database: {e}")
            raise
    
    def restore_database(self, backup_path: str):
        """Restore database from backup."""
        try:
            import shutil
            if self.database_url.startswith("sqlite"):
                db_path = self.database_url.replace("sqlite:///", "")
                shutil.copy2(backup_path, db_path)
                logger.info(f"Database restored from {backup_path}")
            else:
                logger.warning("Restore not implemented for non-SQLite databases")
        except Exception as e:
            logger.error(f"Error restoring database: {e}")
            raise


def main():
    """Main function for migration management."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Database migration manager")
    parser.add_argument("command", choices=[
        "init", "create", "upgrade", "downgrade", "seed", "reset", "status", "history"
    ], help="Migration command")
    parser.add_argument("--revision", help="Target revision")
    parser.add_argument("--message", help="Migration message")
    parser.add_argument("--database-url", help="Database URL")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Create migration manager
    manager = MigrationManager(args.database_url)
    
    try:
        if args.command == "init":
            manager.init_migrations()
            print("Migrations initialized successfully")
            
        elif args.command == "create":
            message = args.message or "New migration"
            manager.create_initial_migration(message)
            print(f"Migration created: {message}")
            
        elif args.command == "upgrade":
            revision = args.revision or "head"
            manager.upgrade_database(revision)
            print(f"Database upgraded to {revision}")
            
        elif args.command == "downgrade":
            if not args.revision:
                print("Error: --revision required for downgrade")
                sys.exit(1)
            manager.downgrade_database(args.revision)
            print(f"Database downgraded to {args.revision}")
            
        elif args.command == "seed":
            manager.seed_database()
            print("Database seeded successfully")
            
        elif args.command == "reset":
            manager.reset_database()
            print("Database reset successfully")
            
        elif args.command == "status":
            current = manager.get_current_revision()
            head = manager.get_head_revision()
            print(f"Current revision: {current}")
            print(f"Head revision: {head}")
            print(f"Up to date: {current == head}")
            
        elif args.command == "history":
            history = manager.get_migration_history()
            for migration in history:
                print(f"{migration['revision']}: {migration['doc']}")
                
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
