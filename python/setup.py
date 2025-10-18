from setuptools import setup, find_packages

setup(
    name="monta-glossary",
    version="0.1.0",
    author="Monta",
    description="Monta terminology glossary with translations",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "openpyxl>=3.1.0",
    ],
)
