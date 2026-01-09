# Monta Glossary

A TypeScript/JavaScript package for accessing Monta's terminology glossary with translations. The glossary is fetched from Monta's public API and provides a simple interface for working with EV charging terminology across multiple languages.

## Features

- 🌍 **Multi-language support** - Access translations in multiple languages
- 🔍 **Search functionality** - Find terms by keyword or description
- 🏷️ **Tag-based filtering** - Get terms by category (industry, product, etc.)
- 📝 **Text normalization** - Replace alternative terms with canonical versions
- ⚡ **Lazy loading** - Data is fetched only when needed
- 🔄 **Caching** - API data is cached in memory for fast access
- 🔐 **Type-safe** - Full TypeScript support with comprehensive types

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

// Get a specific term
const term = await glossary.getTerm('charging cable');
if (term) {
  console.log(term.description);
  console.log(term.translations['da']); // Danish: ladekabel
}

// Search for terms
const results = await glossary.search('charge');
console.log(`Found ${results.length} results`);

// Get terms by tag
const productTerms = await glossary.getByTag('product');

// Normalize text (replace alternatives with canonical terms)
const text = 'The e-car needs a charging wire';
const normalized = await glossary.normalizeText(text);
// Output: "The EV needs a charging cable"
```

## API Reference

### Glossary Class

#### Constructor
```typescript
const glossary = new Glossary();
```

No configuration needed - the glossary fetches data from Monta's public API.

#### Methods

All methods are asynchronous and return Promises.

##### `getTerm(termName: string): Promise<Term | null>`
Get a specific term by name.

```typescript
const term = await glossary.getTerm('charging cable');
```

##### `search(query: string): Promise<Term[]>`
Search for terms matching a query in term names or descriptions.

```typescript
const results = await glossary.search('charge');
```

##### `getAll(): Promise<Term[]>`
Get all terms in the glossary.

```typescript
const allTerms = await glossary.getAll();
```

##### `getByTag(tag: string): Promise<Term[]>`
Get all terms with a specific tag.

```typescript
const industryTerms = await glossary.getByTag('industry');
```

##### `translate(termName: string, languageCode: string): Promise<string | null>`
Quick translation lookup for a term.

```typescript
const translation = await glossary.translate('charge key', 'da');
// Returns: "ladebrik"
```

##### `count(): Promise<number>`
Get the total number of terms in the glossary.

```typescript
const total = await glossary.count();
```

##### `getLanguages(): Promise<string[]>`
Get all available language codes.

```typescript
const languages = await glossary.getLanguages();
// Returns: ['da', 'de', 'en', 'es', ...]
```

##### `normalizeText(text: string): Promise<string>`
Replace alternative terms with their canonical versions.

```typescript
const text = 'The e-car needs a charging wire';
const normalized = await glossary.normalizeText(text);
// Returns: "The EV needs a charging cable"
```

This method:
- Replaces alternative terms with canonical versions
- Respects word boundaries (won't replace partial matches)
- Honors case sensitivity settings per term
- Handles multiple occurrences

##### `refresh(): Promise<void>`
Refresh the glossary data from the API. Use this to get the latest data if the glossary has been updated.

```typescript
await glossary.refresh();
```

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

const term = await glossary.getTerm('EV');
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
const chargeTerms = await glossary.search('charge');

// Filter by tag
const productTerms = await glossary.getByTag('product');
const industryTerms = await glossary.getByTag('industry');

// Get all terms
const allTerms = await glossary.getAll();
console.log(`Total terms: ${await glossary.count()}`);
```

### Text Normalization

```typescript
// Replace alternative terms with canonical ones
const userInput = 'My e-car is connected to the charging station';
const normalized = await glossary.normalizeText(userInput);
// Result: "My EV is connected to the charge point"

// Useful for:
// - Standardizing user input
// - Normalizing content before indexing
// - Ensuring consistent terminology in documentation
```

### Working with Translations

```typescript
// Quick translation
const danishTerm = await glossary.translate('charging cable', 'da');
console.log(danishTerm); // "ladekabel"

// Get all available languages
const languages = await glossary.getLanguages();
console.log(`Available in ${languages.length} languages`);

// Translate multiple terms
const terms = ['EV', 'charge point', 'charging cable'];
for (const termName of terms) {
  const term = await glossary.getTerm(termName);
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
const term = await glossary.getTerm('charge point');

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

The glossary data is fetched from Monta's public API:
- **Endpoint**: `https://translate.monta.app/public/api/glossary`
- **Format**: JSON
- **Caching**: Data is cached in memory after first fetch
- **Refresh**: Use `glossary.refresh()` to get the latest data

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
const normalized = await glossary.normalizeText(userMessage);
// "My EV won't connect to the charge point"
```

### 2. Build a Multilingual Interface

```typescript
const glossary = new Glossary();
const currentLang = 'da'; // User's language

// Get all product terms in user's language
const productTerms = await glossary.getByTag('product');

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
const forbiddenTerms = (await glossary.getAll())
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
