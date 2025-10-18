# Monta Glossary - TypeScript Package

TypeScript/JavaScript package for accessing Monta's terminology glossary with translations.

## Installation

```bash
npm install /path/to/glossary/typescript
```

Or add to your `package.json`:

```json
{
  "dependencies": {
    "@monta/glossary": "file:../path/to/glossary/typescript"
  }
}
```

## Usage

### TypeScript

```typescript
import { Glossary, Term, TermHelpers } from '@monta/glossary';

// Initialize the glossary
const glossary = new Glossary('/path/to/files/outputs/glossary.sqlite');

// Get a term
const term = glossary.getTerm('charging cable');
if (term) {
  console.log(term.description);
  console.log(term.translations['da']); // Danish: ladekabel
}

// Search terms
const results = glossary.search('charge');
console.log(`Found ${results.length} results`);

// Get terms by tag
const productTerms = glossary.getByTag('product');

// Quick translate
const translation = glossary.translate('charge key', 'da');
console.log(translation);

// Check if term has a tag
if (term && TermHelpers.hasTag(term, 'industry')) {
  console.log('This is an industry term');
}

// Get all terms
const allTerms = glossary.getAll();
console.log(`Total terms: ${glossary.count()}`);

// Close when done
glossary.close();
```

### JavaScript

```javascript
const { Glossary, TermHelpers } = require('@monta/glossary');

const glossary = new Glossary();
const term = glossary.getTerm('charging cable');
console.log(term.translations['da']);
glossary.close();
```

## API Reference

### Glossary Class

**Constructor:**
- `new Glossary(dbPath?: string)` - Initialize with optional database path

**Methods:**
- `getTerm(termName: string): Term | null` - Get a specific term
- `search(query: string): Term[]` - Search terms
- `getAll(): Term[]` - Get all terms
- `getByTag(tag: string): Term[]` - Get terms with specific tag
- `translate(termName: string, languageCode: string): string | null` - Quick translate
- `count(): number` - Get total number of terms
- `getLanguages(): string[]` - Get available language codes
- `close(): void` - Close database connection

### Term Interface

```typescript
interface Term {
  id: number;
  term: string;
  description: string;
  caseSensitive: boolean;
  translatable: boolean;
  forbidden: boolean;
  tags: string | null;
  translations: Record<string, string>;
  alternativeWords: string[];
}
```

### TermHelpers

- `hasTag(term: Term, tag: string): boolean` - Check if term has tag
- `getTags(term: Term): string[]` - Get list of tags

## Building

```bash
npm install
npm run build
```

This will compile TypeScript to JavaScript in the `dist/` directory.
