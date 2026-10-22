import json, csv, re, sys, os, unicodedata
from collections import Counter

SP = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SP, "data")
OUT = os.path.join(SP, "dist")
FILES = ["dl", "nlp", "cv", "rl", "molbio", "genomics", "thera", "compstruct"]
REQ = ["id", "title", "authors", "year", "venue", "domain", "field", "subfield", "type", "importance", "summary", "builds_on"]

def slug(s):
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()

entries, seen, log = [], {}, []
for f in FILES:
    p = os.path.join(DATA_DIR, f + ".json")
    if not os.path.exists(p):
        log.append(f"MISSING FILE {f}"); continue
    for e in json.load(open(p)):
        miss = [k for k in REQ if k not in e]
        if miss:
            log.append(f"{f}: {e.get('id')} missing {miss}")
            e.setdefault("builds_on", []); e.setdefault("summary", ""); e.setdefault("venue", ""); e.setdefault("type", "paper"); e.setdefault("importance", 1)
        e["id"] = slug(e["id"]).replace(" ", "")
        e["builds_on"] = [slug(x) for x in e.get("builds_on", [])]
        e["year"] = int(e["year"]); e["importance"] = int(e["importance"])
        if e["id"] in seen:
            other = seen[e["id"]]
            other["builds_on"] = list(dict.fromkeys(other["builds_on"] + e["builds_on"]))
            log.append(f"DUP {e['id']} ({f}) merged into {other['field']}")
            continue
        seen[e["id"]] = e; e["_file"] = f; entries.append(e)

# merge same work filed under different ids (same normalized title, years within 1)
alias = {}
def tkey(t): return re.sub(r"[^a-z0-9]", "", slug(t))[:60]
by_title = {}
for e in list(entries):
    k = tkey(e["title"])
    o = by_title.get(k)
    if o and abs(o["year"] - e["year"]) <= 1:
        alias[e["id"]] = o["id"]
        o["builds_on"] = list(dict.fromkeys(o["builds_on"] + e["builds_on"]))
        for f in ("doi", "arxiv"):
            if f in e and f not in o: o[f] = e[f]
        entries.remove(e); del seen[e["id"]]
        log.append(f"TITLE-DUP {e['id']} -> {o['id']}")
    else:
        by_title[k] = e
for e in entries:
    e["builds_on"] = [alias.get(b, b) for b in e["builds_on"]]

# load optional labels (short names) and fixes
lab_p = os.path.join(DATA_DIR, "labels.json")
labels = json.load(open(lab_p)) if os.path.exists(lab_p) else {}
ids = set(seen)
prefix_index = {}
for i in ids:
    m = re.match(r"([a-z]+?)(\d{4})", i)
    if m: prefix_index.setdefault(m.group(0), []).append(i)

dropped, remapped, future = [], [], []
for e in entries:
    if e["id"] in labels: e["label"] = labels[e["id"]]
    out = []
    for b in e["builds_on"]:
        t = b
        if t not in ids:
            m = re.match(r"([a-z]+?)(\d{4})", t)
            cands = prefix_index.get(m.group(0), []) if m else []
            if len(cands) == 1:
                remapped.append((e["id"], b, cands[0])); t = cands[0]
            else:
                dropped.append((e["id"], b)); continue
        if t == e["id"]: continue
        if seen[t]["year"] > e["year"] + 1:
            future.append((e["id"], t)); continue
        out.append(t)
    e["builds_on"] = list(dict.fromkeys(out))

for e in entries: e.pop("_file", None)

# ---------- radial network layout: radius = time (old at centre), sector = field, springs = lineage ----------
import math
import numpy as np
SECTOR_ORDER = ["Deep Learning Foundations", "Natural Language Processing", "Computer Vision", "Reinforcement Learning",
                "Molecular Biology & Genetic Engineering", "Therapeutics & Medical Biotech", "Genomics & Sequencing",
                "Computational & Structural Biology"]
SEG = [(1790, 1940, 2.2), (1940, 1975, 7), (1975, 2005, 15), (2005, 2012, 30), (2012, 2027, 62)]
def tscale(y):
    x = 0.0
    for a, b, p in SEG:
        if y <= a: break
        x += (min(y, b) - a) * p
    return x
TMAX = tscale(2027)
import bisect
_YEARS = []
def radius(y):
    # equal-area rings: radius ~ sqrt(share of works published before y), so density is even across eras
    lo, hi = bisect.bisect_left(_YEARS, y), bisect.bisect_right(_YEARS, y)
    return 80 + 920 * math.sqrt((lo + 0.5 * (hi - lo)) / len(_YEARS))

def compute_layout(entries, iters=450, seed=7):
    _YEARS[:] = sorted(e["year"] for e in entries)
    rng = np.random.default_rng(seed)
    n = len(entries); idx = {e["id"]: i for i, e in enumerate(entries)}
    nsec = len(SECTOR_ORDER); sw = 2 * math.pi / nsec
    sec = np.array([SECTOR_ORDER.index(e["field"]) if e["field"] in SECTOR_ORDER else 0 for e in entries])
    center = -math.pi / 2 + (sec + 0.5) * sw
    rt = np.array([radius(e["year"]) for e in entries])
    ang = center + rng.uniform(-0.42, 0.42, n) * sw
    pos = np.stack([rt * np.cos(ang), rt * np.sin(ang)], 1)
    E = np.array([(idx[b], idx[e["id"]]) for e in entries for b in e["builds_on"] if b in idx], dtype=int)
    for it in range(iters):
        cool = 1 - it / iters
        d = pos[:, None, :] - pos[None, :, :]
        d2 = (d ** 2).sum(-1) + 25.0
        rep = (d * (1.0 / d2)[..., None]).sum(1) * 900.0
        f = rep
        if len(E):
            v = pos[E[:, 1]] - pos[E[:, 0]]; L = np.sqrt((v ** 2).sum(1)) + 1e-6
            fs = (0.035 * (L - 40.0) / L)[:, None] * v
            np.add.at(f, E[:, 0], fs); np.add.at(f, E[:, 1], -fs)
        r = np.sqrt((pos ** 2).sum(1)) + 1e-6; u = pos / r[:, None]
        f += (0.5 * (rt - r))[:, None] * u
        a = np.arctan2(pos[:, 1], pos[:, 0])
        da = (a - center + math.pi) % (2 * math.pi) - math.pi
        over = np.clip(np.abs(da) - 0.40 * sw, 0, None) * np.sign(da)
        tang = np.stack([-u[:, 1], u[:, 0]], 1)
        f += (-(0.9 * over * r) - 0.02 * da * r)[:, None] * tang
        step = np.sqrt((f ** 2).sum(1)) + 1e-9
        maxs = 2 + 28 * cool
        pos += f * (np.minimum(step, maxs) / step)[:, None]
        r = np.sqrt((pos ** 2).sum(1)) + 1e-6
        pos *= (np.clip(r, rt * 0.96, rt * 1.04) / r)[:, None]
    for e, (x, y) in zip(entries, pos):
        e["gx"] = round(float(x), 1); e["gy"] = round(float(y), 1)

compute_layout(entries)

entries.sort(key=lambda e: (e["year"], e["field"], e["title"]))
os.makedirs(OUT, exist_ok=True)
json.dump(entries, open(os.path.join(OUT, "atlas.json"), "w"), ensure_ascii=False, indent=1)

with open(os.path.join(OUT, "atlas.csv"), "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["id", "year", "title", "authors", "venue", "domain", "field", "subfield", "type", "importance", "doi", "arxiv", "builds_on", "summary"])
    for e in entries:
        w.writerow([e["id"], e["year"], e["title"], e["authors"], e["venue"], e["domain"], e["field"], e["subfield"], e["type"], e["importance"], e.get("doi", ""), e.get("arxiv", ""), " ".join(e["builds_on"]), e["summary"]])

def bib(e):
    au = []
    for a in re.split(r",\s*", e["authors"]):
        if not a: continue
        if re.search(r"et al\.?$", a, re.I): au.append("others"); continue
        m = re.match(r"^(.*?)\s+([A-ZÀ-Ý][A-Za-zÀ-ÿ.\-]*)$", a.strip())
        au.append(f"{m.group(1)}, {m.group(2)}" if m else a.strip())
    t = {"book": "book", "paper": "article"}.get(e["type"], "misc")
    f = [f"  title = {{{e['title']}}}", f"  author = {{{' and '.join(au)}}}", f"  year = {{{e['year']}}}"]
    if e["venue"]: f.append(("  publisher" if t == "book" else "  journal" if t == "article" else "  howpublished") + f" = {{{e['venue']}}}")
    if e.get("doi"): f.append(f"  doi = {{{e['doi']}}}")
    if e.get("arxiv"): f.append(f"  eprint = {{{e['arxiv']}}}, archivePrefix = {{arXiv}}")
    return f"@{t}{{{e['id']},\n" + ",\n".join(f) + "\n}"
open(os.path.join(OUT, "atlas.bib"), "w").write("\n\n".join(bib(e) for e in entries) + "\n")

tpl = open(os.path.join(SP, "template.html")).read()
slim = [{k: v for k, v in e.items() if v not in ("", None)} for e in entries]
html = tpl.replace("/*DATA*/[]", json.dumps(slim, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/"))
open(os.path.join(OUT, "atlas.html"), "w").write(html)

edges = sum(len(e["builds_on"]) for e in entries)
indeg = Counter(b for e in entries for b in e["builds_on"])
orphans = [e["id"] for e in entries if not e["builds_on"] and e["id"] not in indeg]
print(f"entries={len(entries)} edges={edges} html_kb={len(html)//1024}")
print("per field:", Counter(e["field"] for e in entries))
print("by importance:", Counter(e["importance"] for e in entries))
print(f"remapped={len(remapped)} dropped={len(dropped)} future={len(future)} isolated={len(orphans)}")
rep = {"log": log, "remapped": remapped, "dropped": dropped, "future": future, "isolated": orphans,
       "bad_subfields": [(e["id"], e["field"], e["subfield"]) for e in entries if False]}
json.dump(rep, open(os.path.join(OUT, "build_report.json"), "w"), indent=1)
for l in log: print(" ", l)
