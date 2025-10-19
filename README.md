# Monta Glossary

A multi-language repository for managing and accessing Monta's terminology glossary with translations. This project provides packages for Python, Kotlin, and TypeScript/JavaScript to access terminology data from a centralized SQLite database.

## 📁 Project Structure

```
glossary/
├── files/                      # Data files
│   ├── inputs/
│   │   ├── monta_raw_glossary.xlsx  # Master glossary (input)
│   │   ├── amendments.json          # Custom amendments (optional)
│   │   ├── alternatives.json        # Alternative words (AI + manual)
│   │   └── external_glossary.md     # Reference only (not imported)
│   ├── outputs/
│   │   ├── glossary.sqlite          # SQLite database (generated)
│   │   └── glossary.md              # Markdown file (generated)
│   └── test-fixtures.json           # Shared test data for all implementations
├── import.py                   # Unified import script
├── import.sh                   # Wrapper script (auto-activates venv)
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
# Option 1: Use the wrapper script (automatically activates venv)
./import.sh                        # Basic import (generates markdown automatically)
./import.sh --amendments           # With custom amendments
./import.sh --alternatives         # With AI-generated alternatives (requires OpenAI)

# Option 2: Activate venv manually
source .venv/bin/activate
python import.py
python import.py --amendments --alternatives
```

**Processing Pipeline:**

Every import automatically runs:
1. Import from Excel → Database
2. Apply amendments (if `--amendments` flag)
3. Apply alternatives from `alternatives.json`
4. Generate AI alternatives (if `--alternatives` flag) → Save to `alternatives.json`
5. Apply newly generated alternatives
6. Generate `glossary.md` (always)

**⚠️ Note:** The `--alternatives` flag uses OpenAI to generate alternative terms. You must create a `.env` file with your OpenAI API key before using this option:

```bash
echo "OPENAI_API_KEY=sk-your-key-here" > .env
```

### 3. Amendments System (Optional)

The amendment system allows you to make custom modifications to the glossary data after importing from Excel, without modifying the original Excel file. This is useful for:

- **Merging duplicate terms** (e.g., merge "Chargers" into "charge point" as an alternative)
- **Adding custom translations or alternatives** not in the Excel file
- **Updating term descriptions or metadata** programmatically
- **Deleting obsolete terms**
- **Adding completely new terms** via code

**How it works:**

1. Create `files/inputs/amendments.json` with your changes
2. Run the import with `--amendments` flag
3. Amendments are applied **after** Excel import, **before** alternatives generation

**Example Use Cases:**

**1. Merge duplicate terms:**
```json
{
  "amendments": [
    {
      "type": "delete_term",
      "term": "Chargers",
      "comment": "Remove duplicate"
    },
    {
      "type": "add_alternatives",
      "term": "charge point",
      "alternatives": ["Charger", "Chargers"],
      "comment": "Add as alternatives instead"
    }
  ]
}
```

**2. Update term metadata:**
```json
{
  "type": "update_term",
  "term": "charge point",
  "changes": {
    "description": "Updated description text",
    "tags": "hardware, infrastructure",
    "case_sensitive": false
  }
}
```

**3. Add translations:**
```json
{
  "type": "add_translation",
  "term": "charge point",
  "translations": {
    "es": "Punto de Carga",
    "it": "Punto di Ricarica"
  }
}
```

**4. Add new term via code:**
```json
{
  "type": "add_term",
  "term": "New Technical Term",
  "data": {
    "description": "Description here",
    "translations": {
      "en": "New Technical Term",
      "da": "Ny Teknisk Term"
    },
    "alternatives": ["NTT"]
  }
}
```

**5. Other operations:**
```json
{
  "type": "remove_alternative",
  "term": "charge point",
  "alternative": "Unwanted Term"
}
```

```json
{
  "type": "add_description",
  "term": "charge point",
  "descriptions": {
    "nl": "Nederlandse beschrijving",
    "en_US": "American English description"
  }
}
```

**Usage:**

```bash
# Apply amendments
./import.sh --amendments

# Apply amendments without re-importing Excel
./import.sh --skip-import --amendments

# Full pipeline with AI alternatives
./import.sh --amendments --alternatives
```

**Amendment Types:**

- `update_term` - Modify existing term metadata (description, tags, case_sensitive, translatable, forbidden)
- `add_alternatives` - Add alternative words to existing term
- `remove_alternative` - Remove specific alternative word
- `add_translation` - Add/update translations for specific languages
- `add_description` - Add language-specific descriptions (e.g., nl_description)
- `add_term` - Create completely new term (not in Excel)
- `delete_term` - Remove a term entirely

**Notes:**

- Term matching is **case-insensitive** - "Charge Point", "charge point", and "CHARGE POINT" all match the same term
- Amendments are **idempotent** - running multiple times produces the same result
- Amendments are tracked in git for full audit history
- Existing alternatives/translations are preserved when adding new ones

### 4. Alternative Words System

The `alternatives.json` file stores alternative words/phrases for each term. This file serves as the single source of truth for all alternatives, whether AI-generated or manually added.

**How it works:**

1. **Always applied**: Every import automatically loads alternatives from `alternatives.json` and adds them to the database
2. **AI generation (optional)**: Use `--alternatives` flag to generate alternatives with OpenAI
3. **Manual editing**: You can directly edit `alternatives.json` to add/modify alternatives
4. **Version controlled**: Track all alternative words in git with full history

**File format:**

```json
{
  "version": "1.0",
  "description": "Alternative words/phrases for glossary terms",
  "alternatives": {
    "charge point": [
      "Charger",
      "CP",
      "Charging Station",
      "Wall Box",
      "EVSE"
    ],
    "electric vehicle": [
      "EV",
      "e-car",
      "battery electric vehicle"
    ]
  }
}
```

**Workflow:**

```bash
# Generate AI alternatives for all terms (one-time setup)
./import.sh --alternatives

# Review and edit files/inputs/alternatives.json manually
# Add more alternatives, remove bad ones, etc.

# Subsequent imports automatically use alternatives.json
./import.sh

# Generate alternatives for new terms only (skips existing)
./import.sh --alternatives

# Force regenerate all alternatives
./import.sh --alternatives --force

# Test AI on 10 terms first
./import.sh --alternatives --limit 10
```

**Benefits:**

- **Git-trackable**: See who added which alternatives and when
- **Reviewable**: Review AI suggestions before committing
- **Editable**: Manually refine or add alternatives anytime
- **Reusable**: One source of truth used across all imports
- **Incremental**: AI only processes terms without alternatives

## 📥 Data Source

The original Monta raw glossary is maintained in Google Sheets:
[Monta Glossary Master Document](https://docs.google.com/spreadsheets/d/1-lI3H0st_NNaU4BwkQW4mahkHs-kQQEw/edit?rtpof=true&gid=1333186963#gid=1333186963)

Export this spreadsheet as Excel (`.xlsx`) and place it at `files/inputs/monta_raw_glossary.xlsx` before running the import.

## 📦 Integration Guide

### Choose Your Integration Method

**Decision tree:**
- 🏢 Multiple projects need glossary → **Git Submodule**
- 🚀 Single project, auto updates → **Direct Git Install**
- 🔧 Custom setup or offline → **Local Copy**
- 💻 Development/testing → **Local Path Reference**

### Method 1: Git Submodule (Recommended for Teams)

**Why:** Keep glossary in sync across projects, easy updates, single source of truth.

```bash
# Add as submodule
cd your-project
git submodule add git@github.com:monta-app/library-glossary.git libs/glossary
git submodule update --init --recursive

# Install the package
pip install -e libs/glossary/python  # Python
npm install libs/glossary/typescript  # TypeScript
```

**Add to dependencies:**
```txt
# requirements.txt (Python)
-e libs/glossary/python

# package.json (TypeScript)
{
  "dependencies": {
    "@monta/glossary": "file:libs/glossary/typescript"
  }
}

# build.gradle.kts (Kotlin)
dependencies {
    implementation(files("libs/glossary/kotlin"))
}
```

**Team workflow:**
```bash
# First time setup
git clone your-project
git submodule update --init --recursive
pip install -r requirements.txt

# Update glossary
cd libs/glossary && git pull origin main && cd ../..
git add libs/glossary
git commit -m "Update glossary"

# Team members sync
git pull && git submodule update --remote
```

### Method 2: Direct Git Install

**Why:** Simple, automatically gets latest version.

```bash
# Python
pip install git+ssh://git@github.com/monta-app/library-glossary.git#subdirectory=python

# TypeScript
npm install git+ssh://git@github.com/monta-app/library-glossary.git#subdirectory=typescript
```

Add to dependencies:
```txt
# requirements.txt
git+ssh://git@github.com/monta-app/library-glossary.git#subdirectory=python

# package.json
{
  "dependencies": {
    "@monta/glossary": "git+ssh://git@github.com/monta-app/library-glossary.git#subdirectory=typescript"
  }
}
```

### Method 3: Local Copy

**Why:** Custom setups, offline access, or when you need just the database.

```bash
# Copy just the database
cp /path/to/glossary/files/outputs/glossary.sqlite your-project/data/

# Or copy entire package
cp -r /path/to/glossary/python/monta_glossary your-project/libs/
```

### Method 4: Local Path Reference (Development)

**Why:** Perfect for local development, changes reflected immediately.

```bash
# Python
pip install -e /path/to/glossary/python

# Or in requirements.txt
-e /path/to/glossary/python
```

```json
// TypeScript package.json
{
  "dependencies": {
    "@monta/glossary": "file:../path/to/glossary/typescript"
  }
}
```

```kotlin
// Kotlin build.gradle.kts
dependencies {
    implementation(files("/path/to/glossary/kotlin"))
}
```

### CI/CD Integration

**GitHub Actions:**
```yaml
- uses: actions/checkout@v3
  with:
    submodules: recursive  # For submodules

- name: Install dependencies
  run: pip install -r requirements.txt
```

**Docker:**
```dockerfile
FROM python:3.9
WORKDIR /app
COPY . .
RUN git submodule update --init --recursive
RUN pip install -r requirements.txt
# Copy database to container
RUN cp libs/glossary/files/outputs/glossary.sqlite /app/data/
```

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

1. **Update Excel**: Place new `download.xlsx` in `files/`
2. **Run Import**: `./import.sh --amendments --alternatives`
3. **Review**: Check `alternatives.json` for AI-generated alternatives
4. **Distribute**: The `files/outputs/glossary.sqlite` and `glossary.md` files are generated automatically

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
- `alternative` (TEXT) - Alternative word/phrase

### additional_descriptions
- `id` (PRIMARY KEY)
- `term_id` (FOREIGN KEY → terms.id)
- `language_code` (TEXT)
- `description` (TEXT) - Language-specific description
- UNIQUE(term_id, language_code)

## 🔐 Environment Variables (Optional)

The `--alternatives` flag uses OpenAI's GPT-4 API to automatically generate alternative words and saves them to `alternatives.json`. This feature is **optional** but highly recommended.

**To enable AI alternatives generation:**

1. Get an API key from [OpenAI](https://platform.openai.com/api-keys)
2. Create a `.env` file in the project root:

```bash
echo "OPENAI_API_KEY=sk-your-key-here" > .env
```

3. Run import with `--alternatives` flag:

```bash
./import.sh --alternatives --limit 10  # Test with 10 terms first
./import.sh --alternatives              # Generate for all terms
```

**Cost:** ~$0.01-0.02 per term (about $5 for 250 terms). The script includes rate limiting to respect API quotas.

**Note:**
- Import and markdown generation work perfectly fine **without** OpenAI
- AI-generated alternatives are saved to `alternatives.json` for review
- You can manually edit `alternatives.json` anytime
- Future imports automatically use alternatives from `alternatives.json`

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

### 3. Add Alternative Words with AI (Optional)

Alternative words help with text normalization and search. This step uses OpenAI and is optional.

```bash
# 1. Setup OpenAI key first
echo "OPENAI_API_KEY=sk-your-key-here" > .env

# 2. Test with a few terms to verify it works
./import.sh --alternatives --limit 10

# 3. Generate for all terms (takes ~2 minutes for 250 terms)
./import.sh --alternatives

# 4. Review and edit alternatives.json
# Remove unwanted alternatives, add manual ones, etc.

# 5. Future imports automatically use alternatives.json
./import.sh
```

**Without OpenAI:** You can still use the glossary without AI. You can manually edit `alternatives.json` or use alternatives from Excel/amendments.

### 4. Apply Amendments and Alternatives Only
```bash
# Re-apply amendments/alternatives without re-importing Excel
./import.sh --skip-import --amendments
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

This error only occurs if you use the `--alternatives` flag. To fix:

```bash
# Get your API key from https://platform.openai.com/api-keys
echo "OPENAI_API_KEY=sk-your-key-here" > .env
```

**Alternatively:** Skip the `--alternatives` flag if you don't need AI-generated alternative words:

```bash
./import.sh  # Works without OpenAI - markdown generated automatically
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

1. Update `files/inputs/monta_raw_glossary.xlsx` with new terms
2. Run: `./import.sh --amendments --alternatives`
3. Review and commit `alternatives.json` if changes look good
4. Run tests in all packages
5. Commit changes

For package-specific documentation, see the README files in `python/`, `kotlin/`, and `typescript/` directories.
