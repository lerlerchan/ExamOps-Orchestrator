# Impact Brief — ExamOps Orchestrator

Summary
- Problem: Lecturers and course teams spend hours manually creating, aligning, and formatting exam papers (CLO mapping, numbering, institutional templates). This is repetitive, error-prone work that slows down exam production and increases moderation overhead.
- Solution: ExamOps Orchestrator automates CLO extraction from syllabus, provides an AI-assisted question copilot grounded in course materials, and generates moderation forms and polished `.docx` exam papers with a hybrid rule+LLM formatting pipeline.

Evidence & Significance
- Target users: university lecturers, course coordinators, and departmental exam officers.
- Expected benefit: conservative estimate of 3–6 hours saved per paper for a typical course (based on workflow decomposition and time spent on formatting and CLO mapping).
- Strategic fit: complements existing LMS tools (Moodle, SharePoint) by focusing on upstream content preparation and template-compliant output.

Pilot Plan & Success Criteria
- Scope: run a 2–4 week pilot with 1–3 courses (one lecturer per course) using real syllabus and material stored on SharePoint/OneDrive.
- Tasks: 1) ingest syllabus, 2) run question copilot + review, 3) produce filled moderation form (AARO-FM-030), 4) format exam and deliver HTML diff + final `.docx`.
- Success metrics: average time saved per paper (hrs), % of questions accepted into final paper, formatting/numbering fixes count (before vs after), user satisfaction (NPS-like score ≥ 7/10).

Production Readiness Snapshot
- Completed/available: rule-based formatting, LLM validator, Azure Functions endpoints, Azure Blob for storage, MCP server for automation.
- Remaining priorities before broad rollout: secrets + Key Vault integration, structured logging/monitoring, 80%+ critical-unit test coverage, CI mypy checks, documented runbook and staging environment.

Impact & Business Case
- Value drivers: time saved (operational), reduced moderation cycles (quality), and faster exam turnaround (student benefit).
- Pricing options to test: departmental pilot (paid setup + per-course fee), SaaS per-course subscription, or institutional licensing with managed onboarding.

Next Steps
1. Recruit 2 pilot lecturers and run the 2–4 week pilot.  
2. Collect metrics and produce a one-page pilot report with screenshots and sample diffs.  
3. Complete deployment checklist items (Key Vault, monitoring, backups) and prepare a short demo video (60–90s) highlighting time saved.

Contact
- For pilot coordination and details, see `CONTRIBUTING.md` maintainers or open an issue titled "Pilot: Impact brief".
