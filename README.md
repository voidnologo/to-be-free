# To Be Free

A curated archive of Latter-day Saint teachings on **liberty, agency, the Constitution, and
religious freedom** — addresses, scriptures, and writings by prophets, apostles, and others,
normalized into one consistent format and published as a clean, searchable website.

## Repository layout

| Path | What it is |
|---|---|
| `sources/` | The collection — 258 standardized Markdown documents in 23 numbered sections, each with YAML frontmatter (`title, author, date, tags, source…, commentary`). **Edit here.** |
| `sources/README.md` | Master index of the collection. |
| `sources/_duplicates/` | Quarantined duplicate copies (kept for comparison). |
| `docs/` | The built static website (what GitHub Pages serves). **Generated — do not edit by hand.** |
| `build_site.py` | Site generator. Re-run after editing any markdown. |
| `raw/`, `TBF/` | Original source files the collection was extracted from. |

## Edit → rebuild → preview

```bash
# 1. Edit any document in sources/**/*.md (frontmatter + body)
# 2. Rebuild the site
~/.pyenv/versions/rembg_env/bin/python build_site.py
# 3. Preview locally
python3 -m http.server --directory docs 8099
#    then open http://localhost:8099/
```

The builder needs `pandoc` (Markdown→HTML) and the `trafilatura` Python env already used for the
collection. No other dependencies; the site itself is pure static HTML/CSS/JS (no server required).

## Publish on GitHub Pages

1. Create a public repo and push this project.
2. Repo **Settings → Pages → Build and deployment → Source: “Deploy from a branch.”**
3. Choose **branch `main`, folder `/docs`**, then Save.
4. The site appears at `https://<user>.github.io/<repo>/` within a minute or two.

The `docs/.nojekyll` file is included so Pages serves the build as-is.

## Site features

- Landing page with an introduction grounded in prophetic teaching.
- Sticky **section sidebar** + full **Browse** table of contents.
- **Live search** (client-side, every page) over titles, authors, sections, and tags.
- Tag links, prev/next reading flow, responsive layout (desktop-first, clean on mobile).
- Reading typography set in *Source Serif 4*.
