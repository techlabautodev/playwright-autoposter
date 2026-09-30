# Contributing

Thanks for taking the time to improve `playwright-autoposter`.

## What helps most

- Re-check an adapter's selectors against the live site and send a fix when they drift.
- Add a new `SITE` adapter for a site you post to, with a working `title_sel` / `body_sel` / `publish_sel`.
- Keep the tool small: it posts through the real editor, it does not try to be a full CMS.

## Pull requests

1. Open an issue first for anything larger than a selector fix, so we agree on the shape.
2. Keep the minimal example in the README running against the current code.
3. Do not add dependencies beyond `playwright`.

## Style

Plain, honest code. Type hints where they help a reader. No marketing language in the README.
