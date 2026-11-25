# Contributing to Sovereign Archive Kit

Thank you for your interest in improving digital preservation tools!

## Core Design Principle
- **Zero External Dependencies:** All features in `archive_kit.py` must rely strictly on the Python 3 standard library (`stdlib`). Do not add third-party `pip` dependencies.

## Ideas for Contributions
- Export adapters for **Substack**, **WordPress XML**, **Blogger**, or **Ghost**.
- Additional verification helpers or HTML-to-Markdown formatting refinements.

## How to Submit
1. Fork the repository and create a feature branch.
2. Run `python3 archive_kit.py seal . && python3 archive_kit.py verify .` to ensure repository integrity.
3. Open a Pull Request describing your changes.
