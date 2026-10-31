import logging
import re
from typing import Dict, List, Any, Optional

from app.config.settings import get_settings
from app.retrieval.hybrid_retriever import HybridRetriever, get_hybrid_retriever
from app.services.cutoff_service import CutoffService
from app.generation.llm import GeminiGenerator

logger = logging.getLogger(__name__)
settings = get_settings()

# In-memory lightweight session history cache (session_id -> list of messages)
SESSION_HISTORIES: Dict[str, List[Dict[str, str]]] = {}


def extract_query_entities(query: str) -> Dict[str, Any]:
    """
    Extract rank, category, branch, and college code entities from natural language query.
    """
    entities: Dict[str, Any] = {}

    # 1. College Code (e.g., E005, E001)
    code_match = re.search(r"\b(E\d{3})\b", query, re.IGNORECASE)
    if code_match:
        entities["college_code"] = code_match.group(1).upper()

    # 2. Reservation Category
    cat_match = re.search(
        r"\b(GM|GMK|GMP|GMR|1G|1K|1R|2AG|2AK|2AR|2BG|2BK|2BR|3AG|3AK|3AR|3BG|3BK|3BR|"
        r"S1G|S1K|S1R|S2G|S2K|S2R|S3G|S3K|S3R|S4G|S4K|S4R|STG|STK|STR|NRI|OPN|OTH)\b",
        query,
        re.IGNORECASE,
    )
    if cat_match:
        entities["category"] = cat_match.group(1).upper()

    # 3. KCET Rank (e.g. rank 5000, rank is 12000, 4500 rank)
    rank_match = re.search(r"\b(?:rank|merit|rank\s*is|rank:?)\s*(\d+)\b", query, re.IGNORECASE)
    if not rank_match:
        rank_match = re.search(r"\b(\d+)\s*(?:rank|ranking)\b", query, re.IGNORECASE)
    if rank_match:
        try:
            entities["student_rank"] = int(rank_match.group(1))
        except ValueError:
            pass

    # 4. Engineering Branch abbreviations (avoid matching common English words like 'is')
    # Match longer / unambiguous branch tokens first
    branch_match = re.search(
        r"\b(CSE|ECE|ISE|EEE|MECH|CIVIL|AIML|AIDS|BIOTECH|CHEM)\b",
        query,
        re.IGNORECASE,
    )
    if not branch_match:
        # For 2-letter tokens, match case-sensitively or when preceded by branch/course/engineering
        branch_match = re.search(
            r"(?:branch|course|dept|engineering|in)\s+([A-Z]{2})\b",
            query,
        )
        if not branch_match:
            # Match standalone uppercase codes except common words
            for token in query.split():
                clean_t = re.sub(r"[^A-Za-z]", "", token)
                if clean_t in ["CS", "EC", "EE", "ME", "CV", "AI", "AD", "BT", "CH", "IM", "AE", "RO"]:
                    branch_match = re.search(r"\b" + clean_t + r"\b", query)
                    break
    if branch_match:
        raw_b = branch_match.group(1).upper()
        # Normalize to standard code
        branch_map = {
            "CSE": "CS", "CS": "CS",
            "ECE": "EC", "EC": "EC",
            "ISE": "IS", "IS": "IS",
            "EEE": "EE", "EE": "EE",
            "MECH": "ME", "ME": "ME",
            "CIVIL": "CV", "CV": "CV",
            "AIML": "AI", "AI": "AI",
            "AIDS": "AD", "AD": "AD",
            "BIOTECH": "BT", "BT": "BT",
            "CHEM": "CH", "CH": "CH",
        }
        entities["branch"] = branch_map.get(raw_b, raw_b)

    return entities


class ChatbotService:
    """
    Coordinates Intent Extraction, Hybrid RAG Retrieval, Structured SQL Filtering,
    and Gemini LLM Generation.
    """

    def __init__(
        self,
        hybrid_retriever: Optional[HybridRetriever] = None,
        cutoff_service: Optional[CutoffService] = None,
        generator: Optional[GeminiGenerator] = None,
    ):
        self.retriever = hybrid_retriever or get_hybrid_retriever()
        self.cutoff_service = cutoff_service or CutoffService()
        self.generator = generator or GeminiGenerator()

    def process_query(
        self,
        question: str,
        student_rank: Optional[int] = None,
        category: Optional[str] = None,
        branch: Optional[str] = None,
        counselling_round: int = 1,
        seat_region: str = "Rest of Karnataka",
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        End-to-end question processing pipeline.
        """
        logger.info(f"Processing query: '{question}' (Session: {session_id})")

        # 1. Entity Extraction from query text
        extracted_entities = extract_query_entities(question)

        # Explicitly supplied parameters override extracted ones
        final_rank = student_rank if student_rank is not None else extracted_entities.get("student_rank")
        final_category = category or extracted_entities.get("category") or "GM"
        final_branch = branch or extracted_entities.get("branch")
        final_college_code = extracted_entities.get("college_code")

        filters = {
            "category": final_category,
        }
        if final_college_code:
            filters["college_code"] = final_college_code
        if final_branch:
            filters["course_code"] = final_branch

        # 2. Retrieve Hybrid RAG Evidence (Dense + BM25 + RRF)
        search_query = question
        # Enhance query with entities if not already in text
        if final_college_code and final_college_code.lower() not in question.lower():
            search_query += f" college code {final_college_code}"
        if final_branch and final_branch.lower() not in question.lower():
            search_query += f" course {final_branch}"

        retrieval_res = self.retriever.hybrid_search(
            query=search_query,
            top_k=settings.TOP_K,
            filters=filters,
        )
        fused_documents = retrieval_res["fused_results"]

        # 3. Structured Rank Filtering (if student rank is present)
        structured_matches = []
        if final_rank is not None and final_rank > 0:
            logger.info(
                f"Executing structured database filtering for rank {final_rank}, "
                f"category {final_category}, branch {final_branch}"
            )
            structured_matches = self.cutoff_service.filter_by_rank(
                student_rank=final_rank,
                category=final_category,
                branch=final_branch,
                counselling_round=counselling_round,
                seat_region=seat_region,
                college_code=final_college_code,
                limit=15,
            )

        # 4. Manage Session Chat History
        history = []
        if session_id:
            history = SESSION_HISTORIES.get(session_id, [])

        # 5. Generate Grounded Response with Gemini LLM
        generation_res = self.generator.generate_response(
            question=question,
            retrieved_documents=fused_documents,
            structured_records=structured_matches,
            chat_history=history,
        )

        # Update Session History
        if session_id:
            if session_id not in SESSION_HISTORIES:
                SESSION_HISTORIES[session_id] = []
            SESSION_HISTORIES[session_id].append({"role": "user", "content": question})
            SESSION_HISTORIES[session_id].append({"role": "assistant", "content": generation_res["answer"]})
            # Prune to last 10 messages
            if len(SESSION_HISTORIES[session_id]) > 10:
                SESSION_HISTORIES[session_id] = SESSION_HISTORIES[session_id][-10:]

        return {
            "answer": generation_res["answer"],
            "evidence_status": generation_res["evidence_status"],
            "results": structured_matches if structured_matches else [d.get("metadata") for d in fused_documents],
            "sources": generation_res["sources"],
            "retrieval_metadata": {
                "dense_results": retrieval_res["metadata"]["dense_count"],
                "bm25_results": retrieval_res["metadata"]["bm25_count"],
                "hybrid_results": retrieval_res["metadata"]["fused_count"],
                "student_rank_applied": final_rank,
                "category_applied": final_category,
                "branch_applied": final_branch,
            },
        }


_chatbot_service: Optional[ChatbotService] = None


def get_chatbot_service() -> ChatbotService:
    global _chatbot_service
    if _chatbot_service is None:
        _chatbot_service = ChatbotService()
    return _chatbot_service
