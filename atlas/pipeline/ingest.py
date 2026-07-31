#!/usr/bin/env python3
"""
Agentic Atlas - content ingestion pipeline.

Given a curated list of reference links (pipeline/sources.yaml), this script:

  1. DIFFS   the sources against pipeline/registry.json using content hashes,
             ETags/Last-Modified, and declared versions - skipping anything
             already processed.
  2. FETCHES new or changed pages (conditional GET, robots.txt-aware) and caches
             a snapshot under pipeline/cache/.
  3. EXTRACTS the readable main content and title.
  4. PLANS   where each source belongs (section, level, tags) and an outline.
  5. DRAFTS  a 5–15 minute Markdown article with a full attribution block.
             Uses the Anthropic API when ANTHROPIC_API_KEY is set; otherwise
             emits a structured outline stub for a human to finish.
  6. INDEXES the corpus into public/search-index.json and updates the registry.

Nothing is auto-published: new files are written as drafts (draft: true,
aiGenerated: true) and land in Git for human review via pull request.

Usage:
  python pipeline/ingest.py                 # full run
  python pipeline/ingest.py --dry-run       # fetch + plan, write nothing
  python pipeline/ingest.py --plan-only     # print plans as JSON, no drafting
  python pipeline/ingest.py --limit 3       # process at most N new sources
  python pipeline/ingest.py --force <url>   # reprocess a specific URL
  python pipeline/ingest.py --force-all     # ignore the registry entirely

Dependencies: see pipeline/requirements.txt. Runs with graceful degradation if
optional libraries (readability, anthropic) are missing.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys
import textwrap
import urllib.robotparser
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# ---- Third-party (required) -------------------------------------------------
try:
    import requests
    import yaml
    from bs4 import BeautifulSoup
except ImportError as exc:  # pragma: no cover
    sys.exit(
        f"Missing required dependency: {exc.name}. "
        "Install with: pip install -r pipeline/requirements.txt"
    )

# ---- Optional ---------------------------------------------------------------
try:
    from readability import Document as ReadabilityDocument  # readability-lxml
except Exception:  # pragma: no cover
    ReadabilityDocument = None

try:
    import anthropic
except Exception:  # pragma: no cover
    anthropic = None

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
CACHE_DIR = HERE / "cache"
PROMPTS = HERE / "prompts"

VALID_SECTIONS = {
    "foundations", "frameworks", "patterns", "production",
    "comparisons", "case-studies", "news", "learning-paths",
}
VALID_LEVELS = {"beginner", "intermediate", "advanced"}


# ============================================================================
# Config & source loading
# ============================================================================
def load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


@dataclass
class Source:
    url: str
    section: str | None = None
    level: str | None = None
    title: str | None = None
    publisher: str | None = None
    license: str | None = None
    tags: list[str] = field(default_factory=list)
    version: int = 1

    @classmethod
    def parse(cls, item: Any) -> "Source":
        if isinstance(item, str):
            return cls(url=item.strip())
        return cls(
            url=item["url"].strip(),
            section=item.get("section"),
            level=item.get("level"),
            title=item.get("title"),
            publisher=item.get("publisher"),
            license=item.get("license"),
            tags=list(item.get("tags", []) or []),
            version=int(item.get("version", 1)),
        )


def load_sources(path: Path) -> list[Source]:
    data = load_yaml(path)
    return [Source.parse(x) for x in data.get("sources", [])]


# ============================================================================
# Registry (processed-state)
# ============================================================================
def load_registry(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"version": 1, "entries": {}}


def save_registry(path: Path, registry: dict) -> None:
    registry["generated_by"] = "pipeline/ingest.py"
    path.write_text(json.dumps(registry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


# ============================================================================
# Fetching & extraction
# ============================================================================
_robots_cache: dict[str, urllib.robotparser.RobotFileParser] = {}


def robots_allows(url: str, cfg: dict) -> bool:
    if not cfg.get("respect_robots", True):
        return True
    from urllib.parse import urlparse
    parts = urlparse(url)
    root = f"{parts.scheme}://{parts.netloc}"
    rp = _robots_cache.get(root)
    if rp is None:
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(f"{root}/robots.txt")
        try:
            rp.read()
        except Exception:
            # If robots.txt can't be read, be permissive but note it.
            rp = None
        _robots_cache[root] = rp
    if rp is None:
        return True
    return rp.can_fetch(cfg.get("user_agent", "*"), url)


@dataclass
class Fetched:
    status: int
    url: str
    html: str = ""
    etag: str | None = None
    last_modified: str | None = None
    not_modified: bool = False


def fetch(source: Source, prev: dict | None, cfg: dict) -> Fetched:
    headers = {"User-Agent": cfg.get("user_agent", "AgenticAtlasBot/0.1")}
    if prev:
        if prev.get("etag"):
            headers["If-None-Match"] = prev["etag"]
        if prev.get("last_modified"):
            headers["If-Modified-Since"] = prev["last_modified"]
    resp = requests.get(
        source.url,
        headers=headers,
        timeout=cfg.get("request_timeout_seconds", 30),
        allow_redirects=True,
    )
    if resp.status_code == 304:
        return Fetched(status=304, url=source.url, not_modified=True)
    resp.raise_for_status()
    return Fetched(
        status=resp.status_code,
        url=resp.url,
        html=resp.text,
        etag=resp.headers.get("ETag"),
        last_modified=resp.headers.get("Last-Modified"),
    )


def extract(html: str, fallback_title: str | None) -> tuple[str, str]:
    """Return (title, plain_text) from raw HTML."""
    title = fallback_title or ""
    text = ""
    if ReadabilityDocument is not None:
        try:
            doc = ReadabilityDocument(html)
            title = title or (doc.short_title() or "").strip()
            summary_html = doc.summary()
            text = BeautifulSoup(summary_html, "html.parser").get_text("\n", strip=True)
        except Exception:
            text = ""
    if not text:
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "form", "noscript"]):
            tag.decompose()
        if not title and soup.title and soup.title.string:
            title = soup.title.string.strip()
        text = soup.get_text("\n", strip=True)
    # Normalize whitespace and cap length fed downstream.
    text = re.sub(r"\n{3,}", "\n\n", text)
    return title.strip(), text[:16000]


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ============================================================================
# Classification (used when a source lacks explicit overrides)
# ============================================================================
def classify(source: Source, title: str, cfg: dict) -> tuple[str, str]:
    rules = cfg.get("classification", {})
    hay = f"{source.url} {title}".lower()

    section = source.section
    if not section:
        section = rules.get("default_section", "foundations")
        for rule in rules.get("rules", []):
            if any(m.lower() in hay for m in rule.get("match", [])):
                section = rule["section"]
                break
    if section not in VALID_SECTIONS:
        section = "foundations"

    level = source.level
    if not level:
        level = rules.get("default_level", "intermediate")
        hints = rules.get("level_hints", {})
        for lvl in ("advanced", "beginner"):
            if any(h.lower() in hay for h in hints.get(lvl, [])):
                level = lvl
                break
    if level not in VALID_LEVELS:
        level = "intermediate"
    return section, level


def slugify(text: str) -> str:
    text = re.sub(r"[^\w\s-]", "", text.lower()).strip()
    text = re.sub(r"[\s_]+", "-", text)
    return re.sub(r"-{2,}", "-", text)[:60].strip("-") or "untitled"


def estimate_minutes(body: str, cfg: dict) -> int:
    wpm = cfg.get("reading_time", {}).get("words_per_minute", 220)
    words = len(body.split())
    lo = cfg.get("reading_time", {}).get("min", 5)
    hi = cfg.get("reading_time", {}).get("max", 15)
    return max(lo, min(hi, round(words / wpm)))


# ============================================================================
# Planning & drafting
# ============================================================================
def read_prompt(name: str) -> str:
    return (PROMPTS / name).read_text(encoding="utf-8")


def anthropic_client() -> Any | None:
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key or anthropic is None:
        return None
    return anthropic.Anthropic(api_key=key)


def plan_article(client, source: Source, title: str, text: str,
                 section: str, level: str, cfg: dict) -> dict:
    """Return a plan dict. Uses the model if available, else a heuristic plan."""
    base = {
        "title": (source.title or title or source.url)[:90],
        "description": f"Summary and analysis of {source.publisher or source.url}.",
        "section": section,
        "level": level,
        "tags": source.tags[:6] or ["agents"],
        "slug": slugify(source.title or title or source.url),
        "outline": [
            "What it is", "Why it matters", "How it works",
            "When to use it", "Tradeoffs & failure modes", "Next",
        ],
        "key_points": [],
    }
    if client is None:
        return base
    try:
        meta = (f"URL: {source.url}\nSuggested section: {section}\n"
                f"Suggested level: {level}\nPublisher: {source.publisher or '-'}\n")
        msg = client.messages.create(
            model=cfg.get("model", "claude-sonnet-4-6"),
            max_tokens=1024,
            system=read_prompt("plan.md"),
            messages=[{"role": "user", "content": f"{meta}\n\nCONTENT:\n{text[:12000]}"}],
        )
        raw = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
        js = re.search(r"\{.*\}", raw, re.DOTALL)
        plan = json.loads(js.group(0)) if js else {}
        # Merge over the safe base; respect explicit source overrides.
        base.update({k: v for k, v in plan.items() if v})
        if source.section:
            base["section"] = source.section
        if source.level:
            base["level"] = source.level
        base["section"] = base["section"] if base["section"] in VALID_SECTIONS else section
        base["level"] = base["level"] if base["level"] in VALID_LEVELS else level
        base["slug"] = slugify(base.get("slug") or base["title"])
        base["tags"] = list(dict.fromkeys((base.get("tags") or []) + source.tags))[:6]
        return base
    except Exception as exc:  # pragma: no cover
        print(f"    ! planning fell back to heuristic ({exc})")
        return base


def draft_body(client, plan: dict, source: Source, text: str, cfg: dict) -> tuple[str, bool]:
    """Return (markdown_body, drafted_by_model)."""
    if client is not None:
        try:
            ctx = (f"PLAN:\n{json.dumps(plan, indent=2)}\n\n"
                   f"SOURCE ({source.publisher or source.url}):\n{text[:12000]}")
            msg = client.messages.create(
                model=cfg.get("model", "claude-sonnet-4-6"),
                max_tokens=cfg.get("max_output_tokens", 4096),
                system=read_prompt("draft.md"),
                messages=[{"role": "user", "content": ctx}],
            )
            body = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text").strip()
            if body:
                return body, True
        except Exception as exc:  # pragma: no cover
            print(f"    ! drafting fell back to outline stub ({exc})")
    return outline_stub(plan, source), False


def outline_stub(plan: dict, source: Source) -> str:
    """A structured, human-completable stub used when no model is available."""
    lines = [
        f"> **Draft stub - needs a human (or a model-enabled run) to complete.**",
        f"> Auto-generated outline from [{source.publisher or source.url}]({source.url}).",
        "",
        plan.get("description", ""),
        "",
    ]
    for point in plan.get("key_points", []):
        lines.append(f"- Key point to cover: {point}")
    if plan.get("key_points"):
        lines.append("")
    for heading in plan.get("outline", []):
        lines.append(f"## {heading}")
        lines.append("")
        lines.append(f"_TODO: summarize and analyze the source for “{heading}”. "
                     "Original prose only - do not copy source text._")
        lines.append("")
    return "\n".join(lines).strip()


# ============================================================================
# Frontmatter & file writing
# ============================================================================
def yaml_list(items: list[str]) -> str:
    return "[" + ", ".join(items) + "]"


def build_frontmatter(plan: dict, source: Source, minutes: int, cfg: dict) -> str:
    today = dt.date.today().isoformat()
    def esc(s: str) -> str:
        return '"' + str(s).replace('"', "'") + '"'

    src_title = source.title or plan.get("title", source.url)
    fm = [
        "---",
        f"title: {esc(plan['title'])}",
        f"description: {esc(plan['description'])}",
        f"level: {plan['level']}",
        f"readingTime: {minutes}",
        # New articles record both dates; an update should preserve `created`.
        f"created: {today}",
        f"updated: {today}",
        "draft: true" if cfg.get("draft_by_default", True) else "draft: false",
        "aiGenerated: true" if cfg.get("mark_ai_generated", True) else "aiGenerated: false",
        f"license: {cfg.get('content_license', 'CC-BY-4.0')}",
        f"tags: {yaml_list(plan.get('tags', []) or ['agents'])}",
    ]
    # Section-specific required fields so the Astro schema validates.
    section = plan["section"]
    if section == "frameworks":
        fm += [
            f"name: {esc(plan['title'])}",
            "category: toolkit",
            "maturity: beta",
            "supportsMcp: false",
            "supportsMultiAgent: false",
        ]
    if section == "case-studies":
        fm.append(f"company: {esc(source.publisher or 'Unknown')}")
    if section == "news":
        fm.append(f"published: {today}")
    fm += [
        "sources:",
        f"  - title: {esc(src_title)}",
        f"    url: {esc(source.url)}",
    ]
    if source.publisher:
        fm.append(f"    publisher: {esc(source.publisher)}")
    if source.license:
        fm.append(f"    license: {esc(source.license)}")
    fm.append(f"    accessed: {esc(today)}")
    fm.append("---")
    return "\n".join(fm)


def write_article(plan: dict, source: Source, body: str, cfg: dict, dry_run: bool) -> Path:
    section = plan["section"]
    content_root = (HERE / cfg.get("content_root", "../src/content")).resolve()
    target_dir = content_root / section
    target = target_dir / f"{plan['slug']}.md"
    minutes = estimate_minutes(body, cfg)
    document = build_frontmatter(plan, source, minutes, cfg) + "\n\n" + body + "\n"
    if not dry_run:
        target_dir.mkdir(parents=True, exist_ok=True)
        target.write_text(document, encoding="utf-8")
    return target


# ============================================================================
# Search index
# ============================================================================
def rebuild_search_index(cfg: dict) -> int:
    """Scan all Markdown content and emit a lightweight JSON search index."""
    content_root = (HERE / cfg.get("content_root", "../src/content")).resolve()
    index = []
    for md in sorted(content_root.rglob("*.md")):
        raw = md.read_text(encoding="utf-8")
        m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.DOTALL)
        if not m:
            continue
        try:
            meta = yaml.safe_load(m.group(1)) or {}
        except Exception:
            continue
        section = md.parent.name
        slug = md.stem
        index.append({
            "title": meta.get("title", slug),
            "description": meta.get("description", ""),
            "section": section,
            "level": meta.get("level", "intermediate"),
            "tags": meta.get("tags", []),
            "url": f"/{section}/{slug}",
            "aiGenerated": bool(meta.get("aiGenerated", False)),
            "draft": bool(meta.get("draft", False)),
        })
    out = REPO / "public" / "search-index.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return len(index)


# ============================================================================
# Main
# ============================================================================
def main() -> int:
    ap = argparse.ArgumentParser(description="Agentic Atlas ingestion pipeline")
    ap.add_argument("--dry-run", action="store_true", help="fetch + plan, write nothing")
    ap.add_argument("--plan-only", action="store_true", help="print plans, no drafting")
    ap.add_argument("--limit", type=int, default=0, help="max new sources to process")
    ap.add_argument("--force", metavar="URL", help="reprocess a specific URL")
    ap.add_argument("--force-all", action="store_true", help="ignore the registry")
    ap.add_argument("--index-only", action="store_true", help="only rebuild search index")
    args = ap.parse_args()

    cfg = load_yaml(HERE / "config.yaml")
    CACHE_DIR.mkdir(exist_ok=True)

    if args.index_only:
        n = rebuild_search_index(cfg)
        print(f"Search index rebuilt: {n} documents.")
        return 0

    sources = load_sources(HERE / "sources.yaml")
    registry = load_registry(HERE / "registry.json")
    entries: dict = registry.setdefault("entries", {})
    client = anthropic_client()
    mode = "Anthropic API" if client else "offline (outline stubs)"
    print(f"Agentic Atlas ingest - {len(sources)} sources - mode: {mode}\n")

    processed = 0
    for source in sources:
        prev = entries.get(source.url)
        forced = args.force_all or (args.force == source.url)

        # Version bump forces reprocessing.
        version_changed = bool(prev and prev.get("version") != source.version)

        if prev and not forced and not version_changed:
            # We still need to fetch to check for content change (conditional GET).
            pass

        if not robots_allows(source.url, cfg):
            print(f"⏭  robots.txt disallows: {source.url}")
            continue

        print(f"→ {source.url}")
        try:
            fetched = fetch(source, None if forced else prev, cfg)
        except Exception as exc:
            print(f"    ✗ fetch failed: {exc}")
            entries.setdefault(source.url, {})["last_error"] = str(exc)
            continue

        if fetched.not_modified and not forced and not version_changed:
            print("    = not modified (304); skipping")
            continue

        title, text = extract(fetched.html, source.title)
        chash = content_hash(text)

        unchanged = (prev and prev.get("content_hash") == chash
                     and not forced and not version_changed)
        if unchanged:
            print("    = content hash unchanged; skipping")
            entries[source.url]["last_checked"] = dt.date.today().isoformat()
            continue

        # Cache the snapshot for provenance/debugging.
        (CACHE_DIR / f"{slugify(source.url)}.txt").write_text(text, encoding="utf-8")

        section, level = classify(source, title, cfg)
        plan = plan_article(client, source, title, text, section, level, cfg)

        if args.plan_only:
            print(json.dumps(plan, indent=2, ensure_ascii=False))
        else:
            body, by_model = draft_body(client, plan, source, text, cfg)
            target = write_article(plan, source, body, cfg, args.dry_run)
            tag = "drafted" if by_model else "stubbed"
            where = "(dry-run, not written)" if args.dry_run else str(target.relative_to(REPO))
            print(f"    ✓ {tag}: {where}")

        if not args.dry_run and not args.plan_only:
            entries[source.url] = {
                "content_hash": chash,
                "etag": fetched.etag,
                "last_modified": fetched.last_modified,
                "version": source.version,
                "section": plan["section"],
                "slug": plan["slug"],
                "title": plan["title"],
                "processed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
                "drafted_by_model": bool(client),
            }
        processed += 1
        if args.limit and processed >= args.limit:
            print(f"\nReached --limit {args.limit}; stopping.")
            break

    if not args.dry_run and not args.plan_only:
        save_registry(HERE / "registry.json", registry)
        n = rebuild_search_index(cfg)
        print(f"\nRegistry updated. Search index: {n} documents.")
    print(f"\nDone. {processed} source(s) newly processed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
