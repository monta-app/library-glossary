# Monta Glossary - Python Package

Python package for accessing Monta's terminology glossary with translations.

## Installation

```bash
pip install -e /path/to/glossary/python
```

## Usage

```python
from monta_glossary import Glossary

# Initialize the glossary
glossary = Glossary()

# Get a term
term = glossary.get_term("charging cable")
print(term.description)
print(term.translate("da"))  # Danish: ladekabel

# Search terms
results = glossary.search("charge")

# Get terms by tag
product_terms = glossary.get_by_tag("product")

# Quick translate
translation = glossary.translate("charge key", "da")

# Get tone of voice guide
tone_of_voice = Glossary.get_tone_of_voice()
print(f"Tone of voice guide: {len(tone_of_voice)} characters")

glossary.close()
```

## Database Location

By default, the package looks for the database at `files/outputs/glossary.sqlite` relative to the project root. You can override this by passing a path to the `Glossary()` constructor.

## Additional Resources

### Tone of Voice Guide

Access Monta's tone of voice playbook:

```python
from monta_glossary import Glossary

tone_of_voice = Glossary.get_tone_of_voice()
if tone_of_voice:
    print(tone_of_voice)
```

This static method returns the full content of Monta's Tone of Voice Playbook, which provides guidance on writing style, brand values, and communication strategies.

## API Reference

See the main [README](../README.md) for full API documentation.
