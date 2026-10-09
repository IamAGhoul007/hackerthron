# NimbusPay (NextPay) - Mock Expense Management Portal

**NimbusPay** (also tracked under the Jira project key **NPAY**) is a mock enterprise backend application specifically designed to serve as the "ground truth" codebase for the **ReleaseIQ** RAG engine. 

It is an employee expense, reporting, and reimbursement portal that is designed to simulate the complexities, rules, and technical debt found in real-world enterprise software.

---

## 🛑 Important Note
**This is not a standalone executable application.** 
There are no databases to connect to and no servers to run here. It is purely a collection of Python and YAML files containing simulated business logic. Its sole purpose is to be scanned, indexed, and analyzed by the **ReleaseIQ** system to test its ability to understand code context.

---

## 🏗️ Codebase Architecture

The application is structured into microservice-like domains under the `backend/` directory:

### 1. `/approvals/`
Handles the hierarchy of managers approving or rejecting expenses submitted by employees.
- **`delegation_service.py`**: Allows managers to delegate their approval authority to someone else (e.g., during PTO). It strictly enforces that delegations cannot exceed 30 days and requires the target user to have the `APPROVER` role.
- **`escalation_rules.py`**: A background job logic that sweeps pending expenses and automatically escalates them to a higher authority if they sit unapproved for more than 7 days.

### 2. `/expenses/`
The core business logic handling the creation, validation, and submission of expenses.
- **`receipt_upload.py`**: Manages the file size and type validations for users uploading pictures of their receipts. Currently enforces a strict **10MB** maximum limit.
- **`policy_engine.py`**: Enforces company spending limits. For example, it restricts meal limits based on city tiers (Tier 1 vs. Tier 2) and will throw an `EXP-1042` error unless the user provides a written justification.
- **`currency_service.py`**: Handles foreign currency exchanges and validations.

### 3. `/reports/`
Handles exporting data out of the system.
- **`export_service.py`**: Contains the logic to export expense reports into CSV or Excel formats, enforcing limitations like a 10,000-row maximum for Excel exports.
- **`report_router.py`**: Defines that an export can only be triggered if a valid start and end date range is provided.

### 4. `/notifications/`
- **`email_service.py` & `templates.py`**: Manages the automated emails sent to users (e.g., when an expense is approved or rejected).

### 5. `/config/`
YAML files acting as a mock database or environment configuration.
- **`roles.yaml`**: Defines what roles exist in the system (`ADMIN`, `APPROVER`, `EMPLOYEE`).
- **`feature_flags.yaml`**: Simulates a feature-toggling system where certain features (like Excel exports) can be turned on or off for specific tenants.
- **`settings.yaml`**: Contains system-wide defaults like the default currency (`USD`).

---

## 🧠 The Purpose of "Intentional Discrepancies"

One of the main challenges in enterprise software is that the **documentation (Jira/Confluence) often contradicts the actual code in production** due to hotfixes, bugs, or changing requirements.

NimbusPay was purposefully designed with these discrepancies to test ReleaseIQ's Hybrid RAG capabilities. When using ReleaseIQ, it must read both the `jira_tickets_dump.txt` and the `sample_app` code, recognize conflicts, and synthesize an accurate answer.

### Example of a Built-In Discrepancy:
**The Receipt Upload Limit**
* **In Jira (`NPAY-1042`)**: The product manager requested a bulk upload feature allowing up to 20 files, and explicitly stated: *"The max file size should be 50 MB per file."*
* **In Code (`receipt_upload.py`)**: A developer later implemented a hotfix for an infrastructure crash (`NPAY-1043`) and hardcoded the limit to `10 * 1024 * 1024` (10MB).

If a user asks ReleaseIQ: *"What is the maximum file size for a receipt?"*, the AI engine must look at both sources and determine that while the original intention was 50MB, the system will currently reject anything over 10MB due to the code constraint.

---

## 🚀 How ReleaseIQ Uses This
ReleaseIQ uses an ingestion pipeline (`app/ingestion/code_scanner.py`) to parse every file in this directory. It uses regular expressions to strip out sensitive secrets, generates human-readable summaries of what each file does, and embeds the code chunks into a vector database (ChromaDB). 

When you ask a question about NextPay, ReleaseIQ searches these code embeddings to find the technical truth and merges it with the historical context from Jira.
