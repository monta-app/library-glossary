"""Database operations for the glossary."""

import sqlite3
import os
from typing import Optional, List, Dict, Any


class GlossaryDB:
    """Manages SQLite database operations for the glossary."""

    def __init__(self, db_path: Optional[str] = None):
        """Initialize database connection.

        Args:
            db_path: Path to the SQLite database file.
                    If None, uses default location in package directory.
        """
        if db_path is None:
            # Use database in files/outputs directory (two levels up from package)
            package_dir = os.path.dirname(os.path.abspath(__file__))
            project_dir = os.path.dirname(os.path.dirname(package_dir))
            db_path = os.path.join(project_dir, "files", "outputs", "glossary.sqlite")

        self.db_path = db_path
        self.conn = None
        self.connect()

    def connect(self):
        """Establish database connection."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def create_tables(self):
        """Create database schema."""
        cursor = self.conn.cursor()

        # Terms table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS terms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                term TEXT NOT NULL UNIQUE,
                description TEXT,
                case_sensitive BOOLEAN DEFAULT 0,
                translatable BOOLEAN DEFAULT 1,
                forbidden BOOLEAN DEFAULT 0,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Translations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS translations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                term_id INTEGER NOT NULL,
                language_code TEXT NOT NULL,
                translation TEXT,
                FOREIGN KEY (term_id) REFERENCES terms(id) ON DELETE CASCADE,
                UNIQUE(term_id, language_code)
            )
        """)

        # Alternative words table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alternative_words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                term_id INTEGER NOT NULL,
                alternative TEXT NOT NULL,
                FOREIGN KEY (term_id) REFERENCES terms(id) ON DELETE CASCADE
            )
        """)

        # Additional descriptions table (for language-specific descriptions)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS additional_descriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                term_id INTEGER NOT NULL,
                language_code TEXT NOT NULL,
                description TEXT,
                FOREIGN KEY (term_id) REFERENCES terms(id) ON DELETE CASCADE,
                UNIQUE(term_id, language_code)
            )
        """)

        # Create indexes for better query performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_terms_term ON terms(term)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_translations_language ON translations(language_code)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_terms_tags ON terms(tags)
        """)

        self.conn.commit()

    def insert_term(self, term: str, description: str, case_sensitive: bool,
                   translatable: bool, forbidden: bool, tags: Optional[str]) -> int:
        """Insert a new term into the database.

        Args:
            term: The term name
            description: Term description
            case_sensitive: Whether the term is case-sensitive
            translatable: Whether the term is translatable
            forbidden: Whether the term is forbidden
            tags: Comma-separated tags

        Returns:
            The ID of the inserted term
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO terms
            (term, description, case_sensitive, translatable, forbidden, tags)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (term, description, case_sensitive, translatable, forbidden, tags))
        self.conn.commit()
        return cursor.lastrowid

    def insert_translation(self, term_id: int, language_code: str, translation: str):
        """Insert a translation for a term.

        Args:
            term_id: The term ID
            language_code: Language code (e.g., 'en', 'da')
            translation: The translated text
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO translations (term_id, language_code, translation)
            VALUES (?, ?, ?)
        """, (term_id, language_code, translation))
        self.conn.commit()

    def insert_alternative_word(self, term_id: int, alternative: str):
        """Insert an alternative word for a term.

        Args:
            term_id: The term ID
            alternative: The alternative word/phrase
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO alternative_words (term_id, alternative)
            VALUES (?, ?)
        """, (term_id, alternative))
        self.conn.commit()

    def insert_additional_description(self, term_id: int, language_code: str, description: str):
        """Insert an additional language-specific description.

        Args:
            term_id: The term ID
            language_code: Language code
            description: The description text
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO additional_descriptions (term_id, language_code, description)
            VALUES (?, ?, ?)
        """, (term_id, language_code, description))
        self.conn.commit()

    def get_term_by_name(self, term: str) -> Optional[Dict[str, Any]]:
        """Get a term by its name.

        Args:
            term: The term name

        Returns:
            Dictionary with term data or None if not found
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM terms WHERE term = ?", (term,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_term_by_id(self, term_id: int) -> Optional[Dict[str, Any]]:
        """Get a term by its ID.

        Args:
            term_id: The term ID

        Returns:
            Dictionary with term data or None if not found
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM terms WHERE id = ?", (term_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_translations(self, term_id: int) -> Dict[str, str]:
        """Get all translations for a term.

        Args:
            term_id: The term ID

        Returns:
            Dictionary mapping language codes to translations
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT language_code, translation
            FROM translations
            WHERE term_id = ?
        """, (term_id,))
        return {row["language_code"]: row["translation"] for row in cursor.fetchall()}

    def get_alternative_words(self, term_id: int) -> List[str]:
        """Get all alternative words for a term.

        Args:
            term_id: The term ID

        Returns:
            List of alternative words
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT alternative
            FROM alternative_words
            WHERE term_id = ?
        """, (term_id,))
        return [row["alternative"] for row in cursor.fetchall()]

    def get_additional_descriptions(self, term_id: int) -> Dict[str, str]:
        """Get additional language-specific descriptions for a term.

        Args:
            term_id: The term ID

        Returns:
            Dictionary mapping language codes to descriptions
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT language_code, description
            FROM additional_descriptions
            WHERE term_id = ?
        """, (term_id,))
        return {row["language_code"]: row["description"] for row in cursor.fetchall()}

    def search_terms(self, query: str) -> List[Dict[str, Any]]:
        """Search for terms matching a query.

        Args:
            query: Search query

        Returns:
            List of matching terms
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM terms
            WHERE term LIKE ? OR description LIKE ?
            ORDER BY term
        """, (f"%{query}%", f"%{query}%"))
        return [dict(row) for row in cursor.fetchall()]

    def get_all_terms(self) -> List[Dict[str, Any]]:
        """Get all terms.

        Returns:
            List of all terms
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM terms ORDER BY term")
        return [dict(row) for row in cursor.fetchall()]

    def get_terms_by_tag(self, tag: str) -> List[Dict[str, Any]]:
        """Get all terms with a specific tag.

        Args:
            tag: The tag to filter by

        Returns:
            List of matching terms
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM terms
            WHERE tags LIKE ?
            ORDER BY term
        """, (f"%{tag}%",))
        return [dict(row) for row in cursor.fetchall()]

    def clear_all_data(self):
        """Clear all data from the database (useful for re-importing)."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM alternative_words")
        cursor.execute("DELETE FROM translations")
        cursor.execute("DELETE FROM additional_descriptions")
        cursor.execute("DELETE FROM terms")
        self.conn.commit()
