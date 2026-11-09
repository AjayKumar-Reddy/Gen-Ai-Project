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

    # 3. KCET Rank or Numerical Rank Range
    range_match = re.search(r"\b(?:between|from|range)\s+(\d+)\s*(?:and|to|-)\s*(\d+)\b", query, re.IGNORECASE)
    if not range_match:
        range_match = re.search(r"\b(?:rank|ranks)\s+(\d+)\s*(?:to|-)\s*(\d+)\b", query, re.IGNORECASE)
    if range_match:
        try:
            r1 = int(range_match.group(1))
            r2 = int(range_match.group(2))
            entities["min_rank"] = min(r1, r2)
            entities["max_rank"] = max(r1, r2)
        except ValueError:
            pass
    else:
        rank_match = re.search(r"\b(?:rank|merit|rank\s*is|rank:?)\s*(\d+)\b", query, re.IGNORECASE)
        if not rank_match:
            rank_match = re.search(r"\b(\d+)\s*(?:rank|ranking)\b", query, re.IGNORECASE)
        if rank_match:
            try:
                entities["student_rank"] = int(rank_match.group(1))
            except ValueError:
                pass

    # 4. Engineering Branch identification
    full_branch_map = [
        (r"\bcomputer\s+science\b", "CS"),
        (r"\binformation\s+science\b", "IS"),
        (r"\belectronics\s+(?:and|&)\s+communication\b", "EC"),
        (r"\belectrical\s+(?:and|&)\s+electronics\b", "EE"),
        (r"\bmechanical\s+engineering\b", "ME"),
        (r"\bcivil\s+engineering\b", "CV"),
        (r"\bartificial\s+intelligence\b", "AI"),
        (r"\bbiotechnology\b", "BT"),
        (r"\baeronautical\b", "AE"),
        (r"\bchemical\s+engineering\b", "CH"),
    ]
    detected_branch = None
    for pattern, b_code in full_branch_map:
        if re.search(pattern, query, re.IGNORECASE):
            detected_branch = b_code
            break

    if not detected_branch:
        VALID_BRANCH_CODES = {
            "CS": "CS", "CSE": "CS",
            "IS": "IS", "ISE": "IS", "IE": "IS",
            "EC": "EC", "ECE": "EC",
            "EE": "EE", "EEE": "EE",
            "ME": "ME", "MECH": "ME",
            "CV": "CV", "CIVIL": "CV",
            "AI": "AI", "AIML": "AI",
            "AD": "AD", "AIDS": "AD",
            "BT": "BT", "BIOTECH": "BT",
            "CH": "CH", "CHEM": "CH",
            "AE": "AE", "RO": "RO",
        }
        # A. Match "X branch" / "X course" / "X dept" (e.g. "is branch", "cs course")
        m1 = re.search(r"\b([a-zA-Z]{2,6})\s+(?:branch|course|dept|engineering)\b", query, re.IGNORECASE)
        if m1 and m1.group(1).upper() in VALID_BRANCH_CODES:
            detected_branch = VALID_BRANCH_CODES[m1.group(1).upper()]
        else:
            # B. Match "in X" / "for X" (e.g. "in is", "for cs")
            m2 = re.search(r"(?:branch|course|dept|engineering|in|for)\s+([a-zA-Z]{2,6})\b", query, re.IGNORECASE)
            if m2 and m2.group(1).upper() in VALID_BRANCH_CODES:
                detected_branch = VALID_BRANCH_CODES[m2.group(1).upper()]
            else:
                # C. Standalone unambiguous acronyms (CSE, ECE, ISE, AIML, etc.)
                m3 = re.search(r"\b(CSE|ECE|ISE|EEE|MECH|AIML|AIDS|BIOTECH)\b", query, re.IGNORECASE)
                if m3:
                    detected_branch = VALID_BRANCH_CODES.get(m3.group(1).upper())
                else:
                    # D. Standalone uppercase codes
                    for token in query.split():
                        clean_t = re.sub(r"[^A-Za-z]", "", token)
                        if token == clean_t and clean_t in ["CS", "EC", "EE", "CV", "AD", "BT", "CH", "AE"]:
                            detected_branch = clean_t
                            break

    if detected_branch:
        entities["branch"] = detected_branch

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

        # 3. Structured Numerical Rank Filtering (Point Rank or Range)
        structured_matches = []
        min_rank = extracted_entities.get("min_rank")
        max_rank = extracted_entities.get("max_rank")
        has_rank_query = (final_rank is not None and final_rank > 0) or min_rank is not None

        if has_rank_query:
            logger.info(
                f"Executing structured database filtering for rank={final_rank}, "
                f"range={min_rank}-{max_rank}, category={final_category}, branch={final_branch}"
            )
            structured_matches = self.cutoff_service.filter_by_rank(
                student_rank=final_rank,
                min_rank=min_rank,
                max_rank=max_rank,
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

        # If student rank or range was applied, results MUST strictly be the structured rank matches
        # Never fall back to arbitrary retrieved documents with lower closing ranks
        if has_rank_query:
            final_results = structured_matches
        else:
            final_results = [d.get("metadata") for d in fused_documents if d.get("metadata")]

        pipeline_steps = ["Entity & Intent Extraction"]
        if has_rank_query:
            pipeline_steps.append("Structured PostgreSQL SQL Filtering")
        pipeline_steps.extend([
            "BM25 Inverted Index Search",
            "Dense Vector Similarity (pgvector 768d)",
            "Reciprocal Rank Fusion (RRF k=60)",
            "Gemini 3.5 Flash Lite Synthesis",
        ])

        return {
            "answer": generation_res["answer"],
            "evidence_status": generation_res["evidence_status"],
            "results": final_results,
            "sources": generation_res["sources"],
            "retrieval_metadata": {
                "dense_results": retrieval_res["metadata"]["dense_count"],
                "bm25_results": retrieval_res["metadata"]["bm25_count"],
                "hybrid_results": retrieval_res["metadata"]["fused_count"],
                "student_rank_applied": final_rank,
                "category_applied": final_category,
                "branch_applied": final_branch,
                "sql_matches": len(structured_matches),
                "pipeline_steps": pipeline_steps,
            },
        }


_chatbot_service: Optional[ChatbotService] = None


def get_chatbot_service() -> ChatbotService:
    global _chatbot_service
    if _chatbot_service is None:
        _chatbot_service = ChatbotService()
    return _chatbot_service
