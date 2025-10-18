"""Example usage of the Monta Glossary package."""

import sys
import os

# Add python package to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'python'))

from monta_glossary import Glossary

# Initialize the glossary
glossary = Glossary()

print("Monta Glossary Examples")
print("=" * 60)
print()

# Example 1: Get a specific term
print("1. Get a specific term:")
term = glossary.get_term("charging cable")
if term:
    print(f"   Term: {term.term}")
    print(f"   Description: {term.description[:150]}...")
    print(f"   Translatable: {term.translatable}")
    print(f"   Tags: {term.get_tags()}")
print()

# Example 2: Get translations
print("2. Get translations for 'charging cable':")
term = glossary.get_term("charging cable")
if term:
    print(f"   Danish (da): {term.translate('da')}")
    print(f"   German (de): {term.translate('de')}")
    print(f"   French (fr): {term.translate('fr')}")
    print(f"   Spanish (es): {term.translate('es')}")
print()

# Example 3: Quick translate shortcut
print("3. Quick translate:")
translation = glossary.translate("charge key", "da")
print(f"   'charge key' in Danish: {translation}")
print()

# Example 4: Search for terms
print("4. Search for terms containing 'power':")
results = glossary.search("power")
print(f"   Found {len(results)} results:")
for result in results[:5]:
    print(f"   - {result.term}")
print()

# Example 5: Get terms by tag
print("5. Get all 'product' terms:")
product_terms = glossary.get_by_tag("product")
print(f"   Found {len(product_terms)} terms:")
for term in product_terms[:5]:
    print(f"   - {term.term}")
print()

# Example 6: Get all available languages
print("6. Available languages:")
languages = glossary.get_languages()
print(f"   {', '.join(languages)}")
print()

# Example 7: Check if term has a tag
print("7. Check tags for 'API':")
term = glossary.get_term("API")
if term:
    print(f"   Has 'product' tag: {term.has_tag('product')}")
    print(f"   Has 'industry' tag: {term.has_tag('industry')}")
print()

# Example 8: Get statistics
print("8. Glossary statistics:")
print(f"   Total terms: {glossary.count()}")
all_terms = glossary.get_all()
translatable_count = sum(1 for t in all_terms if t.translatable)
print(f"   Translatable terms: {translatable_count}")
print()

# Close the connection
glossary.close()

print("Done!")
