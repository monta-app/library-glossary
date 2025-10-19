"""
Generate plurals.json file with auto-generated plural forms for all glossary terms.

This script:
1. Reads all terms from the glossary database
2. Uses the inflect library to generate plural forms
3. Creates/updates plurals.json with the mappings
"""

import os
import sys
import json
import inflect

# Add python package directory to path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(project_dir, 'python'))

from monta_glossary.database import GlossaryDB


def generate_plural(term: str, p: inflect.engine) -> str:
    """Generate plural form of a term.

    Args:
        term: The term to pluralize
        p: inflect engine instance

    Returns:
        Plural form of the term
    """
    # Handle multi-word terms by pluralizing the last word
    words = term.split()

    if len(words) == 1:
        # Single word - just pluralize it
        return p.plural(term)
    else:
        # Multi-word term - pluralize the last word
        # Examples: "charge point" -> "charge points"
        #           "API key" -> "API keys"
        words[-1] = p.plural(words[-1])
        return ' '.join(words)


def should_skip_term(term: str) -> bool:
    """Determine if a term should be skipped from pluralization.

    Args:
        term: The term to check

    Returns:
        True if the term should be skipped
    """
    # Skip acronyms (all uppercase)
    if term.isupper() and len(term) <= 10:
        return True

    # Skip terms that are already plural
    if term.endswith('s') and len(term.split()) == 1:
        # Check if it's likely already plural
        # This is a simple heuristic
        common_singular_endings = ['ss', 'us', 'is', 'es']
        if not any(term.endswith(ending) for ending in common_singular_endings):
            # Might be plural already, but let inflect handle it
            pass

    return False


def generate_plurals_json(db_path: str, output_path: str, force: bool = False):
    """Generate plurals.json file from database terms.

    Args:
        db_path: Path to SQLite database
        output_path: Path to save plurals.json
        force: If True, regenerate all plurals. If False, preserve existing manual entries.
    """
    print(f"📚 Generating plurals.json from database...")

    # Load existing plurals.json if it exists and not forcing
    existing_plurals = {}
    if os.path.exists(output_path) and not force:
        print(f"📂 Loading existing plurals from: {output_path}")
        with open(output_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            existing_plurals = data.get('plurals', {})
        print(f"   Found {len(existing_plurals)} existing entries")

    # Initialize inflect engine
    p = inflect.engine()

    # Initialize database
    db = GlossaryDB(db_path)

    # Get all terms
    all_terms = db.get_all_terms()
    print(f"📊 Processing {len(all_terms)} terms from database...")

    plurals_data = {
        "version": "1.0",
        "description": "Auto-generated and manual plural forms for glossary terms. Plurals are applied as alternatives during text normalization.",
        "plurals": {}
    }

    generated_count = 0
    skipped_count = 0
    preserved_count = 0

    for term_data in all_terms:
        term = term_data['term']

        # Preserve existing manual entries unless forcing
        if term in existing_plurals and not force:
            plurals_data['plurals'][term] = existing_plurals[term]
            preserved_count += 1
            continue

        # Skip terms that shouldn't be pluralized
        if should_skip_term(term):
            skipped_count += 1
            continue

        # Generate plural
        plural = generate_plural(term, p)

        # Only add if plural is different from singular
        if plural != term:
            plurals_data['plurals'][term] = {
                "singular": term,
                "plural": plural
            }
            generated_count += 1
        else:
            skipped_count += 1

    db.close()

    # Save to file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(plurals_data, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Plurals generation complete!")
    print(f"   • Generated: {generated_count} new plurals")
    print(f"   • Preserved: {preserved_count} existing entries")
    print(f"   • Skipped: {skipped_count} terms")
    print(f"   • Total in file: {len(plurals_data['plurals'])} entries")
    print(f"   • Saved to: {output_path}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Generate plurals.json from glossary database',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate plurals.json (preserve existing manual entries)
  python generate_plurals.py

  # Force regenerate all plurals
  python generate_plurals.py --force
        """
    )

    parser.add_argument(
        '--force',
        action='store_true',
        help='Force regenerate all plurals, ignoring existing entries'
    )

    args = parser.parse_args()

    # Paths
    project_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(project_dir, 'files', 'outputs', 'glossary.sqlite')
    output_path = os.path.join(project_dir, 'files', 'inputs', 'plurals.json')

    if not os.path.exists(db_path):
        print(f"❌ Error: Database not found at {db_path}")
        print("Please run import.py first to create the database.")
        sys.exit(1)

    generate_plurals_json(db_path, output_path, force=args.force)


if __name__ == '__main__':
    main()
