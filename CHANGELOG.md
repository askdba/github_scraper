# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- Functional listing of merged Pull Requests in the Pulse report.
- Deduplication logic for PRs in the report to ensure each PR is only listed once.
- New test file `tests/test_utils.py` for reporting logic verification.

### Changed
- Replaced the interactive JSON export prompt with an optional `--export` command-line flag. Running `--export` without an argument automatically generates a filename using the repository owner, name, and a timestamp.
- Added default `owner` and `repo` parsing from local git remote if run within a cloned repository.

### Fixed
- Fixed double-counting bugs in PR and Issue totals by correctly checking for unique IDs.
- Added 'Active' counts for issues and PRs to provide better context for New/Merged/Closed status.
- Included all active and merged PRs in the itemized PR list.
- Updated the itemized PR list sorting to `updated_at` (descending) to highlight the most recent activity.
- Standardized all scorecard layout tables to a strict 80-character width for improved visual alignment.