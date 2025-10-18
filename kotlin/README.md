# Monta Glossary - Kotlin Package

Kotlin package for accessing Monta's terminology glossary with translations.

## Installation

### Gradle (build.gradle.kts)

```kotlin
dependencies {
    implementation(files("path/to/glossary/kotlin"))
}
```

## Usage

```kotlin
import com.monta.glossary.Glossary

fun main() {
    // Initialize the glossary
    Glossary("/path/to/files/outputs/glossary.sqlite").use { glossary ->

        // Get a term
        val term = glossary.getTerm("charging cable")
        term?.let {
            println(it.description)
            println(it.translate("da"))  // Danish: ladekabel
        }

        // Search terms
        val results = glossary.search("charge")
        println("Found ${results.size} results")

        // Get terms by tag
        val productTerms = glossary.getByTag("product")

        // Quick translate
        val translation = glossary.translate("charge key", "da")
        println(translation)

        // Get all terms
        val allTerms = glossary.getAll()
        println("Total terms: ${glossary.count()}")
    }
}
```

## API Reference

### Glossary Class

**Methods:**
- `getTerm(termName: String): Term?` - Get a specific term
- `search(query: String): List<Term>` - Search terms
- `getAll(): List<Term>` - Get all terms
- `getByTag(tag: String): List<Term>` - Get terms with specific tag
- `translate(termName: String, languageCode: String): String?` - Quick translate
- `count(): Int` - Get total number of terms

### Term Data Class

**Properties:**
- `term: String` - The term name
- `description: String` - Full description
- `tags: String?` - Comma-separated tags
- `translations: Map<String, String>` - All translations
- `alternativeWords: List<String>` - Alternative words/phrases
- `caseSensitive: Boolean` - Is case sensitive
- `translatable: Boolean` - Is translatable
- `forbidden: Boolean` - Is forbidden

**Methods:**
- `translate(languageCode: String): String?` - Get translation
- `hasTag(tag: String): Boolean` - Check if has tag
- `getTags(): List<String>` - Get list of tags
