# Submission export validation — 20 November 2026

Actual Chrome exports were opened programmatically with pypdf:

| Export | Pages | Size |
|---|---:|---|
| Poster | 1 | A1 portrait, approximately 594 × 841 mm |
| Slides | 11 | 16:9, 960 × 540 PDF points |
| Journal | 4 | A4 |

Every PDF page contains extractable text. All linked screenshot/diagram assets
loaded before export. Browser layout checks found no overflow in the poster or
any slide. Poster and title-slide previews were visually inspected. Editable
PowerPoint reopened successfully with eleven slides and populated speaker notes.
Native PowerPoint/LibreOffice rendering has not been verified; its final
appearance should be checked on the presentation laptop during rehearsal.
The separately generated slide PDF was exported and checked.

The poster PDF uses explicit physical dimensions, rather than relying on a
browser's recognition of the A1 name. Export byte counts and page dimensions are
recorded in material-exports.json. Sources and commands are in submission/README.md.

The GitHub audit includes all 24 original issue/PR entries, reviews/inline
comments and all three Discussions with their comments/replies. Pagination
indicators confirm no further Discussion pages. Quoted notification email
footers are omitted from the saved public evidence. No new acceptance criteria,
poster template or format rubric were found in the discussion replies.
