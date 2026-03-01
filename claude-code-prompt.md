# Claude Code Prompt — ExamOps Azure Deploy

## Context
You are helping deploy the ExamOps Orchestrator project to Azure. The repo is at `https://github.com/lerlerchan/examops-orchestrator`. Reference `AZURE_SETUP.md` for all resource provisioning steps and `PRD.md` for architecture context.

## Pre-requisite (done by user)
I have already run `az login` and set my subscription. Proceed without re-authenticating.

## Task: Full Azure Provisioning + Deploy

Execute the following in order. After each step, confirm success before proceeding. Store all outputs (keys, endpoints, connection strings) as shell variables for use in later steps.

**Region**: `southeastasia` | **Resource Group**: `rg-examops-prod`

### Steps
1. Create resource group
2. Create Storage Account + 3 blob containers (`examops-input`, `examops-output`, `examops-templates`)
3. Create Azure AI Search (basic SKU) + create `exam-templates` vector index
4. Create Azure OpenAI resource + deploy `gpt-4o-mini` and `text-embedding-ada-002`
5. Register Entra ID app (ExamOps Bot) + create client secret + grant `Files.ReadWrite.All`
6. Create Azure Bot Framework registration
7. Create App Service Plan (B2 Linux) + Function App (Python 3.11, Functions v4)
8. Set all environment variables/app settings on the Function App (chain all keys/endpoints from previous steps)
9. Deploy function app: `func azure functionapp publish func-examops-prod --python`
10. Update bot messaging endpoint to `https://func-examops-prod.azurewebsites.net/api/messages`
11. Run health check: `curl -X POST https://func-examops-prod.azurewebsites.net/api/format-exam`

### Rules
- If any step fails, diagnose and fix before continuing
- Use globally unique names by appending random suffix if name collision occurs
- Print a summary table of all resources + keys at the end
- Save all env vars to `.env` file in project root

## Task: GitHub Actions CI/CD (after infra is up)

Create `.github/workflows/deploy.yml`:
- Trigger on push to `main`
- Use `azure/functions-action@v1`
- Python 3.11, install deps, run `pytest`, then deploy
- Store secrets as GitHub Actions secrets (list which ones to add)
