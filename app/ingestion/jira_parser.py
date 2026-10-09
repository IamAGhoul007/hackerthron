import re
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Ticket:
    key: str
    type: str
    summary: str
    status: str
    priority: str
    fix_version: str
    components: str
    labels: str
    description: str
    acceptance_criteria: str
    comments: str
    known_issues: str
    user_impact: str
    
    @property
    def is_released(self) -> bool:
        return "Unreleased" not in self.fix_version and "In Progress" not in self.status

@dataclass
class TicketChunk:
    text: str
    metadata: dict

class JiraParser:
    def __init__(self, file_path: str):
        self.file_path = file_path
        
    def _extract_field(self, text: str, field: str) -> str:
        match = re.search(rf"{field}:\s*(.*?)(?=\n[A-Z][a-zA-Z\s]+:|\n\n|\Z)", text, re.DOTALL)
        if match:
            return match.group(1).strip()
        # For multiline blocks without following standard fields
        match = re.search(rf"{field}:\s*(.*)", text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return ""

    def parse(self) -> List[Ticket]:
        with open(self.file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        raw_tickets = [t.strip() for t in content.split("================================================================================") if t.strip()]
        
        tickets = []
        for rt in raw_tickets:
            if not rt.startswith("Key:"):
                continue
                
            try:
                ticket = Ticket(
                    key=self._extract_field(rt, "Key").split("\n")[0],
                    type=self._extract_field(rt, "Type").split("\n")[0],
                    summary=self._extract_field(rt, "Summary").split("\n")[0],
                    status=self._extract_field(rt, "Status").split("\n")[0],
                    priority=self._extract_field(rt, "Priority").split("\n")[0],
                    fix_version=self._extract_field(rt, "Fix Version").split("\n")[0],
                    components=self._extract_field(rt, "Components").split("\n")[0],
                    labels=self._extract_field(rt, "Labels").split("\n")[0],
                    description=self._extract_field(rt, "Description"),
                    acceptance_criteria=self._extract_field(rt, "Acceptance Criteria"),
                    comments=self._extract_field(rt, "Comments"),
                    known_issues=self._extract_field(rt, "Known Issues / Workarounds"),
                    user_impact=self._extract_field(rt, "User Impact"),
                )
                tickets.append(ticket)
            except Exception as e:
                print(f"Skipping malformed ticket: {e}")
                
        return tickets

    def chunk_tickets(self, tickets: List[Ticket]) -> List[TicketChunk]:
        chunks = []
        for t in tickets:
            base_meta = {
                "ticket_key": t.key,
                "type": t.type,
                "status": t.status,
                "fix_version": t.fix_version,
                "components": t.components,
                "labels": t.labels,
                "released": t.is_released,
                "source_type": "jira"
            }
            
            # Summary chunk
            summary_text = f"[{t.key} | {t.type} | Fix {t.fix_version} | {t.status}] Section: Summary\n"
            summary_text += f"{t.summary}\n{t.description[:600]}"
            chunks.append(TicketChunk(text=summary_text, metadata={**base_meta, "section": "Summary"}))
            
            # Additional sections
            sections = [
                ("Description", t.description),
                ("Acceptance Criteria", t.acceptance_criteria),
                ("Comments", t.comments),
                ("Known Issues/Workarounds", t.known_issues),
                ("User Impact", t.user_impact)
            ]
            
            for sec_name, sec_content in sections:
                if len(sec_content) > 10:
                    text = f"[{t.key} | {t.type} | Fix {t.fix_version} | {t.status}] Section: {sec_name}\n{sec_content}"
                    chunks.append(TicketChunk(text=text, metadata={**base_meta, "section": sec_name}))
                    
        return chunks
