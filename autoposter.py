"""Browser-driven autoposter for Playwright: publish posts via real site editors.

Each site is described by a small adapter (URL, selectors, optional tag field).
Posts are read from a JSON queue; the poster opens a fresh browser context per
site, types the title and body through the real editor, adds tags, and submits.
The resulting URL is appended to an output ledger for a later verification job.

Usage:
    from autoposter import Autoposter
    poster = Autoposter(headless=False)
    url = poster.publish_one("posts/my-post.json", site="devto")
"""

import argparse
import json
import random
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from playwright.sync_api import sync_playwright


@dataclass
class Site:
    """A minimal per-site adapter. Selectors are the only per-site knowledge."""

    name: str
    new_post_url: str
    title_sel: str
    body_sel: str
    publish_sel: str
    tag_sel: Optional[str] = None


# Bundled adapters. These are starting points, not guarantees: editors ship
# new markup, so selectors drift and must be re-checked against the live page.
SITES = {
    "devto": Site(
        name="devto",
        new_post_url="https://dev.to/new",
        title_sel="textarea#article-form-title",
        body_sel="div.crayons-editor__content textarea",
        publish_sel="button:has-text('Publish')",
        tag_sel="input#tag-input",
    ),
    "hashnode": Site(
        name="hashnode",
        new_post_url="https://hashnode.com/draft",
        title_sel="input[data-testid='editorTitleInput']",
        body_sel="div[data-testid='editorArea']",
        publish_sel="button[data-testid='publishButton']",
    ),
}


def human_pause(lo: float = 0.6, hi: float = 2.4) -> None:
    """A short, human-ish delay between actions. Deliberately not a timer."""
    time.sleep(random.uniform(lo, hi))


class Autoposter:
    """Publish queued posts through a real browser."""

    def __init__(self, headless: bool = True, ledger: Path = Path("published.jsonl")):
        self.headless = headless
        self.ledger = ledger

    def _load_post(self, path: str) -> dict:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)

    def _fill(self, page, selector: str, text: str) -> None:
        page.click(selector)
        human_pause()
        page.keyboard.type(text)

    def publish_one(self, post_path: str, site_name: str, dry_run: bool = False) -> Optional[str]:
        site = SITES[site_name]
        post = self._load_post(post_path)
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=self.headless)
            ctx = browser.new_context()
            page = ctx.new_page()
            page.goto(site.new_post_url)
            self._fill(page, site.title_sel, post["title"])
            self._fill(page, site.body_sel, post["body"])
            if site.tag_sel and post.get("tags"):
                page.click(site.tag_sel)
                human_pause()
                for tag in post["tags"]:
                    page.keyboard.type(tag)
                    page.keyboard.press("Enter")
            if dry_run:
                browser.close()
                return None
            page.click(site.publish_sel)
            page.wait_for_load_state("networkidle")
            url = page.url
            browser.close()
        with open(self.ledger, "a", encoding="utf-8") as fh:
            fh.write(json.dumps({"url": url, "site": site_name, "post": post_path}) + "\n")
        return url


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish one post through a real browser.")
    parser.add_argument("post", help="path to a post JSON file")
    parser.add_argument("--site", default="devto", choices=sorted(SITES))
    parser.add_argument("--dry-run", action="store_true", help="fill nothing, publish nothing")
    args = parser.parse_args()
    poster = Autoposter(headless=True)
    url = poster.publish_one(args.post, args.site, dry_run=args.dry_run)
    print(url if url else "[dry-run] no publish")


if __name__ == "__main__":
    main()
