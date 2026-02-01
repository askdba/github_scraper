# Quick Start Guide - GitHub Pulse Scraper

## Fastest Path to Results (2 minutes)

### 1. Install dependencies:
```bash
pip install -r requirements.txt
```

### 2. (Optional) Set up authentication:
Create a `.env` file for higher rate limits:
```
GITHUB_TOKEN=your_token_here
```

### 3. Run the scraper:
```bash
# Fast run (uses the pulse helper script)
./pulse

# Specify a different repository
./pulse --owner Altinity --repo clickhouse-operator --days 180
```

## Options & Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--owner` | Repository owner | Altinity |
| `--repo`  | Repository name | altinityknowledgebase |
| `--days`  | Period in days | 30 |
| `--token` | GitHub API Token | (from .env) |
| `--export`| JSON filename | (prompted) |

## Example CLI Usage

```bash
# Weekly report for a specific repo
python3 github_pulse_scraper.py --owner Altinity --repo clickhouse-operator --days 7

# Export data directly to JSON
python3 github_pulse_scraper.py --export clickhouse_pulse.json
```

## Web Scraping Alternative

If API access is not preferred:
```bash
python3 github_pulse_web_scraper.py --owner Altinity --repo altinityknowledgebase --period daily
```

## Troubleshooting

- **Rate limit exceeded**: Ensure `GITHUB_TOKEN` is set in `.env` or passed via `--token`.
- **ImportError**: Run `pip install -r requirements.txt`.
- **ModuleNotFoundError (tests)**: Use `PYTHONPATH=. pytest`.
