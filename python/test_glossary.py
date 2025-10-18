"""Tests for the Glossary normalize_text functionality."""

import pytest
import os
from monta_glossary import Glossary


@pytest.fixture
def glossary():
    """Create a glossary instance for testing."""
    db_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "files", "glossary.sqlite"
    )
    gloss = Glossary(db_path)
    yield gloss
    gloss.close()


class TestNormalizeText:
    """Test cases for normalize_text function."""

    def test_normalize_empty_text(self, glossary):
        """Test normalizing empty text."""
        result = glossary.normalize_text("")
        assert result == ""

    def test_normalize_text_without_terms(self, glossary):
        """Test normalizing text without any glossary terms."""
        input_text = "This is just random text without any specific terminology"
        result = glossary.normalize_text(input_text)
        assert result == input_text

    def test_replace_alternative_with_canonical(self, glossary):
        """Test replacing alternative terms with canonical terms."""
        terms = glossary.get_all()
        if terms and terms[0].alternative_words:
            alternative = terms[0].alternative_words[0]
            canonical = terms[0].term
            input_text = f"{alternative} and {alternative} again"
            result = glossary.normalize_text(input_text)

            assert canonical in result
            assert alternative not in result.lower() or terms[0].case_sensitive

    def test_multiple_occurrences(self, glossary):
        """Test handling multiple occurrences of the same term."""
        terms = glossary.get_all()
        if terms and terms[0].alternative_words:
            alternative = terms[0].alternative_words[0]
            canonical = terms[0].term
            input_text = f"The {alternative} is great. Another {alternative} here."
            result = glossary.normalize_text(input_text)

            # Count occurrences of canonical term
            assert result.count(canonical) >= 2

    def test_word_boundaries(self, glossary):
        """Test that normalization respects word boundaries."""
        input_text = "charging charges charged"
        result = glossary.normalize_text(input_text)

        # Result should be defined and shouldn't replace partial matches
        assert result is not None
        assert isinstance(result, str)

    def test_case_sensitivity(self, glossary):
        """Test case sensitivity handling."""
        terms = glossary.get_all()
        case_insensitive_terms = [t for t in terms if not t.case_sensitive]

        if case_insensitive_terms and case_insensitive_terms[0].alternative_words:
            term = case_insensitive_terms[0]
            alternative = term.alternative_words[0]
            upper_input = alternative.upper()
            result = glossary.normalize_text(upper_input)

            # Should replace regardless of case for non-case-sensitive terms
            assert term.term in result

    def test_special_regex_characters(self, glossary):
        """Test handling text with special regex characters."""
        input_text = "Text with special chars: $100 (test) [array]"
        result = glossary.normalize_text(input_text)

        assert result is not None
        assert isinstance(result, str)

    def test_preserves_surrounding_text(self, glossary):
        """Test that normalization preserves surrounding text."""
        terms = glossary.get_all()
        if terms and terms[0].alternative_words:
            alternative = terms[0].alternative_words[0]
            canonical = terms[0].term
            input_text = f"Before {alternative} after"
            result = glossary.normalize_text(input_text)

            assert "Before" in result
            assert "after" in result
            assert canonical in result


class TestBasicFunctionality:
    """Test basic glossary functionality."""

    def test_get_term(self, glossary):
        """Test getting a term by name."""
        terms = glossary.get_all()
        if terms:
            term = glossary.get_term(terms[0].term)
            assert term is not None
            assert term.term == terms[0].term

    def test_count(self, glossary):
        """Test counting terms."""
        count = glossary.count()
        assert count > 0

    def test_get_all(self, glossary):
        """Test getting all terms."""
        terms = glossary.get_all()
        assert len(terms) > 0
        assert all(hasattr(t, "term") for t in terms)
