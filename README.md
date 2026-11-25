# Sovereign Archive Kit

[![CI Verification](https://github.com/habilozdemir/sovereign-archive-kit/actions/workflows/ci.yml/badge.svg)](https://github.com/habilozdemir/sovereign-archive-kit/actions/workflows/ci.yml)

**Zero-dependency CLI toolkit and 4-layer preservation protocol to turn Medium, Mastodon, Nostr, and personal essay collections into cryptographically verifiable, permanent digital archives.**

> **[Türkçe Kullanım Kılavuzu (README.tr.md)](README.tr.md)**

Platforms shut down, accounts get suspended, and links rot. **Sovereign Archive Kit** transforms messy platform data exports into clean, human-readable, self-verifying repositories that cost **$0/month** to host forever across independent global archives.

## Key Features

- **Zero External Dependencies:** Built purely with Python 3 standard library (`stdlib`). No `pip install` or fragile third-party packages.
- **Privacy-First Filtering:** Automatically strips unpublished drafts (`draft_*`) from Medium exports and excludes private Direct Messages (`direct`) from Mastodon exports.
- **Cryptographic Integrity (`MANIFEST.sha256`):** Generates deterministic SHA-256 checksums, a **Master SHA-256** fingerprint, and built-in cross-platform verification (`verify`).
- **Human & Machine Readable:** Preserves structured raw exports alongside clean plain-text compilations (`*-readable.txt`) readable for decades.

## Quick Start

```bash
# 1. Convert a Medium export (.zip) into a clean, SHA-256 sealed archive
python3 archive_kit.py medium ~/Downloads/medium-export.zip -o ./medium-archive

# 2. Convert a Mastodon export (.tar.gz or .zip) while filtering out DMs
python3 archive_kit.py mastodon ~/Downloads/archive-mastodon.tar.gz -o ./mastodon-archive

# 3. Convert a Nostr backup (.json) into a verified archive
python3 archive_kit.py nostr ~/Downloads/nostr-events.json -o ./nostr-archive

# 4. Seal any existing folder of PDFs, Markdown essays, or notes
python3 archive_kit.py seal ./my-essays

# 5. Verify archive integrity anytime on macOS, Linux, or Windows
python3 archive_kit.py verify ./my-essays
```

## The 4-Layer Permanence Protocol

1. **GitHub Read-Only Vault:** Push the sealed folder to a public GitHub repository and lock it via **Settings -> Danger Zone -> Archive this repository**. *(Tip: Designate a legacy contact under **Settings -> Account -> Successor settings**).*
2. **Software Heritage:** Submit your repository URL to [Software Heritage Save Code Now](https://archive.softwareheritage.org/save/) for permanent academic preservation.
3. **Internet Archive (Wayback Machine):** Capture the snapshot via [Wayback Machine Save Page Now](https://web.archive.org/save/).
4. **Decentralized Cryptographic Timestamp (Nostr):** Publish the **Master SHA-256** hash of `MANIFEST.sha256` to public Nostr relays as an immutable proof-of-existence.

## Live Production Archives Built With This Standard

- [`quran-digital-archive`](https://://github.com) — Multi-translation Quran text, XML, and vector Mushaf PDF archive
- [`nostr-archive`](https://://github.com) — Signed Nostr events and deduplicated media archive
- [`mastodon-archive`](https://://github.com) — Public Fediverse posts, replies, and media archive
- [`medium-archive`](https://://github.com) — 813 published Medium essays and 168 embedded images
- [`medium-archive-2`](https://://github.com-2) — Secondary Medium publication archive
- [`notes-archive`](https://://github.com) — 119 aphorisms and notes on classical logic and philosophy
- [`mantik.blog`](https://://github.com) — 23 Turkish essays on Aristotelian syllogisms and fallacies
- [`habil-ozdemirin-yazilari`](https://://github.com) — 12 CC-licensed PDF essays on financial literacy and logic

## License

Released under the [MIT License](LICENSE).
