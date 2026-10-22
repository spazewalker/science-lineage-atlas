# AI & Biotech Lineage Atlas

An interactive timeline and citation-lineage graph of 863 key works in:

- **AI**: deep learning foundations, natural language processing, computer vision, reinforcement learning
- **Biotech**: molecular biology & genetic engineering, genomics & sequencing, therapeutics & medical biotech, computational & structural biology

It covers 1798 to 2025, with 58 subfields and 1,482 "builds on" links between works. Some links cross between AI and biotech, for example Transformer → AlphaFold 2.

## Using it

Open `dist/atlas.html` in a browser. It is a single self-contained file.

- **Timeline:** one lane per subfield, placed by year. Drag to pan and Ctrl/⌘-scroll to zoom. The strip at the bottom shows how many works were published each year (AI above the line, biotech below); click or drag it to jump to an era.
- **Network:** a radial lineage map. Rings are years, with the oldest work at the centre and each ring band holding a similar share of works. Each field has its own sector, and dots are sized by how many later works build on them directly. Scroll or pinch to zoom; labels appear as you zoom in.
- **Table:** sortable, including by "Built on by". It can copy BibTeX or CSV for the current filter.
- **Selecting a work:** shows its citation, BibTeX, influence (direct and indirect), the work it builds on and the work it led to. Its lineage is highlighted in both graph views.
- **Shortcuts:** `/` opens search and `Esc` clears the selection. Add `#<id>` to the link to open a work, e.g. `atlas.html#vaswani2017attention`.

## Files

| Path | Contents |
|---|---|
| `data/*.json` | Source entries, one file per field (schema in `BRIEF.md`) |
| `data/labels.json` | Short display names used on the timeline |
| `template.html` | The viewer (HTML/CSS/JS, no dependencies) |
| `build.py` | Merges and dedupes the fields, resolves links, computes the network layout (numpy), writes `dist/` |
| `dist/atlas.{html,json,csv,bib}` | Built outputs |

To rebuild after editing data, run `python3 build.py`. It needs numpy and takes about 15 seconds.

## Entry schema

Each entry has these fields: `id`, `title`, `authors`, `year`, `venue`, `domain` (`ai`/`bio`), `field`, `subfield`, `type`, `importance` (3 = landmark, 2 = major, 1 = notable), `summary` and `builds_on` (ids of predecessor works). `doi` and `arxiv` are optional. See `BRIEF.md`.

## Accuracy note

The entries were curated from knowledge of the literature and have **not yet been checked against a bibliographic database**. DOIs and arXiv ids are included only where they could be stated exactly (191 DOIs and 252 arXiv ids). Every entry in the viewer links to Google Scholar and Semantic Scholar so it can be checked. Checking all entries against Semantic Scholar or OpenAlex is a planned next step.
