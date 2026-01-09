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

interface ApiTranslation {
  languageCode: string;
  translation: string;
}

interface ApiAlternative {
  alternative: string;
  isPlural: boolean;
}

interface ApiTerm {
  id: number;
  term: string;
  description: string;
  caseSensitive: boolean;
  translatable: boolean;
  forbidden: boolean;
  tags: string;
  pluralForm: string | null;
  translations: ApiTranslation[];
  alternatives: ApiAlternative[];
  additionalDescriptions: any[];
}

interface ApiResponse {
  terms: ApiTerm[];
}

/**
 * Main interface for accessing the Monta glossary.
 */
export class Glossary {
  private static API_URL = 'https://translate.monta.app/public/api/glossary';
  private static cachedTerms: Term[] | null = null;
  private static fetchPromise: Promise<void> | null = null;

  /**
   * Initialize the glossary.
   * Data will be fetched on first use and cached globally.
   */
  constructor() {
    // Data is fetched lazily on first use and shared across all instances
  }

  /**
   * Fetch and cache glossary data from the API.
   * Uses a static cache shared across all Glossary instances.
   */
  private async ensureData(): Promise<void> {
    // If already cached, return immediately
    if (Glossary.cachedTerms !== null) {
      return;
    }

    // If a fetch is in progress, wait for it
    if (Glossary.fetchPromise !== null) {
      return Glossary.fetchPromise;
    }

    // Start fetching
    Glossary.fetchPromise = (async () => {
      try {
        const response = await fetch(Glossary.API_URL);
        if (!response.ok) {
          throw new Error(`Failed to fetch glossary: ${response.statusText}`);
        }

        const data: ApiResponse = await response.json();
        Glossary.cachedTerms = data.terms.map(apiTerm => this.transformApiTerm(apiTerm));
      } catch (error) {
        Glossary.fetchPromise = null; // Clear promise on error so retry is possible
        throw new Error(`Failed to load glossary: ${error instanceof Error ? error.message : 'Unknown error'}`);
      } finally {
        Glossary.fetchPromise = null;
      }
    })();

    return Glossary.fetchPromise;
  }

  /**
   * Transform API term format to internal Term format.
   */
  private transformApiTerm(apiTerm: ApiTerm): Term {
    const translations: Record<string, string> = {};
    for (const t of apiTerm.translations) {
      translations[t.languageCode] = t.translation;
    }

    const alternativeWords = apiTerm.alternatives.map(a => a.alternative);

    return {
      id: apiTerm.id,
      term: apiTerm.term,
      description: apiTerm.description,
      caseSensitive: apiTerm.caseSensitive,
      translatable: apiTerm.translatable,
      forbidden: apiTerm.forbidden,
      tags: apiTerm.tags || null,
      translations,
      alternativeWords,
    };
  }

  /**
   * Get a term by its name.
   */
  async getTerm(termName: string): Promise<Term | null> {
    await this.ensureData();
    return Glossary.cachedTerms!.find(t => t.term === termName) || null;
  }

  /**
   * Search for terms matching a query.
   */
  async search(query: string): Promise<Term[]> {
    await this.ensureData();
    const lowerQuery = query.toLowerCase();
    return Glossary.cachedTerms!.filter(
      t =>
        t.term.toLowerCase().includes(lowerQuery) ||
        t.description.toLowerCase().includes(lowerQuery)
    );
  }

  /**
   * Get all terms in the glossary.
   */
  async getAll(): Promise<Term[]> {
    await this.ensureData();
    return [...Glossary.cachedTerms!];
  }

  /**
   * Get all terms with a specific tag.
   */
  async getByTag(tag: string): Promise<Term[]> {
    await this.ensureData();
    return Glossary.cachedTerms!.filter(t => t.tags && t.tags.includes(tag));
  }

  /**
   * Get translation for a term in a specific language.
   */
  async translate(termName: string, languageCode: string): Promise<string | null> {
    const term = await this.getTerm(termName);
    return term ? (term.translations[languageCode] || null) : null;
  }

  /**
   * Get total number of terms in the glossary.
   */
  async count(): Promise<number> {
    await this.ensureData();
    return Glossary.cachedTerms!.length;
  }

  /**
   * Get list of all available language codes.
   */
  async getLanguages(): Promise<string[]> {
    await this.ensureData();
    if (Glossary.cachedTerms!.length === 0) return [];

    const languages = new Set<string>();
    for (const term of Glossary.cachedTerms!) {
      Object.keys(term.translations).forEach(lang => languages.add(lang));
    }
    return Array.from(languages).sort();
  }

  /**
   * Normalize text by replacing alternative terms with their canonical versions.
   * This function finds all occurrences of terms (including their alternatives)
   * and replaces them with the correct canonical term from the glossary.
   *
   * @param text The text to normalize
   * @returns The normalized text with all terms replaced
   */
  async normalizeText(text: string): Promise<string> {
    await this.ensureData();
    let result = text;

    // Sort by term length (longest first) to handle overlapping terms correctly
    const sortedTerms = [...Glossary.cachedTerms!].sort((a, b) => b.term.length - a.term.length);

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
   * Refresh the glossary data from the API.
   * Use this to get the latest data if the glossary has been updated.
   * This clears the static cache and forces a new fetch.
   */
  async refresh(): Promise<void> {
    Glossary.cachedTerms = null;
    Glossary.fetchPromise = null;
    await this.ensureData();
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
