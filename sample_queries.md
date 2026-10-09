# ReleaseIQ Sample Project Overview & Queries

## Project Overview

**ReleaseIQ** is a Release Knowledge and Troubleshooting Assistant designed to intelligently answer questions about an enterprise product based on its codebase and issue tracker. 

In this sample environment, ReleaseIQ is configured to support **NextPay**, a fictional enterprise expense and finance management software. The data ingested into ReleaseIQ consists of:
1. **Jira Ticket Dump**: Historical records of feature requests, bug reports, and product changes.
2. **NextPay Codebase (Sample)**: Python and YAML files that enforce strict business logic and define UI behaviors.

By querying ReleaseIQ, users can retrieve answers that synthesize both the technical limitations defined in the code and the product decisions documented in Jira.

---

## 20+ Sample Queries by Scenario

Here are the sample queries meticulously grouped by the **4 testing scenarios** you requested:

### Scenario 1: Answer found only in Jira ticket dump
*These features or decisions are documented heavily in Jira but might not have deep explicit business logic traces in the sample codebase.*
1. How do I enable dark mode?
2. What are the rules for entering an expense in a foreign currency?
3. How do I auto-save my expense drafts?
4. How long do expense drafts stay saved before they expire?
5. I want to export my reports to Excel instead of CSV, is this possible?

### Scenario 1.5: Newly Added Features & AI Git Blame Demo
*These queries demonstrate the newly added context-enrichment features using complex, unstructured, real-world prompts.*

6. **Support Escalation Context:**
   "Hey team, we're getting a bunch of P2 tickets from users trying to log in via the legacy API. It looks like the backend is throwing a `ValueError` with the message 'Invalid token format' right at the authentication step. I'm not sure if this is related to the recent deployment. Did something change in the token validation logic recently, maybe in `auth.py`? Can you check if there were any PRs merged that might be causing this issue?"

7. **Tracing a Breaking Change:**
   "I'm trying to trace down a bug that was introduced in the last release. Someone mentioned in Slack that PR #45 was merged and it had to do with ticket NPAY-123. Ever since that got deployed, certain admin tokens are failing the initial authentication check because they are being rejected by a new length check. Could you summarize what NPAY-123 was trying to achieve and show me exactly what validation rule was added to the code?"

8. **On-Call Incident Investigation:**
   "We have an active incident right now where the login endpoint is completely broken for some integrations. The logs show it's dying at `authenticate_user`. I heard John Doe might have added a new minimum length requirement for tokens to fix a security issue. Can you cross-reference the current code with the git blame and tell me if a length requirement was recently introduced, and what the original Jira ticket requested?"


### Scenario 2: Hybrid (Jira + Codebase)
*These answers require synthesizing the original product intentions from Jira with the hardcoded reality (or active bug workarounds) in the codebase.*
6. How do I upload multiple receipts at once instead of one by one?
7. What is the maximum file size for uploading a receipt right now? (Jira originally wanted 50MB, but the code enforces 10MB due to a recent bug).
8. What is the meal limit for Tier 1 and Tier 2 cities?
9. How do I bypass the meal limit if I took a client out for dinner? (EXP-1042)
10. What is the reimbursement rate per kilometer for mileage claims, and is there a maximum limit?
11. Why is the Export button greyed out on the Reports page?
12. If I want to delegate my approver responsibilities during PTO, what roles can I choose, and what is the maximum number of days I can delegate for?

### Scenario 3: Answer found only in Codebase
*These are strict technical bounds, background behaviors, or internal error codes that developers implemented, but without a dedicated Jira ticket explaining the user flow.*
13. What happens if my manager doesn't approve my expense report within 7 days?
14. What does the `check_escalation` function do for pending expenses?
15. If I don't provide a justification for a policy limit, what specific error code does the `policy_engine.py` throw?
16. What roles are defined in the system according to `roles.yaml`?
17. What exactly happens under the hood when a delegated approval request exceeds 30 days?
18. What is the default currency defined in `settings.yaml`?

### Scenario 4: No solution in Jira or Codebase (Bug / AYS Ticket)
*These queries describe fictitious or undocumented issues. The system should explicitly fail to find an answer and prompt the user to raise an AYS ticket.*
19. What is the recent memory leak bug in the user authentication service and how was it fixed?
20. How do I set up SSO (Single Sign-On) for my NextPay account using Okta?
21. Why did the system crash with a `ERR-999 Database Timeout` when I opened the dashboard?
22. Is there a mobile app version of NextPay available for iOS?
