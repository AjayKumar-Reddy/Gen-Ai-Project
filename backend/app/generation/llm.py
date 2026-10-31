import logging
from typing import List, Dict, Any, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from app.config.settings import get_settings
from app.generation.prompts import SYSTEM_PROMPT, format_context_for_llm

logger = logging.getLogger(__name__)


def extract_text_from_ai_message(content: Any) -> str:
    """Normalize response content whether string or list of message blocks."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and "text" in item:
                parts.append(item["text"])
            elif isinstance(item, str):
                parts.append(item)
            else:
                parts.append(str(item))
        return "".join(parts)
    return str(content)


class GeminiGenerator:
    """
    Manages Google Gemini LLM generation with strict system prompt grounding
    and temperature 0 for factual cutoff responses.
    """

    def __init__(self):
        self.settings = get_settings()
        self.api_key = self.settings.GOOGLE_API_KEY
        self.model = self.settings.GEMINI_CHAT_MODEL

        self.llm = ChatGoogleGenerativeAI(
            model=self.model,
            google_api_key=self.api_key,
            temperature=0,
        )

    def generate_response(
        self,
        question: str,
        retrieved_documents: List[Dict[str, Any]],
        structured_records: Optional[List[Dict[str, Any]]] = None,
        chat_history: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """
        Validate evidence, build prompt, call Gemini, and return grounded answer.
        """
        # 1. Evidence Validation Step
        has_docs = bool(retrieved_documents and len(retrieved_documents) > 0)
        has_records = bool(structured_records and len(structured_records) > 0)

        if not has_docs and not has_records:
            return {
                "answer": (
                    "I could not find relevant cutoff records for your query in the official KCET "
                    f"{self.settings.DATASET_YEAR} dataset ({self.settings.SEAT_REGION}, "
                    f"Round {self.settings.COUNSELLING_ROUND}).\n\n"
                    "Please check if the college code, course name, or category identifier is spelled correctly."
                ),
                "evidence_status": "insufficient_evidence",
                "sources": [],
            }

        # 2. Build Context
        context_str = format_context_for_llm(
            retrieved_documents=retrieved_documents,
            structured_records=structured_records,
        )

        # 3. Assemble Messages
        messages = [SystemMessage(content=SYSTEM_PROMPT)]

        # Add lightweight session conversation history if provided
        if chat_history:
            for msg in chat_history[-6:]:  # Keep last 3 turns
                if msg.get("role") == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                elif msg.get("role") == "assistant":
                    messages.append(AIMessage(content=msg["content"]))

        user_content = (
            f"EVIDENCE CONTEXT:\n{context_str}\n\n"
            f"STUDENT QUESTION:\n{question}\n\n"
            "Please provide an accurate, fact-grounded answer based strictly on the evidence above."
        )
        messages.append(HumanMessage(content=user_content))

        # 4. Invoke LLM
        logger.info(f"Invoking Gemini LLM ({self.model}) with evidence context...")
        response = self.llm.invoke(messages)
        answer_text = extract_text_from_ai_message(response.content)

        # 5. Extract Source References from Evidence
        sources = []
        seen_sources = set()

        all_evidence = []
        if structured_records:
            all_evidence.extend(structured_records)
        if retrieved_documents:
            all_evidence.extend([d.get("metadata", {}) for d in retrieved_documents])

        for item in all_evidence:
            pdf_ref = f"KCET 2026 Round {item.get('counselling_round', 1)} Cutoff PDF"
            page = item.get("page_number")
            key = (pdf_ref, page)
            if key not in seen_sources and page:
                seen_sources.add(key)
                sources.append({
                    "document": pdf_ref,
                    "page_number": page,
                    "college_code": item.get("college_code"),
                    "college_name": item.get("college_name"),
                    "category": item.get("category"),
                    "closing_rank": item.get("closing_rank"),
                })

        return {
            "answer": answer_text,
            "evidence_status": "supported",
            "sources": sources,
        }

