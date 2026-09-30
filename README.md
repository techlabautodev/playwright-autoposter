# playwright-autoposter

A Python helper that publishes queued markdown posts to a site by driving the site's real browser editor with Playwright, one human-paced action at a time.

**For whom:** engineers and content pipelines that already run Playwright and need a small, auditable poster for sites without a usable API, instead of a heavyweight publishing SDK.

**Install (copyable):**

```bash
pip install playwright && playwright install chromium
```

## Minimal example

```python
from autoposter import Autoposter

poster = Autoposter(headless=False)

# post.json = {"title": "...", "body": "markdown...", "tags": ["automation"]}
url = poster.publish_one("posts/my-post.json", site="devto")
print(url)  # https://dev.to/...
```

## Why

Most publishing SDKs stop at the API boundary, and most sites worth posting to do not expose an API you are allowed to use. Autoposter instead drives the exact editor a human fills in — click into the field, type through the keyboard, submit — so the site sees the same event stream it sees from a real author. That keeps the poster honest and small: the only per-site knowledge is a handful of selectors, the input is a queue file, and the output is a URL ledger a later job can verify against.

## What works / what doesn't

- Works: title, body and tags through real keyboard events; human-paced pauses between actions; a dry-run mode that fills nothing and publishes nothing; a JSON-lines URL ledger for downstream verification.
- Doesn't: sites behind a login wall need a session (cookies) you provide before calling `publish_one`; selectors drift whenever a site ships a new editor, so each adapter is a starting point to re-check against the live page, not a guarantee.

## License

MIT — see `LICENSE`. Contributions welcome, see `CONTRIBUTING.md`.

