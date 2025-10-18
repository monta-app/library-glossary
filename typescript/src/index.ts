import Database from 'better-sqlite3';
import * as path from 'path';

/**
 * Represents a glossary term with all its metadata.
 */
export interface Term {
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

/**
 * Main interface for accessing the Monta glossary.
 */
export class Glossary {
  private db: Database.Database;

  /**
   * Initialize the glossary.
   * @param dbPath Optional path to the SQLite database file.
   *               If not provided, uses the default location.
   */
  constructor(dbPath?: string) {
    const finalPath = dbPath || this.getDefaultDbPath();
    this.db = new Database(finalPath, { readonly: true });
  }

  private getDefaultDbPath(): string {
    // Use database in files/outputs directory relative to project root
    return path.join(__dirname, '..', '..', '..', 'files', 'outputs', 'glossary.sqlite');
  }

  /**
   * Get a term by its name.
   */
  getTerm(termName: string): Term | null {
    const row = this.db.prepare('SELECT * FROM terms WHERE term = ?').get(termName) as any;

    if (!row) return null;

    return {
      id: row.id,
      term: row.term,
      description: row.description,
      caseSensitive: Boolean(row.case_sensitive),
      translatable: Boolean(row.translatable),
      forbidden: Boolean(row.forbidden),
      tags: row.tags,
      translations: this.getTranslations(row.id),
      alternativeWords: this.getAlternativeWords(row.id),
    };
  }

  /**
   * Search for terms matching a query.
   */
  search(query: string): Term[] {
    const pattern = `%${query}%`;
    const rows = this.db
      .prepare('SELECT * FROM terms WHERE term LIKE ? OR description LIKE ? ORDER BY term')
      .all(pattern, pattern) as any[];

    return rows.map(row => ({
      id: row.id,
      term: row.term,
      description: row.description,
      caseSensitive: Boolean(row.case_sensitive),
      translatable: Boolean(row.translatable),
      forbidden: Boolean(row.forbidden),
      tags: row.tags,
      translations: this.getTranslations(row.id),
      alternativeWords: this.getAlternativeWords(row.id),
    }));
  }

  /**
   * Get all terms in the glossary.
   */
  getAll(): Term[] {
    const rows = this.db.prepare('SELECT * FROM terms ORDER BY term').all() as any[];

    return rows.map(row => ({
      id: row.id,
      term: row.term,
      description: row.description,
      caseSensitive: Boolean(row.case_sensitive),
      translatable: Boolean(row.translatable),
      forbidden: Boolean(row.forbidden),
      tags: row.tags,
      translations: this.getTranslations(row.id),
      alternativeWords: this.getAlternativeWords(row.id),
    }));
  }

  /**
   * Get all terms with a specific tag.
   */
  getByTag(tag: string): Term[] {
    const pattern = `%${tag}%`;
    const rows = this.db
      .prepare('SELECT * FROM terms WHERE tags LIKE ? ORDER BY term')
      .all(pattern) as any[];

    return rows.map(row => ({
      id: row.id,
      term: row.term,
      description: row.description,
      caseSensitive: Boolean(row.case_sensitive),
      translatable: Boolean(row.translatable),
      forbidden: Boolean(row.forbidden),
      tags: row.tags,
      translations: this.getTranslations(row.id),
      alternativeWords: this.getAlternativeWords(row.id),
    }));
  }

  /**
   * Get translation for a term in a specific language.
   */
  translate(termName: string, languageCode: string): string | null {
    const term = this.getTerm(termName);
    return term ? (term.translations[languageCode] || null) : null;
  }

  /**
   * Get total number of terms in the glossary.
   */
  count(): number {
    const result = this.db.prepare('SELECT COUNT(*) as count FROM terms').get() as any;
    return result.count;
  }

  /**
   * Get list of all available language codes.
   */
  getLanguages(): string[] {
    const terms = this.getAll();
    if (terms.length === 0) return [];

    const languages = Object.keys(terms[0].translations);
    return languages.sort();
  }

  private getTranslations(termId: number): Record<string, string> {
    const rows = this.db
      .prepare('SELECT language_code, translation FROM translations WHERE term_id = ?')
      .all(termId) as any[];

    const translations: Record<string, string> = {};
    for (const row of rows) {
      translations[row.language_code] = row.translation;
    }
    return translations;
  }

  private getAlternativeWords(termId: number): string[] {
    const rows = this.db
      .prepare('SELECT alternative FROM alternative_words WHERE term_id = ?')
      .all(termId) as any[];

    return rows.map(row => row.alternative);
  }

  /**
   * Normalize text by replacing alternative terms with their canonical versions.
   * This function finds all occurrences of terms (including their alternatives)
   * and replaces them with the correct canonical term from the glossary.
   *
   * @param text The text to normalize
   * @returns The normalized text with all terms replaced
   */
  normalizeText(text: string): string {
    let result = text;
    const terms = this.getAll();

    // Sort by term length (longest first) to handle overlapping terms correctly
    const sortedTerms = [...terms].sort((a, b) => b.term.length - a.term.length);

    for (const term of sortedTerms) {
      // Create a list of all variations (canonical + alternatives)
      const variations = [term.term, ...term.alternativeWords];

      for (const variation of variations) {
        if (!variation) continue;

        // Escape special regex characters
        const escapedVariation = variation.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

        // Create regex with word boundaries
        const flags = term.caseSensitive ? 'g' : 'gi';
        const regex = new RegExp(`\\b${escapedVariation}\\b`, flags);

        // Replace the variation with the canonical term
        result = result.replace(regex, term.term);
      }
    }

    return result;
  }

  /**
   * Close the database connection.
   */
  close(): void {
    this.db.close();
  }
}

/**
 * Helper functions for working with terms.
 */
export const TermHelpers = {
  /**
   * Check if a term has a specific tag.
   */
  hasTag(term: Term, tag: string): boolean {
    if (!term.tags) return false;
    return term.tags.split(',').map(t => t.trim()).includes(tag);
  },

  /**
   * Get list of all tags for a term.
   */
  getTags(term: Term): string[] {
    if (!term.tags) return [];
    return term.tags.split(',').map(t => t.trim());
  },
};
