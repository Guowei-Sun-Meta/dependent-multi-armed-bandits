"""Build kdd/related_work_abstracts.md from selected.json and notes.py."""
import json, re, sys, time, urllib.request, urllib.parse, xml.etree.ElementTree as ET
exec(open('notes.py').read())
sel = json.load(open('selected.json'))
order = sorted(range(len(sel)), key=lambda i: (sel[i]['venue'], sel[i]['title']))
NS = {"a": "http://www.w3.org/2005/Atom"}

def venue_label(v):
    v = v.replace(' Poster', '').replace(' poster', '').replace(' Spotlight', '').replace(' spotlight', '')
    v = v.replace(' Oral', '').replace(' oral', '').replace(' regular', '').replace(' Conference', '')
    m = re.search(r'Accepted (?:at|to) (NeurIPS \d{4})', v)
    if m: return m.group(1) + " (accepted; arXiv version)"
    return v.strip()

def year(v):
    m = re.search(r'(20\d\d)', v); return int(m.group(1)) if m else 0

def arxiv_authors(aid):
    try:
        root = ET.fromstring(urllib.request.urlopen(aid.replace('/abs/', '/api/query?id_list=').replace('http://arxiv.org', 'https://export.arxiv.org').split('v')[0] if False else
            "https://export.arxiv.org/api/query?" + urllib.parse.urlencode({"id_list": re.sub(r'v\d+$', '', aid.split('/abs/')[-1])}), timeout=60).read())
        e = root.find('a:entry', NS)
        return [a.find('a:name', NS).text for a in e.findall('a:author', NS)]
    except Exception as ex:  # noqa
        print('author fetch failed', aid, ex, file=sys.stderr); return []

entries = []
for n_, i in enumerate(order):
    if n_ not in N: continue
    r = sel[i]; theme, core, note = N[n_]
    authors = r['authors']
    aid = r.get('arxiv') or (re.sub(r'/pdf/', '/abs/', r['pdf']) if 'arxiv.org/pdf' in r['pdf'] else None)
    if not authors and aid:
        authors = arxiv_authors(aid); time.sleep(3.1)
    entries.append(dict(n=n_, theme=theme, core=core, note=note, title=r['title'], authors=authors,
                        venue=venue_label(r['venue']), year=year(r['venue']), url=r['url'], pdf=r['pdf'],
                        abstract=re.sub(r'\s*\n\s*', ' ', r['abstract']).strip(), no_intro=(n_ in NO_INTRO)))

entries.sort(key=lambda e: (e['theme'], -e['year'], e['venue'], e['title']))
for k, e in enumerate(entries, 1):
    e['id'] = f"P{k:02d}"
def id_of(t):
    return next(e['id'] for e in entries if e['title'].lower().startswith(t.lower()))

out = []
w = out.append
w("# Related Work: Indexed Abstracts from ICLR, ICML, NeurIPS, COLT, AISTATS and KDD, 2024–2026\n")
w("18 October 2026. Compiled for the KDD 2027 paper on correlated arms ([kdd/README.md](README.md)). The scan covers the six venues over the last three years (NeurIPS 2023 to the NeurIPS 2026 accepted list) and keeps the papers that bear on the paper's three questions: structure between arms, dependence over time, and confidence under adaptive sampling.\n")
w("## How the scan was done\n")
w("- **Harvest.** Every accepted paper of NeurIPS 2023–2025, ICLR 2024–2026, ICML 2024–2026 and AISTATS 2025–2026 matching 13 search terms (bandit, confidence sequence, anytime-valid, restless, autoregressive, non-stationary, correlated arms, graph-structured, spectral bandit, time-uniform, sequential testing, Markov reward) was pulled from the OpenReview API; AISTATS 2024, COLT 2024–2026 and ICML 2024–2026 from the PMLR proceedings pages (titles matched against a broader keyword list, abstracts fetched); KDD 2024–2026 from OpenAlex, with arXiv comment fields as a cross-check; NeurIPS 2026 accepted papers from arXiv. 13,039 records, 11,597 unique titles.")
w("- **Screening.** Titles and abstracts were scored by topic buckets (structure, temporal, inference, exposure, spatiotemporal) and screened by hand to 99 candidates.")
w("- **Reading.** For each candidate the PDF was downloaded (arXiv or PMLR; OpenReview and the ACM Digital Library block automated downloads) and the abstract and introduction were read. 77 papers were kept. For " + str(len([e for e in entries if e['no_intro']])) + " of them the PDF was not reachable from this machine, so only the abstract was read; they are marked.")
w("- **Abstracts are verbatim** from OpenReview, PMLR, arXiv or OpenAlex. **Relevance notes are ours**, keyed to the theory labels in [research/correlated_arms](../research/correlated_arms/README.md) (A1–A4, N1, B1–B3, S5, S6) and the verdicts in [experiments/report](../experiments/report/README.md). Papers marked **core** should be cited in the KDD draft; the others are adjacent.")
w("- Scripts to repeat the scan are in [related_work_scan/](related_work_scan/README.md).\n")

w("## What the scan shows\n")
w("1. **Nobody certifies pooling under temporal dependence.** The structured-arm papers (theme A) pool along graphs, clusters or hierarchies and either assume the structure is exact (" + id_of('Context-lumpable') + ", " + id_of('Blocked Collaborative') + ", " + id_of('Near Optimal Best Arm') + ") or tolerate a deviation that enters regret linearly (" + id_of('Online Clustering of Bandits with Misspecified') + "); none checks validity from data, and none combines pooling with autocorrelated rewards. The closest theory, " + id_of('Leveraging Similarities') + " (COLT 2026), uses known within-group ranges, which are our ε_c without the certificate; " + id_of('Laplacian Kernelized') + " (ICLR 2026) is the kernelized Gang-of-Bandits and the natural uncertified baseline to add to Setting B.")
w("2. **Temporal dependence is modelled as drift, change points or action-induced memory, not as exogenous persistence with a confidence guarantee for fixed means.** The AR papers (Autoregressive Bandits, AR temporal dependency) and the latent-dynamics papers (explore-then-commit, block optimism, latent-state bandits at KDD 2026) bound regret against dynamic benchmarks; the only confidence sequences for fixed means under dependence are the state-space A/B paper (AISTATS 2026, one two-arm test, known AR(1)) and the Markovian sequential test (ICML 2026, finite-state chains).")
w("3. **The anytime-valid literature has moved to tighter multivariate and likelihood-ratio sequences.** Martingale-mixture, dual-program, likelihood-ratio and condition-number bounds (NeurIPS 2023 oral, AISTATS 2025, NeurIPS 2024, COLT 2025) are the tools for shrinking B1's √(N log T) width, which is the paper's top open problem.")
w("4. **The A/B-testing papers assume independent daily data.** YEAST, counting-process e-processes, horizon-aware betting and design-based delayed-outcome sequences all take iid or exchangeable increments; the carryover and non-stationarity papers (robust sequential design, state-space A/B, Experimenting Fast and Slow, False Positives at KDD 2024) establish that the assumption fails in practice without measuring the inflation. That is the opening for experiment proposal 1 and for B2.")
w("5. **Network interference is the other 'spatial' dependence.** Five papers in 2024–2026 put a graph between units whose treatments interfere; one (NeurIPS 2025) adds an anytime-valid sequence. They are a distinct channel from ours (dependence through treatments, not through reward shocks) and should be cited to delimit the claim.\n")

w("## Index\n")
w("| ID | Year | Venue | Title | Theme | Core |\n| --- | ---: | --- | --- | --- | :---: |")
for e in entries:
    w(f"| [{e['id']}](#{e['id'].lower()}) | {e['year']} | {e['venue']} | {e['title']} | {e['theme']} | {'yes' if e['core'] else ''} |")
w("")
w("**Themes.**\n")
for k, v in THEMES.items():
    w(f"- **{k}.** {v}")
w("")
w("**By venue.** " + ", ".join(f"{v}: {c}" for v, c in sorted(__import__('collections').Counter(re.sub(r' \(.*', '', e['venue']).split(' ')[0] for e in entries).items())) + ".\n")
w("**Where each theme enters the draft.**\n")
w("| Draft section | Themes | Core papers |\n| --- | --- | --- |")
for sec, th in [("Spatial dependence (related work)", "A, E"), ("Temporal dependence (related work)", "B"), ("Confidence and evaluation on logged data (related work)", "C, D"), ("Experiment proposal 1: sequential stopping in online experiments", "C, D"), ("Open problem: tighter certificate", "C")]:
    ids = ", ".join(e['id'] for e in entries if e['theme'] in th.split(', ') and e['core'])
    w(f"| {sec} | {th} | {ids} |")
w("")

cur = None
for e in entries:
    if e['theme'] != cur:
        cur = e['theme']; w(f"\n## Theme {cur}. {THEMES[cur]}\n")
    w(f"### {e['id']}\n")
    auth = ", ".join(e['authors']) if e['authors'] else "(authors on the linked page)"
    w(f"**{e['title']}**  \n{auth}. *{e['venue']}.* [Page]({e['url']}) · [PDF]({e['pdf']})" + ("  \n*Abstract only: the PDF was not reachable from this machine, so the introduction was not read.*" if e['no_intro'] else "") + "\n")
    w("> " + e['abstract'] + "\n")
    w(("**Relevance (core).** " if e['core'] else "**Relevance.** ") + e['note'] + "\n")

open('related_work_abstracts.md', 'w').write("\n".join(out))
print(len(entries), 'entries written', file=sys.stderr)
