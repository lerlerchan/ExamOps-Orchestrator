# Competitor Matrix — ExamOps Orchestrator

Summary: quick scan of adjacent products and where ExamOps Orchestrator can differentiate.

| Competitor | Core Offering | Pricing model | Strengths | Gaps / Opportunities |
|---|---:|---|---|---|
| ExamSoft | Secure digital exams, psychometric analysis | Enterprise licensing | Strong security, analytics | Manual paper-to-digital conversion work, limited AI-assisted question generation |
| Respondus / LockDown Browser | Exam lockdown + proctoring | Per-institution license | Broad adoption in universities, simple UX | Focus on proctoring only — no question generation or CLO mapping |
| Gradescope (Turnitin) | Auto-grading + rubric workflows | Per-course / enterprise | Excellent grading workflows, autograde for code/math | Not focused on CLO/PLO extraction or docx formatting automation |
| Moodle Quiz + Plugins | LMS-native quizzes (open-source) | Free / hosting costs | Flexible and integrated with LMS | Requires significant configuration; limited AI tooling |
| QuestionPro / QuestionBank SaaS | Question authoring + item banks | SaaS subscriptions | Authoring + bank, analytics | Not integrated with syllabus-to-CLO extraction and not tailored to local templates |
| Custom formatting tools (python-docx scripts) | Rule-based docx formatting | One-off services / OSS | Deterministic formatting | Hard to maintain rules; no LLM validation / RAG grounding |

Key takeaways
- Differentiators for ExamOps Orchestrator: AI-assisted CLO extraction from syllabus, RAG-grounded streaming question copilot, moderation form automation (AARO-FM-030 template), and hybrid rule+LLM formatting pipeline.
- Short-term go-to-market: target lecturers and departmental admins at regional universities with pilot integrations to LMS/SharePoint.
- Pricing options to test: freemium for small courses, per-course pilot pricing, and institution-level licensing with managed setup.
