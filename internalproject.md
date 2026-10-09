# NimbusPay (NextPay) - Internal Sample Project

## Overview
**NimbusPay** (also tracked under the Jira project key **NPAY** or referred to as **NextPay**) is a mock enterprise backend application designed to serve as the "ground truth" codebase for the **ReleaseIQ** RAG engine. 

It acts as an employee expense, reporting, and reimbursement portal that simulates the complexities, business rules, and technical debt typically found in real-world enterprise software. It is not a standalone executable application but a collection of simulated business logic (Python and YAML files) used to test ReleaseIQ's ability to understand code context and resolve "Intentional Discrepancies" between Jira tickets and actual code implementation.

## Core Functionalities

The application architecture is divided into microservice-like domains:

### 1. Approvals (`/approvals/`)
- **Manager Hierarchy & Delegation**: Managers can approve/reject expenses and temporarily delegate their approval authority (e.g., during PTO) for a maximum of 30 days to users with the `APPROVER` role.
- **Auto-Escalation**: Background jobs automatically sweep pending expenses and escalate them to higher authorities if unapproved for more than 7 days.

### 2. Expenses (`/expenses/`)
- **Receipt Validation**: Manages file size and type validations for receipt uploads (e.g., enforcing a strict 10MB maximum limit).
- **Policy Enforcement**: Enforces company spending limits, such as restricting meal limits based on city tiers (Tier 1 vs. Tier 2) and requiring written justifications to avoid `EXP-1042` errors.
- **Currency Exchange**: Handles foreign currency exchanges and validations.

### 3. Reports (`/reports/`)
- **Exporting Data**: Allows users to export expense reports into CSV or Excel formats, enforcing limitations like a 10,000-row maximum for Excel.
- **Report Routing**: Ensures exports are only triggered within valid start and end date ranges.

### 4. Notifications (`/notifications/`)
- **Automated Emails**: Manages communication templates and sends automated emails when an expense is approved or rejected.

### 5. Configuration (`/config/`)
- **Simulated Database/Environment**: Uses YAML files to simulate roles (`ADMIN`, `APPROVER`, `EMPLOYEE`), feature toggles (like enabling Excel exports for specific tenants), and system-wide defaults (like `USD` as the default currency).

---

## New Features Introduced in ReleaseIQ

Recent updates to the ReleaseIQ testing environment introduce advanced **context-enrichment features** and an **AI Git Blame Demo**. These features enhance ReleaseIQ's ability to handle complex, unstructured, real-world prompts, specifically for scenarios such as:

* **Support Escalation Context:** Ability to analyze user support tickets (e.g., P2 tickets regarding legacy API login failures) and map errors like `ValueError: Invalid token format` directly back to recent deployments or specific files (e.g., `auth.py`).
* **Tracing Breaking Changes:** Correlating Slack chatter, merged PRs, and Jira tickets to track down the root cause of breaking changes (e.g., tracing a new token length validation rule back to the original intentions outlined in ticket `NPAY-123`).
* **On-Call Incident Investigation:** Cross-referencing current codebase states with `git blame` history to assist during active incidents, identifying exactly who introduced a change, what the change was, and the original context that prompted it (e.g., fixing a security issue).
