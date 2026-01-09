# Monta Glossary

A TypeScript/JavaScript package for accessing Monta's terminology glossary with translations. Data is automatically updated daily from Monta's API and bundled statically for instant, offline-ready access to EV charging terminology across multiple languages.

## Features

- 🌍 **Multi-language support** - Access translations in multiple languages
- 🔍 **Search functionality** - Find terms by keyword or description
- 🏷️ **Tag-based filtering** - Get terms by category (industry, product, etc.)
- 📝 **Text normalization** - Replace alternative terms with canonical versions
- ⚡ **Zero runtime dependencies** - No API calls, all data bundled statically
- 🔄 **Auto-updated** - GitHub Action updates data daily from API
- 🔐 **Type-safe** - Full TypeScript support with comprehensive types
- 🚀 **Instant access** - No async/await needed, synchronous API

## Installation

```bash
npm install @monta/glossary
```

Or with yarn:

```bash
yarn add @monta/glossary
```

## Quick Start

```typescript
import { Glossary } from '@monta/glossary';

const glossary = new Glossary();

// Get a specific term (synchronous - no await needed!)
const term = glossary.getTerm('charging cable');
if (term) {
  console.log(term.description);
  console.log(term.translations['da']); // Danish: ladekabel
}

// Search for terms
const results = glossary.search('charge');
console.log(`Found ${results.length} results`);

// Get terms by tag
const productTerms = glossary.getByTag('product');

// Normalize text (replace alternatives with canonical terms)
const text = 'The e-car needs a charging wire';
const normalized = glossary.normalizeText(text);
// Output: "The EV needs a charging cable"
```

## API Reference

### Glossary Class

#### Constructor
```typescript
const glossary = new Glossary();
```

No configuration needed - the glossary loads from bundled static data.

#### Methods

All methods are synchronous and return data immediately.

##### `getTerm(termName: string): Term | null`
Get a specific term by name.

```typescript
const term = glossary.getTerm('charging cable');
```

##### `search(query: string): Term[]`
Search for terms matching a query in term names or descriptions.

```typescript
const results = glossary.search('charge');
```

##### `getAll(): Term[]`
Get all terms in the glossary.

```typescript
const allTerms = glossary.getAll();
```

##### `getByTag(tag: string): Term[]`
Get all terms with a specific tag.

```typescript
const industryTerms = glossary.getByTag('industry');
```

##### `translate(termName: string, languageCode: string): string | null`
Quick translation lookup for a term.

```typescript
const translation = glossary.translate('charge key', 'da');
// Returns: "ladebrik"
```

##### `count(): number`
Get the total number of terms in the glossary.

```typescript
const total = glossary.count();
```

##### `getLanguages(): string[]`
Get all available language codes.

```typescript
const languages = glossary.getLanguages();
// Returns: ['da', 'de', 'en', 'es', ...]
```

##### `normalizeText(text: string): string`
Replace alternative terms with their canonical versions.

```typescript
const text = 'The e-car needs a charging wire';
const normalized = glossary.normalizeText(text);
// Returns: "The EV needs a charging cable"
```

This method:
- Replaces alternative terms with canonical versions
- Respects word boundaries (won't replace partial matches)
- Honors case sensitivity settings per term
- Handles multiple occurrences

### Term Interface

```typescript
interface Term {
  id: number;
  term: string;                    // Canonical term name
  description: string;              // Full description with usage rules
  caseSensitive: boolean;           // Whether the term is case-sensitive
  translatable: boolean;            // Whether the term can be translated
  forbidden: boolean;               // Whether the term should be avoided
  tags: string | null;              // Comma-separated tags
  translations: Record<string, string>;  // Language code to translation mapping
  alternativeWords: string[];       // Alternative words/phrases for this term
}
```

### TermHelpers

Utility functions for working with terms.

```typescript
import { TermHelpers } from '@monta/glossary';

// Check if term has a specific tag
if (TermHelpers.hasTag(term, 'industry')) {
  console.log('This is an industry term');
}

// Get list of all tags for a term
const tags = TermHelpers.getTags(term);
```

## Usage Examples

### Basic Term Lookup

```typescript
import { Glossary } from '@monta/glossary';

const glossary = new Glossary();

const term = glossary.getTerm('EV');
if (term) {
  console.log(`${term.term}: ${term.description}`);

  // Get all translations
  for (const [lang, translation] of Object.entries(term.translations)) {
    console.log(`  ${lang}: ${translation}`);
  }
}
```

### Search and Filter

```typescript
// Search for terms
const chargeTerms = glossary.search('charge');

// Filter by tag
const productTerms = glossary.getByTag('product');
const industryTerms = glossary.getByTag('industry');

// Get all terms
const allTerms = glossary.getAll();
console.log(`Total terms: ${glossary.count()}`);
```

### Text Normalization

```typescript
// Replace alternative terms with canonical ones
const userInput = 'My e-car is connected to the charging station';
const normalized = glossary.normalizeText(userInput);
// Result: "My EV is connected to the charge point"

// Useful for:
// - Standardizing user input
// - Normalizing content before indexing
// - Ensuring consistent terminology in documentation
```

### Working with Translations

```typescript
// Quick translation
const danishTerm = glossary.translate('charging cable', 'da');
console.log(danishTerm); // "ladekabel"

// Get all available languages
const languages = glossary.getLanguages();
console.log(`Available in ${languages.length} languages`);

// Translate multiple terms
const terms = ['EV', 'charge point', 'charging cable'];
for (const termName of terms) {
  const term = glossary.getTerm(termName);
  if (term) {
    console.log(`${termName}:`);
    console.log(`  Danish: ${term.translations['da']}`);
    console.log(`  German: ${term.translations['de']}`);
  }
}
```

### Checking Term Tags

```typescript
import { Glossary, TermHelpers } from '@monta/glossary';

const glossary = new Glossary();
const term = glossary.getTerm('charge point');

if (term) {
  // Check for specific tag
  if (TermHelpers.hasTag(term, 'industry')) {
    console.log('This is an industry-standard term');
  }

  // Get all tags
  const tags = TermHelpers.getTags(term);
  console.log(`Tags: ${tags.join(', ')}`);
}
```

## Data Source

The glossary data is automatically updated from Monta's public API:
- **Source**: `https://translate.monta.app/public/api/glossary`
- **Update frequency**: Daily at 2 AM UTC (via GitHub Actions)
- **Storage**: Bundled as static JSON file (`src/glossary-data.json`)
- **No runtime API calls**: All data is pre-fetched and bundled with the package

## Development

### Building

```bash
npm install
npm run build
```

This will compile TypeScript to JavaScript in the `dist/` directory.

### Testing

```bash
npm test
```

## Project Structure

```
glossary/
├── src/
│   └── index.ts            # Main library code
├── test/
│   └── glossary.test.ts    # Test suite
├── package.json
├── tsconfig.json
├── jest.config.js
└── README.md               # This file
```

## Common Use Cases

### 1. Standardize User Input

```typescript
const glossary = new Glossary();

// User submits a support ticket with inconsistent terminology
const userMessage = 'My e-car won\'t connect to the charging station';

// Normalize to use canonical terms
const normalized = glossary.normalizeText(userMessage);
// "My EV won't connect to the charge point"
```

### 2. Build a Multilingual Interface

```typescript
const glossary = new Glossary();
const currentLang = 'da'; // User's language

// Get all product terms in user's language
const productTerms = glossary.getByTag('product');

const localizedTerms = productTerms.map(term => ({
  english: term.term,
  localized: term.translations[currentLang] || term.term,
  description: term.description
}));
```

### 3. Validate Terminology in Content

```typescript
const glossary = new Glossary();

// Check if content uses forbidden terms
const content = 'Check out our new charging pole!';
const forbiddenTerms = (glossary.getAll())
  .filter(t => t.forbidden);

for (const term of forbiddenTerms) {
  if (content.toLowerCase().includes(term.term.toLowerCase())) {
    console.warn(`Content uses forbidden term: ${term.term}`);
    console.log(`Suggestion: Use alternatives like ${term.alternativeWords.join(', ')}`);
  }
}
```

## License

Copyright © Monta

## Contributing

This package is maintained by the Monta team. For issues or feature requests, please contact the development team.
