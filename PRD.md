# 📘 Product Requirements Document (PRD)
# ExamOps Orchestrator

**Version**: 1.0  
**Date**: February 12, 2026  
**Status**: Active Development (Hackathon MVP)  
**Team**: Southern University College Engineering & IT Faculty

---

## Tagline
**"The AI That Knows Your Exam Template Better Than You Do."**

---

## 🧭 1. Executive Summary

### What is ExamOps Orchestrator?
ExamOps Orchestrator is an **AI-powered, multi-agent academic workflow system** designed to automate final exam paper preparation within the Faculty of Engineering and Information Technology, Southern University College. 

### The Core Problem
Lecturers currently waste **2-4 hours per exam paper** manually adjusting:
- Margins, headers, footers
- Question numbering (Q1. → (a) → (i))
- Marks formatting: `(3 marks)` with exact spacing rules
- CLO alignment entries
- Template-specific institutional formatting

This results in:
- ❌ Papers bounced back during vetting/moderation
- ❌ Inconsistent formatting across courses
- ❌ Delayed exam processing timelines
- ❌ Reduced time for improving question quality

### The Solution (Phase 1 MVP)
**Strict, template-adherent exam formatting** through:
1. **Hybrid AI + Rule-Based Engine**:
   - Rule engine: Deterministic formatting (python-docx)
   - AI validator: Azure OpenAI GPT-4o-mini for edge cases
2. **Vector Database**: Store template rules for multi-campus scalability
3. **Microsoft Teams Bot**: Simple upload → format → download workflow
4. **Diff Reporting**: Visual before/after comparison for lecturer confidence

### Technology Stack (AI Dev Days Hackathon Requirements)
✅ **Microsoft Agent Framework** (Semantic Kernel)  
✅ **Azure MCP** (OneDrive/SharePoint integration)  
✅ **Azure AI Foundry** (Centralized AI orchestration)  
✅ **Azure-Native Services** (Functions, Blob Storage, AI Search, OpenAI)

### Success Metrics (MVP Goals)
| Metric | Target | Current Baseline |
|--------|--------|------------------|
| Manual formatting time reduction | 90% (from 2-4hrs → 10-15min) | 0% |
| Template compliance rate | 95%+ | ~60% (manual errors) |
| Processing speed | <20 seconds per paper | N/A |
| Moderation rejection rate (due to formatting) | <5% | ~25% |
| User satisfaction score | 4.5/5.0 | 2.8/5.0 (current manual process) |

---

## 🎯 2. Problem Statement

### Current Workflow Pain Points

#### 2.1 Lecturer Experience
**Scenario**: Dr. Tan prepares final exam for *Data Structures & Algorithms*
1. ⏰ **Hour 1**: Downloads old template (possibly outdated version)
2. ⏰ **Hour 2**: Copy-pastes questions, manually adjusts numbering
3. ⏰ **Hour 3**: Fights with Word to fix indentation (Tab 0.5 × 6 for sub-questions)
4. ⏰ **Hour 4**: Realizes marks totals don't match, recalculates
5. 📧 **Day 2**: Receives rejection from Course Coordinator due to:
   - Wrong header format
   - Inconsistent spacing around colons ("DATE :" vs "DATE:")
   - Missing CLO alignment entries
6. ⏰ **Hour 5-6**: Rework and resubmit

**Total Time Wasted**: 6 hours  
**Emotional Cost**: High frustration, reduced focus on question quality

#### 2.2 Course Coordinator Experience
**Scenario**: Dr. Lee reviews 15 exam papers before moderation
- ❌ 8 papers have formatting errors → sent back for revision
- ❌ 3 papers have inconsistent numbering schemes
- ❌ 5 papers missing proper CLO alignment tables
- ⏰ Spends 1 hour per paper on quality checks (15 hours total)

#### 2.3 Institutional Impact
- **Delayed Exam Cycles**: Formatting issues push back moderation timelines
- **Inconsistent Quality**: Student experience varies based on lecturer's Word skills
- **Admin Overhead**: Exam unit staff manually fix common errors
- **Missed Opportunities**: Time spent formatting ≠ time improving pedagogy

### Root Causes
1. **Template Complexity**: 40+ formatting rules documented across 3 guideline documents
2. **Human Error**: Easy to miss subtle spacing/indentation requirements
3. **Version Control Issues**: Lecturers use outdated templates
4. **Tool Limitations**: Microsoft Word doesn't enforce custom institutional rules
5. **Knowledge Transfer**: New faculty unaware of all formatting conventions

---

## 🎯 3. Project Goals

### Primary Goal (Phase 1: AI Dev Days Hackathon)
**Deliver a production-ready exam formatting agent** that:
- ✅ Accepts raw exam drafts (.docx) via Teams Bot
- ✅ Applies 100% template compliance automatically
- ✅ Produces formatted output + diff report within 20 seconds
- ✅ Achieves 95%+ compliance score validated by LLM
- ✅ Demonstrates multi-campus scalability via Vector DB architecture

**Non-Goals for Phase 1**:
- ❌ Automatic CLO mapping (manual entry preserved)
- ❌ Answer scheme formatting
- ❌ Moderation form auto-fill
- ❌ Integration with LMS/SIS

### Secondary Goals (Phase 2: Post-Hackathon)
Expand intelligence layer with additional agents:
1. **CLO Mapping Agent**: Automatically align questions to Course Learning Outcomes
2. **Question Quality Agent**: Analyze difficulty distribution (Bloom's taxonomy)
3. **Marks Validation Agent**: Ensure totals match, flag discrepancies
4. **Moderation Report Generator**: Auto-fill AARO-FM-030 forms

### Long-Term Vision (Phase 3: 6-12 Months)
**Full Assessment Lifecycle Orchestrator**:
```
Draft → Format → Moderate → Teach → Assess → Analyze → Report (EoBE)
```
- Student-level grading analytics
- Plagiarism detection for answer scripts
- Evidence of Best Evidence (EoBE) summary generation
- Automated archival to institutional repository

---

## 👥 4. Target Users

### Primary Users (Phase 1)
| User Role | Count (SUC) | Pain Points | Success Criteria |
|-----------|-------------|-------------|------------------|
| **Lecturers** | ~40 (Engineering & IT) | Hours wasted on formatting, confusion about rules | "I upload messy draft, get perfect template in 20 seconds" |
| **Course Coordinators** | ~8 (per semester) | Reviewing 10-20 papers, sending back for rework | "95% of submissions need zero formatting fixes" |

### Secondary Users (Phase 2+)
| User Role | Pain Points | How ExamOps Helps |
|-----------|-------------|-------------------|
| **Internal Moderators** | Need consistent format to focus on content quality | Pre-formatted papers → faster moderation |
| **Heads of Programme** | Approve multiple exams under tight deadlines | Batch processing, compliance dashboards |
| **Exam Unit Staff** | Manual final checks before printing | Automated pre-flight validation |

### Future Users (Multi-Campus Expansion)
- Other faculties at SUC (Business, Education, etc.)
- Partner universities in Malaysia/ASEAN region
- International accreditation bodies (template compliance proof)

---

## 📦 5. In-Scope (MVP – Phase 1)

### 5.1 Functional Requirements

#### FR-1: File Upload & Handling
- **Input**: Microsoft Word .docx files (Office 2016+ format)
- **Channels**: 
  - Microsoft Teams Bot (`/upload` command)
  - Future: OneDrive folder monitoring (via Azure MCP)
- **Validation**: 
  - Max file size: 10 MB
  - File type check (reject .doc, .pdf, .txt)
  - Malware scan (Azure Storage built-in)

#### FR-2: Template Rule Enforcement
**Must reproduce exactly**:

##### A. Header/Footer
```
┌─────────────────────────────────────────────────┐
│     SOUTHERN UNIVERSITY COLLEGE                  │
│ FACULTY OF ENGINEERING AND INFORMATION TECHNOLOGY│
│                                                  │
│              [Page Number]                       │
└─────────────────────────────────────────────────┘
```
- Font: Arial 12pt, centered
- Header on every page except page 1
- Page numbers: Bottom center, Arabic numerals

##### B. Title Block
```
FINAL EXAMINATION
Semester A Academic Session 2024/2025

Program : Bachelor of Computer Science (Honours)
          Bachelor of Information Technology (Honours)

Course Code : BAIT2073
Course Name : Data Structures & Algorithms

DATE : 15 June 2025
DURATION : 3 hours
```
**Spacing Rules**:
- 1 space before and after colon (` : `)
- Double-line spacing between sections
- Multiple programs: separate lines, aligned

##### C. Instruction Block
```
ANSWER ALL QUESTIONS.
ALL QUESTIONS CARRY EQUAL MARKS UNLESS OTHERWISE STATED.
```
- Style: Bold, ALL CAPS
- Position: After title block, before Q1

##### D. Question Numbering (Critical!)
**Input variations** (all messy formats seen in real submissions):
```
❌ Q1)              → ✅ Q1.
❌ 1.               → ✅ Q1.
❌ 1a)              → ✅    (a)
❌ a)               → ✅    (a)
❌ 1(a)(i)          → ✅       (i)
❌ Q1 a i           → ✅ Q1. (a) (i)
```

**Standard hierarchy**:
```
Q1.                     (Level 1: 0cm indent)
   (a)                  (Level 2: 1.5cm indent = Tab 0.5 × 3)
      (i)               (Level 3: 3.0cm indent = Tab 0.5 × 6)
         (A)            (Level 4: 4.5cm indent - rarely used)
```

##### E. Marks Formatting
```
✅ Correct: Calculate the Big-O complexity.                    (3 marks)
❌ Wrong:   Calculate the Big-O complexity. (3marks)
❌ Wrong:   Calculate the Big-O complexity.(3 marks)
❌ Wrong:   Calculate the Big-O complexity  (3 marks)
```
**Rules**:
- 1 space before opening bracket `(`
- No space between number and "marks"
- Right-aligned on same line as question text
- Alternative: New line, indented to match question level

##### F. Total Marks
```
                                              [Total : 25 marks]
```
- Square brackets, 1 space before/after colon
- Right-aligned
- End of each major question

##### G. Continuation Across Pages
When a question spans multiple pages:
```
Page 1:
Q2. Explain the difference between...
   (a) Arrays and linked lists

Page 2:
Q2. (Continued)                    [underlined]
   (b) Stacks and queues
```

##### H. Appendix Formatting (if present)
```
APPENDIX

Table 1: ASCII Character Codes
┌──────┬────────┐
│ Char │  Code  │
├──────┼────────┤
│  A   │   65   │
│  B   │   66   │
└──────┴────────┘
```
- Separate section after last question
- Tables: Preserve structure, adjust spacing only

#### FR-3: Output Generation
**Deliverables** (all within 20 seconds):
1. **Formatted Exam Paper.docx**
   - Download link (Azure Blob SAS token, 1-hour expiry)
   - OneDrive copy (optional, if user connected)
2. **Diff Report (HTML)**
   - Color-coded changes:
     - 🟢 Green: Additions (headers, missing elements)
     - 🔴 Red: Deletions (wrong spacing, bad formatting)
     - 🟡 Yellow: Modifications (numbering corrections)
   - Summary statistics (X numbering fixes, Y spacing fixes)
3. **Compliance Score**
   - LLM-generated: 0-100%
   - Breakdown: Header (20%), Numbering (30%), Marks (20%), Spacing (15%), Other (15%)

#### FR-4: Diff Comparison Viewer
**Purpose**: Build lecturer trust by showing exactly what changed

**Format**: HTML report with side-by-side view
```html
┌─────────────────────────────┬─────────────────────────────┐
│         BEFORE              │          AFTER              │
├─────────────────────────────┼─────────────────────────────┤
│ 1) Question one             │ Q1. Question one            │ ← Numbering fix
│ 1a) Sub-question            │    (a) Sub-question         │ ← Indentation fix
│ Calculate value(3marks)     │ Calculate value (3 marks)   │ ← Spacing fix
│ DATE: 15 June               │ DATE : 15 June              │ ← Colon spacing
└─────────────────────────────┴─────────────────────────────┘
```

**Delivery**: Embedded in Teams Bot message as adaptive card

### 5.2 Non-Functional Requirements

#### NFR-1: Performance
- **Processing Time**: <20 seconds for typical exam (5 pages, 4 questions)
- **Concurrent Users**: Support 10 simultaneous formatting requests (hackathon demo)
- **Scalability Target**: 100 users, 500 papers/month (Phase 2)

#### NFR-2: Reliability
- **Uptime**: 99% (Azure Functions SLA)
- **Formatting Consistency**: 100% deterministic for same input
- **Error Recovery**: Graceful degradation if LLM timeout (return rule-based output with warning)

#### NFR-3: Security & Compliance
- **Data Encryption**: 
  - At rest: Azure Storage AES-256
  - In transit: TLS 1.2+
- **Access Control**: Azure AD authentication for bot users
- **Data Retention**: 
  - Original files deleted after 24 hours
  - Formatted outputs: 7-day retention (configurable)
- **Audit Trail**: All actions logged to Application Insights
- **Exam Confidentiality**: 
  - No logging of question content
  - SAS tokens for secure download (1-hour expiry)

#### NFR-4: Usability
**Principle**: "Simpler than sending an email"

**Teams Bot Commands**:
```
/upload       - Start upload flow (attach .docx)
/format       - Process uploaded file
/download     - Get formatted output links
/diff         - View comparison report
/help         - Show command reference
/feedback     - Report issues or suggest improvements
```

**User Journey** (5 steps, <2 minutes):
1. Open Teams, message `@ExamOps Bot`
2. Type `/upload`, attach `exam_draft.docx`
3. Type `/format` → Wait 15 seconds
4. Receive results message with:
   - ✅ Compliance: 95%
   - 📥 Download formatted .docx
   - 📊 View diff report
5. Review, download, done!

#### NFR-5: Maintainability
**Architecture Principle**: Modular agents, extensible design

**Component Independence**:
- Rule engine: Pure Python, no LLM dependency
- LLM validator: Swappable (GPT-4o-mini → GPT-4 → Claude)
- Template storage: Database-agnostic (Azure AI Search → PostgreSQL)
- Bot interface: Decoupled from core logic (Teams → Slack → Web)

**Configuration-Driven**:
```yaml
# config/template_rules.yaml
template_id: suc_engineering_v1
version: 1.0
rules:
  margins: {top: 2.54, bottom: 2.54, left: 2.54, right: 2.54, unit: cm}
  fonts: {body: Times New Roman, size: 12}
  numbering:
    level_1: {format: "Q{n}.", indent: 0cm}
    level_2: {format: "({letter})", indent: 1.5cm}
    level_3: {format: "({roman})", indent: 3.0cm}
  # ... (100+ rules)
```

---

## 🚫 6. Out-of-Scope (Phase 1)

Explicitly **NOT included** in MVP to maintain focus:

### 6.1 Content Intelligence
- ❌ Automatic CLO (Course Learning Outcome) mapping
  - *Why deferred*: Requires course database integration, complex NLP
  - *Phase 2 requirement*: LMS/SIS access, CLO taxonomy database
- ❌ Question difficulty classification (Bloom's taxonomy)
- ❌ Duplicate question detection (plagiarism check)
- ❌ Language quality checks (grammar, clarity)

### 6.2 Workflow Automation
- ❌ Answer scheme formatting (separate template, different rules)
- ❌ Moderation form (AARO-FM-030) auto-fill
- ❌ Email notifications to stakeholders
- ❌ Approval workflows (Lecturer → Coordinator → HoD)

### 6.3 System Integrations
- ❌ LMS integration (Moodle, Canvas)
- ❌ Student Information System (SIS) data pull
- ❌ EoBE (Evidence of Best Evidence) report generation
- ❌ Institutional repository upload

### 6.4 Advanced Features
- ❌ Batch processing (upload 10 exams, format all)
- ❌ Custom template editor UI
- ❌ Version history / rollback
- ❌ Collaborative editing (multi-user)
- ❌ Mobile app (iOS/Android)

**Rationale**: MVP focuses on **core formatting pain** to deliver maximum impact with minimum complexity for hackathon timeline.

---

## 🧑‍💼 7. User Personas

### Persona 1: Dr. Tan Wei Lun (Primary User - Lecturer)
**Role**: Senior Lecturer, Computer Science  
**Age**: 42  
**Tech Proficiency**: Medium (comfortable with Office, basic Python)  
**Courses Taught**: Data Structures, Algorithms, Operating Systems

**Current Workflow**:
- Prepares 3 exams per semester (Final, Resit, Special)
- Spends 2-3 hours per exam on formatting
- Often copy-pastes from old templates → inconsistencies
- Has been rejected by coordinators 4 times in past 2 years

**Pain Points**:
1. 😤 "I waste a whole afternoon just fixing numbering and spacing"
2. 😫 "Word keeps breaking my indentation when I paste questions"
3. 😰 "I'm never sure if I followed all the template rules"
4. 😡 "Why isn't there just a button that fixes everything?"

**Goals**:
- ✅ Spend <15 minutes on formatting per exam
- ✅ Zero rejections due to formatting errors
- ✅ Focus time on improving question quality, not Word wrestling

**How ExamOps Helps**:
- Upload draft → Formatted in 20 seconds
- Diff report shows all fixes → builds confidence
- Compliance score 95%+ → no more rejections

**Quote**: *"This is like having a teaching assistant who actually knows the template rules!"*

---

### Persona 2: Dr. Lee Siew Mei (Secondary User - Course Coordinator)
**Role**: Associate Professor, Head of IT Programme  
**Age**: 51  
**Tech Proficiency**: High (PhD in CS, comfortable with most tools)  
**Responsibility**: Oversees 15 courses, reviews all exam papers before moderation

**Current Workflow**:
- Receives 10-15 exam drafts per semester
- Manually checks each for template compliance
- Creates detailed feedback documents → sends back to lecturers
- Chases late submissions due to formatting rework

**Pain Points**:
1. 😩 "I spend 1 hour per paper just checking formatting, not content"
2. 🤦‍♀️ "Same mistakes every semester (wrong numbering, missing headers)"
3. ⏰ "Delays from formatting rework push moderation deadlines"
4. 📧 "Endless email threads: 'Please fix spacing', 'Still not right', etc."

**Goals**:
- ✅ Reduce review time from 1 hour → 15 minutes per paper
- ✅ 90%+ submissions pass format check on first attempt
- ✅ Focus review on content quality, CLO alignment, difficulty distribution

**How ExamOps Helps**:
- Lecturers submit pre-formatted papers → no format review needed
- Compliance scores visible → prioritize low-scoring papers
- Diff reports → quickly verify what was changed

**Success Metric**: *"If I can review 15 papers in one afternoon instead of three days, this is a game-changer."*

---

### Persona 3: Prof. Ahmad bin Hassan (Tertiary User - Head of Department)
**Role**: Professor, Dean of Engineering & IT Faculty  
**Age**: 58  
**Tech Proficiency**: Low (delegates technical tasks to staff)  
**Responsibility**: Final approval of all exams, strategic planning

**Current Workflow**:
- Signs off 30-40 exam papers per semester
- Trusts coordinators for quality, but occasionally spot-checks
- Receives complaints from external moderators about inconsistent formatting

**Pain Points**:
1. 🎯 "Institutional reputation: External moderators notice our inconsistencies"
2. 📊 "No visibility into formatting quality across faculty"
3. ⚖️ "Worried about accreditation audits (template compliance proof)"
4. 🚀 "Want to expand to other faculties, but process doesn't scale"

**Goals**:
- ✅ Consistent, professional exam presentation across all courses
- ✅ Data-driven insights (compliance trends, common errors)
- ✅ Scalable solution for 3 faculties (Engineering, Business, Education)

**How ExamOps Helps**:
- Automated compliance enforcement → consistent quality
- Dashboard: Faculty-wide formatting metrics (Phase 2)
- Multi-template support → ready for expansion

**Quote**: *"If this can save my lecturers 100 hours per semester, that's 100 hours reinvested in research and teaching quality."*

---

### Anti-Persona: Dr. Khairul (Not a Target User)
**Role**: Lecturer who manually typesets exams in LaTeX  
**Tech Proficiency**: Very High (Computer Science PhD, loves automation)  
**Current Workflow**: Custom LaTeX templates with Makefile automation

**Why Not Target**:
- Already has automated workflow (LaTeX → PDF)
- Template enforces rules programmatically
- Small minority (<5% of faculty)
- ExamOps targets majority (Word users, ~95%)

**Potential Future Use**: Phase 3 could support LaTeX → .docx conversion for institutional archival.

---

## 🤖 8. Agent Design (Microsoft Agent Framework)

### 8.1 Architecture Pattern
**Orchestrator Pattern** with specialized agents coordinated by Semantic Kernel

```
┌─────────────────────────────────────────────────────────────┐
│           Coordinator Agent (Orchestrator)                   │
│  - Entry point from Teams Bot                                │
│  - Workflow state management                                 │
│  - Agent invocation & result aggregation                     │
└───────┬──────────────┬──────────────┬─────────────────────┘
        │              │              │
        ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐
│ File Handler │ │  Formatting  │ │  Diff Generator      │
│    Agent     │ │    Engine    │ │     Agent            │
│              │ │    Agent     │ │                      │
│ - Upload     │ │ - Rule-based │ │ - Compare docs       │
│ - Download   │ │ - LLM valid. │ │ - Generate HTML      │
│ - OneDrive   │ │ - Template   │ │ - Stats summary      │
└──────────────┘ └──────────────┘ └──────────────────────┘
        │              │              │
        ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐
│ Azure Blob   │ │ Azure OpenAI │ │ Azure AI Search      │
│   Storage    │ │  (Foundry)   │ │  (Vector DB)         │
└──────────────┘ └──────────────┘ └──────────────────────┘
```

### 8.2 Agent Specifications

#### Agent 1: Coordinator Agent
**Responsibility**: Orchestrate end-to-end workflow

**Technology**: Semantic Kernel with Azure Functions trigger

**Inputs**:
- `job_id`: Unique identifier for processing job
- `user_id`: Teams user requesting format
- `file_url`: Blob storage URL of uploaded .docx

**Workflow Steps**:
```python
async def coordinate_formatting(job_id, user_id, file_url):
    # Step 1: Retrieve file
    original_doc = await file_handler.download_from_blob(file_url)
    
    # Step 2: Get template rules
    template = await file_handler.get_template_from_vectordb(
        query="SUC Engineering exam template"
    )
    
    # Step 3: Format document
    formatted_doc = await formatting_engine.process(
        original=original_doc,
        template=template
    )
    
    # Step 4: Validate with LLM
    validation = await formatting_engine.validate_with_llm(
        original=original_doc,
        formatted=formatted_doc,
        template=template
    )
    
    # Step 5: Generate diff
    diff_report = await diff_generator.create_html_diff(
        original=original_doc,
        formatted=formatted_doc,
        validation=validation
    )
    
    # Step 6: Save outputs
    output_urls = await file_handler.save_outputs(
        formatted_doc=formatted_doc,
        diff_report=diff_report,
        job_id=job_id
    )
    
    # Step 7: Return results
    return {
        "status": "success",
        "compliance_score": validation["score"],
        "formatted_url": output_urls["docx"],
        "diff_url": output_urls["html"],
        "onedrive_link": output_urls["onedrive"],
        "summary": validation["summary"]
    }
```

**Error Handling**:
- Timeout: Return rule-based output with warning ("LLM validation timed out")
- Invalid file: Reject with clear message ("File appears corrupted")
- Template not found: Use default SUC template, log warning

---

#### Agent 2: File Handler Agent (Azure MCP Integration)
**Responsibility**: Manage file I/O with Azure services

**Technology**: 
- Azure Blob Storage SDK
- Microsoft Graph API (OneDrive)
- Azure MCP connectors

**Functions**:

##### Function 2.1: Upload to Blob
```python
async def upload_to_blob(file_stream, filename, user_id):
    """
    Upload to Azure Blob Storage
    Container: examops-input
    Naming: {timestamp}_{user_id}_{filename}
    Returns: Blob URL + SAS token
    """
    blob_name = f"{datetime.now().isoformat()}_{user_id}_{filename}"
    blob_client = blob_service.get_blob_client(
        container="examops-input",
        blob=blob_name
    )
    await blob_client.upload_blob(file_stream, overwrite=True)
    
    # Generate SAS token (1-hour expiry)
    sas_token = generate_sas_token(blob_client, expiry_hours=1)
    return f"{blob_client.url}?{sas_token}"
```

##### Function 2.2: Retrieve Template from Vector DB
```python
async def get_template_from_vectordb(query):
    """
    Semantic search in Azure AI Search
    Returns: Template rules JSON + sample .docx URL
    """
    # Generate query embedding
    embedding = await openai_client.embeddings.create(
        model="text-embedding-ada-002",
        input=query
    )
    
    # Vector search
    search_client = SearchClient(
        endpoint=SEARCH_ENDPOINT,
        index_name="exam-templates",
        credential=SEARCH_KEY
    )
    
    results = search_client.search(
        search_text=None,
        vector_queries=[{
            "vector": embedding.data[0].embedding,
            "k_nearest_neighbors": 1,
            "fields": "embedding_vector"
        }]
    )
    
    top_result = next(results)
    return json.loads(top_result["rules"])
```

##### Function 2.3: Save Outputs & Create OneDrive Link
```python
async def save_outputs(formatted_doc, diff_report, job_id):
    """
    Save to Blob + create OneDrive sharing link
    Returns: Dict with download URLs
    """
    # Save formatted .docx
    docx_blob = f"output/{job_id}_formatted.docx"
    docx_url = await upload_to_blob(formatted_doc, docx_blob, "system")
    
    # Save diff report (HTML)
    html_blob = f"output/{job_id}_diff.html"
    html_url = await upload_to_blob(diff_report, html_blob, "system")
    
    # Create OneDrive link (optional)
    onedrive_link = await create_onedrive_share_link(docx_url)
    
    return {
        "docx": docx_url,
        "html": html_url,
        "onedrive": onedrive_link
    }
```

**Azure MCP Configuration**:
```yaml
# Azure MCP connector definition
mcp_connector:
  name: examops-storage
  type: azure_storage
  config:
    connection_string: ${AZURE_STORAGE_CONNECTION_STRING}
    containers:
      input: examops-input
      output: examops-output
      templates: examops-templates
    retention_policy:
      input: 24h
      output: 168h  # 7 days
```

---

#### Agent 3: Formatting Engine Agent (Hybrid: Rules + LLM)
**Responsibility**: Apply template rules with LLM validation

**Architecture**: Two-layer processing

##### Layer 1: Rule-Based Formatter
**Technology**: python-docx library

**Processing Pipeline**:
```python
class RuleBasedFormatter:
    def __init__(self, template_rules):
        self.rules = template_rules
        
    def process(self, doc_path):
        """Main formatting pipeline"""
        doc = Document(doc_path)
        
        # Apply formatting in sequence
        self.apply_header_footer(doc)
        self.standardize_margins(doc)
        self.fix_numbering(doc)
        self.format_marks(doc)
        self.enforce_spacing_rules(doc)
        self.fix_indentation(doc)
        self.add_continuation_markers(doc)
        
        return doc
    
    def fix_numbering(self, doc):
        """
        Convert messy numbering to standard format
        Patterns handled:
          Q1) → Q1.
          1a) → (a)
          1.a.i → (a)(i)
          Q1ai → Q1. (a) (i)
        """
        import re
        
        # Regex patterns for common mistakes
        patterns = {
            r'Q(\d+)\)': r'Q\1.',           # Q1) → Q1.
            r'^(\d+)\)': r'Q\1.',           # 1) → Q1.
            r'\s+(\d+)([a-z])\)': r' (\2)', # 1a) → (a)
            r'\(([a-z])\)\(([ivx]+)\)': r'(\1)\n      (\2)',  # Nested
        }
        
        for para in doc.paragraphs:
            original = para.text
            for pattern, replacement in patterns.items():
                para.text = re.sub(pattern, replacement, para.text)
                
            # Adjust indentation based on level
            if para.text.startswith('Q'):
                para.paragraph_format.left_indent = Cm(0)
            elif re.match(r'\s*\([a-z]\)', para.text):
                para.paragraph_format.left_indent = Cm(1.5)
            elif re.match(r'\s*\([ivx]+\)', para.text):
                para.paragraph_format.left_indent = Cm(3.0)
```

**Key Rules Implemented**:
| Rule | Description | Implementation |
|------|-------------|----------------|
| Header/Footer | Institutional branding | `section.header.paragraphs[0].text = rules['header_text']` |
| Margins | 2.54cm all sides | `section.top_margin = Cm(2.54)` for all sections |
| Numbering | Q1. → (a) → (i) | Regex replacement + indentation adjustment |
| Marks | `(3 marks)` format | Right-align, ensure spacing: `r'\s+\((\d+)\s*marks\)'` |
| Spacing | 1 space before/after `:` | `text.replace(':', ' : ').replace('  ', ' ')` |
| Indentation | Tab 0.5 × 6 = 3.0cm | `para.paragraph_format.left_indent = Cm(n * 0.5)` |

##### Layer 2: LLM Validator (Azure OpenAI GPT-4o-mini)
**Technology**: Azure AI Foundry (centralized endpoint)

**Purpose**:
1. Validate rule-based output against template
2. Catch edge cases (ambiguous numbering, complex formatting)
3. Generate human-readable compliance report
4. Preserve mathematical expressions/special content

**Prompt Template**:
```python
VALIDATION_PROMPT = """
You are an exam paper formatting validator for Southern University College's Faculty of Engineering and Information Technology.

TEMPLATE RULES (from vector database):
{template_rules}

ORIGINAL DOCUMENT (before formatting):
{original_content}

FORMATTED DOCUMENT (after rule-based engine):
{formatted_content}

TASK:
1. Compare formatted document against template rules
2. Score compliance: 0-100%
3. Identify any issues the rule engine missed
4. Suggest fixes for ambiguous cases
5. Verify mathematical expressions were preserved

OUTPUT FORMAT (strict JSON):
{{
  "compliance_score": <0-100>,
  "category_scores": {{
    "header_footer": <0-100>,
    "numbering": <0-100>,
    "marks_formatting": <0-100>,
    "spacing": <0-100>,
    "indentation": <0-100>
  }},
  "issues_found": [
    {{
      "line_number": <int>,
      "category": "<header|numbering|marks|spacing|indentation>",
      "issue": "<description>",
      "suggestion": "<how to fix>",
      "severity": "<low|medium|high>"
    }}
  ],
  "edge_cases": [
    {{
      "description": "<what was ambiguous>",
      "resolution": "<how rule engine handled it>",
      "confidence": "<low|medium|high>"
    }}
  ],
  "math_expressions_preserved": <true|false>,
  "summary": "<2-3 sentence human-readable summary>"
}}

EXAMPLE OUTPUT:
{{
  "compliance_score": 94,
  "category_scores": {{
    "header_footer": 100,
    "numbering": 92,
    "marks_formatting": 95,
    "spacing": 90,
    "indentation": 95
  }},
  "issues_found": [
    {{
      "line_number": 42,
      "category": "numbering",
      "issue": "Ambiguous sub-numbering: '1.a.i' could be interpreted multiple ways",
      "suggestion": "Converted to standard '(a)(i)' format",
      "severity": "medium"
    }}
  ],
  "edge_cases": [
    {{
      "description": "Question uses unusual nested structure (4 levels deep)",
      "resolution": "Applied Level 4 indentation (4.5cm) as per template guidelines",
      "confidence": "high"
    }}
  ],
  "math_expressions_preserved": true,
  "summary": "Document formatting is 94% compliant with template. Fixed 12 numbering issues and 5 spacing violations. All mathematical expressions preserved correctly."
}}
"""
```

**Integration Code**:
```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

class LLMValidator:
    def __init__(self):
        self.client = AIProjectClient(
            endpoint=os.getenv("AZURE_FOUNDRY_ENDPOINT"),
            credential=DefaultAzureCredential()
        )
        
    async def validate(self, original, formatted, template_rules):
        """Call GPT-4o-mini via Foundry"""
        prompt = VALIDATION_PROMPT.format(
            template_rules=json.dumps(template_rules, indent=2),
            original_content=self._extract_text(original),
            formatted_content=self._extract_text(formatted)
        )
        
        response = await self.client.inference.get_chat_completions(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a precise exam template validator."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,  # Low temperature for consistency
            max_tokens=2000
        )
        
        # Parse JSON response
        result = json.loads(response.choices[0].message.content)
        
        # Log to Application Insights
        self._log_validation_result(result)
        
        return result
```

**Fallback Behavior** (if LLM fails):
```python
try:
    validation = await llm_validator.validate(...)
except Exception as e:
    logger.error(f"LLM validation failed: {e}")
    
    # Return rule-based output with warning
    validation = {
        "compliance_score": None,
        "summary": "Warning: LLM validation timed out. Document formatted using rule engine only. Please review manually.",
        "issues_found": [],
        "fallback_mode": True
    }
```

---

#### Agent 4: Diff Generator Agent
**Responsibility**: Create visual comparison reports

**Outputs**:
1. **HTML Diff Report** (primary - shown in Teams)
2. **Side-by-side Word Document** (optional download)
3. **Summary Statistics** (for Teams message)

**Implementation**:

##### Function 4.1: HTML Diff Generation
```python
import difflib
from docx import Document

class DiffGenerator:
    def create_html_diff(self, original_doc, formatted_doc, validation):
        """
        Generate color-coded HTML comparison
        Green: Additions (headers, formatting improvements)
        Red: Deletions (wrong spacing, bad formatting)
        Yellow: Modifications (numbering corrections)
        """
        # Extract text from both documents
        original_text = self._extract_text_with_formatting(original_doc)
        formatted_text = self._extract_text_with_formatting(formatted_doc)
        
        # Use difflib for line-by-line comparison
        differ = difflib.HtmlDiff(wrapcolumn=80)
        html = differ.make_file(
            original_text.splitlines(),
            formatted_text.splitlines(),
            fromdesc='Original Draft',
            todesc='Formatted (ExamOps)',
            context=True,  # Show context around changes
            numlines=3     # 3 lines of context
        )
        
        # Enhance with metadata
        html = self._add_summary_header(html, validation)
        html = self._add_change_statistics(html)
        html = self._add_css_styling(html)
        
        return html
    
    def _add_summary_header(self, html, validation):
        """Prepend summary card to HTML"""
        summary = f"""
        <div class="summary-card">
          <h2>ExamOps Formatting Summary</h2>
          <div class="score">
            <span class="score-value">{validation['compliance_score']}%</span>
            <span class="score-label">Compliance Score</span>
          </div>
          <div class="stats">
            <div class="stat">
              <strong>{len(validation['issues_found'])}</strong> issues fixed
            </div>
            <div class="stat">
              <strong>{validation['category_scores']['numbering']}</strong>% numbering accuracy
            </div>
            <div class="stat">
              <strong>{validation['category_scores']['spacing']}</strong>% spacing accuracy
            </div>
          </div>
          <p class="summary-text">{validation['summary']}</p>
        </div>
        """
        return html.replace('<body>', f'<body>{summary}')
```

##### Function 4.2: Summary Statistics
```python
def generate_summary_stats(self, original_doc, formatted_doc, validation):
    """
    Calculate statistics for Teams message
    Returns: Dict with counts of different change types
    """
    changes = {
        "numbering_fixes": 0,
        "spacing_fixes": 0,
        "mark_formatting_fixes": 0,
        "indentation_fixes": 0,
        "header_footer_added": False,
        "total_changes": 0
    }
    
    # Count from validation issues
    for issue in validation['issues_found']:
        category = issue['category']
        if category == 'numbering':
            changes['numbering_fixes'] += 1
        elif category == 'spacing':
            changes['spacing_fixes'] += 1
        elif category == 'marks_formatting':
            changes['mark_formatting_fixes'] += 1
        elif category == 'indentation':
            changes['indentation_fixes'] += 1
            
    changes['total_changes'] = sum([
        changes['numbering_fixes'],
        changes['spacing_fixes'],
        changes['mark_formatting_fixes'],
        changes['indentation_fixes']
    ])
    
    # Check if header was added
    if not self._has_header(original_doc) and self._has_header(formatted_doc):
        changes['header_footer_added'] = True
        
    return changes
```

**Teams Bot Display Format**:
```
╔══════════════════════════════════════════════════════════╗
║           ✅ FORMATTING COMPLETE                          ║
╚══════════════════════════════════════════════════════════╝

📊 Compliance Score: 95% 

📝 Changes Applied:
  • Numbering fixes: 12
  • Spacing corrections: 5
  • Mark formatting: 8
  • Indentation adjustments: 3
  • Header/footer: ✅ Added

📥 Download Options:
  1. 📄 Formatted Exam Paper.docx
  2. 📊 Diff Report (HTML)
  3. 📋 Side-by-side Comparison.docx

🔗 OneDrive Link: [Click here to access]

⚠️ Please review the diff report before finalizing!

[View Diff] [Download All] [Report Issue]
```

---

## 🏗️ 9. Architecture Diagram

### 9.1 System Context Diagram
```
┌─────────────────────────────────────────────────────────────────┐
│                    EXTERNAL SYSTEMS                              │
│                                                                  │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐        │
│  │   Lecturer  │  │Course Coord. │  │  Exam Unit      │        │
│  │   (Teams)   │  │   (Teams)    │  │  Staff (Teams)  │        │
│  └──────┬──────┘  └──────┬───────┘  └────────┬────────┘        │
│         │                 │                    │                 │
│         └─────────────────┼────────────────────┘                 │
│                           │                                      │
└───────────────────────────┼──────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                  EXAMOPS ORCHESTRATOR                            │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │         Microsoft Teams Bot (Azure Bot Service)         │    │
│  │  Commands: /upload /format /download /diff /help       │    │
│  └───────────────────────┬────────────────────────────────┘    │
│                          │                                      │
│                          ▼                                      │
│  ┌────────────────────────────────────────────────────────┐    │
│  │   Azure Functions (HTTP Trigger - Consumption Plan)    │    │
│  │              Coordinator Agent (Semantic Kernel)        │    │
│  └────┬───────────────┬───────────────┬────────────────┬──┘    │
│       │               │               │                │        │
│       ▼               ▼               ▼                ▼        │
│  ┌─────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐     │
│  │  File   │   │Formatting│   │   Diff   │   │  Azure   │     │
│  │ Handler │   │  Engine  │   │Generator │   │  OpenAI  │     │
│  │  Agent  │   │  Agent   │   │  Agent   │   │(Foundry) │     │
│  └────┬────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘     │
│       │             │              │              │            │
│       ▼             ▼              ▼              ▼            │
│  ┌────────────────────────────────────────────────────────┐    │
│  │              AZURE BACKEND SERVICES                     │    │
│  │                                                         │    │
│  │  • Azure Blob Storage (Input/Output/Templates)         │    │
│  │  • Azure AI Search (Vector DB for template rules)      │    │
│  │  • Azure Application Insights (Logging/Monitoring)     │    │
│  │  • Azure Key Vault (Secrets management)                │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 9.2 Data Flow Diagram
```
USER ACTION                          SYSTEM PROCESSING                    OUTPUT

┌──────────────┐
│ 1. Upload    │
│  exam.docx   │
│  via Teams   │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│ 2. Azure Function receives file                              │
│    • Validate file type (.docx)                              │
│    • Generate job_id                                         │
│    • Upload to Blob Storage (examops-input container)        │
└──────┬───────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│ 3. Coordinator Agent starts workflow                         │
│    Semantic Kernel orchestrates:                             │
│    ┌─────────────────────────────────────────────┐           │
│    │ a) File Handler Agent: Download from Blob   │           │
│    │ b) File Handler Agent: Get template (Vector DB) │       │
│    │ c) Formatting Engine Agent: Rule-based format  │        │
│    │ d) Formatting Engine Agent: LLM validation     │        │
│    │ e) Diff Generator Agent: Create comparison     │        │
│    │ f) File Handler Agent: Save outputs            │        │
│    └─────────────────────────────────────────────┘           │
└──────┬───────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│ 4a. Formatting Engine (Layer 1: Rule-Based)                  │
│     python-docx processing:                                  │
│     • Header/footer injection                                │
│     • Margin standardization                                 │
│     • Numbering correction (regex patterns)                  │
│     • Marks formatting                                       │
│     • Spacing enforcement                                    │
│     • Indentation adjustment                                 │
│     Output: formatted_draft.docx                             │
└──────┬───────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│ 4b. Formatting Engine (Layer 2: LLM Validation)              │
│     Azure OpenAI GPT-4o-mini via Foundry:                    │
│     • Compare against template rules                         │
│     • Score compliance (0-100%)                              │
│     • Identify edge cases                                    │
│     • Verify math expressions preserved                      │
│     Output: validation_result.json                           │
└──────┬───────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│ 5. Diff Generator creates reports                            │
│    • HTML diff (color-coded)                                 │
│    • Summary statistics                                      │
│    • Side-by-side Word doc (optional)                        │
│    Output: diff_report.html, stats.json                      │
└──────┬───────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│ 6. File Handler saves outputs                                │
│    • formatted_exam.docx → Azure Blob (examops-output)       │
│    • diff_report.html → Azure Blob                           │
│    • Generate SAS tokens (1-hour expiry)                     │
│    • Create OneDrive sharing link (optional)                 │
│    Output: URLs for download                                 │
└──────┬───────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│ 7. Teams Bot delivers results                                │
│    Adaptive Card with:                                       │
│    • ✅ Compliance Score: 95%                                │
│    • 📊 Summary: 12 fixes, 5 spacing, 8 marks               │
│    • 📥 Download buttons (formatted .docx, diff HTML)        │
│    • 🔗 OneDrive link                                        │
│    • ⚠️ Review reminder                                     │
└──────┬───────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────┐
│ Lecturer     │
│ downloads &  │
│ reviews      │
└──────────────┘
```

---

## 📏 10. Success Metrics & KPIs

### 10.1 Primary Metrics (MVP - Phase 1)

| Metric | Baseline (Current Manual Process) | Target (ExamOps MVP) | Measurement Method |
|--------|-----------------------------------|----------------------|--------------------|
| **Time to format 1 exam paper** | 2-4 hours | <15 minutes (90% reduction) | User surveys, time tracking |
| **Template compliance rate** | ~60% (many rejections) | >95% | LLM validation scores |
| **Processing speed** | N/A (manual) | <20 seconds | Application Insights latency logs |
| **First-submission acceptance** | ~75% (25% rejected for formatting) | >95% | Coordinator feedback tracking |
| **User satisfaction** | 2.8/5.0 (current frustration) | >4.5/5.0 | Post-usage surveys (Net Promoter Score) |

### 10.2 Technical Performance Metrics

| Metric | Target | Monitoring Tool |
|--------|--------|-----------------|
| **API uptime** | 99% | Azure Monitor |
| **Average processing time** | <20 seconds | Application Insights (custom metric) |
| **LLM validation success rate** | >95% (fallback <5%) | Custom telemetry |
| **Error rate** | <2% | Application Insights exceptions |
| **Cost per paper processed** | <$0.05 | Azure Cost Management |

### 10.3 Quality Metrics

| Metric | Target | Validation Method |
|--------|--------|-------------------|
| **Compliance score distribution** | 80%+ of papers score >90% | Database analytics |
| **Manual fixes required post-formatting** | <10% of papers | User feedback |
| **False positive formatting changes** | <5% | Diff report audits |
| **Math expression preservation** | 100% (zero corruption) | Test suite |

### 10.4 Business Impact Metrics

| Metric | Calculation | Target |
|--------|-------------|--------|
| **Faculty-wide time saved** | (40 lecturers × 3 exams × 2 hours saved) | 240 hours/semester |
| **Moderation cycle time reduction** | (Avg days from draft → approval) | -40% (from 10 days → 6 days) |
| **Coordinator review time** | (Per paper review time) | -60% (from 1 hour → 24 minutes) |
| **ROI** | (Time saved value / Azure costs) | >100:1 |

### 10.5 Hackathon Judging Metrics

| Judging Criteria | Our Approach | Expected Score |
|------------------|--------------|----------------|
| **Technological Implementation** | Azure-only, Agent Framework, MCP, Foundry | 25/25 |
| **Agentic Design** | 4 specialized agents, clear responsibilities | 20/20 |
| **Real-World Impact** | Solves verified pain point, 240hrs saved/semester | 20/20 |
| **UX & Presentation** | 5-step Teams Bot, visual diff, <2min user journey | 20/20 |
| **Innovation** | Hybrid AI+Rules, Vector DB multi-campus, production-ready | 15/15 |
| **Total** | | **100/100** |

---

## ⚠️ 11. Risks & Mitigations

### 11.1 Technical Risks

| Risk | Probability | Impact | Mitigation Strategy |
|------|-------------|--------|---------------------|
| **LLM breaks complex layouts** | Medium | High | • Hybrid approach: Rule engine handles structure<br>• LLM only validates, doesn't reconstruct<br>• Fallback to rule-only mode if LLM fails |
| **Complex tables/figures formatting** | High | Medium | • Preserve original table structure<br>• Only adjust spacing/fonts, not layout<br>• Flag for manual review if complex |
| **Azure OpenAI rate limits** | Low | Medium | • Use GPT-4o-mini (higher limits)<br>• Implement retry with exponential backoff<br>• Queue system for batch processing |
| **Teams Bot deployment issues** | Medium | Low | • Use Microsoft Bot Framework templates<br>• Extensive testing in dev environment<br>• Backup: Direct HTTP API for demo |
| **Document corruption during processing** | Low | High | • Input validation before processing<br>• Backup original to separate container<br>• Versioned output (v1, v2 if reprocessed) |

### 11.2 Operational Risks

| Risk | Probability | Impact | Mitigation Strategy |
|------|-------------|--------|---------------------|
| **Template rules change frequently** | Medium | Medium | • Vector DB allows easy template updates<br>• Versioning system (v1.0, v1.1, v2.0)<br>• Admin UI for template management (Phase 2) |
| **User resistance to AI tools** | Medium | Low | • Transparent diff reports build trust<br>• Lecturers retain final approval<br>• Emphasize "assistant, not replacement" |
| **Dependency on Azure services** | Low | High | • Use Azure-native services (high SLA)<br>• Multi-region failover (Phase 2)<br>• Export formatted docs immediately |
| **Cost overruns** | Low | Medium | • Consumption-based pricing (pay per use)<br>• Set Azure budget alerts<br>• Monitor token usage closely |

### 11.3 Security & Compliance Risks

| Risk | Probability | Impact | Mitigation Strategy |
|------|-------------|--------|---------------------|
| **Exam content leakage** | Low | Critical | • No logging of question text<br>• Encrypted storage (AES-256)<br>• SAS tokens expire after 1 hour<br>• Delete originals after 24 hours |
| **Unauthorized access to formatted exams** | Low | High | • Azure AD authentication required<br>• User-specific SAS tokens<br>• Audit trail of all downloads |
| **LLM prompt injection** | Low | Medium | • Azure Foundry content safety filters<br>• Template-only grounding (no external data)<br>• Input sanitization |

### 11.4 Project Delivery Risks

| Risk | Probability | Impact | Mitigation Strategy |
|------|-------------|--------|---------------------|
| **Hackathon timeline too tight** | Medium | High | • MVP scope clearly defined (formatting only)<br>• Pre-built Azure infrastructure<br>• GitHub Copilot accelerates coding<br>• Backup: Demo with recorded video |
| **Learning curve: Agent Framework** | Medium | Medium | • Use Semantic Kernel tutorials<br>• Simplify to 4 agents (not 10+)<br>• Allocate 2 days for framework learning |
| **Real exam papers unavailable for testing** | Low | Medium | • Use guideline documents as ground truth<br>• Create synthetic test cases<br>• Faculty advisor provides samples |

---

## 🔮 12. Future Roadmap

### Phase 2: Intelligence Expansion (Post-Hackathon, Month 1-2)

**New Agents**:

#### 2.1 CLO Mapping Agent
**Purpose**: Automatically align questions to Course Learning Outcomes

**Inputs**:
- Formatted exam paper
- Course Learning Outcomes (from syllabus/LMS)
- Bloom's taxonomy mapping

**Outputs**:
- CLO coverage matrix
- Recommendations: "Question 2(b) should map to CLO3 based on 'evaluate' verb"

**Technology**:
- Azure OpenAI for semantic understanding
- Vector DB: Store CLO definitions
- Integration: Fetch CLOs from LMS API (Moodle)

#### 2.2 Question Quality Agent
**Purpose**: Analyze difficulty distribution and cognitive levels

**Metrics**:
- Bloom's taxonomy classification (Remember → Create)
- Difficulty balance (Easy 30%, Medium 50%, Hard 20%)
- Keyword density (avoid repetition)

**Outputs**:
- "Warning: 70% of questions are 'Remember' level. Add higher-order thinking."
- "Q3 and Q4 have similar phrasing. Consider rewording."

#### 2.3 Marks Validation Agent
**Purpose**: Ensure marks totals match, flag discrepancies

**Checks**:
- Sum of sub-question marks = Total marks
- Consistent marks per CLO
- Marks distribution aligns with time allocation

**Outputs**:
- "Error: Q2 total is 23 marks but sub-questions sum to 25"
- "Suggestion: Increase Q1(c) from 5 to 7 marks to balance CLO weighting"

---

### Phase 3: Full Lifecycle Automation (Month 3-6)

#### 3.1 Moderation Report Generator
**Purpose**: Auto-fill AARO-FM-030 moderation forms

**Data Sources**:
- Formatted exam paper
- CLO mapping results
- Question quality analysis
- Marks validation

**Outputs**:
- Pre-filled moderation form (.docx)
- Moderator only reviews/approves, doesn't fill manually

#### 3.2 Answer Scheme Formatter
**Purpose**: Apply template rules to marking schemes

**Similar workflow**:
- Upload answer_scheme_draft.docx
- Apply Marking Scheme Format Guideline 1 rules
- Generate formatted marking_scheme.docx

#### 3.3 EoBE Summary Agent
**Purpose**: Evidence of Best Evidence report generation

**Inputs**:
- Exam papers
- Grading data
- CLO attainment analysis

**Outputs**:
- Automated EoBE narrative
- Charts: CLO attainment trends, difficulty analysis
- Export to PDF for accreditation evidence

---

### Phase 4: Multi-Campus Expansion (Month 6-12)

#### 4.1 Template Marketplace
**Concept**: Universities share/sell template rules

**Features**:
- Upload custom templates to Vector DB
- Semantic search: "Find engineering exam templates in Malaysia"
- Version control & change tracking
- Community ratings (5-star system)

#### 4.2 White-Label SaaS
**Target**: Sell to other universities in ASEAN region

**Pricing Model**:
- Free tier: 50 papers/month
- Pro: $500/month (unlimited)
- Enterprise: Custom (multi-faculty, SSO, dedicated support)

**Go-to-Market**:
- Target Malaysian public universities first (11 institutions)
- Partner with Ministry of Higher Education
- Showcase SUC as reference customer

---

## 📎 13. Appendix

### 13.1 Template Reference Documents (Included in Sample Folder)

1. **Exam Paper Format Guideline 1.docx**
   - Strict spacing, numbering, margin rules
   - Header/footer specifications
   - Continuation page formatting

2. **Marking Scheme Format Guideline 1.docx**
   - Answer scheme structure
   - Rubric formatting
   - Marks allocation tables

3. **AARO-FM-030 Moderation Form.docx**
   - CLO alignment table
   - Difficulty level mapping
   - Moderator feedback workflow

### 13.2 Sample Before/After Files

#### Before: messy_exam_draft.docx
**Issues**:
- ❌ No header/footer
- ❌ Numbering: `1)`, `1a)`, `1(a)(i)` (inconsistent)
- ❌ Marks: `(3marks)`, `(3 marks)`, `[3 marks]` (mixed formats)
- ❌ Spacing: `DATE:`, `DURATION :` (inconsistent colons)
- ❌ Indentation: Manual tabs (not Tab 0.5 × N)
- ❌ Missing CLO alignment entries

#### After: formatted_exam_final.docx
**Fixed**:
- ✅ Header: "SOUTHERN UNIVERSITY COLLEGE / FACULTY OF ENGINEERING..."
- ✅ Numbering: `Q1.`, `   (a)`, `      (i)` (standard hierarchy)
- ✅ Marks: `(3 marks)` (consistent, right-aligned)
- ✅ Spacing: `DATE : `, `DURATION : ` (1 space before/after)
- ✅ Indentation: Tab 0.5 × 3 = 1.5cm, Tab 0.5 × 6 = 3.0cm
- ✅ CLO slots: Preserved existing entries

### 13.3 Estimated Development Timeline (Hackathon Sprint)

| Day | Tasks | Owner | Status |
|-----|-------|-------|--------|
| **Day 1** | Azure infrastructure setup<br>• Create resource group<br>• Provision Storage, AI Search, OpenAI<br>• Set up Teams Bot registration | DevOps | 🔄 In Progress |
| **Day 2-3** | Template rules extraction & Vector DB<br>• Parse 3 guideline documents<br>• Create JSON schema<br>• Upload to Azure AI Search with embeddings | Data Engineer | 📋 Planned |
| **Day 4-5** | Rule-based formatter (python-docx)<br>• Implement numbering correction<br>• Marks formatting<br>• Spacing & indentation rules | Backend Dev | 📋 Planned |
| **Day 6-7** | LLM validation integration<br>• Azure Foundry setup<br>• Prompt engineering<br>• Fallback logic | AI Engineer | 📋 Planned |
| **Day 8** | Diff generator & reporting<br>• HTML diff creation<br>• Summary statistics | Backend Dev | 📋 Planned |
| **Day 9** | Teams Bot integration<br>• Bot Framework setup<br>• Command handlers<br>• Adaptive cards | Frontend Dev | 📋 Planned |
| **Day 10** | End-to-end testing<br>• Test with 5 real exam papers<br>• Bug fixes | QA + All | 📋 Planned |
| **Day 11** | Demo preparation<br>• Slides<br>• Before/after examples<br>• Backup video | Product Manager | 📋 Planned |
| **Day 12** | **Hackathon Demo Day** | All | 🎯 Milestone |

### 13.4 Cost-Benefit Analysis

#### Costs (MVP - First Year)
| Item | Monthly | Annual |
|------|---------|--------|
| Azure Functions (Consumption) | $0 | $0 |
| Azure Blob Storage (100 GB) | $2 | $24 |
| Azure AI Search (Basic tier) | $75 | $900 |
| Azure OpenAI (500K tokens/month) | $15 | $180 |
| Bot Service (Free tier) | $0 | $0 |
| Application Insights | $5 | $60 |
| **Total** | **$97** | **$1,164** |

#### Benefits (SUC Faculty - First Year)
| Benefit | Calculation | Annual Value |
|---------|-------------|--------------|
| Lecturer time saved | 40 lecturers × 3 exams × 2 hours × $50/hour | $12,000 |
| Coordinator time saved | 8 coordinators × 15 papers × 0.6 hours × $70/hour | $5,040 |
| Reduced printing waste (fewer rejections) | 25% rejection rate → 5% × 120 exams × $20 rework cost | $480 |
| **Total Benefits** | | **$17,520** |

**ROI**: ($17,520 - $1,164) / $1,164 = **1,405%** 🚀

---

## 🏆 14. Hackathon Presentation Plan

### 14.1 Demo Script (5 Minutes)

**Slide 1: The Problem (30 seconds)**
```
[Show messy exam paper on screen]

"Lecturers at Southern University College waste 2-4 HOURS per exam just fixing formatting. 
Look at this - wrong numbering, missing headers, bad spacing. 
This gets rejected by coordinators, causing delays and frustration."
```

**Slide 2: The Solution (30 seconds)**
```
[Show architecture diagram]

"ExamOps Orchestrator uses Azure AI to automate this.
Hybrid engine: Rule-based for speed + GPT-4o-mini for validation.
Multi-campus ready with Vector DB template storage."
```

**Slide 3: Live Demo (2 minutes)**
```
[Open Teams Bot]
Narrator: "Watch this. I upload a messy draft..."
[/upload command, attach messy_exam_draft.docx]

Narrator: "Hit format..."
[/format command]

[Progress indicator: 🔄 Formatting... 5 seconds]

[Results appear]
Bot: "✅ Compliance: 95%
      📊 Fixed: 12 numbering, 5 spacing, 8 marks
      📥 Download ready"

Narrator: "15 seconds. Done."
```

**Slide 4: Before/After Comparison (1 minute)**
```
[Split screen: Original vs Formatted in Word]

Narrator: "Look at the difference:
- Left: Messy numbering '1)' '1a)'
- Right: Perfect 'Q1.' '(a)'

- Left: Wrong spacing 'DATE:'
- Right: Correct 'DATE : '

All automatically fixed. Look at the diff report..."

[Open HTML diff]
"Color-coded changes. Lecturer knows exactly what changed. Builds trust."
```

**Slide 5: Impact (30 seconds)**
```
[Show metrics slide]

"This saves SUC faculty 240 hours per semester.
95% compliance score. <5% rejections.
Production-ready architecture. Ready to scale to other faculties."
```

**Slide 6: Tech Stack (30 seconds)**
```
[Highlight hero technologies]

"Built 100% on Azure:
✅ Microsoft Agent Framework (Semantic Kernel)
✅ Azure MCP (OneDrive integration)
✅ Azure AI Foundry (centralized orchestration)
✅ Azure OpenAI, Blob Storage, AI Search

Four specialized agents. Clear responsibilities. Extensible design."
```

**Slide 7: Q&A (30 seconds)**
```
"Questions? 
We've solved a real pain point, delivered production-grade architecture, 
and built it to scale. Thank you!"
```

### 14.2 Backup Plan
- **Recorded demo video** (in case Wi-Fi issues)
- **Static before/after screenshots** (if live demo fails)
- **Architecture diagram printouts** (judges love visuals)

---

## 📞 15. Contact & Support

**Project Team**:
- **Product Owner**: Dr. Lee Siew Mei (Course Coordinator, IT Programme)
- **Technical Lead**: [Your Name]
- **Faculty Advisor**: Prof. Ahmad bin Hassan (Dean of Engineering & IT)

**GitHub Repository**: `https://github.com/suc-examops/orchestrator`

**Documentation**:
- `claude.md` - AI assistant context (this document's companion)
- `PRD.md` - This document
- `README.md` - Quick start guide
- `ARCHITECTURE.md` - Technical deep dive

**Support Channels** (Post-Hackathon):
- Teams: `@ExamOps Bot` (in-app help)
- Email: `examops-support@suc.edu.my`
- GitHub Issues: For bug reports and feature requests

---

## ✅ 16. Acceptance Criteria (MVP Sign-Off)

**The MVP is considered complete when**:

1. ✅ A lecturer can upload a .docx exam draft via Teams Bot
2. ✅ Formatting completes in <20 seconds for typical 5-page exam
3. ✅ Output achieves >90% compliance score on 9/10 test papers
4. ✅ Diff report accurately shows all changes (validated by faculty)
5. ✅ Formatted .docx downloads successfully from Teams
6. ✅ Zero content corruption (mathematical expressions preserved)
7. ✅ System handles 10 concurrent requests without failure
8. ✅ All Azure resources provisioned and integrated
9. ✅ Demo runs successfully for 3 dry-run audiences
10. ✅ Documentation complete (claude.md, PRD.md, README.md, demo slides)

**Sign-Off Required**:
- [ ] Technical Lead (Architecture validated)
- [ ] Faculty Advisor (Formatting accuracy validated)
- [ ] Product Owner (User requirements met)
- [ ] Hackathon Team (Demo-ready confirmed)

---

## 🎯 17. Final Notes

ExamOps Orchestrator represents a **paradigm shift** in academic workflow automation:

**From**: Manual, error-prone, time-consuming formatting  
**To**: Automated, consistent, fast template enforcement

**Impact**: 240 hours saved per semester at SUC → $17,520/year value  
**Scalability**: Multi-campus, multi-faculty, multi-template architecture  
**Production-Ready**: Azure-native, secure, monitored, extensible

This is not a hackathon toy. This is a **real solution to a real problem**, built on enterprise-grade technology, ready for immediate deployment.

**Let's win this hackathon and transform academic assessment workflows! 🚀**

---

*Last Updated: February 12, 2026*  
*Version: 1.0*  
*Status: Ready for Development Sprint*
