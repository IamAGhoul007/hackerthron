import os
import time
from datetime import datetime
from typing import Dict, Any

from app.core.schemas import ChatResponse, Source, MismatchDetail
from app.core.security import screen_prompt_injection
from app.engine.query_understanding import QueryUnderstanding
from app.retrieval.hybrid import HybridRetriever
from app.retrieval.confidence import compute_confidence, check_confidence
from app.engine.cross_check import CrossCheck
from app.engine.answer_composer import AnswerComposer

class CascadeOrchestrator:
    def __init__(self):
        self.query_understanding = QueryUnderstanding()
        self.jira_retriever = HybridRetriever("jira_tickets")
        self.code_retriever = HybridRetriever("code_chunks")
        self.cross_check = CrossCheck()
        self.answer_composer = AnswerComposer()

    def process(self, session_id: str, message: str, history: list, request_id: str) -> ChatResponse:
        start_time = time.time()
        
        # Step 1: Query Understanding & Security
        if screen_prompt_injection(message):
            return self._build_response(session_id, request_id, start_time, 
                                        "I cannot fulfill requests that attempt to bypass my instructions.",
                                        "refused", 1.0, [], MismatchDetail(detected=False))

        qu_result = self.query_understanding.understand(message, history)
        
        intent = qu_result.get("intent")
        if intent in ["out_of_scope", "gibberish"]:
            fallback_msg = "I didn't quite catch what you mean." if intent == "gibberish" else "I am a read-only guide and cannot answer questions outside the scope of this project."
            msg = qu_result.get("clarifying_question") or fallback_msg
            return self._build_response(session_id, request_id, start_time,
                                        msg, "refused", 1.0, [], MismatchDetail(detected=False))
                                        
        if qu_result.get("needs_clarification"):
            return self._build_response(session_id, request_id, start_time,
                                        qu_result.get("clarifying_question", "Could you provide more details?"),
                                        "clarification", 1.0, [], MismatchDetail(detected=False))

        queries = qu_result.get("rewrites", [message])
        top_k_retrieve = int(os.getenv("TOP_K_RETRIEVE", "12"))
        top_k_context = int(os.getenv("TOP_K_CONTEXT", "5"))

        # Step 2: Jira Retrieval
        jira_results = self.jira_retriever.search(queries, top_k=top_k_retrieve)
        jira_confidence = compute_confidence(jira_results)
        
        # Step 3 & 4: Cascade & Cross-check
        final_answer = ""
        route = ""
        sources = []
        mismatch = MismatchDetail(detected=False)
        escalation_note = None
        
        if check_confidence(jira_confidence, "jira"):
            route = "jira"
            sources = self._format_sources(jira_results[:top_k_context], "jira")
            context = "\n".join([r['document'] for r in jira_results[:top_k_context]])
            
            # Warranty Check
            intent = qu_result.get("intent")
            warranty_msg = ""
            if intent in ["code_change_request", "error", "troubleshooting", "missing_feature"]:
                latest_date = None
                if jira_results:
                    rd_str = jira_results[0]['metadata'].get('release_date')
                    if rd_str:
                        try:
                            latest_date = datetime.strptime(rd_str, "%Y-%m-%d")
                        except ValueError:
                            pass
                            
                if latest_date:
                    gap = (datetime.now() - latest_date).days
                    if gap <= 90:
                        warranty_msg = "\n\n**Warranty Status**: This issue is in warranty. Please contact the dev team of the app."
                    else:
                        warranty_msg = "\n\n**Warranty Status**: This issue is out of warranty. Please contact the internal team asking them to look into the bugs / code changes."
            
            if os.getenv("ENABLE_CROSS_CHECK", "true").lower() == "true":
                code_results = self.code_retriever.search(queries, top_k=top_k_context)
                cc_res = self.cross_check.compare(jira_results[:top_k_context], code_results)
                if not cc_res.get("consistent", True):
                    mismatch = MismatchDetail(detected=True, explanation=cc_res.get("difference"))
                    route = "jira+code"
                    sources.extend(self._format_sources(code_results, "code"))
                    escalation_note = self.answer_composer.compose_escalation(message, context + str(cc_res))
            
            final_answer = self.answer_composer.compose(message, context, "jira")
            if warranty_msg:
                final_answer += warranty_msg
            
        else:
            # Code Retrieval
            code_results = self.code_retriever.search(queries, top_k=top_k_retrieve)
            code_confidence = compute_confidence(code_results)
            
            if check_confidence(code_confidence, "code"):
                route = "code"
                sources = self._format_sources(code_results[:top_k_context], "code")
                context = "\n".join([r['document'] for r in code_results[:top_k_context]])
                final_answer = self.answer_composer.compose(message, context, "code")
                
                if os.getenv("ENABLE_CROSS_CHECK", "true").lower() == "true":
                    cc_res = self.cross_check.compare(jira_results[:top_k_context], code_results[:top_k_context])
                    if not cc_res.get("consistent", True):
                        mismatch = MismatchDetail(detected=True, explanation=cc_res.get("difference"))
                        route = "jira+code"
                        sources.extend(self._format_sources(jira_results[:top_k_context], "jira"))
            else:
                route = "not_found"
                final_answer = "I couldn't find this in release notes or the app. Here is what I did find and a ready-to-send summary you can give to Support."
                escalation_note = self.answer_composer.compose_escalation(message, "\n".join([r['document'] for r in jira_results[:2] + code_results[:2]]))
                sources = self._format_sources(jira_results[:2] + code_results[:2], "mixed")
                
        latency = int((time.time() - start_time) * 1000)
        return self._build_response(session_id, request_id, start_time, final_answer, route, 
                                    max(jira_confidence, 0.5), sources, mismatch, escalation_note)

    def _format_sources(self, results: list, default_type: str) -> list:
        sources = []
        for r in results:
            meta = r['metadata']
            stype = meta.get('source_type', default_type)
            if stype == "jira":
                sources.append(Source(
                    type="jira", id=meta.get("ticket_key"), title=meta.get("summary", ""),
                    fix_version=meta.get("fix_version"), snippet=r['document'][:200], score=r['score']
                ))
            else:
                sources.append(Source(
                    type="code", path=meta.get("file_path"), lines=f"{meta.get('start_line', '')}-{meta.get('end_line', '')}",
                    snippet=r['document'][:200], score=r['score']
                ))
        return sources

    def _build_response(self, session_id, req_id, start, answer, route, conf, sources, mismatch, esc=None) -> ChatResponse:
        return ChatResponse(
            session_id=session_id or "new",
            answer=answer,
            route=route,
            confidence=conf,
            sources=sources,
            possible_mismatch=mismatch,
            escalation_note=esc,
            request_id=req_id,
            latency_ms=int((time.time() - start) * 1000)
        )
