# robots.txt Tracker

A tool that fetches and analyzes `robots.txt` files from a curated list of websites, producing a color-coded Excel spreadsheet that tracks crawler access policies and emerging standards adoption over time.

## What it does  

1. **Fetches** the `robots.txt` file from each website listed in `config.txt` and saves a local copy.
2. **Analyzes** every file for:
   - **Feature detection** -- checks for the presence of newer directives:
     - **CS Support** -- [Cloudflare Content Signals](https://contentsignals.org/) (`Content-signal:`) for expressing AI usage preferences
     - **RSL Support** -- [Really Simple Licensing](https://rslstandard.org/rsl) (`License:`) for machine-readable content licensing
     - **Sitemap** -- Standard [`Sitemap:`](https://developers.google.com/crawling/docs/robots-txt/create-robots-txt) declarations
   - **User-agent access** -- whether each bot found across all files is allowed or blocked from crawling `/`
3. **Outputs** a date-stamped sheet in `robots-analysis.xlsx` with results color-coded green (present/allowed) or red (absent/blocked).

## Project structure

```
robots-txt/
  config.txt               # One URL per line -- the sites to track
  fetch_robots.py           # Main script
  robots-analysis-YYYY.xlsx  # Output spreadsheet, one per year (auto-generated)
  robots_files/             # Downloaded robots.txt files (auto-generated)
  .github/workflows/
    fetch-robots-txt.yml    # GitHub Actions workflow for weekly automation
```

## Usage

### Manual 

```bash
pip install requests pandas openpyxl
python fetch_robots.py
```

### Automated

A GitHub Actions workflow runs every Sunday at midnight UTC. It fetches fresh copies of all `robots.txt` files, regenerates the spreadsheet, and commits the results back to the repo.

The workflow can also be triggered manually via `workflow_dispatch`.

## Configuration

Edit `config.txt` to add or remove websites -- one full URL per line:

```
https://www.google.com
https://www.nytimes.com
https://www.bbc.co.uk
```

## Spreadsheet output

Each run adds a new sheet named with the current date (e.g. `2026-03-01`) to that year's workbook (e.g. `robots-analysis-2026.xlsx`). New sheets are inserted at the front so the most recent data is always the first tab. A new file is created automatically on the first run of each year. The sheet contains:

| Row type | Description |
|---|---|
| **CS Support** | Does the site include a `Content-signal:` directive? |
| **RSL Support** | Does the site include a `License:` directive? |
| **Sitemap** | Does the site include a `Sitemap:` directive? |
| *User-agents* | Is this bot allowed to crawl `/`? One row per bot found across all files. |

Cells are colored green (1 = yes) or red (0 = no). Over time, the workbook accumulates sheets that let you compare how policies change week to week.

You can download the latest spreadsheet directly from the repository without cloning -- just navigate to the `.xlsx` file on GitHub and click the download button.

## Dependencies

- [requests](https://pypi.org/project/requests/) -- HTTP fetching
- [pandas](https://pypi.org/project/pandas/) -- DataFrame construction and Excel writing
- [openpyxl](https://pypi.org/project/openpyxl/) -- Excel styling and sheet manipulation
