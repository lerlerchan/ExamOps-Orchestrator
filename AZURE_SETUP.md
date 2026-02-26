# Azure Setup Guide — ExamOps Orchestrator

Step-by-step provisioning guide for deploying ExamOps Orchestrator to Azure.

---

## Prerequisites

- [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli) ≥ 2.57
- [Azure Functions Core Tools](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local) v4
- Python 3.11
- An active Azure subscription
- A Microsoft 365 / Teams tenant (for the bot)

```bash
az login
az account set --subscription "<YOUR_SUBSCRIPTION_ID>"
```

---

## 1. Resource Group

```bash
REGION=southeastasia          # choose region closest to Southern University College
RG=rg-examops-prod

az group create --name $RG --location $REGION
```

---

## 2. Azure Storage Account + Blob Containers

```bash
STORAGE_ACCOUNT=stexamopsprod   # must be globally unique, 3-24 lowercase letters/digits

az storage account create \
  --name $STORAGE_ACCOUNT \
  --resource-group $RG \
  --location $REGION \
  --sku Standard_LRS \
  --kind StorageV2

# Retrieve connection string (save for env vars)
STORAGE_CONN=$(az storage account show-connection-string \
  --name $STORAGE_ACCOUNT --resource-group $RG --query connectionString -o tsv)

# Create the three required containers
for CONTAINER in examops-input examops-output examops-templates; do
  az storage container create \
    --name $CONTAINER \
    --connection-string "$STORAGE_CONN"
done
```

---

## 3. Azure AI Search

```bash
SEARCH_SERVICE=srch-examops-prod   # globally unique

az search service create \
  --name $SEARCH_SERVICE \
  --resource-group $RG \
  --location $REGION \
  --sku basic

# Retrieve admin key
SEARCH_KEY=$(az search admin-key show \
  --service-name $SEARCH_SERVICE \
  --resource-group $RG \
  --query primaryKey -o tsv)

SEARCH_ENDPOINT="https://${SEARCH_SERVICE}.search.windows.net"

# Create the exam-templates vector index
az rest --method POST \
  --uri "${SEARCH_ENDPOINT}/indexes?api-version=2024-03-01-Preview" \
  --headers "api-key=${SEARCH_KEY}" "Content-Type=application/json" \
  --body '{
    "name": "exam-templates",
    "fields": [
      {"name": "id",             "type": "Edm.String",              "key": true},
      {"name": "template_rules", "type": "Edm.ComplexType"},
      {"name": "content_vector", "type": "Collection(Edm.Single)",
       "dimensions": 1536, "vectorSearchProfile": "default-profile"}
    ],
    "vectorSearch": {
      "profiles":    [{"name": "default-profile", "algorithm": "default-hnsw"}],
      "algorithms":  [{"name": "default-hnsw",    "kind": "hnsw"}]
    }
  }'
```

### Upload Template Rules

```bash
# After provisioning, upload your institutional template rules:
# python scripts/upload_template.py
# (Script reads sample/ .docx files and upserts structured rules into the index)
```

---

## 4. Azure OpenAI Resource

```bash
OPENAI_RESOURCE=oai-examops-prod

az cognitiveservices account create \
  --name $OPENAI_RESOURCE \
  --resource-group $RG \
  --location $REGION \
  --kind OpenAI \
  --sku S0

# Deploy gpt-4o-mini
az cognitiveservices account deployment create \
  --name $OPENAI_RESOURCE \
  --resource-group $RG \
  --deployment-name gpt-4o-mini \
  --model-name gpt-4o-mini \
  --model-version "2024-07-18" \
  --model-format OpenAI \
  --sku-capacity 10 \
  --sku-name Standard

# Deploy text-embedding-ada-002
az cognitiveservices account deployment create \
  --name $OPENAI_RESOURCE \
  --resource-group $RG \
  --deployment-name text-embedding-ada-002 \
  --model-name text-embedding-ada-002 \
  --model-version "2" \
  --model-format OpenAI \
  --sku-capacity 10 \
  --sku-name Standard

OPENAI_ENDPOINT=$(az cognitiveservices account show \
  --name $OPENAI_RESOURCE --resource-group $RG --query properties.endpoint -o tsv)
OPENAI_KEY=$(az cognitiveservices account keys list \
  --name $OPENAI_RESOURCE --resource-group $RG --query key1 -o tsv)
```

---

## 5. Azure AI Foundry (LLM Validator)

1. Open [Azure AI Foundry](https://ai.azure.com) in the Portal
2. Create a new **Project** in the `$RG` resource group
3. Under **Settings → Connections**, copy the **Endpoint** and **Key**
4. Deploy `gpt-4o-mini` inside the project

```bash
FOUNDRY_ENDPOINT=https://<your-project>.cognitiveservices.azure.com
FOUNDRY_KEY=<your-foundry-key>
```

---

## 6. Microsoft Entra ID App Registration (Graph API + Teams Bot)

```bash
# Register app
APP_DISPLAY_NAME="ExamOps Bot"
APP_ID=$(az ad app create --display-name "$APP_DISPLAY_NAME" --query appId -o tsv)
TENANT_ID=$(az account show --query tenantId -o tsv)

# Create client secret (save the value — only shown once)
APP_SECRET=$(az ad app credential reset --id $APP_ID --query password -o tsv)

# Grant API permissions: Files.ReadWrite.All (delegated) + offline_access
az ad app permission add \
  --id $APP_ID \
  --api 00000003-0000-0000-c000-000000000000 \
  --api-permissions 863451e7-0667-486c-a5d6-d135439485f0=Scope  # Files.ReadWrite.All

# Admin-consent the permissions
az ad app permission admin-consent --id $APP_ID
```

---

## 7. Azure Bot Framework Resource

```bash
BOT_NAME=bot-examops-prod

az bot create \
  --name $BOT_NAME \
  --resource-group $RG \
  --kind registration \
  --appid $APP_ID \
  --password "$APP_SECRET" \
  --location global

# After deploying the bot endpoint (step 10), set the messaging endpoint:
# az bot update --name $BOT_NAME --resource-group $RG \
#   --endpoint "https://<func-app>.azurewebsites.net/api/messages"
```

---

## 8. Azure App Service Plan + Function App

```bash
APP_PLAN=plan-examops-prod
FUNC_APP=func-examops-prod    # globally unique

# Linux Consumption plan (Python 3.11)
az appservice plan create \
  --name $APP_PLAN \
  --resource-group $RG \
  --location $REGION \
  --sku B2 \
  --is-linux

az functionapp create \
  --name $FUNC_APP \
  --resource-group $RG \
  --plan $APP_PLAN \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --storage-account $STORAGE_ACCOUNT \
  --os-type Linux
```

---

## 9. Environment Variables (App Settings)

```bash
az functionapp config appsettings set \
  --name $FUNC_APP \
  --resource-group $RG \
  --settings \
    "AZURE_STORAGE_CONNECTION_STRING=${STORAGE_CONN}" \
    "AZURE_SEARCH_ENDPOINT=${SEARCH_ENDPOINT}" \
    "AZURE_SEARCH_KEY=${SEARCH_KEY}" \
    "AZURE_OPENAI_ENDPOINT=${OPENAI_ENDPOINT}" \
    "AZURE_OPENAI_KEY=${OPENAI_KEY}" \
    "AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini" \
    "AZURE_FOUNDRY_ENDPOINT=${FOUNDRY_ENDPOINT}" \
    "AZURE_FOUNDRY_KEY=${FOUNDRY_KEY}" \
    "AZURE_FOUNDRY_DEPLOYMENT=gpt-4o-mini" \
    "GRAPH_TENANT_ID=${TENANT_ID}" \
    "GRAPH_CLIENT_ID=${APP_ID}" \
    "GRAPH_CLIENT_SECRET=${APP_SECRET}" \
    "MICROSOFT_APP_ID=${APP_ID}" \
    "MICROSOFT_APP_PASSWORD=${APP_SECRET}" \
    "BLOB_CONTAINER_INPUT=examops-input" \
    "BLOB_CONTAINER_OUTPUT=examops-output" \
    "BLOB_CONTAINER_TEMPLATES=examops-templates" \
    "SEARCH_INDEX_NAME=exam-templates" \
    "AZURE_EMBEDDING_MODEL=text-embedding-ada-002"
```

---

## 10. Deploy to Azure Functions

### Via GitHub Actions (recommended — see `.github/workflows/deploy.yml`)

Push to `main` branch — the workflow deploys automatically.

### Via Azure Functions Core Tools (manual)

```bash
cd src/functions
func azure functionapp publish $FUNC_APP --python
```

---

## 11. Update Bot Messaging Endpoint

```bash
FUNC_ENDPOINT="https://${FUNC_APP}.azurewebsites.net/api/messages"

az bot update \
  --name $BOT_NAME \
  --resource-group $RG \
  --endpoint "$FUNC_ENDPOINT"
```

---

## 12. Verify Deployment

```bash
# Health check — should return 400 (missing fields) rather than 5xx
curl -X POST "https://${FUNC_APP}.azurewebsites.net/api/format-exam" \
  -H "Content-Type: multipart/form-data"

# Check function logs
az functionapp logs show --name $FUNC_APP --resource-group $RG
```

---

## Local Development

```bash
# Copy and fill in your values
cp .env.example .env

# Install dependencies
pip install -r requirements.txt

# Run Azure Function locally
cd src/functions
func start

# Run tests
cd ../..
pytest tests/ -v
```

---

## Cost Estimate (approximate, Southeast Asia region)

| Resource | SKU | Est. monthly |
|---|---|---|
| Storage Account | Standard_LRS | ~$0.02 / GB |
| Azure AI Search | Basic | ~$75 |
| Azure OpenAI (gpt-4o-mini) | Pay-as-you-go | ~$0.15 / 1M tokens |
| Azure Functions | B2 Linux | ~$75 |
| Bot Framework | Free registration | $0 |

> For production: enable **Soft Delete** on Blob Storage, set **Diagnostic Settings** on all resources, and use **Azure Key Vault** for secrets instead of App Settings.
