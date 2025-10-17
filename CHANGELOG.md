# Changelog

## [Unreleased]

### Added
- Added whatsapp-web.js bridge with asyncio support and multi-group Node scraper output alignment.
- Introduced CLI backend selection and failover handling in `run_optimal_scraper.py`.

### Changed
- Normalized whatsapp-web.js scraper output to structured JSON for easier parsing.
- Extended configuration dataclasses with webjs backend settings and max message controls.

### Docs
- Updated README and integration guides for dual backend workflows and npm usage.
- Documented whatsapp-web.js setup commands and new CLI flags.

### Tests
- Added unit coverage for whatsapp-web.js bridge success and failure scenarios.
- Updated multi-group configuration tests for new dataclass fields.
