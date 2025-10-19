# Monta Glossary

A multi-language repository for managing and accessing Monta's terminology glossary with translations. This project provides packages for Python, Kotlin, and TypeScript/JavaScript to access terminology data from a centralized SQLite database.

## 📁 Project Structure

```
glossary/
├── files/                      # Data files
│   ├── inputs/
│   │   ├── monta_raw_glossary.xlsx  # Master glossary (input)
│   │   ├── amendments.json          # Term lifecycle changes (add/delete terms)
│   │   ├── alternatives.json        # Alternative words (AI + manual)
│   │   ├── plurals.json             # Auto-generated plural forms
│   │   └── external_glossary.md     # Reference only (not imported)
│   ├── outputs/
│   │   ├── glossary.sqlite          # SQLite database (generated)
│   │   └── glossary.md              # Markdown file (generated)
│   └── test-fixtures.json           # Shared test data for all implementations
├── import.py                   # Main import script
├── import.sh                   # Wrapper script (auto-activates venv, always runs with --amendments)
├── generate_alternatives.py    # AI-powered alternatives generation (optional)
├── generate_plurals.py         # Auto-generate plural forms
├── python/                     # Python package
│   ├── monta_glossary/
│   └── test_glossary.py        # Test suite with fixtures
├── kotlin/                     # Kotlin package
│   └── src/
│       ├── main/kotlin/com/monta/glossary/
│       └── test/kotlin/com/monta/glossary/  # Test suite with fixtures
└── typescript/                 # TypeScript package
    ├── src/
    └── test/                   # Test suite with fixtures
```

## 🚀 Quick Start

### 1. Setup

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Mac/Linux
# or: .venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Import Data

Place your master glossary file at `files/inputs/monta_raw_glossary.xlsx`, then:

```bash
# Recommended: Use the wrapper script (automatically activates venv and applies amendments)
./import.sh                        # Standard import with amendments
./import.sh --truncate-db          # Full clean rebuild
./import.sh --skip-import          # Only reapply amendments/alternatives/plurals

# Alternative: Activate venv manually
source .venv/bin/activate
python import.py --amendments      # With amendments (recommended)
python import.py                   # Without amendments
```

**Processing Pipeline:**

Every import automatically runs these steps:
1. **Import from Excel** → SQLite database (unless `--skip-import`)
2. **Apply amendments** from `amendments.json` (if `--amendments` flag)
3. **Apply alternatives** from `alternatives.json` (always - AI + manual)
4. **Apply plurals** from `plurals.json` (always - auto-generated)
5. **Generate markdown** → `glossary.md` (always)

**Important Notes:**
- `./import.sh` **always runs with `--amendments`** by default for consistency
- Alternatives and plurals are **always applied automatically** from JSON files
- Use `--truncate-db` for a clean rebuild (clears database first)
- To generate new AI alternatives: `python generate_alternatives.py` (see section 4)
- To regenerate plurals: `python generate_plurals.py` (see section 5)

### 3. Amendments System

The amendment system allows you to manage the **term lifecycle** after importing from Excel. Use amendments for structural changes like adding or removing terms.

**What amendments are for:**
- ✅ **Deleting redundant or obsolete terms**
- ✅ **Adding new terms** not in the Excel file
- ✅ **Updating term metadata** (description, tags, case_sensitive, etc.)
- ✅ **Managing translations** for specific languages

**What amendments are NOT for:**
- ❌ **Adding/removing alternative words** → Use `alternatives.json` instead
- ❌ **Managing plurals** → Auto-generated via `generate_plurals.py`

**How it works:**

1. Edit `files/inputs/amendments.json` with your term lifecycle changes
2. Run the import (amendments are always applied by `./import.sh`)
3. Amendments are applied **after** Excel import, **before** alternatives/plurals

**Example: Delete redundant terms**
```json
{
  "version": "1.0",
  "description": "Term lifecycle changes only. For alternatives, edit alternatives.json instead.",
  "amendments": [
    {
      "type": "delete_term",
      "term": "Chargers",
      "comment": "Remove duplicate - consolidating into 'charge point'"
    },
    {
      "type": "delete_term",
      "term": "charger",
      "comment": "Consolidate into 'charge point'"
    }
  ]
}
```

**Note:** After deleting terms, add them as alternatives in `alternatives.json`:
```json
{
  "alternatives": {
    "charge point": ["Charger", "Chargers", "charger", "chargers"]
  }
}
```

**Example: Add new term**
```json
{
  "type": "add_term",
  "term": "electric vehicle",
  "data": {
    "description": "Battery powered vehicle",
    "case_sensitive": false,
    "translatable": true,
    "alternatives": []
  },
  "comment": "Add as canonical term (alternatives in alternatives.json)"
}
```

**Supported Amendment Types:**
- `delete_term` - Remove a term entirely
- `add_term` - Create a new term (not in Excel)
- `update_term` - Modify term metadata (description, tags, case_sensitive, translatable, forbidden)
- `add_translation` - Add/update translations for specific languages
- `add_description` - Add language-specific descriptions

**Best Practices:**
- ✅ Use amendments for **structural changes** (term lifecycle)
- ✅ Use `alternatives.json` for **alternative words**
- ✅ Use `generate_plurals.py` for **plural forms**
- ✅ Keep amendments simple and focused
- ✅ Add comments to explain why each amendment exists

**Notes:**
- `./import.sh` always applies amendments automatically
- Term matching is **case-insensitive**
- Amendments are **idempotent** (safe to run multiple times)
- Track amendments in git for audit history

### 4. Alternative Words System

The `alternatives.json` file stores alternative words/phrases for each term. This file serves as the single source of truth for all alternatives, whether AI-generated or manually added.

**How it works:**

1. **Always applied**: Every import automatically loads alternatives from `alternatives.json`
2. **AI generation (optional)**: Use `generate_alternatives.py` to generate alternatives with OpenAI
3. **Manual editing**: Directly edit `alternatives.json` to add/modify alternatives anytime
4. **Alphabetically sorted**: Terms are sorted A-Z for easier maintenance
5. **Version controlled**: Track all changes in git with full history

**File format:**

```json
{
  "version": "1.0",
  "description": "Alternative words/phrases for glossary terms. All term keys are normalized to lowercase.",
  "alternatives": {
    "charge point": [
      "charger",
      "cp",
      "charging station",
      "wall box",
      "evse"
    ],
    "electric vehicle": [
      "ev",
      "e-car",
      "battery electric vehicle"
    ]
  }
}
```

**Generating Alternatives with AI:**

```bash
# First, set up your OpenAI API key
echo "OPENAI_API_KEY=sk-your-key-here" > .env

# Generate alternatives for NEW terms only (skips existing)
python generate_alternatives.py

# Force regenerate ALL alternatives (overwrites existing)
python generate_alternatives.py --force

# Test with 10 terms first
python generate_alternatives.py --limit 10

# Force regenerate 10 terms
python generate_alternatives.py --force --limit 10
```

**Workflow:**

```bash
# 1. Generate AI alternatives (one-time setup or when adding new terms)
python generate_alternatives.py

# 2. Review and edit files/inputs/alternatives.json manually
#    - Remove unwanted alternatives
#    - Add manual alternatives
#    - Fix any issues

# 3. Commit to git
git add files/inputs/alternatives.json
git commit -m "Update alternatives"

# 4. Subsequent imports automatically use alternatives.json
./import.sh
```

**Benefits:**

- **Separate concern**: AI generation is optional and separate from import
- **Git-trackable**: See who added which alternatives and when
- **Reviewable**: Review AI suggestions before committing
- **Editable**: Manually refine or add alternatives anytime
- **Reusable**: One source of truth used across all imports
- **Incremental**: Without --force, AI only processes new terms
- **Normalized**: All lowercase for consistent text matching

### 5. Plurals System

The `plurals.json` file contains auto-generated plural forms for all countable terms. Plurals are automatically applied as alternative words during import, enabling proper text normalization.

**How it works:**

1. **Auto-generated**: Use `generate_plurals.py` to create plural forms using the `inflect` library
2. **Always applied**: Every import automatically loads plurals and adds them as alternatives
3. **Lowercase keys**: All term keys are lowercase for consistency
4. **Regenerate after changes**: Run `generate_plurals.py` when adding new terms

**File format:**

```json
{
  "version": "1.0",
  "description": "Auto-generated plural forms for glossary terms",
  "plurals": {
    "charge point": {
      "singular": "charge point",
      "plural": "charge points"
    },
    "connector": {
      "singular": "connector",
      "plural": "connectors"
    },
    "vehicle": {
      "singular": "vehicle",
      "plural": "vehicles"
    }
  }
}
```

**Generating Plurals:**

```bash
# Generate plurals for all terms (preserves manual edits by default)
python generate_plurals.py

# Force regenerate ALL plurals (overwrites everything)
python generate_plurals.py --force

# After generating, reimport to apply
./import.sh --skip-import
```

**What gets pluralized:**

✅ Countable nouns (charge point → charge points)
✅ Multi-word terms (last word pluralized: API key → API keys)
❌ Acronyms (CP, EVSE, API remain unchanged)
❌ Proper nouns (Monta, Charge app)
❌ Adjectives (charge, charging)

**Workflow:**

```bash
# 1. Add new terms to Excel or via amendments
./import.sh

# 2. Generate plurals for new terms
python generate_plurals.py

# 3. Review plurals.json (remove incorrect plurals if needed)
# Edit files/inputs/plurals.json manually

# 4. Reimport to apply
./import.sh --skip-import

# 5. Commit to git
git add files/inputs/plurals.json
git commit -m "Update plurals"
```

**Benefits:**

- **Automatic**: Smart pluralization using linguistic rules
- **Consistent**: Same pluralization logic across all terms
- **Maintainable**: Regenerate anytime new terms are added
- **Reviewable**: Manual edits are preserved unless using `--force`
- **Text normalization**: "chargers" automatically normalizes to "charge point"

## 📥 Data Source

The original Monta raw glossary is maintained in Google Sheets:
[Monta Glossary Master Document](https://docs.google.com/spreadsheets/d/1-lI3H0st_NNaU4BwkQW4mahkHs-kQQEw/edit?rtpof=true&gid=1333186963#gid=1333186963)

Export this spreadsheet as Excel (`.xlsx`) and place it at `files/inputs/monta_raw_glossary.xlsx` before running the import.

## 📦 Integration Guide

### About This Project

**This project uses a vendored glossary library approach.** The complete glossary library (Python, Kotlin, and TypeScript implementations) is included directly in the `libs/glossary/` directory rather than as a git submodule or external dependency.

**Why vendored?** After extensive testing with git submodules, we encountered deployment blockers with AWS OIDC permissions when using organizational reusable GitHub Actions workflows. Vendoring solved these issues while maintaining full compatibility with CI/CD pipelines.

**Trade-offs:**
- ✅ **Works everywhere:** No authentication, no submodule complexity, no deployment issues
- ✅ **Simple CI/CD:** Standard workflows work without modifications
- ✅ **Reliable builds:** Docker, GitHub Actions, and local builds all work consistently
- ⚠️ **Manual updates:** Library updates require manual copying (not automatic sync)
- ⚠️ **Larger repo:** Adds ~500KB to repository size

### Vendored Library Structure

```
your-project/
├── libs/glossary/          # Vendored glossary library
│   ├── python/             # Python implementation
│   │   └── monta_glossary/
│   ├── kotlin/             # Kotlin implementation
│   │   └── src/
│   └── typescript/         # TypeScript implementation
│       └── src/
├── requirements.txt        # References vendored Python package
└── Dockerfile              # Copies libs/ directory
```

### Using the Vendored Library

**Python:**
```txt
# requirements.txt
-e libs/glossary/python
```

```bash
# Install
pip install -r requirements.txt
```

**TypeScript:**
```json
// package.json
{
  "dependencies": {
    "@monta/glossary": "file:libs/glossary/typescript"
  }
}
```

**Kotlin:**
```kotlin
// build.gradle.kts
dependencies {
    implementation(files("libs/glossary/kotlin"))
}
```

### CI/CD Integration

**GitHub Actions:**
```yaml
- uses: actions/checkout@v5

- name: Install dependencies
  run: pip install -r requirements.txt
```

**Docker:**
```dockerfile
FROM python:3.9
WORKDIR /app

# Copy requirements and vendored library
COPY requirements.txt .
COPY libs/ libs/

# Install Python dependencies (includes vendored glossary)
RUN pip install --no-cache-dir -r requirements.txt

# Copy database to container
RUN cp libs/glossary/files/outputs/glossary.sqlite /app/data/
```

### Updating the Vendored Library

When the upstream glossary library is updated:

```bash
# 1. Copy updated files from the source repository
cp -r /path/to/source/glossary/python libs/glossary/
cp -r /path/to/source/glossary/kotlin libs/glossary/
cp -r /path/to/source/glossary/typescript libs/glossary/

# 2. Commit the changes
git add libs/glossary/
git commit -m "Update vendored glossary library"
git push
```

### Alternative Integration Methods (For Other Projects)

If you're starting a new project and want to integrate this glossary library, consider these options:

**Method 1: Vendored Copy (Recommended - same as this project)**
- Copy `libs/glossary/` directory into your project
- Reference as local dependency in requirements.txt/package.json
- ✅ Works with all CI/CD systems
- ⚠️ Requires manual updates

**Method 2: Direct Git Install**
- Install directly from git repository
- Automatically gets latest version
- ⚠️ Requires git authentication in CI/CD

```bash
# Python
pip install git+ssh://git@github.com/monta-app/library-glossary.git#subdirectory=python

# TypeScript
npm install git+ssh://git@github.com/monta-app/library-glossary.git#subdirectory=typescript
```

**Method 3: Git Submodule**
- Keep glossary in sync across projects
- ⚠️ Requires careful CI/CD configuration
- ⚠️ May require AWS IAM trust policy updates for custom workflows

```bash
# Add as submodule
git submodule add git@github.com:monta-app/library-glossary.git libs/glossary
git submodule update --init --recursive
```

**For most projects, we recommend the vendored approach (Method 1) based on our experience with deployment reliability.**

## 📦 Using in Your Projects

### Python

**Installation:**
```bash
pip install -e /path/to/glossary/python
```

**Usage:**
```python
from monta_glossary import Glossary

with Glossary() as glossary:
    # Get a term
    term = glossary.get_term("charging cable")
    print(term.description)
    print(term.translate("da"))  # Output: ladekabel

    # Search terms
    results = glossary.search("charge")

    # Get terms by tag
    product_terms = glossary.get_by_tag("product")

    # Normalize text (replace alternative terms with canonical ones)
    text = "The e-car needs a charging wire"
    normalized = glossary.normalize_text(text)
    # Output: "The EV needs a charging cable"
```

### Kotlin

**Installation:**
Add to your `build.gradle.kts`:
```kotlin
dependencies {
    implementation(files("/path/to/glossary/kotlin"))
}
```

**Usage:**
```kotlin
import com.monta.glossary.Glossary

Glossary("/path/to/files/outputs/glossary.sqlite").use { glossary ->
    // Get a term
    val term = glossary.getTerm("charging cable")
    term?.let {
        println(it.description)
        println(it.translate("da"))  // Output: ladekabel
    }

    // Search terms
    val results = glossary.search("charge")

    // Normalize text
    val text = "The e-car needs a charging wire"
    val normalized = glossary.normalizeText(text)
    // Output: "The EV needs a charging cable"
}
```

### TypeScript/JavaScript

**Installation:**
```bash
npm install /path/to/glossary/typescript
```

**Usage:**
```typescript
import { Glossary, TermHelpers } from '@monta/glossary';

const glossary = new Glossary('/path/to/files/outputs/glossary.sqlite');

// Get a term
const term = glossary.getTerm('charging cable');
if (term) {
    console.log(term.description);
    console.log(term.translations['da']);  // Output: ladekabel
}

// Search terms
const results = glossary.search('charge');

// Normalize text
const text = 'The e-car needs a charging wire';
const normalized = glossary.normalizeText(text);
// Output: "The EV needs a charging cable"

// Check if term has a tag
if (term && TermHelpers.hasTag(term, 'industry')) {
    console.log('This is an industry term');
}

glossary.close();
```

## 📖 API Reference

All packages provide similar APIs with these core methods:

| Method | Description |
|--------|-------------|
| `getTerm` / `get_term` | Get a specific term with all metadata |
| `search` | Find terms by keyword |
| `getAll` / `get_all` | Get all terms |
| `getByTag` / `get_by_tag` | Get terms with specific tag |
| `translate` | Get translation for a term |
| `count` | Get total number of terms |
| `getLanguages` / `get_languages` | Get available language codes |
| `normalizeText` / `normalize_text` | Replace alternative terms with canonical versions |

### Text Normalization

The `normalizeText` function standardizes terminology in text:

```python
# Python
text = "The e-car charging wire is important"
normalized = glossary.normalize_text(text)
# Result: "The EV charging cable is important"
```

This function:
- Replaces alternative terms with canonical versions
- Respects word boundaries (won't replace partial matches)
- Honors case sensitivity settings per term
- Handles multiple occurrences

## 🔄 Workflow

### Standard Update Workflow

1. **Update Excel**: Place new `monta_raw_glossary.xlsx` in `files/inputs/`
2. **Run Import**: `./import.sh` (or `./import.sh --truncate-db` for clean rebuild)
3. **Generate Plurals** (if new terms added): `python generate_plurals.py`
4. **Reimport** (to apply plurals): `./import.sh --skip-import`
5. **Commit**: Files in `files/outputs/` are generated automatically

### First-Time Setup or Adding AI Alternatives

1. **Setup OpenAI**: `echo "OPENAI_API_KEY=sk-..." > .env`
2. **Generate Alternatives**: `python generate_alternatives.py`
3. **Review** `alternatives.json` and edit manually as needed
4. **Import**: `./import.sh --truncate-db`
5. **Commit**: `git add files/inputs/alternatives.json && git commit`

### Quick Reference Commands

```bash
# Full clean rebuild
./import.sh --truncate-db

# Reapply alternatives/plurals without Excel reimport
./import.sh --skip-import

# Generate new AI alternatives (optional)
python generate_alternatives.py --limit 10  # test first
python generate_alternatives.py             # generate all

# Regenerate plurals after adding terms
python generate_plurals.py
./import.sh --skip-import
```

## 📚 Database Schema

### terms
- `id` (PRIMARY KEY)
- `term` (UNIQUE) - Canonical term name
- `description` - Full description with usage rules
- `case_sensitive` (BOOLEAN)
- `translatable` (BOOLEAN)
- `forbidden` (BOOLEAN)
- `tags` (TEXT) - Comma-separated tags
- `created_at`, `updated_at`

### translations
- `id` (PRIMARY KEY)
- `term_id` (FOREIGN KEY → terms.id)
- `language_code` (TEXT)
- `translation` (TEXT)
- UNIQUE(term_id, language_code)

### alternative_words
- `id` (PRIMARY KEY)
- `term_id` (FOREIGN KEY → terms.id)
- `alternative` (TEXT) - Alternative word/phrase (from `alternatives.json` and `plurals.json`)

### additional_descriptions
- `id` (PRIMARY KEY)
- `term_id` (FOREIGN KEY → terms.id)
- `language_code` (TEXT)
- `description` (TEXT) - Language-specific description
- UNIQUE(term_id, language_code)

## 🔐 Environment Variables (Optional)

The `generate_alternatives.py` script uses OpenAI's GPT-4 API to automatically generate alternative words and saves them to `alternatives.json`. This feature is **optional** but highly recommended.

**To enable AI alternatives generation:**

1. Get an API key from [OpenAI](https://platform.openai.com/api-keys)
2. Create a `.env` file in the project root:

```bash
echo "OPENAI_API_KEY=sk-your-key-here" > .env
```

3. Run the generation script:

```bash
python generate_alternatives.py --limit 10  # Test with 10 terms first
python generate_alternatives.py              # Generate for all new terms
python generate_alternatives.py --force      # Regenerate all terms
```

**Cost:** ~$0.01-0.02 per term (about $5 for 250 terms). The script includes rate limiting to respect API quotas.

**Note:**
- Import works perfectly fine **without** OpenAI - just uses existing alternatives.json
- AI-generated alternatives are saved to `alternatives.json` for review before committing
- You can manually edit `alternatives.json` anytime
- All imports automatically use alternatives from `alternatives.json`

## 🧪 Running Tests

All three implementations share the same test data from `files/test-fixtures.json`, ensuring consistent behavior across languages.

### Python
```bash
cd python
pytest test_glossary.py -v
```

### TypeScript
```bash
cd typescript
npm install
npm test
```

### Kotlin
```bash
cd kotlin
./gradlew test
```

### Test Coverage

All implementations test:
- Text normalization (replacing alternatives with canonical terms)
- Word boundaries and case sensitivity
- Special character handling
- Basic CRUD operations (get, search, count)
- Shared test fixtures ensure consistency across all languages

## 💡 Common Use Cases

### 1. First Time Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
./import.sh
```

### 2. Update Glossary from New Excel
```bash
# Place new file at files/inputs/monta_raw_glossary.xlsx
./import.sh
```

### 3. Generate Alternative Words with AI (Optional)

Alternative words help with text normalization and search. This step uses OpenAI and is optional.

```bash
# 1. Setup OpenAI key first
echo "OPENAI_API_KEY=sk-your-key-here" > .env

# 2. Test with a few terms to verify it works
python generate_alternatives.py --limit 10

# 3. Generate for all new terms (takes ~2 minutes for 250 terms)
python generate_alternatives.py

# 4. Review and edit alternatives.json
# Remove unwanted alternatives, add manual ones, etc.

# 5. Commit the updated alternatives.json
git add files/inputs/alternatives.json
git commit -m "Update AI-generated alternatives"

# 6. Future imports automatically use alternatives.json
./import.sh
```

**Without OpenAI:** You can still use the glossary without AI. You can manually edit `alternatives.json` or use alternatives from Excel/amendments.

### 4. Regenerate Plurals After Adding Terms
```bash
# Generate plurals for new terms
python generate_plurals.py

# Reimport to apply (skips Excel import)
./import.sh --skip-import
```

### 5. Clean Rebuild
```bash
# Nuclear option: completely fresh rebuild
./import.sh --truncate-db
```

## 🐛 Troubleshooting

### "Module not found" error
```bash
# Make sure you're in the project root
cd /path/to/glossary

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### "OPENAI_API_KEY not found"

This error only occurs if you use `generate_alternatives.py`. To fix:

```bash
# Get your API key from https://platform.openai.com/api-keys
echo "OPENAI_API_KEY=sk-your-key-here" > .env
```

**Alternatively:** You don't need OpenAI for basic import - it only generates alternatives:

```bash
./import.sh  # Works without OpenAI - uses existing alternatives.json
```

### Database file not found
```bash
# Run import first
./import.sh
```

## ⚡ Performance

- **Import**: ~1-2 seconds for 250 terms
- **Markdown generation**: ~1 second
- **Alternatives (OpenAI)**: ~0.5 seconds per term (~2 minutes for 250 terms)

## 📝 Data Flow

```
files/inputs/monta_raw_glossary.xlsx (Master)
       ↓
  [import.py]
       ↓
  files/outputs/glossary.sqlite (Source of Truth)
       ↓
  Used by: Python, Kotlin, TypeScript packages
```

## 📄 License

Copyright © Monta

## 🤝 Contributing

### Adding New Terms

1. **Update Excel**: Add new terms to `files/inputs/monta_raw_glossary.xlsx`
2. **Import**: Run `./import.sh --truncate-db`
3. **Generate Plurals**: Run `python generate_plurals.py`
4. **Generate AI Alternatives** (optional): Run `python generate_alternatives.py`
5. **Review**: Check `alternatives.json` and `plurals.json` for accuracy
6. **Reimport**: Run `./import.sh --skip-import` to apply changes
7. **Test**: Run test suites in all three packages (Python, Kotlin, TypeScript)
8. **Commit**:
   ```bash
   git add files/inputs/*.json files/outputs/*
   git commit -m "Add new glossary terms"
   ```

### Making Amendments

1. **Edit**: Update `files/inputs/amendments.json`
2. **Import**: Run `./import.sh --truncate-db`
3. **Test**: Verify changes work as expected
4. **Commit**: Track amendments in git

### Best Practices

- ✅ Always use `./import.sh` (includes amendments automatically)
- ✅ Regenerate plurals after adding new countable nouns
- ✅ Review AI-generated alternatives before committing
- ✅ Run all test suites before committing
- ✅ Use `--truncate-db` for clean state after major changes
- ✅ Keep `alternatives.json` sorted alphabetically

For package-specific documentation, see the README files in `python/`, `kotlin/`, and `typescript/` directories.
