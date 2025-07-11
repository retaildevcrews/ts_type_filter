#!/usr/bin/env python3
"""
Setup script for ts_type_filter package.
This file provides compatibility with pip installation from git repositories.
"""

from setuptools import setup, find_packages

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ts_type_filter",
    version="0.1.0",
    author="Michael Hopcroft",
    author_email="mhop@microsoft.com",
    description="Experimental library to assist in preparing Typescript type definitions for use in Large Language Model (LLM) prompts.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MikeHopcroft/ts_type_filter",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.12",
    install_requires=[
        "nltk>=3.9.1",
        "rich>=13.9.4",
        "tiktoken>=0.9.0",
        "gotaglio @ git+https://github.com/MikeHopcroft/gotaglio",
        "lark>=1.2.2",
        "pydantic>=2.11.1",
    ],
    extras_require={
        "dev": [
            "ipykernel>=6.29.5",
            "pytest>=8.3.4",
        ],
    },
)
