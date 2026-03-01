---
active: true
iteration: 1
max_iterations: 0
completion_promise: "DONE"
started_at: "2026-03-01T21:13:19Z"
---

Create a simple but polished web frontend for ExamOps Orchestrator at src/web/index.html - single page with drag-drop .docx upload zone, progress indicator during processing, then display compliance score with category breakdown, color-coded HTML diff report inline, and download buttons for formatted .docx and diff report. Style it professionally with SUC branding (Southern University College, Faculty of Engineering and IT). Add a /api/web route to the Azure Function that serves this static page. Update the Function App auth settings to allow unauthenticated access to /api/web and /api/format-exam endpoints. Deploy to func-examops-prod via GitHub Actions. Run all tests after changes, fix any failures. If you hit any rate limit, wait and retry automatically. Auto approve all steps.
