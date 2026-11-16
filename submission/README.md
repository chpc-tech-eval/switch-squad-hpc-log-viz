# Switch Squad submission materials

Prepared from verified repository work on **16 November 2026** for the stated
**Friday, 20 November 2026** deadline. These are reviewable submission exports;
the organiser's exact format, poster size and presentation duration were not
provided. A1 portrait and a ten-slide deck are explicit working choices.
No claim is made that these formats have organiser approval.

| Deliverable | Editable source | Export |
|---|---|---|
| Poster | poster.html; assets/pipeline.svg | poster.pdf |
| Presentation | slides.md; slides.pptx; scripts/build_materials.py | slides.pdf |
| Journal | journal.md | journal.pdf |
| Practical demo | demo.md | Use alongside the local dashboard |
| Evidence | assets/*.png; ../docs/evidence/ | Actual screenshots and JSON results |
| Submission checks | checklist.md | Team sign-off remains open |

The deck has editable text and diagrams in PowerPoint; screenshots are embedded
images. The poster's HTML/CSS and SVG are editable text sources. Keep the whole
submission directory together so linked images remain available.

## Re-export — Windows PowerShell

Run from the repository root, using the existing virtual environment:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-materials.txt
.\.venv\Scripts\python.exe -m scripts.browser_qa
.\.venv\Scripts\python.exe -m scripts.build_materials
```

Chrome must be installed. For Edge set `$env:BROWSER_CHANNEL = 'msedge'` first.
Linux uses `.venv/bin/python` and an installed supported Chrome/Edge channel;
do not claim browser checks ran on Linux unless you actually run them there.
The builder exports the PDFs, PPTX and previews from local sources. It does not
upload or submit anything. Browser QA requires the local Grafana instance.

Read `demo.md` together as a team, confirm the organiser's format requirements,
review the journal's retrospective entries, then complete `checklist.md`.
