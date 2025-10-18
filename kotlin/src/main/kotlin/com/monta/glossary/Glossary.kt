package com.monta.glossary

import java.io.File
import java.sql.Connection
import java.sql.DriverManager

/**
 * Represents a glossary term with all its metadata.
 */
data class Term(
    val id: Int,
    val term: String,
    val description: String,
    val caseSensitive: Boolean,
    val translatable: Boolean,
    val forbidden: Boolean,
    val tags: String?,
    val translations: Map<String, String>,
    val alternativeWords: List<String>
) {
    /**
     * Get translation for a specific language.
     */
    fun translate(languageCode: String): String? = translations[languageCode]

    /**
     * Check if term has a specific tag.
     */
    fun hasTag(tag: String): Boolean {
        return tags?.split(",")?.map { it.trim() }?.contains(tag) ?: false
    }

    /**
     * Get list of all tags for this term.
     */
    fun getTags(): List<String> {
        return tags?.split(",")?.map { it.trim() } ?: emptyList()
    }
}

/**
 * Main interface for accessing the Monta glossary.
 */
class Glossary(dbPath: String? = null) : AutoCloseable {
    private val connection: Connection

    init {
        val finalPath = dbPath ?: run {
            // Use database in files/outputs directory relative to project root
            val resourcePath = this::class.java.classLoader.getResource("outputs/glossary.sqlite")
            resourcePath?.path ?: throw IllegalStateException("Database not found")
        }
        connection = DriverManager.getConnection("jdbc:sqlite:$finalPath")
    }

    /**
     * Get a term by its name.
     */
    fun getTerm(termName: String): Term? {
        val stmt = connection.prepareStatement(
            "SELECT * FROM terms WHERE term = ?"
        )
        stmt.setString(1, termName)
        val rs = stmt.executeQuery()

        return if (rs.next()) {
            val termId = rs.getInt("id")
            Term(
                id = termId,
                term = rs.getString("term"),
                description = rs.getString("description"),
                caseSensitive = rs.getBoolean("case_sensitive"),
                translatable = rs.getBoolean("translatable"),
                forbidden = rs.getBoolean("forbidden"),
                tags = rs.getString("tags"),
                translations = getTranslations(termId),
                alternativeWords = getAlternativeWords(termId)
            )
        } else null
    }

    /**
     * Search for terms matching a query.
     */
    fun search(query: String): List<Term> {
        val stmt = connection.prepareStatement(
            "SELECT * FROM terms WHERE term LIKE ? OR description LIKE ? ORDER BY term"
        )
        val pattern = "%$query%"
        stmt.setString(1, pattern)
        stmt.setString(2, pattern)
        val rs = stmt.executeQuery()

        val results = mutableListOf<Term>()
        while (rs.next()) {
            val termId = rs.getInt("id")
            results.add(
                Term(
                    id = termId,
                    term = rs.getString("term"),
                    description = rs.getString("description"),
                    caseSensitive = rs.getBoolean("case_sensitive"),
                    translatable = rs.getBoolean("translatable"),
                    forbidden = rs.getBoolean("forbidden"),
                    tags = rs.getString("tags"),
                    translations = getTranslations(termId),
                    alternativeWords = getAlternativeWords(termId)
                )
            )
        }
        return results
    }

    /**
     * Get all terms in the glossary.
     */
    fun getAll(): List<Term> {
        val stmt = connection.prepareStatement("SELECT * FROM terms ORDER BY term")
        val rs = stmt.executeQuery()

        val results = mutableListOf<Term>()
        while (rs.next()) {
            val termId = rs.getInt("id")
            results.add(
                Term(
                    id = termId,
                    term = rs.getString("term"),
                    description = rs.getString("description"),
                    caseSensitive = rs.getBoolean("case_sensitive"),
                    translatable = rs.getBoolean("translatable"),
                    forbidden = rs.getBoolean("forbidden"),
                    tags = rs.getString("tags"),
                    translations = getTranslations(termId),
                    alternativeWords = getAlternativeWords(termId)
                )
            )
        }
        return results
    }

    /**
     * Get all terms with a specific tag.
     */
    fun getByTag(tag: String): List<Term> {
        val stmt = connection.prepareStatement(
            "SELECT * FROM terms WHERE tags LIKE ? ORDER BY term"
        )
        stmt.setString(1, "%$tag%")
        val rs = stmt.executeQuery()

        val results = mutableListOf<Term>()
        while (rs.next()) {
            val termId = rs.getInt("id")
            results.add(
                Term(
                    id = termId,
                    term = rs.getString("term"),
                    description = rs.getString("description"),
                    caseSensitive = rs.getBoolean("case_sensitive"),
                    translatable = rs.getBoolean("translatable"),
                    forbidden = rs.getBoolean("forbidden"),
                    tags = rs.getString("tags"),
                    translations = getTranslations(termId),
                    alternativeWords = getAlternativeWords(termId)
                )
            )
        }
        return results
    }

    /**
     * Get translation for a term in a specific language.
     */
    fun translate(termName: String, languageCode: String): String? {
        return getTerm(termName)?.translate(languageCode)
    }

    /**
     * Get total number of terms in the glossary.
     */
    fun count(): Int {
        val stmt = connection.prepareStatement("SELECT COUNT(*) FROM terms")
        val rs = stmt.executeQuery()
        return if (rs.next()) rs.getInt(1) else 0
    }

    private fun getTranslations(termId: Int): Map<String, String> {
        val stmt = connection.prepareStatement(
            "SELECT language_code, translation FROM translations WHERE term_id = ?"
        )
        stmt.setInt(1, termId)
        val rs = stmt.executeQuery()

        val translations = mutableMapOf<String, String>()
        while (rs.next()) {
            translations[rs.getString("language_code")] = rs.getString("translation")
        }
        return translations
    }

    private fun getAlternativeWords(termId: Int): List<String> {
        val stmt = connection.prepareStatement(
            "SELECT alternative FROM alternative_words WHERE term_id = ?"
        )
        stmt.setInt(1, termId)
        val rs = stmt.executeQuery()

        val alternatives = mutableListOf<String>()
        while (rs.next()) {
            alternatives.add(rs.getString("alternative"))
        }
        return alternatives
    }

    /**
     * Normalize text by replacing alternative terms with their canonical versions.
     * This function finds all occurrences of terms (including their alternatives)
     * and replaces them with the correct canonical term from the glossary.
     *
     * @param text The text to normalize
     * @return The normalized text with all terms replaced
     */
    fun normalizeText(text: String): String {
        var result = text
        val terms = getAll()

        // Sort by term length (longest first) to handle overlapping terms correctly
        val sortedTerms = terms.sortedByDescending { it.term.length }

        for (term in sortedTerms) {
            // Create a list of all variations (canonical + alternatives)
            val variations = listOf(term.term) + term.alternativeWords

            for (variation in variations) {
                if (variation.isEmpty()) continue

                // Escape special regex characters
                val escapedVariation = Regex.escape(variation)

                // Create regex with word boundaries
                val flags = if (term.caseSensitive) setOf() else setOf(RegexOption.IGNORE_CASE)
                val regex = Regex("\\b$escapedVariation\\b", flags)

                // Replace the variation with the canonical term
                result = regex.replace(result, term.term)
            }
        }

        return result
    }

    override fun close() {
        connection.close()
    }
}
