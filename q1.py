# q1.py — Q1 YouTube Metadata Filter (faithful to the fixed grader spec)
import json, subprocess, sys

PARAM_FILE = "q-youtube-metadata-filter-server.json"
try:
    P = json.load(open(PARAM_FILE, encoding="utf-8"))
except FileNotFoundError:
    print(f"Error: {PARAM_FILE} not found. Download it from the Q1 card into this folder.")
    sys.exit(1)

req  = [w.lower() for w in P["required_words"]]
forb = [w.lower() for w in P["forbidden_words"]]
lo, hi, limit = P["min_duration_seconds"], P["max_duration_seconds"], P["limit"]

kept = []
for url in P["source_urls"]:
    try:
        out = subprocess.check_output(
            ["yt-dlp", "--dump-json", "--no-warnings", url],
            stderr=subprocess.DEVNULL, text=True, encoding="utf-8")
        m = json.loads(out)
    except Exception as e:
        print(f"skip {url}: {e}", file=sys.stderr)          # deleted/private -> skip
        continue

    # Rule 2 — duration in range (inclusive).
    dur = m.get("duration") or 0
    if not (lo <= dur <= hi):
        continue

    # Rules 3 & 4 — FULL title + FULL description, case-insensitive, substring match.
    blob = ((m.get("title") or "") + " " + (m.get("description") or "")).lower()
    if not all(w in blob for w in req):     # ALL required words present
        continue
    if any(w in blob for w in forb):        # ANY forbidden word -> exclude
        continue

    kept.append({"id": m.get("id") or "", "url": url,
                 "upload_date": m.get("upload_date") or "00000000"})

# Rule 5 — upload_date DESC, ties by id ASC (case-insensitive, like JS localeCompare).
# Python sort is stable: sort by the tie-break key first, then the primary key.
kept.sort(key=lambda v: v["id"].lower())
kept.sort(key=lambda v: v["upload_date"], reverse=True)

# Rule 6 — top `limit`.
print(json.dumps({"urls": [v["url"] for v in kept[:limit]]}, indent=2))