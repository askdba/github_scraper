# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- Functional listing of up to 3 merged Pull Requests in the Pulse report (if available).
- Deduplication logic for PRs in the report to ensure each PR is only listed once even if it was both opened and merged.
- New test file `tests/test_utils.py` for reporting logic verification.
- Dynamic default filenames for JSON exports in the interactive prompt, incorporating the repository owner, name, and a timestamp.
