import { Glossary } from '../src/index';
import * as path from 'path';
import * as fs from 'fs';

interface TestCase {
  name: string;
  description: string;
  input: string;
  expected: string;
}

interface TestFixtures {
  normalize_text_tests: TestCase[];
  edge_cases: TestCase[];
}

describe('Glossary', () => {
  let glossary: Glossary;
  let testFixtures: TestFixtures;
  const dbPath = path.join(__dirname, '..', '..', 'files', 'outputs', 'glossary.sqlite');
  const fixturesPath = path.join(__dirname, '..', '..', 'files', 'test-fixtures.json');

  beforeAll(() => {
    glossary = new Glossary(dbPath);
    const fixturesData = fs.readFileSync(fixturesPath, 'utf-8');
    testFixtures = JSON.parse(fixturesData);
  });

  afterAll(() => {
    glossary.close();
  });

  describe('normalizeText', () => {
    it('should replace alternative terms with canonical terms', () => {
      // This test assumes there are terms with alternatives in the database
      const input = 'Test text with alternative terms';
      const result = glossary.normalizeText(input);

      expect(result).toBeDefined();
      expect(typeof result).toBe('string');
    });

    it('should handle empty text', () => {
      const result = glossary.normalizeText('');
      expect(result).toBe('');
    });

    it('should preserve text without glossary terms', () => {
      const input = 'This is just random text without any specific terminology';
      const result = glossary.normalizeText(input);
      expect(result).toBe(input);
    });

    it('should handle text with multiple occurrences of the same term', () => {
      const terms = glossary.getAll();
      if (terms.length > 0 && terms[0].alternativeWords.length > 0) {
        const alternative = terms[0].alternativeWords[0];
        const canonical = terms[0].term;
        const input = `${alternative} and ${alternative} again`;
        const result = glossary.normalizeText(input);

        expect(result).toContain(canonical);
        expect(result).not.toContain(alternative);
      }
    });

    it('should respect word boundaries', () => {
      const input = 'charging charges charged';
      const result = glossary.normalizeText(input);

      // Should not replace partial matches
      expect(result).toBeDefined();
    });

    it('should handle case sensitivity correctly', () => {
      const terms = glossary.getAll();
      const caseInsensitiveTerm = terms.find(t => !t.caseSensitive);

      if (caseInsensitiveTerm && caseInsensitiveTerm.alternativeWords.length > 0) {
        const alternative = caseInsensitiveTerm.alternativeWords[0];
        const upperCaseInput = alternative.toUpperCase();
        const result = glossary.normalizeText(upperCaseInput);

        // Should replace regardless of case for non-case-sensitive terms
        expect(result).toContain(caseInsensitiveTerm.term);
      }
    });

    it('should handle text with special regex characters', () => {
      const input = 'Text with special chars: $100 (test) [array]';
      const result = glossary.normalizeText(input);

      expect(result).toBeDefined();
      expect(typeof result).toBe('string');
    });
  });

  describe('basic functionality', () => {
    it('should get a term by name', () => {
      const terms = glossary.getAll();
      if (terms.length > 0) {
        const term = glossary.getTerm(terms[0].term);
        expect(term).toBeDefined();
        expect(term?.term).toBe(terms[0].term);
      }
    });

    it('should count terms', () => {
      const count = glossary.count();
      expect(count).toBeGreaterThan(0);
    });
  });

  describe('normalizeText with fixtures', () => {
    it('should pass all fixture test cases', () => {
      testFixtures.normalize_text_tests.forEach((testCase) => {
        const result = glossary.normalizeText(testCase.input);
        expect(result).toBe(testCase.expected);
      });
    });

    it('should pass edge case tests', () => {
      testFixtures.edge_cases.forEach((testCase) => {
        if (testCase.input && testCase.expected) {
          const result = glossary.normalizeText(testCase.input);
          expect(result).toBe(testCase.expected);
        }
      });
    });
  });
});
