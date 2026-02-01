# GitHub Pulse Data Scraper

This package provides tools to scrape contribution data from GitHub repositories, similar to what's displayed on the GitHub Pulse page.

## Files Included

1. **github_pulse_scraper.py** - Main API-based scraper (requires GitHub API access)
2. **github_pulse_web_scraper.py** - Alternative web scraping approach using Selenium
3. **utils.py** - Shared utilities for reporting and exports
4. **requirements.txt** - Python dependencies
5. **tests/** - Unit tests for the scraper

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. (Optional but recommended) Get a GitHub Personal Access Token:
   - Go to: https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Select scopes: `public_repo`, `read:user`
   - Copy the token

3. Configure authentication:
   - Create a `.env` file in the root directory:
     ```
     GITHUB_TOKEN=your_token_here
     ```
   - OR provide it via the `--token` command-line argument.

## Method 1: GitHub API (Recommended)

### Usage

The recommended way to run the scraper is using the `./pulse` helper script, which automatically handles the correct Python version:

```bash
# Basic usage with defaults
./pulse

# Custom repository and period
./pulse --owner Altinity --repo clickhouse-operator --days 7

# Export to JSON automatically
./pulse --export report.json
```

Alternatively, you can run the Python script directly:
```bash
python3.9 github_pulse_scraper.py [args]
```

### Features

- **Repository Info**: Basic stats (stars, forks, open issues)
- **Commits**: Total count, contributor breakdown, recent commits
- **Issues**: Opened/closed counts, recent activity
- **Pull Requests**: Opened/merged/closed counts, recent activity
- **CLI Interface**: Full control over parameters via command line
- **JSON Export**: Integrated export for further analysis

## Method 2: Web Scraping (Alternative)

If you don't want to use the API or need an alternative observation tool:

```bash
python3 github_pulse_web_scraper.py --owner Altinity --repo altinityknowledgebase --period weekly
```

### Additional Setup for Web Scraping

- Install Chrome WebDriver (or ensure Chrome is installed, modern Selenium handles driver management automatically in most cases).

## Testing

Run unit tests using `pytest`:

```bash
# Ensure PYTHONPATH is set if running from root
PYTHONPATH=. pytest tests/test_scraper.py
```

## Logging & Errors

The scrapers now use standard Python logging. If you exceed rate limits, the API scraper will warn you and suggest using a token.

## License

This tool is for educational and reporting purposes. Respect GitHub's Terms of Service and rate limits.
