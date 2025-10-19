#!/usr/bin/env python3
"""
Generate alternative words for glossary terms using OpenAI.

This script reads terms from the database and generates alternative words/phrases
using AI, saving them to alternatives.json. The alternatives are then automatically
applied during the import process.

Usage:
    python generate_alternatives.py              # Generate for new terms only
    python generate_alternatives.py --force      # Regenerate all terms
    python generate_alternatives.py --limit 10   # Test with 10 terms
"""

import os
import sys
import time
import json
import argparse
from dotenv import load_dotenv
from openai import OpenAI

# Add python package directory to path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(project_dir, 'python'))

from monta_glossary.database import GlossaryDB


def generate_alternatives_for_term(client: OpenAI, term: str, description: str, existing_alternatives: list) -> list:
    """Use OpenAI to generate alternative words/phrases for a term."""
    existing_text = ""
    if existing_alternatives:
        existing_text = f"\n\nExisting alternatives: {', '.join(existing_alternatives)}"

    prompt = f"""Given the following glossary term from Monta (an EV charging platform), suggest 3-5 alternative words or phrases that could be used to refer to the same concept. These should be:
- Synonyms or closely related terms
- Common variations or abbreviations
- Terms used in the same context
- Industry-standard alternatives

Term: {term}

Description: {description[:300]}...{existing_text}

Return ONLY a comma-separated list of alternatives in lowercase, nothing else. Example format:
alternative 1, alternative 2, alternative 3

Alternatives:"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a technical writer specializing in EV charging terminology."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=150
        )

        # Parse response
        alternatives_text = response.choices[0].message.content.strip()

        # Split by comma and clean up
        new_alternatives = [alt.strip().lower() for alt in alternatives_text.split(',')]
        new_alternatives = [alt for alt in new_alternatives if alt and len(alt) > 1]

        # Combine with existing, removing duplicates
        all_alternatives = list(set(existing_alternatives + new_alternatives))

        return all_alternatives

    except Exception as e:
        print(f"   ⚠️  Error generating alternatives: {e}")
        return existing_alternatives


def generate_alternatives(db_path: str, alternatives_path: str, limit: int = None, force: bool = False):
    """Generate alternative words using AI and save to alternatives.json.

    Args:
        db_path: Path to SQLite database
        alternatives_path: Path to alternatives.json file
        limit: Limit number of terms to process (for testing)
        force: If True, regenerate alternatives even for terms that already have them

    Returns:
        Number of terms updated
    """
    # Load environment variables
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')

    if not api_key:
        print("❌ Error: OPENAI_API_KEY not found in .env file")
        print("\nTo fix this:")
        print("1. Get an API key from https://platform.openai.com/api-keys")
        print("2. Create a .env file in the project root:")
        print("   echo 'OPENAI_API_KEY=sk-your-key-here' > .env")
        return 0

    # Load existing alternatives.json
    if os.path.exists(alternatives_path):
        with open(alternatives_path, 'r', encoding='utf-8') as f:
            alternatives_data = json.load(f)
    else:
        alternatives_data = {
            "version": "1.0",
            "description": "Alternative words/phrases for glossary terms. All term keys are normalized to lowercase for consistency.",
            "alternatives": {}
        }

    existing_alternatives_json = alternatives_data.get('alternatives', {})

    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)

    # Initialize database
    db = GlossaryDB(db_path)

    # Get all terms
    all_terms = db.get_all_terms()

    if limit:
        all_terms = all_terms[:limit]

    skip_existing = not force

    print(f"🤖 Generating alternatives for {len(all_terms)} terms using OpenAI")
    print(f"   Mode: {'FORCE (regenerate all)' if force else 'ADD (skip existing)'}")
    print(f"   Results will be saved to: {alternatives_path}")
    print()

    processed = 0
    skipped = 0
    updated = 0

    for i, term_data in enumerate(all_terms, 1):
        term_name = term_data['term']
        description = term_data['description']

        # Normalize term name to lowercase for JSON key
        term_key = term_name.lower()

        # Skip if already has alternatives in JSON (unless force mode)
        if skip_existing and term_key in existing_alternatives_json:
            skipped += 1
            if i % 50 == 0:
                print(f"  [{i}/{len(all_terms)}] Processed {processed}, skipped {skipped}, updated {updated}...")
            continue

        if i % 10 == 0 or i == 1:
            print(f"  [{i}/{len(all_terms)}] Generating for '{term_name}'...")

        # Get existing alternatives from JSON (if any) using lowercase key
        existing_alts = existing_alternatives_json.get(term_key, [])

        # Generate alternatives
        new_alternatives = generate_alternatives_for_term(
            client, term_name, description, existing_alts
        )

        # In force mode, always update. In add mode, only update if we have new alternatives
        should_update = force or len(new_alternatives) > len(existing_alts)

        if should_update:
            existing_alternatives_json[term_key] = new_alternatives
            updated += 1

        processed += 1

        # Rate limiting to respect OpenAI API quotas
        if processed < len(all_terms):
            time.sleep(0.5)

    db.close()

    # Save updated alternatives.json
    alternatives_data['alternatives'] = existing_alternatives_json
    with open(alternatives_path, 'w', encoding='utf-8') as f:
        json.dump(alternatives_data, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Alternative generation complete!")
    print(f"   • Processed: {processed} terms")
    print(f"   • Updated: {updated} terms")
    print(f"   • Skipped: {skipped} terms")
    print(f"   • Saved to: {alternatives_path}")

    return updated


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Generate alternative words for glossary terms using OpenAI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate alternatives for new terms only (skips existing)
  python generate_alternatives.py

  # Regenerate alternatives for ALL terms (including existing)
  python generate_alternatives.py --force

  # Test with 10 terms first
  python generate_alternatives.py --limit 10

  # Force regenerate 10 terms
  python generate_alternatives.py --force --limit 10

Note:
  - Requires OPENAI_API_KEY in .env file
  - Cost: ~$0.01-0.02 per term (about $5 for 250 terms)
  - Results are saved to files/inputs/alternatives.json
  - Alternatives are automatically applied during import
        """
    )

    parser.add_argument(
        '--force',
        action='store_true',
        help='Regenerate alternatives even for terms that already have them'
    )

    parser.add_argument(
        '--limit',
        type=int,
        metavar='N',
        help='Limit number of terms to process (for testing)'
    )

    args = parser.parse_args()

    # Determine paths
    project_dir = os.path.dirname(os.path.abspath(__file__))
    alternatives_path = os.path.join(project_dir, 'files', 'inputs', 'alternatives.json')
    db_path = os.path.join(project_dir, 'files', 'outputs', 'glossary.sqlite')

    # Check if database exists
    if not os.path.exists(db_path):
        print(f"❌ Error: Database not found at {db_path}")
        print("\nPlease run the import first:")
        print("  ./import.sh")
        sys.exit(1)

    print("=" * 70)
    print("  Generate Alternative Words (AI-Powered)")
    print("=" * 70)
    print()

    # Generate alternatives
    updated = generate_alternatives(db_path, alternatives_path, limit=args.limit, force=args.force)

    print()
    print("=" * 70)
    print("✨ Done!")
    print()
    print("Next steps:")
    print("  1. Review alternatives.json - edit/remove any unwanted alternatives")
    print("  2. Run import to apply: ./import.sh")
    print()


if __name__ == '__main__':
    main()
