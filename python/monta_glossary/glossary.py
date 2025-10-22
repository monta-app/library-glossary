"""Main Glossary API for accessing terminology and translations."""

import os
from typing import Optional, List, Dict
from dataclasses import dataclass
from .database import GlossaryDB


@dataclass
class Term:
    """Represents a glossary term with all its metadata."""

    id: int
    term: str
    description: str
    case_sensitive: bool
    translatable: bool
    forbidden: bool
    tags: Optional[str]
    plural_form: Optional[str]
    translations: Dict[str, str]
    alternative_words: List[str]
    additional_descriptions: Dict[str, str]

    def translate(self, language_code: str) -> Optional[str]:
        """Get translation for a specific language.

        Args:
            language_code: Language code (e.g., 'da', 'de', 'fr')

        Returns:
            Translated term or None if translation doesn't exist
        """
        return self.translations.get(language_code)

    def get_description(self, language_code: Optional[str] = None) -> str:
        """Get description, optionally in a specific language.

        Args:
            language_code: Optional language code for language-specific description

        Returns:
            Description text
        """
        if language_code and language_code in self.additional_descriptions:
            return self.additional_descriptions[language_code]
        return self.description

    def has_tag(self, tag: str) -> bool:
        """Check if term has a specific tag.

        Args:
            tag: Tag to check for

        Returns:
            True if term has the tag
        """
        if not self.tags:
            return False
        return tag in [t.strip() for t in self.tags.split(",")]

    def get_tags(self) -> List[str]:
        """Get list of all tags for this term.

        Returns:
            List of tags
        """
        if not self.tags:
            return []
        return [t.strip() for t in self.tags.split(",")]


class Glossary:
    """Main interface for accessing the Monta glossary."""

    def __init__(self, db_path: Optional[str] = None):
        """Initialize the glossary.

        Args:
            db_path: Optional path to the SQLite database file.
                    If None, uses the default package database.
        """
        self.db = GlossaryDB(db_path)

    def close(self):
        """Close the database connection."""
        self.db.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def _build_term_object(self, term_data: Dict) -> Term:
        """Build a Term object from database data.

        Args:
            term_data: Dictionary with term data from database

        Returns:
            Term object
        """
        term_id = term_data["id"]
        return Term(
            id=term_id,
            term=term_data["term"],
            description=term_data["description"],
            case_sensitive=bool(term_data["case_sensitive"]),
            translatable=bool(term_data["translatable"]),
            forbidden=bool(term_data["forbidden"]),
            tags=term_data["tags"],
            plural_form=term_data.get("plural_form"),
            translations=self.db.get_translations(term_id),
            alternative_words=self.db.get_alternative_words(term_id),
            additional_descriptions=self.db.get_additional_descriptions(term_id),
        )

    def get_term(self, term_name: str) -> Optional[Term]:
        """Get a term by its name.

        Args:
            term_name: The term to look up

        Returns:
            Term object or None if not found
        """
        term_data = self.db.get_term_by_name(term_name)
        if term_data:
            return self._build_term_object(term_data)
        return None

    def search(self, query: str) -> List[Term]:
        """Search for terms matching a query.

        Args:
            query: Search query (searches in term names and descriptions)

        Returns:
            List of matching Term objects
        """
        results = self.db.search_terms(query)
        return [self._build_term_object(term_data) for term_data in results]

    def get_all(self) -> List[Term]:
        """Get all terms in the glossary.

        Returns:
            List of all Term objects
        """
        all_terms = self.db.get_all_terms()
        return [self._build_term_object(term_data) for term_data in all_terms]

    def get_by_tag(self, tag: str) -> List[Term]:
        """Get all terms with a specific tag.

        Args:
            tag: The tag to filter by

        Returns:
            List of matching Term objects
        """
        results = self.db.get_terms_by_tag(tag)
        return [self._build_term_object(term_data) for term_data in results]

    def translate(self, term_name: str, language_code: str) -> Optional[str]:
        """Get translation for a term in a specific language.

        Args:
            term_name: The term to translate
            language_code: Target language code (e.g., 'da', 'de', 'fr')

        Returns:
            Translated term or None if term or translation doesn't exist
        """
        term = self.get_term(term_name)
        if term:
            return term.translate(language_code)
        return None

    def get_languages(self) -> List[str]:
        """Get list of all available language codes.

        Returns:
            List of language codes
        """
        # Get a sample of terms and collect all language codes
        all_terms = self.db.get_all_terms()
        if not all_terms:
            return []

        # Get translations for the first term to determine available languages
        first_term_id = all_terms[0]["id"]
        translations = self.db.get_translations(first_term_id)
        return sorted(translations.keys())

    def count(self) -> int:
        """Get total number of terms in the glossary.

        Returns:
            Number of terms
        """
        return len(self.db.get_all_terms())

    def normalize_text(self, text: str) -> str:
        """Normalize text by replacing alternative terms with their canonical versions.

        This function finds all occurrences of terms (including their alternatives)
        and replaces them with the correct canonical term from the glossary.
        If a plural alternative is matched, it will be replaced with the plural
        form of the canonical term (if available).

        Args:
            text: The text to normalize

        Returns:
            The normalized text with all terms replaced
        """
        import re

        result = text
        terms = self.get_all()

        # Sort by term length (longest first) to handle overlapping terms correctly
        sorted_terms = sorted(terms, key=lambda t: len(t.term), reverse=True)

        for term in sorted_terms:
            # Get alternatives with metadata (including is_plural flag)
            alternatives_with_metadata = self.db.get_alternative_words_with_metadata(term.id)

            # Create a map of alternative -> is_plural
            alternative_plural_map = {
                alt["alternative"]: alt["is_plural"]
                for alt in alternatives_with_metadata
            }

            # Process the canonical term first (always singular)
            if term.term:
                escaped_term = re.escape(term.term)
                flags = 0 if term.case_sensitive else re.IGNORECASE
                pattern = re.compile(rf"\b{escaped_term}\b", flags)
                result = pattern.sub(term.term, result)

            # Process alternatives
            for alternative in term.alternative_words:
                if not alternative:
                    continue

                # Escape special regex characters
                escaped_alternative = re.escape(alternative)

                # Create regex with word boundaries
                flags = 0 if term.case_sensitive else re.IGNORECASE
                pattern = re.compile(rf"\b{escaped_alternative}\b", flags)

                # Determine replacement: if alternative is plural and we have a plural_form, use it
                is_plural = alternative_plural_map.get(alternative, False)
                if is_plural and term.plural_form:
                    replacement = term.plural_form
                else:
                    replacement = term.term

                # Replace the alternative with the appropriate form
                result = pattern.sub(replacement, result)

        return result

    @staticmethod
    def get_tone_of_voice() -> Optional[str]:
        """Get the Monta tone of voice guide content.

        Returns:
            The full content of the tone of voice guide, or None if file not found
        """
        # Get the path relative to this package
        package_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.join(package_dir, "..", "..")
        tone_of_voice_path = os.path.join(
            project_root, "files", "prompts", "tone-of.voice.md"
        )

        try:
            with open(tone_of_voice_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return None
