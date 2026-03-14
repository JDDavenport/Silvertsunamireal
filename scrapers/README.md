# ACQUISITOR Scrapers

This directory contains Python-based scrapers for data acquisition.

## Directory Structure

```
scrapers/
├── base/
│   └── scraper.py          # Base scraper class with common utilities
├── sources/
│   ├── companies.py        # Company data scrapers
│   ├── realestate.py       # Real estate listings
│   └── patents.py          # IP/patent scrapers
├── pipelines/
│   └── transform.py        # Data transformation utilities
├── storage/
│   └── db.py               # Database insertion helpers
└── requirements.txt        # Python dependencies
```

## Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Run specific scraper
python -m scrapers.sources.companies

# Run all scrapers
python -m scrapers.run_all
```

## Development Guidelines

1. All scrapers must extend `BaseScraper`
2. Implement rate limiting (min 1 second between requests)
3. Cache responses to avoid redundant calls
4. Store raw data before transformation
5. Log all errors with context

## Data Flow

```
Source → Fetch → Cache → Parse → Transform → Validate → Store
```

## Adding New Scrapers

1. Create new file in `sources/` directory
2. Extend `BaseScraper` class
3. Implement `extract()` method
4. Add to `run_all.py` pipeline
