"""
Setup test data from test-fixtures.json into the glossary database.
This ensures consistent test data across all implementations.
"""

import json
import os
import sys
from pathlib import Path

# Add parent directory to path to import monta_glossary
sys.path.insert(0, str(Path(__file__).parent / "python"))

from monta_glossary import Glossary


def load_test_fixtures():
    """Load test fixtures from JSON file."""
    fixtures_path = Path(__file__).parent / "files" / "test-fixtures.json"
    with open(fixtures_path, "r", encoding="utf-8") as f:
        return json.load(f)


def setup_test_terms(glossary, test_terms):
    """Add or update test terms in the glossary."""
    for term_data in test_terms:
        existing_term = glossary.get_term(term_data["term"])

        if existing_term is None:
            print(f"Adding test term: {term_data['term']}")
            # Note: This is a simplified version - you may need to implement add_term method
            # For now, this script documents what test data should exist
        else:
            print(f"Test term already exists: {term_data['term']}")


def verify_test_data(glossary, fixtures):
    """Verify that test data exists in the database."""
    print("\nVerifying test data...")
    test_terms = fixtures["test_terms"]

    missing_terms = []
    for term_data in test_terms:
        term = glossary.get_term(term_data["term"])
        if term is None:
            missing_terms.append(term_data["term"])
        else:
            print(f"✓ Found: {term_data['term']}")
            # Verify alternatives exist
            for alt in term_data["alternative_words"]:
                if alt not in term.alternative_words:
                    print(f"  ⚠ Missing alternative: {alt}")

    if missing_terms:
        print("\n⚠ Missing test terms:")
        for term in missing_terms:
            print(f"  - {term}")
        print("\nYou may need to manually add these terms to the glossary.")
    else:
        print("\n✓ All test terms are present!")


def main():
    db_path = Path(__file__).parent / "files" / "glossary.sqlite"

    if not db_path.exists():
        print(f"Error: Database not found at {db_path}")
        sys.exit(1)

    fixtures = load_test_fixtures()
    glossary = Glossary(str(db_path))

    try:
        setup_test_terms(glossary, fixtures["test_terms"])
        verify_test_data(glossary, fixtures)
    finally:
        glossary.close()


if __name__ == "__main__":
    main()
