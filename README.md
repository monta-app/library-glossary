# Monta Glossary

A multi-language repository for managing and accessing Monta's terminology glossary with translations. This project provides packages for Python, Kotlin, and TypeScript/JavaScript to access terminology data from a centralized SQLite database.

## 📁 Project Structure

```
glossary/
├── files/                      # Data files
│   ├── inputs/
│   │   └── monta_raw_glossary.xlsx  # Master glossary (input)
│   └── outputs/
│       ├── glossary.sqlite    # SQLite database (generated)
│       └── glossary.md        # Markdown file (generated)
├── scripts/                    # Data processing
│   └── import.py              # Unified import script
├── python/                     # Python package
│   └── monta_glossary/
├── kotlin/                     # Kotlin package
│   └── src/main/kotlin/com/monta/glossary/
└── typescript/                 # TypeScript package
    └── src/
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
./import.sh                                    # Basic import
./import.sh --markdown                         # Import + markdown
./import.sh --markdown --alternatives          # Full workflow

# Option 2: Activate venv manually
source .venv/bin/activate
python scripts/import.py --markdown --alternatives
```

## 📥 Data Source

The original Monta raw glossary is maintained in Google Sheets:
[Monta Glossary Master Document](https://docs.google.com/spreadsheets/d/1-lI3H0st_NNaU4BwkQW4mahkHs-kQQEw/edit?rtpof=true&gid=1333186963#gid=1333186963)

Export this spreadsheet as Excel (`.xlsx`) and place it at `files/inputs/monta_raw_glossary.xlsx` before running the import.

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
2. **Run Import**: `./import.sh --markdown --alternatives`
3. **Distribute**: The `files/glossary.sqlite` file can be used by all packages

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

## 🔐 Environment Variables

Create a `.env` file for OpenAI integration:

```env
OPENAI_API_KEY=your_api_key_here
```

Required only for `--alternatives` option.

## 🧪 Running Tests

### Python
```bash
cd python
pytest test_glossary.py
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

## 💡 Common Use Cases

### 1. First Time Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
./import.sh --markdown
```

### 2. Update Glossary from New Excel
```bash
# Place new file at files/inputs/monta_raw_glossary.xlsx
./import.sh --markdown
```

### 3. Add Alternative Words with AI
```bash
# Setup OpenAI key first
echo "OPENAI_API_KEY=your_key_here" > .env

# Test with a few terms
./import.sh --alternatives --limit 10

# Generate for all terms
./import.sh --alternatives
```

### 4. Regenerate Markdown Only
```bash
./import.sh --skip-import --markdown
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
```bash
# Create .env file with your OpenAI API key
echo "OPENAI_API_KEY=your_key_here" > .env
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
2. Run: `./import.sh --alternatives --markdown`
3. Run tests in all packages
4. Commit changes

---

**Additional Documentation:**
- [STRUCTURE.md](STRUCTURE.md) - Detailed architecture
- [QUICKSTART.md](QUICKSTART.md) - Fast reference
- Package-specific READMEs in `python/`, `kotlin/`, `typescript/` directories
