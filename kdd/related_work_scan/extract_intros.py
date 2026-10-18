"""Download the PDFs of selected candidates into pdfs/ (untrusted data) and extract abstract + introduction text.
Usage: extract_intros.py selected.json  -> intros.json
"""
import json, os, re, sys, time, urllib.request
from pypdf import PdfReader

sel = json.load(open(sys.argv[1]))
os.makedirs("pdfs", exist_ok=True)
out = {}
if os.path.exists("intros.json"):
    out = json.load(open("intros.json"))

def intro_text(path):
    try:
        reader = PdfReader(path)
    except Exception as e:  # noqa
        return "", f"unreadable: {e}"
    pages = []
    for p in reader.pages[:4]:
        try:
            pages.append(p.extract_text() or "")
        except Exception:  # noqa
            pages.append("")
    text = re.sub(r"[ \t]+", " ", "\n".join(pages))
    text = re.sub(r"-\n(?=[a-z])", "", text)  # de-hyphenate line breaks
    m = re.search(r"\n\s*(?:1\.?|I\.?)?\s*Introduction\s*\n", text, re.I)
    start = m.start() if m else 0
    body = text[start:]
    # stop at section 2 or after ~1400 words
    m2 = re.search(r"\n\s*2\.?\s+[A-Z][A-Za-z ,\-]{3,60}\n", body)
    if m2 and m2.start() > 800:
        body = body[:m2.start()]
    words = body.split()
    return " ".join(words[:1400]), ("ok" if m else "no-intro-heading")

for i, r in enumerate(sel):
    key = r["url"]
    if key in out and out[key].get("status", "").startswith("ok"):
        continue
    fn = os.path.join("pdfs", re.sub(r"[^A-Za-z0-9]+", "_", key)[-80:] + ".pdf")
    if not os.path.exists(fn):
        for attempt in range(3):
            try:
                req = urllib.request.Request(r["pdf"], headers={"User-Agent": "Mozilla/5.0 lit-scan"})
                with urllib.request.urlopen(req, timeout=90) as resp, open(fn, "wb") as f:
                    f.write(resp.read())
                break
            except Exception as e:  # noqa
                err = str(e)
                time.sleep(3 + 3 * attempt)
        else:
            out[key] = {"status": "download-failed: " + err, "intro": ""}
            json.dump(out, open("intros.json", "w"), indent=1)
            continue
    text, status = intro_text(fn)
    out[key] = {"status": status, "intro": text, "title": r["title"]}
    json.dump(out, open("intros.json", "w"), indent=1)
    print(i, status, r["title"][:70], file=sys.stderr)
    time.sleep(1.0)
