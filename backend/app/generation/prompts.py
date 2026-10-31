from typing import List, Dict, Any, Optional

SYSTEM_PROMPT = """You are an AI-powered KCET engineering college information assistant.
Your purpose is to help engineering aspirants understand official KCET engineering cutoff information.

STRICT RULES:
1. Answer cutoff-related questions using ONLY the supplied retrieved KCET records.
2. Never invent college names, college codes, course codes, cutoff ranks or categories.
3. Never assume missing information.
4. Preserve exact numerical cutoff values.
5. Always identify the category and counselling round when relevant.
6. Mention the year (2026) and seat region (Rest of Karnataka) when available.
7. Cite the source PDF and page number for factual cutoff information.
8. Distinguish historical cutoff information from admission guarantees.
9. Never claim that a student will definitely receive a seat. Admission cutoffs fluctuate annually.
10. If the retrieved records do not support the question, explicitly state that the information is unavailable in the current dataset.
11. Do not answer unrelated questions using invented KCET information.
12. If records conflict, explain the discrepancy instead of choosing an unsupported value.

Answer in clear, courteous, and accurate language suitable for engineering aspirants and parents.
Include markdown tables or bullet points where appropriate for clarity.
Always add a cautionary disclaimer that past cutoffs are indicative benchmarks and do not guarantee future seat allotment."""


def format_context_for_llm(
    retrieved_documents: List[Dict[str, Any]],
    structured_records: Optional[List[Dict[str, Any]]] = None,
) -> str:
    """Format evidence documents and structured records into LLM context."""
    sections = []

    if structured_records:
        sec = ["=== STRUCTURED RANK FILTERING EVIDENCE (Deterministic Database Results) ==="]
        for r in structured_records[:15]:
            sec.append(
                f"- College: {r['college_code']} - {r['college_name']} ({r.get('location', 'Karnataka')})\n"
                f"  Branch: {r['course_code']} ({r['course_name']})\n"
                f"  Category: {r['category']} | Historical Closing Rank: {r['closing_rank']}\n"
                f"  Round: {r['counselling_round']} | Year: {r['year']} | Seat Region: {r['seat_region']}\n"
                f"  Source: Official KCET Cutoff PDF, Page {r['page_number']}"
            )
        sections.append("\n".join(sec))

    if retrieved_documents:
        sec = ["=== RETRIEVED HYBRID RAG EVIDENCE (Dense pgvector + BM25 + RRF) ==="]
        for idx, doc in enumerate(retrieved_documents[:10], start=1):
            meta = doc.get("metadata", {})
            sec.append(
                f"[{idx}] {meta.get('college_code', '')} - {meta.get('college_name', '')}\n"
                f"    Course: {meta.get('course_code', '')} ({meta.get('course_name', '')})\n"
                f"    Category: {meta.get('category', '')} | Closing Rank: {meta.get('closing_rank', 'N/A')}\n"
                f"    Round: {meta.get('counselling_round', 1)} | Year: {meta.get('year', 2026)} | Region: {meta.get('seat_region', 'Rest of Karnataka')}\n"
                f"    Source: Official KCET Cutoff PDF | Page: {meta.get('page_number', 'N/A')}"
            )
        sections.append("\n".join(sec))

    return "\n\n".join(sections)

