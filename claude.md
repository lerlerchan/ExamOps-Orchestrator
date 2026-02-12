# ExamOps Orchestrator - Claude AI Context Document

## Project Overview
**ExamOps Orchestrator** is a production-grade AI-powered academic workflow system for automating exam paper formatting at Southern University College's Faculty of Engineering and Information Technology. Built for AI Dev Days Hackathon with Microsoft Agent Framework, Azure MCP, and Azure Foundry.

**Tagline**: *"The AI That Knows Your Exam Template Better Than You Do."*

---

## Core Problem & Solution

### The Pain Point
Lecturers waste 2-4 hours per exam paper on manual formatting:
- Fixing numbering inconsistencies (Q1) vs 1. vs Q1. vs 1)
- Adjusting margins, spacing, indentation (Tab 0.5 for 6 times)
- Formatting marks: (3 marks) with exact spacing rules
- Aligning CLO entries
- Header/footer institutional requirements
- Result: Papers get bounced back during moderation, causing delays

### The Solution
Hybrid AI + Rule-Based Formatting Engine:
1. **Rule-Based Engine**: Deterministic formatting for structure, spacing, numbering
2. **LLM Validation**: Azure OpenAI GPT-4o via Foundry for edge cases and quality checks
3. **Vector DB**: Template storage for multi-campus scalability
4. **Diff Viewer**: Before/after comparison for lecturer confidence

---

## Technology Stack (Azure-Only per Hackathon Requirements)

### Core Services
- **Azure AI Foundry**: Centralized AI orchestration and safety guardrails
- **Azure OpenAI Service**: GPT-4o for formatting validation and edge cases
- **Azure AI Search**: Vector database for template storage and retrieval
- **Azure Functions**: Serverless processing (Consumption Plan - cheapest)
- **Azure Blob Storage**: File staging (Hot tier for temp, Cool for archive)
- **Azure Communication Services**: Bot Framework for Teams integration
- **Microsoft Agent Framework**: Multi-agent orchestration (Semantic Kernel)
- **Azure Monitor + Application Insights**: Logging and telemetry

### Development Tools
- **GitHub Copilot / Claude Code**: Accelerated development
- **Python 3.11+**: Primary language
- **python-docx**: Document manipulation library
- **Semantic Kernel SDK**: Agent framework implementation

### Cost Optimization (Azure for Students)
- **Azure Functions Consumption Plan**: Pay-per-execution ($0 for first 1M executions)
- **Azure AI Search Free Tier**: Up to 50MB storage
- **Azure OpenAI**: Use GPT-4o-mini for validation (cheaper than GPT-4o)
- **Blob Storage LRS**: Locally redundant (cheapest)
- **Total Estimated Monthly Cost**: ~$5-10 for MVP usage

---

## Architecture Design

### High-Level Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                    Microsoft Teams Interface                     │
│                  (Azure Bot Framework SDK)                       │
└────────────────────┬────────────────────────────────────────────┘
                     │ Upload .docx
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│              Azure Functions (HTTP Trigger)                      │
│                     Coordinator Agent                            │
└────────┬────────────────────────────────┬─────────────────────┘
         │                                 │
         ▼                                 ▼
┌────────────────────┐          ┌─────────────────────────────┐
│  File Handler      │          │  Formatting Engine          │
│  Agent             │          │  (Hybrid: Rules + LLM)      │
│  (Azure MCP)       │          └──────────┬──────────────────┘
└────────┬───────────┘                     │
         │                                 │
         ▼                                 ▼
┌────────────────────┐          ┌─────────────────────────────┐
│  Azure Blob        │          │  Azure OpenAI (Foundry)     │
│  Storage           │          │  GPT-4o-mini                │
│  (Input/Output)    │          │  + Azure AI Search          │
└────────────────────┘          │  (Template Vector DB)       │
                                └─────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│              Output: Formatted .docx + Diff Report               │
│              Delivered via Teams + OneDrive Link                 │
└─────────────────────────────────────────────────────────────────┘
```

### Agent Architecture (Microsoft Agent Framework)

```python
# Semantic Kernel Multi-Agent Design

1. Coordinator Agent (Orchestrator)
   - Entry point from Teams Bot
   - Routes file to appropriate agents
   - Manages workflow state
   - Returns final output

2. File Handler Agent (Azure MCP)
   - Uploads to Azure Blob Storage
   - Retrieves templates from Vector DB
   - Saves formatted output
   - Generates OneDrive sharing links

3. Formatting Engine Agent (Hybrid)
   - Rule-Based Layer: python-docx for structure
   - LLM Validation Layer: GPT-4o-mini for edge cases
   - Applies template rules from Vector DB
   - Generates diff comparison

4. Diff Generator Agent
   - Compares original vs formatted
   - Highlights changes (color-coded)
   - Produces HTML report for Teams
```

---

## Detailed Component Design

### 1. File Handler Agent (Azure MCP Integration)

**Purpose**: Manage file I/O with Azure Storage and OneDrive

**Technology**:
- Azure Blob Storage SDK
- Microsoft Graph API (for OneDrive links)
- Azure MCP connectors

**Flow**:
```python
class FileHandlerAgent:
    async def upload_to_blob(self, file_stream, filename):
        """Upload to Azure Blob Storage (Hot tier)"""
        # Container: examops-input
        # Naming: {timestamp}_{user_id}_{filename}
        
    async def retrieve_template(self, template_name):
        """Retrieve from Azure AI Search Vector DB"""
        # Query: "official exam paper template"
        # Returns: Template rules + sample .docx
        
    async def save_output(self, formatted_doc, original_filename):
        """Save to Azure Blob + generate OneDrive link"""
        # Container: examops-output
        # Generate SAS token for secure download
        
    async def create_onedrive_link(self, blob_url):
        """Create shareable OneDrive link via Graph API"""
        # POST to /me/drive/root/children
```

**Azure MCP Configuration**:
```yaml
# Azure MCP Connector for Storage
mcp_connector:
  type: azure_storage
  connection_string: ${AZURE_STORAGE_CONNECTION_STRING}
  container_input: examops-input
  container_output: examops-output
  container_templates: examops-templates
```

---

### 2. Formatting Engine Agent (Hybrid Approach)

**Purpose**: Apply strict template rules + LLM validation

**Architecture**: Two-layer system

#### Layer 1: Rule-Based Engine (python-docx)

**Handles**:
- Header/Footer injection
- Margin standardization (2.54cm all sides)
- Font enforcement (Times New Roman 12pt)
- Numbering structure correction
- Marks formatting
- Spacing rules (1 space before/after colon)
- Indentation (Tab 0.5 × 6 = 3.0cm)

**Implementation**:
```python
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH

class RuleBasedFormatter:
    def __init__(self, template_rules):
        self.rules = template_rules  # From Vector DB
        
    def apply_header_footer(self, doc):
        """Insert institutional header exactly as per guideline"""
        section = doc.sections[0]
        header = section.header
        header_para = header.paragraphs[0]
        header_para.text = self.rules['header_text']
        header_para.style = 'Header'
        
    def fix_numbering(self, doc):
        """Convert messy numbering to standard format"""
        # Q1) → Q1.
        # 1a) → (a)
        # Uses regex patterns from template rules
        
    def format_marks(self, doc):
        """Standardize marks notation: (3 marks)"""
        # Right-align on same line
        # Ensure spacing: space before '(' and after ')'
        
    def apply_spacing_rules(self, doc):
        """Enforce 1 space before/after colon"""
        # "DATE :" → "DATE : "
        # "DURATION :" → "DURATION : "
        
    def fix_indentation(self, doc):
        """Apply Tab 0.5 × 6 indentation for nested items"""
        # Q1. → 0cm
        #   (a) → 1.5cm
        #     (i) → 3.0cm
```

#### Layer 2: LLM Validation (Azure OpenAI GPT-4o-mini)

**Handles**:
- Edge case detection (ambiguous numbering)
- Content preservation (mathematical expressions)
- Quality validation (template compliance score)
- Generates diff report explanations

**Prompt Engineering**:
```python
VALIDATION_PROMPT = """
You are an exam paper formatting validator for Southern University College.

TEMPLATE RULES (from vector database):
{template_rules}

INPUT DOCUMENT (parsed):
{parsed_content}

RULE-BASED OUTPUT:
{formatted_content}

TASK:
1. Validate that formatting matches template rules EXACTLY
2. Identify any edge cases the rule engine missed
3. Suggest fixes for ambiguous numbering
4. Score compliance: 0-100%
5. Generate human-readable diff explanations

OUTPUT FORMAT (JSON):
{
  "compliance_score": 95,
  "issues_found": [
    {"line": 42, "issue": "Ambiguous sub-numbering", "suggestion": "Convert '1.a.i' to '(a)(i)'"}
  ],
  "edge_cases": [],
  "diff_summary": "Fixed 12 numbering issues, adjusted 5 spacing violations"
}
"""
```

**Integration with Azure Foundry**:
```python
from azure.ai.projects import AIProjectClient
from semantic_kernel import Kernel

class LLMValidator:
    def __init__(self, foundry_endpoint, api_key):
        self.client = AIProjectClient(
            endpoint=foundry_endpoint,
            credential=api_key
        )
        self.kernel = Kernel()
        
    async def validate_formatting(self, original, formatted, template_rules):
        """Call GPT-4o-mini via Foundry for validation"""
        prompt = VALIDATION_PROMPT.format(
            template_rules=template_rules,
            parsed_content=original,
            formatted_content=formatted
        )
        
        response = await self.kernel.invoke(
            plugin_name="openai",
            function_name="chat_completion",
            arguments={"messages": [{"role": "user", "content": prompt}]}
        )
        
        return response.choices[0].message.content
```

---

### 3. Template Vector Database (Azure AI Search)

**Purpose**: Store and retrieve template rules for multi-campus scalability

**Schema**:
```json
{
  "template_id": "suc_engineering_exam_v1",
  "campus": "southern_university_college",
  "faculty": "engineering_it",
  "version": "1.0",
  "rules": {
    "margins": {"top": 2.54, "bottom": 2.54, "left": 2.54, "right": 2.54, "unit": "cm"},
    "fonts": {"body": "Times New Roman", "size": 12, "header": "Arial"},
    "spacing": {
      "before_colon": 1,
      "after_colon": 1,
      "line_spacing": 1.5
    },
    "numbering": {
      "level_1": "Q{n}.",
      "level_2": "({letter})",
      "level_3": "({roman})"
    },
    "marks_format": "({n} marks)",
    "indentation": {
      "tab_size": 0.5,
      "level_2_tabs": 3,
      "level_3_tabs": 6
    },
    "header_template": "SOUTHERN UNIVERSITY COLLEGE\nFACULTY OF ENGINEERING AND INFORMATION TECHNOLOGY",
    "instruction_block": "Answer ALL questions.\nAll questions carry equal marks unless otherwise stated."
  },
  "sample_docx_url": "https://examops.blob.core.windows.net/templates/suc_exam_template_v1.docx",
  "guideline_docs": [
    "Exam Paper Format Guideline 1.docx",
    "Marking Scheme Format Guideline 1.docx",
    "AARO-FM-030 Moderation Form.docx"
  ],
  "embedding_vector": [0.123, 0.456, ...],  // For semantic search
  "created_date": "2025-01-15",
  "last_updated": "2025-01-15"
}
```

**Indexing Strategy**:
```python
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchableField,
    VectorSearch,
    HnswAlgorithmConfiguration
)

def create_template_index():
    index = SearchIndex(
        name="exam-templates",
        fields=[
            SimpleField(name="template_id", type="Edm.String", key=True),
            SearchableField(name="campus", type="Edm.String"),
            SearchableField(name="faculty", type="Edm.String"),
            SearchableField(name="rules", type="Edm.String"),  # JSON stringified
            VectorSearchField(
                name="embedding_vector",
                dimensions=1536,  # OpenAI ada-002 dimension
                vector_search_configuration="vector-config"
            )
        ],
        vector_search=VectorSearch(
            algorithms=[HnswAlgorithmConfiguration(name="vector-config")]
        )
    )
    return index
```

**Retrieval Flow**:
```python
async def retrieve_template_for_exam(exam_metadata):
    """
    Query: "Southern University College Engineering exam template"
    Returns: Most relevant template rules
    """
    query_embedding = await get_embedding(exam_metadata['description'])
    
    results = search_client.search(
        search_text=None,
        vector_queries=[{
            "vector": query_embedding,
            "k_nearest_neighbors": 1,
            "fields": "embedding_vector"
        }]
    )
    
    return results[0]['rules']
```

---

### 4. Diff Generator Agent

**Purpose**: Create visual before/after comparison

**Output Formats**:
1. **HTML Report** (for Teams display)
2. **Side-by-side Word document** (optional download)

**Implementation**:
```python
import difflib
from docx import Document
from docx.shared import RGBColor

class DiffGenerator:
    def generate_html_diff(self, original_text, formatted_text):
        """Create HTML diff with color highlighting"""
        differ = difflib.HtmlDiff()
        html = differ.make_file(
            original_text.splitlines(),
            formatted_text.splitlines(),
            fromdesc='Original',
            todesc='Formatted'
        )
        return html
    
    def generate_word_diff(self, original_doc, formatted_doc):
        """Create side-by-side Word comparison"""
        diff_doc = Document()
        
        # Create 2-column table
        table = diff_doc.add_table(rows=1, cols=2)
        table.cell(0, 0).text = "BEFORE"
        table.cell(0, 1).text = "AFTER"
        
        # Highlight changes in red (deletions) and green (additions)
        # ... (implementation details)
        
        return diff_doc
    
    def generate_summary_stats(self, changes):
        """Generate statistics for Teams message"""
        return {
            "numbering_fixes": len([c for c in changes if c['type'] == 'numbering']),
            "spacing_fixes": len([c for c in changes if c['type'] == 'spacing']),
            "formatting_fixes": len([c for c in changes if c['type'] == 'format']),
            "compliance_score": 95
        }
```

**Teams Bot Display**:
```
✅ Formatting Complete!

📊 Summary:
- Numbering fixes: 12
- Spacing fixes: 5
- Mark formatting: 8
- Compliance score: 95%

📥 Download Options:
1. Formatted Exam Paper.docx
2. Diff Report (HTML)
3. Side-by-side Comparison.docx

🔗 OneDrive Link: [Click here]

⚠️ Please review the diff report before finalizing!
```

---

### 5. Microsoft Teams Bot Integration

**Technology**: Azure Bot Framework SDK

**Commands**:
```
/upload         - Upload exam paper for formatting
/format         - Process uploaded file
/download       - Get formatted output
/diff           - View comparison report
/help           - Show available commands
```

**Implementation**:
```python
from botbuilder.core import ActivityHandler, TurnContext
from botbuilder.schema import ChannelAccount, Attachment

class ExamOpsBot(ActivityHandler):
    async def on_message_activity(self, turn_context: TurnContext):
        text = turn_context.activity.text.lower()
        
        if text == "/upload":
            await self.handle_upload(turn_context)
        elif text == "/format":
            await self.handle_format(turn_context)
        elif text == "/download":
            await self.handle_download(turn_context)
        elif text == "/diff":
            await self.handle_diff(turn_context)
        else:
            await turn_context.send_activity("Unknown command. Type /help")
    
    async def handle_upload(self, turn_context: TurnContext):
        # Prompt user to attach .docx file
        await turn_context.send_activity(
            "Please upload your exam paper (.docx format)"
        )
        
        # Wait for file attachment
        if turn_context.activity.attachments:
            file_url = turn_context.activity.attachments[0].content_url
            # Download and store in Blob Storage
            await file_handler_agent.upload_to_blob(file_url)
            await turn_context.send_activity("✅ File uploaded! Use /format to process.")
    
    async def handle_format(self, turn_context: TurnContext):
        await turn_context.send_activity("🔄 Formatting in progress...")
        
        # Call Coordinator Agent
        result = await coordinator_agent.process_exam()
        
        await turn_context.send_activity(
            f"✅ Formatting complete!\n\n"
            f"Compliance: {result['compliance_score']}%\n"
            f"Changes: {result['total_changes']}\n\n"
            f"Use /download or /diff to view results."
        )
```

---

## Data Flow Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│ STEP 1: Lecturer uploads messy_exam.docx via Teams Bot           │
└────────────────────┬─────────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────────┐
│ STEP 2: Azure Function (HTTP Trigger) receives file              │
│         - Validates .docx format                                  │
│         - Generates unique job_id                                 │
│         - Stores in Blob Storage (examops-input container)        │
└────────────────────┬─────────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────────┐
│ STEP 3: Coordinator Agent (Semantic Kernel) starts workflow      │
│         - Retrieves template rules from Azure AI Search           │
│         - Parses document with python-docx                        │
│         - Passes to Formatting Engine Agent                       │
└────────────────────┬─────────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────────┐
│ STEP 4: Formatting Engine Agent (Hybrid)                         │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ Layer 1: Rule-Based Formatter (python-docx)                │  │
│  │ - Apply header/footer                                       │  │
│  │ - Fix numbering (Q1., (a), (i))                            │  │
│  │ - Format marks: (3 marks)                                  │  │
│  │ - Adjust spacing (1 space before/after :)                  │  │
│  │ - Fix indentation (Tab 0.5 × 6)                            │  │
│  └────────────────────────────────────────────────────────────┘  │
│                     │                                             │
│                     ▼                                             │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ Layer 2: LLM Validator (GPT-4o-mini via Foundry)           │  │
│  │ - Check compliance with template rules                     │  │
│  │ - Handle edge cases (ambiguous numbering)                  │  │
│  │ - Generate compliance score (0-100%)                       │  │
│  │ - Preserve mathematical expressions                        │  │
│  └────────────────────────────────────────────────────────────┘  │
└────────────────────┬─────────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────────┐
│ STEP 5: Diff Generator Agent creates comparison                  │
│         - Generate HTML diff report                               │
│         - Create side-by-side Word comparison                     │
│         - Calculate summary statistics                            │
└────────────────────┬─────────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────────┐
│ STEP 6: File Handler Agent saves outputs                         │
│         - Save formatted_exam.docx to Blob Storage                │
│         - Generate OneDrive sharing link (Graph API)              │
│         - Store diff report as HTML                               │
└────────────────────┬─────────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────────┐
│ STEP 7: Teams Bot delivers results                               │
│         📥 Formatted Exam Paper.docx                              │
│         📊 Diff Report (HTML)                                     │
│         🔗 OneDrive Link                                          │
│         ✅ Compliance Score: 95%                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Implementation Phases

### Phase 1: MVP (AI Dev Days Hackathon - Week 1-2)
**Goal**: Working demo with one template

**Deliverables**:
- [ ] Azure infrastructure setup (Functions, Blob, AI Search)
- [ ] Template rules uploaded to Vector DB (1 template: SUC Engineering)
- [ ] Rule-based formatter (python-docx) - core logic
- [ ] LLM validator integration (GPT-4o-mini via Foundry)
- [ ] Teams Bot with /upload, /format, /download commands
- [ ] Diff generator (HTML report)
- [ ] Sample before/after files for demo
- [ ] GitHub repo with README + architecture diagrams

**Testing**:
- Test with 3 real messy exam papers from faculty
- Validate 90%+ compliance score
- Ensure <20 second processing time

**Demo Script**:
```
1. Show messy exam paper (ugly numbering, wrong spacing)
2. Upload via Teams Bot: /upload
3. Trigger formatting: /format
4. Show progress message: "🔄 Formatting..."
5. Display results:
   - ✅ Compliance: 95%
   - 📥 Download links
6. Open diff report (HTML) - highlight changes
7. Open formatted .docx - show perfect formatting
8. Humor: "From 'lecturer nightmare' to 'template perfection' in 15 seconds!"
```

---

### Phase 2: Multi-Template Support (Post-Hackathon - Week 3-4)
**Goal**: Scale to multiple campuses/faculties

**New Features**:
- [ ] Template management UI (upload new templates)
- [ ] Multi-campus vector search (semantic matching)
- [ ] Template versioning (v1.0, v1.1, v2.0)
- [ ] User permissions (admin vs lecturer roles)

---

### Phase 3: Intelligence Expansion (Month 2-3)
**Goal**: Add CLO mapping, difficulty analysis, moderation automation

**New Agents**:
- [ ] CLO Mapping Agent (align questions to learning outcomes)
- [ ] Question Quality Agent (difficulty classification)
- [ ] Marks Validation Agent (ensure totals match)
- [ ] Moderation Report Generator (auto-fill AARO-FM-030 form)

---

## Security & Compliance

### Data Protection
- **Encryption**: All blob storage encrypted at rest (AES-256)
- **Access Control**: Azure AD authentication for bot users
- **Exam Confidentiality**: SAS tokens expire after 1 hour
- **No Data Retention**: Original files deleted after 24 hours
- **Audit Trail**: All formatting actions logged to Application Insights

### Azure Foundry Safety Guardrails
```python
foundry_config = {
    "content_safety": {
        "enabled": True,
        "block_harmful_content": True,
        "detect_jailbreak_attempts": True
    },
    "grounding": {
        "enabled": True,
        "source": "template_vector_db"
    },
    "evaluation": {
        "compliance_threshold": 0.85,
        "auto_reject_below": 0.70
    }
}
```

---

## Monitoring & Observability

### Key Metrics (Azure Monitor + App Insights)
```python
metrics = {
    "formatting_success_rate": 0.95,  # Target: >90%
    "avg_processing_time": 12,        # Target: <20 seconds
    "compliance_score_avg": 0.93,     # Target: >85%
    "api_error_rate": 0.02,           # Target: <5%
    "template_retrieval_time": 0.5    # Target: <1 second
}
```

### Logging Strategy
```python
import logging
from opencensus.ext.azure.log_exporter import AzureLogHandler

logger = logging.getLogger(__name__)
logger.addHandler(AzureLogHandler(
    connection_string=os.getenv('APPLICATIONINSIGHTS_CONNECTION_STRING')
))

# Log formatting events
logger.info("Formatting started", extra={
    "job_id": job_id,
    "user_id": user_id,
    "template_id": template_id
})

logger.info("Formatting completed", extra={
    "job_id": job_id,
    "compliance_score": 0.95,
    "processing_time_ms": 12000,
    "changes_count": 25
})
```

---

## Cost Breakdown (Monthly Estimate for MVP)

| Service | Tier | Est. Usage | Cost |
|---------|------|------------|------|
| Azure Functions | Consumption | 1,000 executions/month | $0 (free tier) |
| Azure Blob Storage | Hot LRS | 10 GB | $0.18 |
| Azure AI Search | Free | 50 MB index | $0 |
| Azure OpenAI (GPT-4o-mini) | Pay-per-token | 500K tokens/month | $0.75 |
| Azure Bot Service | F0 (Free) | Unlimited messages | $0 |
| Application Insights | Basic | 1 GB logs | $2.30 |
| **Total** | | | **~$3.23/month** |

**Scaling Costs** (100 users, 500 papers/month):
- Azure OpenAI: ~$15/month
- Blob Storage: ~$5/month
- AI Search: Upgrade to Basic ($75/month)
- **Total**: ~$100/month

---

## Development Workflow

### GitHub Copilot / Claude Code Usage
```bash
# Use Copilot for boilerplate generation
# Prompt: "Create Azure Function HTTP trigger for file upload"

# Use Claude Code for complex logic
# Prompt: "Implement rule-based numbering correction for exam papers"

# Use both for debugging
# Prompt: "Fix python-docx indentation issue for nested lists"
```

### Repository Structure
```
examops-orchestrator/
├── .github/
│   └── workflows/
│       └── azure-deploy.yml          # CI/CD pipeline
├── src/
│   ├── agents/
│   │   ├── coordinator_agent.py      # Main orchestrator
│   │   ├── file_handler_agent.py     # Azure MCP integration
│   │   ├── formatting_engine.py      # Hybrid formatter
│   │   └── diff_generator.py         # Comparison reports
│   ├── utils/
│   │   ├── template_retrieval.py     # Vector DB queries
│   │   ├── docx_parser.py            # Document parsing
│   │   └── validation.py             # LLM validation
│   ├── functions/
│   │   ├── format_exam/              # Azure Function
│   │   │   ├── __init__.py
│   │   │   └── function.json
│   │   └── host.json
│   └── bot/
│       ├── bot.py                    # Teams Bot logic
│       └── app.py                    # Bot Framework adapter
├── templates/
│   ├── sample_templates/
│   │   ├── suc_exam_template.docx
│   │   ├── exam_format_guideline.docx
│   │   └── marking_scheme_guideline.docx
│   └── before_after_samples/
│       ├── messy_exam_before.docx
│       └── formatted_exam_after.docx
├── tests/
│   ├── test_formatting_engine.py
│   ├── test_template_retrieval.py
│   └── test_diff_generator.py
├── docs/
│   ├── claude.md                     # This file
│   ├── PRD.md                        # Product requirements
│   └── architecture_diagrams/
├── requirements.txt
├── azure-config.json                 # Azure resource config
└── README.md
```

---

## Sample Template Rules (Embedded in Vector DB)

### SUC Engineering Exam Template Rules
```json
{
  "template_id": "suc_engineering_v1",
  "header": {
    "text": "SOUTHERN UNIVERSITY COLLEGE\nFACULTY OF ENGINEERING AND INFORMATION TECHNOLOGY",
    "font": "Arial",
    "size": 12,
    "alignment": "center"
  },
  "title_block": {
    "exam_type": "FINAL EXAMINATION",
    "semester_format": "Semester {A|B|C} Academic Session {YYYY}/{YYYY}",
    "program_list": "multichoice",
    "course_format": "Course Code : {CODE}\nCourse Name : {NAME}",
    "spacing_rules": {
      "before_colon": 1,
      "after_colon": 1
    }
  },
  "instruction_block": {
    "text": "Answer ALL questions.\nAll questions carry equal marks unless otherwise stated.",
    "style": "bold",
    "case": "uppercase"
  },
  "numbering": {
    "level_1": {
      "format": "Q{n}.",
      "indent": "0cm",
      "examples": ["Q1.", "Q2.", "Q3."]
    },
    "level_2": {
      "format": "({letter})",
      "indent": "1.5cm",
      "tab_count": 3,
      "examples": ["(a)", "(b)", "(c)"]
    },
    "level_3": {
      "format": "({roman})",
      "indent": "3.0cm",
      "tab_count": 6,
      "examples": ["(i)", "(ii)", "(iii)"]
    }
  },
  "marks": {
    "format": "({n} marks)",
    "position": "right_aligned_same_line",
    "spacing": {
      "before_bracket": 1,
      "after_bracket": 0
    },
    "total_format": "[Total : {n} marks]"
  },
  "continuation": {
    "format": "<u>Q{n}. (Continued)</u>",
    "trigger": "page_break_mid_question"
  },
  "margins": {
    "top": 2.54,
    "bottom": 2.54,
    "left": 2.54,
    "right": 2.54,
    "unit": "cm"
  },
  "fonts": {
    "body": "Times New Roman",
    "size": 12,
    "line_spacing": 1.5
  }
}
```

---

## Error Handling & Edge Cases

### Common Edge Cases
1. **Ambiguous Numbering**: `1.a.i` vs `1(a)(i)` vs `Q1ai`
   - **Solution**: LLM validates and suggests correction
   
2. **Mathematical Expressions**: LaTeX, MathML, images
   - **Solution**: Rule engine skips, LLM preserves

3. **Tables and Figures**: Appendix data
   - **Solution**: Preserve formatting, only adjust spacing

4. **Mixed Languages**: English + Chinese characters
   - **Solution**: Unicode-safe processing

5. **Corrupted DOCX**: Malformed XML
   - **Solution**: Validation before processing, user notification

### Error Response Flow
```python
try:
    formatted_doc = formatting_engine.process(original_doc)
except CorruptedDocumentError as e:
    return {
        "status": "error",
        "message": "Document appears corrupted. Please re-export from Word.",
        "error_code": "DOC_001"
    }
except TemplateNotFoundError as e:
    return {
        "status": "error",
        "message": "No matching template found. Please contact admin.",
        "error_code": "TPL_001"
    }
except LLMValidationTimeout as e:
    return {
        "status": "partial_success",
        "message": "Formatting completed, but validation timed out. Review manually.",
        "compliance_score": None,
        "formatted_doc": formatted_doc
    }
```

---

## Testing Strategy

### Unit Tests
```python
# tests/test_formatting_engine.py
import pytest
from src.agents.formatting_engine import RuleBasedFormatter

def test_numbering_correction():
    formatter = RuleBasedFormatter(template_rules)
    
    input_text = "1) Question one\n1a) Sub question"
    expected = "Q1. Question one\n   (a) Sub question"
    
    result = formatter.fix_numbering(input_text)
    assert result == expected

def test_marks_formatting():
    formatter = RuleBasedFormatter(template_rules)
    
    input_text = "Calculate the value (3marks)"
    expected = "Calculate the value (3 marks)"
    
    result = formatter.format_marks(input_text)
    assert result == expected
```

### Integration Tests
```python
# tests/test_end_to_end.py
import pytest
from src.agents.coordinator_agent import CoordinatorAgent

@pytest.mark.asyncio
async def test_full_formatting_workflow():
    coordinator = CoordinatorAgent()
    
    # Upload test file
    job_id = await coordinator.upload_file("tests/samples/messy_exam.docx")
    
    # Process
    result = await coordinator.process_exam(job_id)
    
    # Assertions
    assert result['status'] == 'success'
    assert result['compliance_score'] >= 0.85
    assert 'formatted_url' in result
    assert 'diff_report_url' in result
```

### Load Testing
```bash
# Use Azure Load Testing service
# Simulate 100 concurrent users uploading exams

az load test create \
  --test-id "examops-load-test" \
  --load-test-config-file "load-test-config.yaml" \
  --resource-group "examops-rg"
```

---

## Deployment Guide

### Prerequisites
```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Install Python 3.11
sudo apt install python3.11 python3.11-venv

# Install Azure Functions Core Tools
npm install -g azure-functions-core-tools@4
```

### Step 1: Azure Resource Provisioning
```bash
# Login to Azure
az login

# Create resource group
az group create \
  --name examops-rg \
  --location southeastasia

# Create storage account
az storage account create \
  --name examopsstorage \
  --resource-group examops-rg \
  --location southeastasia \
  --sku Standard_LRS

# Create containers
az storage container create \
  --name examops-input \
  --account-name examopsstorage

az storage container create \
  --name examops-output \
  --account-name examopsstorage

# Create Azure Function App
az functionapp create \
  --name examops-functions \
  --resource-group examops-rg \
  --consumption-plan-location southeastasia \
  --runtime python \
  --runtime-version 3.11 \
  --storage-account examopsstorage \
  --os-type Linux

# Create Azure AI Search
az search service create \
  --name examops-search \
  --resource-group examops-rg \
  --sku free \
  --location southeastasia

# Create Azure OpenAI (via Foundry)
az cognitiveservices account create \
  --name examops-openai \
  --resource-group examops-rg \
  --kind OpenAI \
  --sku S0 \
  --location eastus \
  --yes
```

### Step 2: Deploy Function Code
```bash
# Navigate to project
cd examops-orchestrator

# Install dependencies
pip install -r requirements.txt

# Deploy to Azure Functions
func azure functionapp publish examops-functions
```

### Step 3: Configure Teams Bot
```bash
# Create Bot registration in Azure Portal
# Get App ID and Secret

# Configure Bot endpoint
az bot create \
  --name examops-bot \
  --resource-group examops-rg \
  --kind registration \
  --endpoint https://examops-functions.azurewebsites.net/api/messages \
  --app-id <APP_ID>

# Connect to Teams channel
az bot teams create \
  --name examops-bot \
  --resource-group examops-rg
```

### Step 4: Upload Template to Vector DB
```python
# scripts/upload_template.py
from azure.search.documents import SearchClient
import json

template_data = {
    "template_id": "suc_engineering_v1",
    "campus": "southern_university_college",
    "rules": json.dumps(template_rules),
    "embedding_vector": generate_embedding("SUC Engineering exam template")
}

search_client.upload_documents([template_data])
print("✅ Template uploaded to Vector DB")
```

### Step 5: Test Deployment
```bash
# Test Azure Function endpoint
curl -X POST https://examops-functions.azurewebsites.net/api/format_exam \
  -H "Content-Type: application/json" \
  -d '{"job_id": "test-123"}'

# Test Teams Bot (manual via Teams app)
```

---

## Hackathon Demo Checklist

### Pre-Demo Setup (Day Before)
- [ ] Deploy all Azure services (production environment)
- [ ] Upload 3 test templates to Vector DB
- [ ] Prepare 3 messy exam papers (real examples from faculty)
- [ ] Test full workflow end-to-end (5 dry runs)
- [ ] Record backup demo video (in case of live issues)
- [ ] Prepare slides with before/after screenshots
- [ ] Print architecture diagrams (judges love visuals!)

### Demo Flow (5 minutes)
**Minute 1: Problem Statement**
- Show messy exam paper (projected on screen)
- Highlight issues: wrong numbering, bad spacing, missing headers
- Quote: "Lecturers waste 2-4 hours on this!"

**Minute 2: Solution Overview**
- Show architecture diagram
- Emphasize: "Hybrid AI + Rule Engine for 95% accuracy"
- Mention: "Multi-campus scalable via Vector DB"

**Minute 3: Live Demo**
- Open Teams Bot
- Upload messy exam: `/upload`
- Trigger formatting: `/format`
- Show progress indicator
- Display results (15 seconds later):
  - ✅ Compliance: 95%
  - 📥 Download formatted .docx
  - 📊 Diff report (HTML)

**Minute 4: Show Impact**
- Open formatted exam in Word
- Side-by-side comparison with original
- Highlight: "Perfect numbering, spacing, headers"
- Show diff report: "25 fixes applied automatically"

**Minute 5: Future Vision**
- Mention Phase 2: CLO mapping, moderation automation
- Emphasize: "Built for hackathon, ready for production"
- Thank judges + Q&A

### Judging Criteria Alignment

| Criteria | How ExamOps Delivers | Score Target |
|----------|---------------------|--------------|
| **Technological Implementation** | Azure-only stack, Agent Framework, MCP, Foundry | 25/25 |
| **Agentic Design** | 4 specialized agents (Coordinator, File Handler, Formatter, Diff) | 20/20 |
| **Real-World Impact** | Saves 2-4 hours per exam, 90%+ compliance, multi-campus scalable | 20/20 |
| **UX & Presentation** | Simple Teams Bot, visual diff reports, clear before/after | 20/20 |
| **Innovation** | Hybrid AI+Rules, Vector DB for templates, production-ready | 15/15 |
| **Total** | | **100/100** |

---

## Troubleshooting Guide

### Common Issues

**Issue 1: LLM validation timeout**
```python
# Solution: Implement retry logic with exponential backoff
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def validate_with_llm(content):
    return await llm_client.validate(content)
```

**Issue 2: Template not found in Vector DB**
```python
# Solution: Fallback to default template
if not template:
    logger.warning("Template not found, using default")
    template = load_default_template("suc_engineering_v1")
```

**Issue 3: python-docx corrupts mathematical equations**
```python
# Solution: Preserve equation runs
from docx.oxml import CT_R

def preserve_equations(paragraph):
    for run in paragraph.runs:
        if run.element.xpath('.//m:oMath'):
            # Skip equation runs
            continue
```

**Issue 4: Teams Bot not responding**
```bash
# Check Azure Function logs
az functionapp logs tail \
  --name examops-functions \
  --resource-group examops-rg

# Restart Function App
az functionapp restart \
  --name examops-functions \
  --resource-group examops-rg
```

---

## Success Metrics Dashboard (Azure Monitor)

### KPIs to Track
```json
{
  "formatting_metrics": {
    "total_papers_processed": 150,
    "success_rate": 0.96,
    "avg_compliance_score": 0.94,
    "avg_processing_time_seconds": 14.2,
    "user_satisfaction": 4.7
  },
  "cost_metrics": {
    "total_monthly_cost": 3.50,
    "cost_per_paper": 0.023,
    "openai_token_usage": 485000
  },
  "quality_metrics": {
    "papers_rejected_after_formatting": 3,
    "manual_fixes_required": 8,
    "compliance_score_distribution": {
      "90-100%": 142,
      "80-89%": 6,
      "70-79%": 2,
      "below_70%": 0
    }
  }
}
```

---

## Conclusion

ExamOps Orchestrator is a **production-ready, scalable, cost-effective** solution to a real academic pain point. By combining:
- **Deterministic rule-based formatting** (speed + accuracy)
- **LLM validation** (edge case handling)
- **Vector database** (multi-campus scalability)
- **Azure-native architecture** (compliance with hackathon requirements)

...we deliver a system that:
1. **Saves 2-4 hours per exam paper**
2. **Achieves 90%+ template compliance**
3. **Costs <$5/month for MVP usage**
4. **Scales to multiple campuses**
5. **Ready for Phase 2 intelligence expansion**

**Next Steps**:
1. Review this document with development team
2. Set up Azure resources (Day 1)
3. Implement core formatting engine (Days 2-5)
4. Integrate Teams Bot (Days 6-7)
5. Test with real exam papers (Days 8-10)
6. Prepare demo materials (Days 11-12)
7. **Win the hackathon!** 🏆

---

## Appendix: Useful Links

- [Microsoft Agent Framework Docs](https://github.com/microsoft/semantic-kernel)
- [Azure MCP Documentation](https://learn.microsoft.com/azure/ai-studio/how-to/use-mcp)
- [Azure OpenAI via Foundry](https://learn.microsoft.com/azure/ai-studio/what-is-ai-studio)
- [python-docx Documentation](https://python-docx.readthedocs.io/)
- [Azure Bot Framework SDK](https://learn.microsoft.com/azure/bot-service/)
- [Azure AI Search Vector Search](https://learn.microsoft.com/azure/search/vector-search-overview)
