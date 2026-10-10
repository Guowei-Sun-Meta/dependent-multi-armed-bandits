"""Freeze source evidence and expand current technical papers into appendices.

Original documents are read only. All labels/citations are namespaced and input
tables are expanded; figures are copied locally. This preserves full derivations
without requiring files outside the new paper directory to compile the PDF.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
TRACKS = ["spatiotemporal_bandits", "alignment_paper", "predictive_ar1", "two_arm_ar1", "ar_p_bandits"]
records, references = {}, {}
INPUT = re.compile(r"\\(?:inputtable|input)\b\s*(?:\{([^}]+)\}|([^\s%\\{}]+))")


def record(path):
    key = str(path.relative_to(REPO))
    records[key] = {"sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "bytes": path.stat().st_size}


def expand(path, directory):
    record(path)
    source = path.read_text()
    def nested(match):
        p = directory / (match.group(1) or match.group(2))
        if not p.suffix:
            p = p.with_suffix(".tex")
        return "\n"+expand(p, directory)+"\n"
    return INPUT.sub(nested, source)


def appendix(track):
    directory = REPO / "research" / track
    original = expand(directory / "manuscript.tex", directory)
    body = original[original.index("\\section{"):original.index("\\begin{thebibliography}")]
    bibliography = original[original.index("\\begin{thebibliography}"):original.index("\\end{thebibliography}")]
    mapping = {}
    for item in re.finditer(r"\\bibitem\{([^}]+)\}([\s\S]*?)(?=\\bibitem|\Z)", bibliography):
        key, text = item.groups()
        urls = re.findall(r"\\(?:url|href)\{([^}]+)\}", text)
        identity = urls[0].rstrip("/.") if urls else re.sub(r"\s+", " ", text.strip())
        if identity not in references:
            references[identity] = (f"collected{len(references)+1}", text.strip())
        mapping[key] = references[identity][0]
    body = re.sub(r"\\cite\{([^}]+)\}", lambda m: "\\cite{"+",".join(mapping[k.strip()] for k in m.group(1).split(","))+"}", body)
    body = re.sub(r"\\(label|eqref|ref|pageref)\{([^}]+)\}", lambda m: "\\"+m.group(1)+"{"+track+":"+m.group(2)+"}", body)
    def graphic(match):
        args, relative = match.groups()
        path = directory / relative
        if not path.suffix:
            path = path.with_suffix(".pdf")
        record(path)
        dest = ROOT / "figures" / (track+"_"+path.name)
        dest.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(path, dest)
        return "\\includegraphics"+(args or "")+"{figures/"+dest.name+"}"
    body = re.sub(r"\\includegraphics(\[[^\]]*\])?\{([^}]+)\}", graphic, body)
    body = re.sub(r"\{(results/[^}]+\.csv)\}", lambda m: "{evidence/"+track+"/"+m.group(1)+"}", body)
    # A collected appendix must not reset the enclosing paper's counters.
    body = re.sub(r"\\appendix\b", "", body)
    body = re.sub(r"\\(subsubsection|subsection|section)(\*?)\{", lambda m: "\\"+{"section":"subsection", "subsection":"subsubsection", "subsubsection":"paragraph"}[m.group(1)]+m.group(2)+"{", body)
    path = ROOT / "appendices" / (track+".tex")
    path.parent.mkdir(parents=True, exist_ok=True); path.write_text(body)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--appendices-only", action="store_true", help="Refresh technical appendices without replacing the existing evidence snapshot")
    args = parser.parse_args()
    if args.appendices_only:
        records.update(json.loads((ROOT / "evidence_manifest.json").read_text()))
    for track in TRACKS:
        appendix(track)
    (ROOT / "collected_references.tex").write_text("\n\n".join("\\bibitem{"+key+"}"+text for key, text in references.values())+"\n")
    if args.appendices_only:
        (ROOT / "evidence_manifest.json").write_text(json.dumps(records, indent=2)+"\n")
        print(f"Refreshed five appendices and {len(references)} distinct references; retained existing evidence snapshot")
        return
    # Freeze all current research notes and compact result artifacts, including
    # negative findings and alternative models. Large raw runs remain referenced.
    for directory in (REPO / "research").iterdir():
        if not directory.is_dir() or directory.name in (ROOT.name, "claude_opus_10_09"):
            continue
        for path in directory.rglob("*"):
            if path.is_file() and path.suffix in (".md", ".csv", ".json", ".tex"):
                if path.stat().st_size > 1500000:
                    record(path); continue
                destination = ROOT / "evidence" / path.relative_to(REPO / "research")
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, destination); record(path)
    for path in (REPO / "research").glob("*.md"):
        destination = ROOT / "evidence/notes" / path.name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, destination); record(path)
    for path in (REPO / "experiments").rglob("*.py"):
        if path.stat().st_size < 300000:
            destination = ROOT / "evidence/code" / path.relative_to(REPO / "experiments")
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, destination); record(path)
    (ROOT / "evidence_manifest.json").write_text(json.dumps(records, indent=2)+"\n")
    print(f"Collected {len(records)} source/result fingerprints, {len(references)} distinct references and five technical appendices")


if __name__ == "__main__":
    main()
