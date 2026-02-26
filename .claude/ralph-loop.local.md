---
active: true
iteration: 1
max_iterations: 5
completion_promise: "DONE"
started_at: "2026-02-26T14:45:50Z"
---

You are completing the examops-orchestrator project. Work in phases:

## PHASE 1: Build Locally
- Read all existing code/specs in the repo first
- Implement all endpoints/services per the spec
- Ensure the app runs locally (npm start / npm run dev)
- Commit after each working module

## PHASE 2: Unit Tests
- Write unit tests for every service/controller
- Use Jest (or existing test framework in repo)
- Achieve >80% coverage
- All tests must pass before moving on
- Commit

## PHASE 3: Azure Setup Guide
- Generate AZURE_SETUP.md with step-by-step:
  - Resource group, App Service Plan, App Service creation
  - Environment variables config
  - Database setup (if needed)
  - CI/CD via GitHub Actions or Azure CLI

## PHASE 4: Deploy to Azure
- Create/update deployment configs:
  -  (GitHub Actions)
  - Or 
  -  if containerized
  - App Settings / env vars mapping
- Test deployment script locally (dry-run)

## RULES
- Work autonomously, don't ask questions
- If you hit context limit, save progress summary to PROGRESS.md
- On session resume, read PROGRESS.md first and continue
- Commit frequently with clear messages
- Log blockers in BLOCKERS.md
