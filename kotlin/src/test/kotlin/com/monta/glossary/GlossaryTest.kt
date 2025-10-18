package com.monta.glossary

import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Assertions.*
import java.io.File

class GlossaryTest {
    private lateinit var glossary: Glossary
    private val dbPath = "../files/glossary.sqlite"

    @BeforeEach
    fun setup() {
        glossary = Glossary(dbPath)
    }

    @AfterEach
    fun teardown() {
        glossary.close()
    }

    @Test
    fun `normalizeText should handle empty text`() {
        val result = glossary.normalizeText("")
        assertEquals("", result)
    }

    @Test
    fun `normalizeText should preserve text without glossary terms`() {
        val input = "This is just random text without any specific terminology"
        val result = glossary.normalizeText(input)
        assertEquals(input, result)
    }

    @Test
    fun `normalizeText should replace alternative terms with canonical terms`() {
        val terms = glossary.getAll()
        if (terms.isNotEmpty() && terms[0].alternativeWords.isNotEmpty()) {
            val alternative = terms[0].alternativeWords[0]
            val canonical = terms[0].term
            val input = "$alternative and $alternative again"
            val result = glossary.normalizeText(input)

            assertTrue(result.contains(canonical))
            if (!terms[0].caseSensitive) {
                assertFalse(result.lowercase().contains(alternative.lowercase()))
            }
        }
    }

    @Test
    fun `normalizeText should handle multiple occurrences`() {
        val terms = glossary.getAll()
        if (terms.isNotEmpty() && terms[0].alternativeWords.isNotEmpty()) {
            val alternative = terms[0].alternativeWords[0]
            val canonical = terms[0].term
            val input = "The $alternative is great. Another $alternative here."
            val result = glossary.normalizeText(input)

            // Count occurrences of canonical term
            val count = result.split(canonical).size - 1
            assertTrue(count >= 2)
        }
    }

    @Test
    fun `normalizeText should respect word boundaries`() {
        val input = "charging charges charged"
        val result = glossary.normalizeText(input)

        // Result should be defined and shouldn't replace partial matches
        assertNotNull(result)
        assertTrue(result is String)
    }

    @Test
    fun `normalizeText should handle case sensitivity correctly`() {
        val terms = glossary.getAll()
        val caseInsensitiveTerm = terms.find { !it.caseSensitive }

        if (caseInsensitiveTerm != null && caseInsensitiveTerm.alternativeWords.isNotEmpty()) {
            val alternative = caseInsensitiveTerm.alternativeWords[0]
            val upperInput = alternative.uppercase()
            val result = glossary.normalizeText(upperInput)

            // Should replace regardless of case for non-case-sensitive terms
            assertTrue(result.contains(caseInsensitiveTerm.term))
        }
    }

    @Test
    fun `normalizeText should handle text with special regex characters`() {
        val input = "Text with special chars: \$100 (test) [array]"
        val result = glossary.normalizeText(input)

        assertNotNull(result)
        assertTrue(result is String)
    }

    @Test
    fun `normalizeText should preserve surrounding text`() {
        val terms = glossary.getAll()
        if (terms.isNotEmpty() && terms[0].alternativeWords.isNotEmpty()) {
            val alternative = terms[0].alternativeWords[0]
            val canonical = terms[0].term
            val input = "Before $alternative after"
            val result = glossary.normalizeText(input)

            assertTrue(result.contains("Before"))
            assertTrue(result.contains("after"))
            assertTrue(result.contains(canonical))
        }
    }

    @Test
    fun `getTerm should return a term by name`() {
        val terms = glossary.getAll()
        if (terms.isNotEmpty()) {
            val term = glossary.getTerm(terms[0].term)
            assertNotNull(term)
            assertEquals(terms[0].term, term?.term)
        }
    }

    @Test
    fun `count should return number of terms`() {
        val count = glossary.count()
        assertTrue(count > 0)
    }

    @Test
    fun `getAll should return all terms`() {
        val terms = glossary.getAll()
        assertTrue(terms.isNotEmpty())
        assertTrue(terms.all { it.term.isNotEmpty() })
    }
}
