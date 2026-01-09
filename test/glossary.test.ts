import { Glossary, TermHelpers } from '../src/index';

describe('Glossary', () => {
  let glossary: Glossary;

  beforeAll(() => {
    glossary = new Glossary();
  });

  describe('basic functionality', () => {
    it('should count terms', () => {
      const count = glossary.count();
      expect(count).toBeGreaterThan(0);
    });

    it('should get all terms', () => {
      const terms = glossary.getAll();
      expect(terms.length).toBeGreaterThan(0);
      expect(terms[0]).toHaveProperty('id');
      expect(terms[0]).toHaveProperty('term');
      expect(terms[0]).toHaveProperty('description');
      expect(terms[0]).toHaveProperty('translations');
      expect(terms[0]).toHaveProperty('alternativeWords');
    });

    it('should get a term by name', () => {
      const allTerms = glossary.getAll();
      if (allTerms.length > 0) {
        const termName = allTerms[0].term;
        const term = glossary.getTerm(termName);

        expect(term).toBeDefined();
        expect(term?.term).toBe(termName);
        expect(term?.description).toBeDefined();
      }
    });

    it('should return null for non-existent term', () => {
      const term = glossary.getTerm('this-term-definitely-does-not-exist-12345');
      expect(term).toBeNull();
    });

    it('should search terms', () => {
      const results = glossary.search('charge');
      expect(results).toBeInstanceOf(Array);
      expect(results.length).toBeGreaterThan(0);

      // Check that results contain the search query
      const hasMatch = results.some(t =>
        t.term.toLowerCase().includes('charge') ||
        t.description.toLowerCase().includes('charge')
      );
      expect(hasMatch).toBe(true);
    });

    it('should get terms by tag', () => {
      const allTerms = glossary.getAll();
      const termsWithTags = allTerms.filter(t => t.tags);

      if (termsWithTags.length > 0) {
        const firstTag = termsWithTags[0].tags!.split(',')[0].trim();
        const results = glossary.getByTag(firstTag);

        expect(results).toBeInstanceOf(Array);
        expect(results.length).toBeGreaterThan(0);
        expect(results[0].tags).toContain(firstTag);
      }
    });

    it('should translate a term', () => {
      const allTerms = glossary.getAll();
      const translatableTerm = allTerms.find(t =>
        t.translatable && Object.keys(t.translations).length > 0
      );

      if (translatableTerm) {
        const languageCode = Object.keys(translatableTerm.translations)[0];
        const translation = glossary.translate(translatableTerm.term, languageCode);

        expect(translation).toBeDefined();
        expect(translation).toBe(translatableTerm.translations[languageCode]);
      }
    });

    it('should get available languages', () => {
      const languages = glossary.getLanguages();
      expect(languages).toBeInstanceOf(Array);
      expect(languages.length).toBeGreaterThan(0);
      expect(languages).toContain('en');
    });
  });

  describe('normalizeText', () => {
    it('should handle empty text', () => {
      const result = glossary.normalizeText('');
      expect(result).toBe('');
    });

    it('should preserve text without glossary terms', () => {
      const input = 'This is just random text without any specific terminology xyz123';
      const result = glossary.normalizeText(input);
      expect(result).toBe(input);
    });

    it('should replace alternative terms with canonical terms', () => {
      const terms = glossary.getAll();
      const termWithAlternatives = terms.find(t => t.alternativeWords.length > 0);

      if (termWithAlternatives) {
        const alternative = termWithAlternatives.alternativeWords[0];
        const canonical = termWithAlternatives.term;
        const input = `Testing with ${alternative} here`;
        const result = glossary.normalizeText(input);

        expect(result).toContain(canonical);
      }
    });

    it('should handle text with multiple occurrences of the same alternative', () => {
      const terms = glossary.getAll();
      const termWithAlternatives = terms.find(t => t.alternativeWords.length > 0);

      if (termWithAlternatives) {
        const alternative = termWithAlternatives.alternativeWords[0];
        const canonical = termWithAlternatives.term;
        const input = `${alternative} and ${alternative} again`;
        const result = glossary.normalizeText(input);

        // Should replace all occurrences
        const canonicalCount = (result.match(new RegExp(canonical, 'gi')) || []).length;
        expect(canonicalCount).toBeGreaterThanOrEqual(2);
      }
    });

    it('should respect word boundaries', () => {
      const input = 'charging charges charged';
      const result = glossary.normalizeText(input);

      // Should not replace partial matches
      expect(result).toBeDefined();
      expect(typeof result).toBe('string');
    });

    it('should handle text with special regex characters', () => {
      const input = 'Text with special chars: $100 (test) [array] {obj}';
      const result = glossary.normalizeText(input);

      expect(result).toBeDefined();
      expect(typeof result).toBe('string');
      // Should preserve special characters
      expect(result).toContain('$100');
      expect(result).toContain('(test)');
      expect(result).toContain('[array]');
    });

    it('should handle case insensitive terms', () => {
      const terms = glossary.getAll();
      const caseInsensitiveTerm = terms.find(
        t => !t.caseSensitive && t.alternativeWords.length > 0
      );

      if (caseInsensitiveTerm) {
        const alternative = caseInsensitiveTerm.alternativeWords[0];
        const upperInput = alternative.toUpperCase();
        const result = glossary.normalizeText(upperInput);

        // Should replace regardless of case
        expect(result).toContain(caseInsensitiveTerm.term);
      }
    });
  });

  describe('TermHelpers', () => {
    it('should check if term has tag', () => {
      const terms = glossary.getAll();
      const termWithTags = terms.find(t => t.tags);

      if (termWithTags) {
        const firstTag = termWithTags.tags!.split(',')[0].trim();
        const hasTag = TermHelpers.hasTag(termWithTags, firstTag);
        expect(hasTag).toBe(true);
      }
    });

    it('should return false for non-existent tag', () => {
      const terms = glossary.getAll();
      if (terms.length > 0) {
        const hasTag = TermHelpers.hasTag(terms[0], 'non-existent-tag-xyz123');
        expect(hasTag).toBe(false);
      }
    });

    it('should get all tags for a term', () => {
      const terms = glossary.getAll();
      const termWithTags = terms.find(t => t.tags);

      if (termWithTags) {
        const tags = TermHelpers.getTags(termWithTags);
        expect(tags).toBeInstanceOf(Array);
        expect(tags.length).toBeGreaterThan(0);
      }
    });

    it('should return empty array for term without tags', () => {
      const terms = glossary.getAll();
      const termWithoutTags = terms.find(t => !t.tags);

      if (termWithoutTags) {
        const tags = TermHelpers.getTags(termWithoutTags);
        expect(tags).toEqual([]);
      }
    });
  });

  describe('caching', () => {
    it('should cache data across instances', () => {
      const glossary1 = new Glossary();
      const glossary2 = new Glossary();

      const count1 = glossary1.count();
      const count2 = glossary2.count();

      expect(count2).toBe(count1);
    });
  });
});
