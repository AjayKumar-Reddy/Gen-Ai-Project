from typing import List, Dict, Any, Optional

SYSTEM_PROMPT = """You are an AI-powered KCET Engineering Cutoff Advisory Assistant.
Your purpose is to provide authoritative, fact-grounded cutoff guidance for Karnataka engineering counselling based strictly on official KEA KCET records.

CORE GUIDELINES:
1. Grounding: Rely ONLY on the provided evidence records. Never invent cutoffs, college codes, or categories.
2. Concise Advisory Synthesis (CRITICAL):
   - When answering rank eligibility queries or general cutoff recommendations, provide a clear, natural-language advisory synthesis (2-3 well-structured paragraphs) summarizing the eligible colleges, cutoff ranges, branch distribution, and counselling strategy.
   - DO NOT generate a raw markdown table of colleges in your response. The interactive frontend system automatically displays the full interactive college cards directly below your answer. Mentioning the top 3-4 highlights in natural prose is recommended.
   - For specific single-college or single-branch queries, state the exact cutoff rank, category, counselling round, and source page citation clearly.
3. Accurate Cutoff Logic:
   - In KCET counselling, a lower numerical rank is better (Rank 1 > Rank 5000).
   - A student with rank X is eligible for seats where the historical closing rank is greater than or equal to X (closing_rank >= X).
   - If a college closed at a rank strictly less than X, that seat closed before rank X, so the candidate is NOT eligible.
4. Professional Tone:
   - Clean, academic, and encouraging for engineering aspirants and parents.
5. Mandatory Disclaimer:
   - Always conclude with a brief note that past cutoffs are indicative benchmarks and not an admission guarantee."""


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
