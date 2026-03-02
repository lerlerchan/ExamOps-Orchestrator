# Deployment Readiness Checklist — ExamOps Orchestrator

Purpose: minimum checklist to move a pilot into a production-ready deployment.

1) Environment & Configuration
- Provide `/.env.example` with required keys and descriptions.
- Validate environment variables at startup and fail fast with clear errors.
- Centralize config in `src/config.py` (or similar) and avoid scattered `os.environ` reads.

2) Secrets & Access
- Do not commit secrets. Use Azure Key Vault or CI secrets for production credentials.
- Ensure least-privilege service principals for Graph API and Blob Storage.

3) Infrastructure & Deployment
- Use IaC (Bicep/Terraform) or documented deployment script for functions and storage.
- Staging and production environments must be separate (different storage containers, keys).
- Automated deploy workflow (GitHub Actions) with approvals for production.

4) Observability & Monitoring
- Structured logging (JSON) and consistent log levels across modules.
- Metrics: request counts, latencies, error rates, job durations, queue/backlog.
- Error reporting: integrate with Sentry or Azure Monitor for exceptions and alerts.

5) Testing & CI
- Unit tests for critical modules (formatting engine, session store, agents). Target 80%+ coverage for core logic.
- Integration test for end-to-end flow on sample documents (use small fixtures).
- CI runs lint, formatting checks, mypy (gradual), tests, and coverage reporting.

6) Security & Compliance
- Data handling policy: redact PII in logs, anonymize uploaded material used in pilots.
- Retention policy for uploaded files and moderation forms.
- Confirm legal & institutional requirements for storing exam materials.

7) Backups & Recovery
- Regular backups of critical blobs (templates, outputs) and documented restore steps.
- Versioning enabled on storage containers if supported.

8) Cost & Scaling
- Estimate storage/AI API cost per pilot and publish a cost runbook.
- Load test critical endpoints and document autoscale settings for Functions.

9) Rollout & Runbook
- Define pilot run plan (timeline, sample courses, success criteria).
- On-call runbook: how to triage, roll back a release, and who to contact.

10) Documentation & Handover
- `README.md` with quickstart, `DEPLOYMENT_CHECKLIST.md`, and a short `RUNBOOK.md`.
- Admin guide: how to add templates, configure AI keys, and manage sessions.

11) Privacy & Consent
- Consent form for use of sample materials during pilot.
- Mechanism to delete pilot data on request.

12) Post-deploy metrics
- Collect pilot metrics: time-per-paper, number of questions generated, compliance score.
- Review metrics weekly during pilot and prepare the impact brief.
