# Future improvements

## Dependency pinning

There is no `requirements.txt`. The GitHub Actions workflow installs latest versions of `requests`, `pandas`, and `openpyxl` on each run. A breaking change in any of these could silently break the workflow. Consider adding a `requirements.txt` with pinned versions and a periodic update process (e.g. Dependabot).

## Redirect handling

`requests.get` follows redirects by default. A site could redirect `/robots.txt` to an unexpected location. Currently no action is taken as this is standard behaviour and generally desirable, but a future improvement could log when a redirect occurs so it's visible in the output.

Noted in code at `fetch_and_save_robots_txt()`.

## User-agent parsing edge case

The `disallow:` split in `get_user_agents_from_files()` is a workaround for malformed robots.txt files that put `Disallow` on the same line as `User-agent`. This could theoretically strip a legitimate user-agent name containing "disallow:" but that is extremely unlikely in practice.

Noted in code at `get_user_agents_from_files()`.
