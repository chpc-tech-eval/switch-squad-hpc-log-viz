"""Export editable poster/slides and PDFs from verified project evidence."""
import html
import json
import os
from pathlib import Path
import subprocess

from playwright.sync_api import sync_playwright
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.util import Inches, Pt
from pypdf import PdfReader

from scripts.project import ROOT

OUT = ROOT / "submission"
ESC = html.escape
INK = "113C42"
GREEN = "14786B"


def journal():
    entries = subprocess.check_output([
        "git", "log", "--reverse", "--no-merges", "main",
        "--format=%h|%aI|%an|%s", "--", "db", "scripts", "tests", "grafana",
        "compose.yaml", "requirements.txt", "requirements-dev.txt", "submission",
    ], cwd=ROOT, text=True).splitlines()
    lines = ["# Switch Squad project journal", "", "Prepared 18 November 2026.", "",
             "## Retrospective repository record", "",
             "Retrospective chronology compiled from Git commit dates, author metadata and "
             "validation records. Meeting attendance and person-hours are not inferred.", "",
             "| Recorded date | Commit | Author | Recorded change |", "|---|---|---|---|"]
    for entry in entries:
        sha, date, author, subject = entry.split("|", 3)
        lines.append(f"| {date[:10]} | {sha} | {author} | {subject.replace('|', '/')} |")
    lines += ["", "## Database loader development — retrospective", "",
              "PR #27 by Jury Tsoka supplied a batched psycopg2 loader and mocked unit tests. "
              "Subsequent changes added required-field and BIGINT validation, conflict detection, "
              "real PostgreSQL integration tests, rollback recovery and full-dataset verification. "
              "The original contributor commits are preserved in repository history.", "",
              "## 16 November 2026 — implementation and validation", "",
              "Retrospective summary of repository changes and recorded validation results. "
              "Test evidence is stored in docs/evidence/.", "",
              "1. Compared the supplied log fields with the project requirements and documented "
              "which metrics the aggregate snapshots can support.",
              "2. Verified Python 3.13 and Linux containers through Docker Desktop on Windows. "
              "Added a Linux tooling container and reproducible setup instructions.",
              "3. Reproduced cleaning: 3,169 files, 917,919 nonblank rows, 903,522 accepted, 12,489 "
              "extra identical duplicates, 937 conflicting timestamps (1,907 variants) and one rejected row.",
              "4. Extended the loader with strict validation, conflict detection and preflight accounting. "
              "Real TimescaleDB tests verified repeat imports and rollback recovery. All 43 tests and "
              "13 subtests passed on Windows and inside the Linux tooling container.",
              "5. Loaded 903,522 accepted rows with zero failures. Reimport inserted zero and skipped "
              "903,522 identical rows. Every row and all 12 fields matched the cleaned CSV; the Linux "
              "runner independently completed that comparison.",
              "6. Implemented SQL analysis and provisioned Grafana. All 36 panel/bucket API checks "
              "passed; the full count was 903,522 and an empty range returned zero. Chrome rendered "
              "the dashboard and passed a real bucket-dropdown click. Actual screenshots were saved.",
              "7. Prepared poster, slide, journal, demo and checklist sources/exports from the saved "
              "evidence. The implementation and materials were merged through PRs #27–30. "
              "Presentation rehearsal and final submission remain outstanding.", "",
              "## Decisions, challenges and lessons", "",
              "- The existing cleaner and schema provided the foundation for the ingestion and dashboard work.",
              "- Identical timestamps require measurement comparison before a reimport can be classified as a duplicate.",
              "- Real transactions expose rollback and constraint behaviour that mocked insert counts cannot establish.",
              "- Aggregate snapshots support occupancy and backlog trends, but not individual waiting times or throughput.",
              "- Unknown timezone, changing capacity, missing data and anomalous percentages limit interpretation.",
              "- Linux containers provide a portable application deployment across Windows and Linux hosts.", "",
              "## Evidence and outstanding requirements", "",
              "Validation records are in docs/evidence/ and findings are in docs/analysis.md. "
              "On 17 November 2026, the mentor accepted the alternative metrics in issue #9 and the Linux-container deployment in issue #12. A separate VirtualBox cluster is not required. "
              "The final format, poster size and submission cutoff require organiser confirmation. "
              "Fresh-checkout reproduction and presentation rehearsal are tracked in "
              "submission/checklist.md.", ""]
    (OUT / "journal.md").write_text("\n".join(lines), encoding="utf-8")


def poster(summary):
    text = f"""<!doctype html><html lang="en"><meta charset="utf-8"><title>Switch Squad poster</title>
<style>
@page {{ size: 594mm 841mm; margin: 0; }}
* {{ box-sizing: border-box; }}
body {{ margin:0; background:#e6eeeb; font-family:Arial,sans-serif; color:#{INK}; }}
.poster {{ width:594mm; height:841mm; padding:24mm; background:#fafcf9; overflow:hidden; }}
.eyebrow {{ letter-spacing:4px; font-size:24pt; font-weight:bold; color:#{GREEN}; }}
h1 {{ font-size:78pt; line-height:1.02; margin:10mm 0 7mm; letter-spacing:-3px; }}
.sub {{ font-size:31pt; line-height:1.3; max-width:510mm; margin:0 0 13mm; }}
.metrics {{ display:grid; grid-template-columns:repeat(3,1fr); border-top:2mm solid #{INK}; border-bottom:.6mm solid #a1b9af; padding:8mm 0; gap:10mm; }}
.value {{ font-size:58pt; font-weight:bold; color:#{GREEN}; }} .label {{ font-size:23pt; margin-top:2mm; }}
.two {{ display:grid; grid-template-columns:1fr 1fr; gap:17mm; margin-top:10mm; }}
h2 {{ font-size:33pt; margin:0 0 5mm; }} p,li {{ font-size:22pt; line-height:1.35; }} p {{ margin:0 0 5mm; }}
ul {{ padding-left:9mm; margin:0; }} li {{ margin-bottom:4mm; }}
.screen {{ width:100%; border:1mm solid #{INK}; border-radius:3mm; }}
.caption {{ font-size:19pt; color:#476264; line-height:1.4; margin-top:4mm; }}
.pipeline {{ width:100%; margin:12mm 0 0; }}
.proof {{ background:#{INK}; color:white; padding:11mm; border-radius:4mm; }}
.proof h2 {{ color:#a9e8cf; }} .proof p {{ font-size:24pt; }}
.foot {{ margin-top:12mm; padding-top:7mm; border-top:.6mm solid #a1b9af; font-size:18pt; line-height:1.5; }}
</style><main class="poster">
<div class="eyebrow">SWITCH SQUAD · SCC 2026 · HISTORICAL HPC DATA</div>
<h1>From cluster logs<br>to evidence.</h1>
<p class="sub">A reproducible pipeline for exploring reported CPU usage, node availability and job backlog—without hiding uncertainty.</p>
<div class="metrics"><div><div class="value">903,522</div><div class="label">accepted cluster snapshots</div></div><div><div class="value">70.97%</div><div class="label">mean reported CPU value</div></div><div><div class="value">2017–25</div><div class="label">historical source coverage</div></div></div>
<div class="two"><section><h2>The question</h2><p>How does reported cluster activity change over time, and which observations can we trust?</p>
<h2>Our approach</h2><p>Read both source formats, validate measurements, preserve missing values and quarantine conflicting timestamps. Load accepted snapshots into TimescaleDB, then explore SQL results in Grafana.</p>
<h2>What the data shows</h2><ul><li>Mean reported CPU: <b>70.97%</b> across 894,438 CPU-present snapshots.</li><li>Highest daily mean with ≥200 CPU samples: <b>98.63%</b>, 26 June 2025 (288 samples).</li><li>Peak observed queued-job count: <b>2,536</b>. This is backlog, not job waiting time.</li></ul></section>
<section><h2>A working interactive view</h2><img class="screen" src="assets/dashboard-overview.png" alt="Actual Grafana CPU, job and node charts"><p class="caption">Actual system screenshot, 16 November 2026. Choose a date range and hourly, daily or weekly buckets. Source wall-clock time is preserved; the displayed UTC axis is only a plotting convention.</p><h2>Quality stays visible</h2><p>Of 917,919 nonblank source rows: 903,522 accepted, 12,489 extra identical duplicates, 1,907 conflicting variants and one rejected row. All 937 conflicting timestamps were quarantined.</p></section></div>
<img class="pipeline" src="assets/pipeline.svg" alt="Raw logs to cleaning to TimescaleDB to SQL to Grafana">
<div class="two"><section class="proof"><h2>Verified, not assumed</h2><p><b>All 903,522 rows and all 12 fields</b> match the cleaned CSV.</p><p><b>43 tests + 13 subtests</b> pass with real TimescaleDB, including repeat import and rollback recovery.</p><p><b>36 panel-query checks</b> cover three aggregation settings. Chrome rendering and bucket selection were tested.</p></section><section><h2>What we cannot claim</h2><p>These are whole-cluster snapshots. No per-node CPU, memory, job completions or individual waiting times can be calculated.</p><p>9,084 CPU values are missing; 212 exceed 100%. CPU semantics and source timezone are unconfirmed. Averages weight snapshots, not missing elapsed time.</p><h2>What we learned</h2><p>Preserve evidence, test real transactions, show coverage alongside trends, and make uncertainty part of the interface.</p></section></div>
<footer class="foot"><b>Switch Squad</b> · Python · TimescaleDB · Grafana · Linux containers<br>
Source and reproducibility: github.com/chpc-tech-eval/switch-squad-hpc-log-viz<br>
Evidence: docs/evidence/ · Findings: docs/analysis.md · Prepared 18 November 2026.</footer>
</main></html>"""
    (OUT / "poster.html").write_text(text, encoding="utf-8")


def slides():
    return [
        ("From cluster logs\nto evidence", ["Switch Squad · SCC 2026", "A reproducible historical HPC dashboard", "Prepared 18 November 2026"], None,
         "Introduce the team. We process historical whole-cluster snapshots, not individual job histories."),
        ("Start with what the data supports", ["3,169 files; 917,919 nonblank source rows", "January 2017 to October 2025; roughly five-minute observations", "Reported CPU, node counts and aggregate job-state counts", "No node IDs, memory, job arrivals or completions"], None,
         "Explain the photo-album analogy. A queued count is not a waiting-time measurement."),
        ("One traceable pipeline", ["Validate both log formats; preserve NULLs", "Deduplicate identical rows; quarantine every conflicting timestamp", "Store accepted rows; analyse with SQL; explore in Grafana"], "assets/pipeline.svg",
         "Point to each stage. Quality reports retain source locations and reasons. Linux containers carry the same workflow across hosts."),
        ("Where the services run", ["Windows: browser and optional Python tools", "Linux containers: Grafana, TimescaleDB and optional Python runner", "Browser → localhost:3000 → Grafana", "Grafana and runner → db:5432; Windows loader → localhost:5433", "Grafana reads with a restricted account; database data persists in a volume"], None,
         "Docker Desktop provides the Linux container environment. Compose resolves db on its service network. Browser requests go to Grafana; Grafana queries PostgreSQL. The cleaner and loader can run on Windows or in the Linux runner. Ubuntu through WSL2 is also acceptable. See docs/deployment.md."),
        ("Quality is part of the result", ["903,522 accepted snapshots", "12,489 extra identical duplicates", "937 conflicting timestamps → 1,907 quarantined variants", "1 rejected row; row accounting passes", "9,084 missing CPU values; 212 reported CPU values above 100%"], None,
         "These are actual full-archive counts. Warnings are events, not necessarily distinct bad rows. Missing values remain distinct from zero."),
        ("Explore the working dashboard", ["Absolute date range + hour/day/week buckets", "CPU, job backlog, nodes and observation coverage", "Actual Grafana screenshot · 16 November 2026"], "assets/dashboard-overview.png",
         "Show the interface. Its database role can SELECT but cannot modify snapshots. Point out the source-timezone caveat."),
        ("Observed findings, with context", ["70.97% mean reported CPU, across 894,438 CPU-present snapshots", "98.63% highest daily mean with ≥200 CPU samples: 26 June 2025", "2,536 maximum observed queued-job count", "Largest accepted-snapshot gap: 4 days, 5 minutes", "Snapshot-weighted results; changing capacity limits comparisons"], None,
         "The peak day has 288 CPU samples. We do not infer causes. Exactly zero reported CPU does not prove the hardware was idle."),
        ("Trust comes from comparison", ["All 903,522 rows and all 12 database fields match the clean CSV", "Repeat import: 0 inserted; 903,522 identical rows skipped", "43 tests + 13 subtests pass with real TimescaleDB", "36 panel-query checks; Chrome UI and bucket-click checks", "Linux tooling container independently verifies the stored data"], None,
         "Explain the repaired loader: matching timestamps alone are not enough. A differing reimport is a reported failure. Batches commit independently and can be resumed."),
        ("An honest boundary", ["CPU percentage semantics and source timezone remain unconfirmed", "No per-node usage, memory, throughput or individual wait time", "Missing buckets stay empty; no artificial snapshot records", "Mentor accepted the container deployment and alternative metrics on 17 November"], None,
         "The mentor accepted cluster-wide CPU and running/queued job counts in issue #9. The data limitations remain. Issue #12 confirms that no separate VirtualBox cluster is required."),
        ("Live demo: ask a narrower question", ["Open the historical dashboard and its coverage panels", "Choose 26 June 2025; switch Bucket to 1 hour", "Hover CPU and queue-count series", "Show the verification evidence and CI", "Fallback: actual screenshots and PDF, clearly labelled"], "assets/dashboard-filtered.png",
         "Follow submission/demo.md. Allow six minutes if the organiser permits. Do not run the full import during the live demo."),
        ("What we accomplished", ["Raw logs → validated storage → supported analysis → interactive dashboard", "Reproducible Linux/Windows workflow and real-database tests", "Evidence-backed poster, journal, slides and demo guide", "Next: confirm requirements and rehearse the presentation", "Repository: github.com/chpc-tech-eval/switch-squad-hpc-log-viz"], None,
         "Conclude with the deliverables and remaining questions: source timezone, CPU units and organiser formats."),
    ]


def build_slides():
    deck = slides()
    markdown = ["# Switch Squad presentation", "", "Editable narrative source. Speaker allocation and organiser timing remain to be confirmed.", ""]
    sections = []
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)

    def textbox(slide, x, y, w, h, text, size, color=INK, bold=False):
        box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
        frame = box.text_frame
        frame.word_wrap = True
        for number, line in enumerate(text.split("\n")):
            paragraph = frame.paragraphs[0] if number == 0 else frame.add_paragraph()
            paragraph.text = line
            paragraph.font.name = "Arial"
            paragraph.font.size = Pt(size)
            paragraph.font.bold = bold
            paragraph.font.color.rgb = RGBColor.from_string(color)
            paragraph.space_after = Pt(15)

    for index, (title, bullets, image, notes) in enumerate(deck, 1):
        markdown += [f"## {index}. {title.replace(chr(10), ' ')}", ""] + ["- " + bullet for bullet in bullets] + ["", "Speaker notes: " + notes, ""]
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        slide.background.fill.solid()
        slide.background.fill.fore_color.rgb = RGBColor.from_string("FAFCF9")
        textbox(slide, .55, .25, 12, .4, "SWITCH SQUAD  /  SCC 2026", 13, GREEN, True)
        textbox(slide, .55, .9, 12, 1.7 if index == 1 else 1.0, title, 42 if index == 1 else 32, bold=True)
        if image and image.endswith(".png"):
            textbox(slide, .55, 2.0, 4.0, 4.7, "\n".join(bullets), 22)
            from PIL import Image
            with Image.open(OUT / image) as source:
                width, height = source.size
            scale = min(7.8 / width, 4.7 / height)
            slide.shapes.add_picture(str(OUT / image), Inches(4.8), Inches(2), width=Inches(width * scale))
        elif image:
            textbox(slide, .55, 2.0, 12, 2.3, "\n".join(bullets), 24)
            # Editable native PowerPoint diagram, matching the supplied SVG.
            for number, label in enumerate(["Raw archive", "Clean + explain", "TimescaleDB", "SQL analysis", "Grafana"]):
                shape = slide.shapes.add_shape(5, Inches(.6 + number * 2.55), Inches(4.65), Inches(2.25), Inches(1.15))
                shape.fill.solid()
                shape.fill.fore_color.rgb = RGBColor.from_string(INK)
                shape.line.fill.background()
                shape.text_frame.text = label
                p = shape.text_frame.paragraphs[0]
                p.font.size = Pt(19)
                p.font.color.rgb = RGBColor(255, 255, 255)
        else:
            textbox(slide, .55, 2.7 if index == 1 else 2, 12.0, 4.6, "\n".join(bullets), 27 if index == 1 else 25)
        textbox(slide, .55, 7.05, 12, .3, f"Source: repository evidence · 16 Nov 2026     |     {index:02d} / {len(deck):02d}", 10, GREEN)
        slide.notes_slide.notes_text_frame.text = notes
        image_html = f'<img src="{image}" alt="Verified system screenshot or pipeline">' if image else ""
        sections.append(f'<section class="slide"><header>SWITCH SQUAD / SCC 2026</header><h1>{ESC(title).replace(chr(10), "<br>")}</h1><div class="content {"with-image" if image else ""}"><ul>{"".join("<li>" + ESC(bullet) + "</li>" for bullet in bullets)}</ul>{image_html}</div><footer>Repository evidence · 16 November 2026 <span>{index:02d} / {len(deck):02d}</span></footer></section>')
    prs.save(str(OUT / "slides.pptx"))
    (OUT / "slides.md").write_text("\n".join(markdown), encoding="utf-8")
    slide_html = """<!doctype html><html lang="en"><meta charset="utf-8"><title>Switch Squad slides</title><style>
@page {size:13.333in 7.5in; margin:0} *{box-sizing:border-box} body{margin:0;font-family:Arial,sans-serif;color:#113c42;background:#fafcf9}
.slide{width:13.333in;height:7.5in;padding:.4in .55in;position:relative;break-after:page;overflow:hidden}
header{font-size:13pt;color:#14786b;letter-spacing:2px;font-weight:bold} h1{font-size:34pt;margin:.3in 0 .3in;line-height:1.1}
.content{font-size:24pt;line-height:1.3}ul{margin:0;padding-left:.3in}li{margin-bottom:.16in}.with-image{display:grid;grid-template-columns:3.9in 7.7in;gap:.45in;font-size:20pt}.with-image img{width:100%;max-height:4.7in;object-fit:contain;object-position:top}
footer{position:absolute;bottom:.25in;left:.55in;right:.55in;font-size:10pt;color:#14786b}footer span{float:right}
</style>""" + "".join(sections) + "</html>"
    (OUT / "slides.html").write_text(slide_html, encoding="utf-8")


def export():
    # Render the simple source structure without hiding or rewriting entries.
    journal_text = (OUT / "journal.md").read_text(encoding="utf-8")
    rendered = []
    in_table = False
    for line in journal_text.splitlines():
        if line.startswith("|"):
            if line.startswith("|---"):
                continue
            if not in_table:
                rendered.append("<table>")
                in_table = True
            cells = line.strip("|").split("|")
            rendered.append("<tr>" + "".join("<td>" + ESC(cell.strip()) + "</td>" for cell in cells) + "</tr>")
            continue
        if in_table:
            rendered.append("</table>")
            in_table = False
        if line.startswith("## "):
            rendered.append("<h2>" + ESC(line[3:]) + "</h2>")
        elif line.startswith("# "):
            rendered.append("<h1>" + ESC(line[2:]) + "</h1>")
        elif line.strip():
            rendered.append("<p>" + ESC(line) + "</p>")
    if in_table:
        rendered.append("</table>")
    journal_html = '<!doctype html><html lang="en"><meta charset="utf-8"><title>Switch Squad journal</title><style>@page{size:A4;margin:18mm}body{font:11pt Arial;line-height:1.5;color:#113c42}h2{break-after:avoid}table{border-collapse:collapse;font-size:9pt;width:100%}td{padding:5px;border-bottom:1px solid #a1b9af}tr{break-inside:avoid}p{orphans:3;widows:3}</style>' + "".join(rendered) + '</html>'
    (OUT / "journal.html").write_text(journal_html, encoding="utf-8")
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel=os.getenv("BROWSER_CHANNEL", "chrome"), headless=True)
        page = browser.new_page(viewport={"width": 1500, "height": 1100}, device_scale_factor=1)
        evidence = {}
        for name in ("poster", "slides", "journal"):
            page.goto((OUT / f"{name}.html").as_uri(), wait_until="networkidle")
            assert page.locator("img").evaluate_all("images => images.every(i => i.complete && i.naturalWidth > 0)"), f"Missing image in {name}"
            if name == "poster":
                size = page.locator(".poster").evaluate("el => ({height: el.clientHeight, content: el.scrollHeight})")
                assert size["content"] <= size["height"], size
                page.locator(".poster").screenshot(path=str(OUT / "assets/poster-preview.png"))
            if name == "slides":
                overflow = page.locator(".slide").evaluate_all("els => els.map((e,i) => ({slide:i+1,height:e.clientHeight, content:e.scrollHeight})).filter(e => e.content > e.height)")
                assert not overflow, overflow
                page.locator(".slide").first.screenshot(path=str(OUT / "assets/slides-preview.png"))
            page.pdf(path=str(OUT / f"{name}.pdf"), print_background=True, prefer_css_page_size=True)
            pdf = PdfReader(OUT / f"{name}.pdf")
            if name in ("poster", "slides"):
                assert len(pdf.pages) == (1 if name == "poster" else len(slides()))
            assert all((item.extract_text() or "").strip() for item in pdf.pages)
            evidence[name] = {"pdf_bytes": (OUT / f"{name}.pdf").stat().st_size,
                              "pdf_pages": len(pdf.pages), "linked_images_loaded": True,
                              "page_width_points": float(pdf.pages[0].mediabox.width),
                              "page_height_points": float(pdf.pages[0].mediabox.height)}
        browser.close()
    (ROOT / "docs/evidence/material-exports.json").write_text(json.dumps(evidence, indent=2) + "\n")
    print(json.dumps(evidence, indent=2))


def main():
    summary = json.loads((ROOT / "docs/evidence/analysis.json").read_text())["summary"][0]
    assert summary["snapshots"] == 903522
    assert summary["cpu_samples"] == 894438 and summary["missing_cpu_samples"] == 9084
    assert summary["max_queued_jobs"] == 2536 and round(float(summary["mean_reported_cpu_percent"]), 2) == 70.97
    journal()
    poster(summary)
    build_slides()
    export()


if __name__ == "__main__":
    main()
