import os

TICKETS = []

# Base templates to ensure variety without looking repetitive
features = [
    ("Receipt Upload", "Expenses, Receipts"),
    ("Multi-currency", "Expenses, Currencies"),
    ("Delegated Approvals", "Approvals, Settings"),
    ("Policy Limits", "Expenses, Policy Engine"),
    ("Report Export", "Reports, Export"),
    ("Dark Mode", "Profile, Appearance"),
    ("Auto-save Drafts", "Expenses, Drafts"),
    ("Mileage Claims", "Expenses, Mileage")
]

statuses = ["Done", "In Progress", "To Do", "Won't Fix"]
priorities = ["Highest", "High", "Medium", "Low"]

# Add core feature tickets directly
manual_tickets = [
"""================================================================================
Key: NPAY-1042
Type: Story
Summary: Bulk receipt upload with drag-and-drop
Status: Done
Priority: High
Fix Version: 3.5.0
Release Date: 2026-03-18
Components: Expenses, Receipts
Labels: new-feature, upload
Reporter: Priya Nair
Assignee: Daniel Okafor
Description:
We need a bulk upload feature for receipts. Users complain that uploading one by one is too slow. 
Let's add a drag-and-drop zone. The system should support up to 20 files at once.
Allowed file types: JPG, PNG, PDF. 
The max file size should be 50 MB per file to accommodate large multi-page PDF scans.
Acceptance Criteria:
- Drag and drop zone added to New Expense screen.
- Max 20 files.
- Allowed types: JPG/PNG/PDF.
- Size limit: 50 MB per file.
Comments:
[2026-03-02 10:14] Daniel Okafor: Started working on the UI for the drop zone.
[2026-03-05 16:40] QA - Mei Tanaka: Verified bulk upload works. It throws UPL-413 when I upload a 60MB file.
Linked Issues: relates to NPAY-1031, blocks NPAY-1077
Known Issues / Workarounds:
None.
User Impact:
Users can now upload multiple receipts easily.""",

"""================================================================================
Key: NPAY-1043
Type: Bug
Summary: Bulk upload failing with UPL-413 for 15MB files
Status: Won't Fix
Priority: Medium
Fix Version: 3.5.1
Release Date: 2026-04-01
Components: Expenses, Receipts
Labels: bug, upload
Reporter: John Doe
Assignee: Daniel Okafor
Description:
Users are reporting UPL-413 errors when uploading files larger than 10MB, even though the release notes for NPAY-1042 stated 50MB.
Acceptance Criteria:
- Fix the limit to match 50MB.
Comments:
[2026-03-20 10:14] Daniel Okafor: After the infrastructure incident last week, DevOps lowered the hard limit on the ingress controller to 10MB to prevent memory exhaustion.
[2026-03-21 11:00] Product - Sarah: We will update the docs later. For now, users must compress their files.
Linked Issues: relates to NPAY-1042
Known Issues / Workarounds:
Compress PDFs or use an online tool to reduce size before uploading. Max allowed size is currently 10MB.
User Impact:
Users cannot upload files > 10MB.""",

"""================================================================================
Key: NPAY-123
Type: Story
Summary: Improve auth token validation
Status: Done
Priority: High
Fix Version: 3.9.0
Release Date: 2026-08-15
Components: Security, Auth
Labels: security, auth
Reporter: Security Team
Assignee: John Doe
Description:
We need to ensure that admin tokens are no longer allowed via the standard authentication endpoint.
Acceptance Criteria:
- Disallow admin tokens.
- Return PermissionError.
Comments:
[2026-08-10 10:14] John Doe: PR #45 merged, which introduced a new validation rule in auth.py.
Linked Issues: none
Known Issues / Workarounds:
None.
User Impact:
Improves system security.""",

"""================================================================================
Key: NPAY-1050
Type: Story
Summary: Excel export option for expense reports
Status: Done
Priority: High
Fix Version: 3.6.0
Release Date: 2026-05-10
Components: Reports, Export
Labels: new-feature, export
Reporter: Alice Smith
Assignee: Bob Chen
Description:
Currently we only support CSV export. Finance team needs Excel (.xlsx) export.
This should be available under the Reports tab.
Acceptance Criteria:
- Add Excel option to the export dropdown.
- This feature should be gated behind the `reports_excel` feature flag.
Comments:
[2026-05-01 09:00] Bob Chen: Implemented the Excel export. It caps at 10,000 rows.
[2026-05-02 14:20] QA - Mei Tanaka: Works well. If I select Excel but the flag is off, it fails as expected.
Linked Issues: blocks NPAY-1055
Known Issues / Workarounds:
Excel export is not available for all tenants by default. Admin must enable the `reports_excel` flag.
User Impact:
Better reporting for Finance.""",

"""================================================================================
Key: NPAY-1055
Type: Bug
Summary: Export button is greyed out and cannot be clicked
Status: Done
Priority: High
Fix Version: 3.6.1
Release Date: 2026-05-20
Components: Reports, Export
Labels: bug, export
Reporter: Mike Jones
Assignee: Bob Chen
Description:
Users on the Reports page complain that the Export button is disabled/greyed out. They don't know how to export.
Acceptance Criteria:
- Ensure the export button is only disabled when it should be.
Comments:
[2026-05-15 10:00] Bob Chen: This is by design. The export button is disabled UNTIL a date range (date-from and date-to) is selected. 
[2026-05-16 11:00] Product - Sarah: Ok, let's keep the behavior but we need to explain this in our release notes.
Linked Issues: relates to NPAY-1050
Known Issues / Workarounds:
Users must select both a start date and end date before the Export button becomes clickable.
User Impact:
Confusion on Reports page.""",

"""================================================================================
Key: NPAY-1060
Type: Story
Summary: Mileage claims support
Status: Done
Priority: High
Fix Version: 3.4.0
Release Date: 2026-02-15
Components: Expenses, Mileage
Labels: new-feature, mileage
Reporter: Emma Watson
Assignee: Daniel Okafor
Description:
Add support for mileage claims. Employees need to input start location, end location, and distance in km.
Acceptance Criteria:
- Fields for start location, end location, and distance.
- Maximum 500 km per claim.
- Rate should be 0.55 per km.
Comments:
[2026-02-10 10:14] Daniel Okafor: Added the 500km validation.
Linked Issues: none
Known Issues / Workarounds:
None.
User Impact:
Allows claiming car mileage.""",

"""================================================================================
Key: NPAY-1065
Type: Story
Summary: Auto-save drafts for new expenses
Status: Done
Priority: Medium
Fix Version: 3.7.0
Release Date: 2026-06-01
Components: Expenses, Drafts
Labels: new-feature, usability
Reporter: Priya Nair
Assignee: Alice Smith
Description:
Users lose their typed justification and uploaded receipts if they close the browser. We should auto-save drafts.
Acceptance Criteria:
- Auto-save every 30 seconds.
- Show a "Draft restored" banner when reopening.
- Drafts expire after 14 days.
Comments:
[2026-05-25 10:14] Alice Smith: Auto-save implemented. Polling every 30s.
Linked Issues: none
Known Issues / Workarounds:
None.
User Impact:
Prevents data loss during expense creation.""",

"""================================================================================
Key: NPAY-1070
Type: Story
Summary: Policy limit warnings and justification
Status: Done
Priority: High
Fix Version: 3.5.0
Release Date: 2026-03-18
Components: Expenses, Policy Engine
Labels: new-feature, compliance
Reporter: Finance Dept
Assignee: Bob Chen
Description:
We need strict enforcement of meal limits.
Limit is 100 for Tier 1 cities, 50 for Tier 2 cities.
Acceptance Criteria:
- Soft warning at 80% of the limit.
- Hard block at 100% of the limit.
- Allow exceeding 100% ONLY if the user provides a Justification.
- Show error EXP-1042 if no justification is provided.
Comments:
[2026-03-10 10:14] Bob Chen: Logic added to policy_engine.py.
Linked Issues: none
Known Issues / Workarounds:
If you see EXP-1042, type a reason in the Justification box to proceed.
User Impact:
Ensures compliance with company spending rules.""",

"""================================================================================
Key: NPAY-1080
Type: Story
Summary: Delegate approvals during PTO
Status: Done
Priority: High
Fix Version: 3.8.0
Release Date: 2026-07-15
Components: Approvals, Settings
Labels: new-feature, approvals
Reporter: HR Dept
Assignee: Daniel Okafor
Description:
Managers need to delegate their approval rights when they go on vacation.
Acceptance Criteria:
- Add a Delegate button under Approvals -> Settings (gear icon).
- Target user must have the APPROVER role.
- Delegation max duration is 30 days.
- Throw error DEL-422 for invalid requests.
Comments:
[2026-07-05 10:14] Daniel Okafor: Implemented. The gear icon is the only place to set this up.
Linked Issues: none
Known Issues / Workarounds:
None.
User Impact:
Prevents approval bottlenecks during holidays.""",

"""================================================================================
Key: NPAY-1090
Type: Story
Summary: Multi-currency expense support
Status: Done
Priority: Medium
Fix Version: 3.9.0
Release Date: Unreleased
Components: Expenses, Currencies
Labels: new-feature, currencies
Reporter: Alice Smith
Assignee: Bob Chen
Description:
Allow employees to enter expenses in foreign currencies (e.g., EUR).
Acceptance Criteria:
- Show a currency picker.
- Convert automatically at the day's rate.
- Hide the picker unless the cost-center allows foreign currency.
Comments:
[2026-08-01 10:14] Bob Chen: Currently in progress, scheduled for 3.9.0.
Linked Issues: none
Known Issues / Workarounds:
Not released yet.
User Impact:
Better international travel support.""",

"""================================================================================
Key: NPAY-1095
Type: Story
Summary: Dark mode support
Status: Done
Priority: Low
Fix Version: 3.4.5
Release Date: 2026-02-28
Components: Profile, Appearance
Labels: new-feature, UI
Reporter: John Doe
Assignee: Alice Smith
Description:
Users want a dark mode for the application.
Acceptance Criteria:
- Add a toggle under Profile -> Appearance.
- Save user preference.
Comments:
[2026-02-20 10:14] Alice Smith: Added CSS classes and toggle button.
Linked Issues: none
Known Issues / Workarounds:
None.
User Impact:
Reduces eye strain."""
]

# Generate additional filler tickets to reach ~75 tickets total
for i in range(1100, 1165):
    feature, component = features[i % len(features)]
    status = statuses[i % len(statuses)]
    priority = priorities[i % len(priorities)]
    
    manual_tickets.append(f"""================================================================================
Key: NPAY-{i}
Type: Task
Summary: Improve performance of {feature}
Status: {status}
Priority: {priority}
Fix Version: 3.7.{i % 5}
Release Date: 2026-08-{i%28 + 1:02d}
Components: {component}
Labels: tech-debt
Reporter: System
Assignee: DevTeam
Description:
Routine optimization for {feature} to reduce latency and improve database query efficiency.
Acceptance Criteria:
- P99 latency under 200ms.
Comments:
[2026-07-01 09:00] DevTeam: Query analyzed and indexed.
Linked Issues: relates to NPAY-1001
Known Issues / Workarounds:
None.
User Impact:
Faster load times.""")

# Write all to file
os.makedirs("d:/hackerthon/ReleaseIQ/data/jira", exist_ok=True)
with open("d:/hackerthon/ReleaseIQ/data/jira/jira_tickets_dump.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(manual_tickets))

print(f"Generated {len(manual_tickets)} tickets.")
