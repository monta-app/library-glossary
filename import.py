"""
Unified import script for Monta Glossary.

This script handles:
1. Importing data from Excel to SQLite database
2. Generating alternative words using OpenAI (optional)
3. Generating markdown file from database (optional)
"""

import os
import sys
import time
import argparse
from openpyxl import load_workbook
from dotenv import load_dotenv
from openai import OpenAI

# Add python package directory to path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(project_dir, 'python'))

from monta_glossary.database import GlossaryDB
from monta_glossary import Glossary


# ============================================================================
# PART 1: IMPORT FROM EXCEL
# ============================================================================

def parse_alternative_words(row, columns):
    """Parse alternative words from the row if they exist."""
    # Look for 'Alternative words' column
    alt_col_index = None
    for i, col in enumerate(columns):
        if col and 'alternative' in col.lower():
            alt_col_index = i
            break

    if alt_col_index is None or not row[alt_col_index]:
        return []

    # Parse the alternative words (usually comma-separated)
    alt_text = str(row[alt_col_index])
    alternatives = [alt.strip() for alt in alt_text.split(',')]
    return [alt for alt in alternatives if alt]


def import_from_excel(excel_path: str, db_path: str):
    """Import glossary data from Excel file to SQLite database."""
    if not os.path.exists(excel_path):
        print(f"❌ Error: Excel file not found at {excel_path}")
        sys.exit(1)

    print(f"📂 Loading Excel file: {excel_path}")
    wb = load_workbook(excel_path)
    ws = wb.active

    # Get column headers
    columns = [cell.value for cell in ws[1]]

    # Create column index mapping
    col_idx = {col: i for i, col in enumerate(columns) if col}

    # Language columns
    language_columns = ['en', 'en_US', 'da', 'de', 'fr', 'no', 'ro', 'sv', 'es', 'it', 'nl', 'fr_CA']

    # Initialize database
    print(f"🗄️  Initializing database: {db_path}")
    db = GlossaryDB(db_path)
    db.create_tables()

    # Clear existing data
    print("🧹 Clearing existing data...")
    db.clear_all_data()

    # Import data
    print("📥 Importing terms...")
    imported_count = 0
    skipped_count = 0

    for row_num, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        # Get term name
        term = row[col_idx['term']] if 'term' in col_idx else None

        if not term:
            skipped_count += 1
            continue

        # Get metadata
        description = row[col_idx['description']] if 'description' in col_idx else ''
        case_sensitive = str(row[col_idx['casesensitive']]).lower() == 'yes' if 'casesensitive' in col_idx else False
        translatable = str(row[col_idx['translatable']]).lower() == 'yes' if 'translatable' in col_idx else True
        forbidden = str(row[col_idx['forbidden']]).lower() == 'yes' if 'forbidden' in col_idx else False
        tags = row[col_idx['tags']] if 'tags' in col_idx else None

        # Insert term
        try:
            term_id = db.insert_term(
                term=term,
                description=description if description else '',
                case_sensitive=case_sensitive,
                translatable=translatable,
                forbidden=forbidden,
                tags=tags
            )

            # Insert translations
            for lang in language_columns:
                if lang in col_idx and row[col_idx[lang]]:
                    translation = row[col_idx[lang]]
                    db.insert_translation(term_id, lang, translation)

            # Insert alternative words if present
            alternatives = parse_alternative_words(row, columns)
            for alt in alternatives:
                db.insert_alternative_word(term_id, alt)

            # Insert additional descriptions
            if 'nl_description' in col_idx and row[col_idx['nl_description']]:
                db.insert_additional_description(term_id, 'nl', row[col_idx['nl_description']])

            if 'en_US_description' in col_idx and row[col_idx['en_US_description']]:
                db.insert_additional_description(term_id, 'en_US', row[col_idx['en_US_description']])

            imported_count += 1

            if imported_count % 100 == 0:
                print(f"  ✓ Imported {imported_count} terms...")

        except Exception as e:
            print(f"  ⚠️  Error importing term '{term}' at row {row_num}: {e}")
            skipped_count += 1

    db.close()

    print(f"\n✅ Import complete!")
    print(f"   • Successfully imported: {imported_count} terms")
    if skipped_count > 0:
        print(f"   • Skipped: {skipped_count} rows")

    return imported_count


# ============================================================================
# PART 2: GENERATE ALTERNATIVE WORDS (OPENAI)
# ============================================================================

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

Return ONLY a comma-separated list of alternatives, nothing else. Example format:
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
        new_alternatives = [alt.strip() for alt in alternatives_text.split(',')]
        new_alternatives = [alt for alt in new_alternatives if alt and len(alt) > 1]

        # Combine with existing, removing duplicates
        all_alternatives = list(set(existing_alternatives + new_alternatives))

        return all_alternatives

    except Exception as e:
        print(f"   ⚠️  Error generating alternatives: {e}")
        return existing_alternatives


def generate_alternatives(db_path: str, limit: int = None, skip_existing: bool = True):
    """Generate alternative words for all terms in the database."""
    # Load environment variables
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')

    if not api_key:
        print("❌ Error: OPENAI_API_KEY not found in .env file")
        return 0

    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)

    # Initialize database
    db = GlossaryDB(db_path)

    # Get all terms
    all_terms = db.get_all_terms()

    if limit:
        all_terms = all_terms[:limit]

    print(f"🤖 Generating alternatives for {len(all_terms)} terms using OpenAI...")

    processed = 0
    skipped = 0
    updated = 0

    for i, term_data in enumerate(all_terms, 1):
        term_id = term_data['id']
        term_name = term_data['term']
        description = term_data['description']

        # Get existing alternatives
        existing_alternatives = db.get_alternative_words(term_id)

        # Skip if already has alternatives and skip_existing is True
        if skip_existing and existing_alternatives:
            skipped += 1
            if i % 50 == 0:
                print(f"  [{i}/{len(all_terms)}] Processed {processed}, skipped {skipped}, updated {updated}...")
            continue

        if i % 10 == 0 or i == 1:
            print(f"  [{i}/{len(all_terms)}] Generating for '{term_name}'...")

        # Generate alternatives
        new_alternatives = generate_alternatives_for_term(
            client, term_name, description, existing_alternatives
        )

        # Update database if we have new alternatives
        if len(new_alternatives) > len(existing_alternatives):
            # Clear old alternatives
            db.conn.execute("DELETE FROM alternative_words WHERE term_id = ?", (term_id,))

            # Insert new ones
            for alt in new_alternatives:
                db.insert_alternative_word(term_id, alt)

            updated += 1

        processed += 1

        # Rate limiting
        if processed < len(all_terms):
            time.sleep(0.5)

    db.close()

    print(f"\n✅ Alternative generation complete!")
    print(f"   • Processed: {processed} terms")
    print(f"   • Updated: {updated} terms")
    print(f"   • Skipped: {skipped} terms")

    return updated


# ============================================================================
# PART 3: GENERATE MARKDOWN
# ============================================================================

def format_term_as_markdown(term) -> str:
    """Format a Term object as markdown."""
    lines = []

    # Term heading
    lines.append(f"## {term.term}")

    # Tags
    if term.tags:
        lines.append(f"**Tag:** {term.tags}")
        lines.append("")

    # Alternative words
    if term.alternative_words:
        alt_words = ", ".join(term.alternative_words)
        lines.append(f"**Alternative words:** {alt_words}")
        lines.append("")

    # Description
    lines.append(f"**Description:** {term.description}")
    lines.append("")

    # Translations
    if term.translations:
        lines.append("**Translations:**")
        # Sort languages for consistent output
        for lang_code in sorted(term.translations.keys()):
            translation = term.translations[lang_code]
            lines.append(f"- {lang_code.upper()}: {translation}")
        lines.append("")

    # Separator
    lines.append("---")
    lines.append("")

    return "\n".join(lines)


def generate_markdown(output_path: str, db_path: str):
    """Generate glossary.md file from database."""
    print(f"📝 Generating markdown file: {output_path}")

    # Initialize glossary
    with Glossary(db_path) as glossary:
        # Get all terms
        all_terms = glossary.get_all()

        if not all_terms:
            print("⚠️  Warning: No terms found in database!")
            return 0

        # Generate markdown content
        lines = []

        # Header
        lines.append("# Monta Glossary (AI-Ready)")
        lines.append("")
        lines.append("This glossary maps Monta terminology for AI models. Each entry includes description, usage rules, and translations.")
        lines.append("")

        # Add each term
        for i, term in enumerate(all_terms, 1):
            lines.append(format_term_as_markdown(term))

            if i % 100 == 0:
                print(f"  ✓ Processed {i}/{len(all_terms)} terms...")

        # Write to file
        content = "\n".join(lines)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"\n✅ Markdown generation complete!")
        print(f"   • Total terms: {len(all_terms)}")
        print(f"   • File size: {len(content):,} characters")

        return len(all_terms)


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point for the unified import script."""
    parser = argparse.ArgumentParser(
        description='Monta Glossary - Unified Import Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic import only
  python scripts/import.py

  # Import and generate markdown
  python scripts/import.py --markdown

  # Import and generate alternatives
  python scripts/import.py --alternatives

  # Import, alternatives, and markdown
  python scripts/import.py --alternatives --markdown

  # Test alternatives on 10 terms
  python scripts/import.py --alternatives --limit 10

  # Force regenerate alternatives for all terms
  python scripts/import.py --alternatives --force
        """
    )

    parser.add_argument(
        '--alternatives',
        action='store_true',
        help='Generate alternative words using OpenAI (requires OPENAI_API_KEY in .env)'
    )

    parser.add_argument(
        '--markdown',
        action='store_true',
        help='Generate glossary.md file from database'
    )

    parser.add_argument(
        '--limit',
        type=int,
        metavar='N',
        help='Limit number of terms for alternatives generation (for testing)'
    )

    parser.add_argument(
        '--force',
        action='store_true',
        help='Force regenerate alternatives even for terms that already have them'
    )

    parser.add_argument(
        '--skip-import',
        action='store_true',
        help='Skip Excel import, only run alternatives/markdown generation'
    )

    args = parser.parse_args()

    # Determine paths
    project_dir = os.path.dirname(os.path.abspath(__file__))
    excel_path = os.path.join(project_dir, 'files', 'inputs', 'monta_raw_glossary.xlsx')
    db_path = os.path.join(project_dir, 'files', 'outputs', 'glossary.sqlite')
    md_path = os.path.join(project_dir, 'files', 'outputs', 'glossary.md')

    print("=" * 70)
    print("  Monta Glossary - Unified Import Tool")
    print("=" * 70)
    print()

    # Step 1: Import from Excel
    if not args.skip_import:
        if not os.path.exists(excel_path):
            print(f"❌ Error: Excel file not found at {excel_path}")
            sys.exit(1)

        import_from_excel(excel_path, db_path)
        print()
    else:
        print("⏭️  Skipping Excel import")
        print()
        if not os.path.exists(db_path):
            print(f"❌ Error: Database not found at {db_path}")
            print("Cannot skip import if database doesn't exist!")
            sys.exit(1)

    # Step 2: Generate alternatives (optional)
    if args.alternatives:
        print("=" * 70)
        skip_existing = not args.force
        generate_alternatives(db_path, limit=args.limit, skip_existing=skip_existing)
        print()

    # Step 3: Generate markdown (optional)
    if args.markdown:
        print("=" * 70)
        generate_markdown(md_path, db_path)
        print()

    # Summary
    print("=" * 70)
    print("✨ All done!")
    print()
    print("📊 Quick stats:")
    with Glossary(db_path) as glossary:
        print(f"   • Total terms: {glossary.count()}")
        print(f"   • Languages: {len(glossary.get_languages())}")

    print()
    print("💡 Next steps:")
    if not args.markdown:
        print("   • Run with --markdown to generate glossary.md")
    if not args.alternatives:
        print("   • Run with --alternatives to generate alternative words")
    print("   • Use the glossary in your Python/Kotlin/TypeScript projects")
    print()


if __name__ == '__main__':
    main()
