import os
import sys
import json
import logging

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.chatbot import get_chatbot_service

logging.basicConfig(level=logging.WARNING)

BENCHMARK_TESTS = [
    {
        "id": "Q1",
        "category": "BM25 Keyword Retrieval",
        "question": "What is the GM cutoff for Computer Science at RV College of Engineering (E005)?",
        "expected_college_code": "E005",
        "expected_branch": "CS",
        "expected_cutoff": 266,
        "expected_page": 2,
        "evaluation_notes": "Exact college code E005, CS branch, GM category. Verified PDF Page 2.",
    },
    {
        "id": "Q2",
        "category": "BM25 Keyword Retrieval",
        "question": "What is the 2AG cutoff for Civil Engineering at MS Ramaiah (E006)?",
        "expected_college_code": "E006",
        "expected_branch": "CV",
        "expected_cutoff": 21515,
        "expected_page": 2,
        "evaluation_notes": "Exact college code E006, CV branch, 2AG category. Verified PDF Page 2.",
    },
    {
        "id": "Q3",
        "category": "Dense Vector Semantic Retrieval",
        "question": "What is the GM cutoff for Mechanical Engineering at the state autonomous public university on IIT model at KR Circle Bangalore?",
        "expected_college_code": "E001",
        "expected_branch": "ME",
        "expected_cutoff": 22974,
        "expected_page": 1,
        "evaluation_notes": "Semantic paraphrase of UVCE (no college code mentioned). Verified PDF Page 1.",
    },
    {
        "id": "Q4",
        "category": "Dense Vector Semantic Retrieval",
        "question": "What is the GM cutoff for Biotechnology at JSS Science and Technology University in Mysore?",
        "expected_college_code": "E057",
        "expected_branch": "BT",
        "expected_cutoff": 8903,
        "expected_page": 14,
        "evaluation_notes": "Semantic institution name JSS STU Mysore (E057), BT branch. Verified PDF Page 14.",
    },
    {
        "id": "Q5",
        "category": "Hybrid Retrieval (Dense + BM25 RRF)",
        "question": "BMS College of Engineering Bull Temple Road CS cutoff for GM category",
        "expected_college_code": "E048",
        "expected_branch": "CS",
        "expected_cutoff": 2084,
        "expected_page": 13,
        "evaluation_notes": "Combines landmark 'Bull Temple Road' with acronym 'CS'. Verified PDF Page 13.",
    },
    {
        "id": "Q6",
        "category": "Hybrid Retrieval (Dense + BM25 RRF)",
        "question": "Dayananda Sagar College of Engineering cutoff for Artificial Intelligence under 3AG category",
        "expected_college_code": "E007",
        "expected_branch": "AI",
        "expected_cutoff": 4548,
        "expected_page": 3,
        "evaluation_notes": "Autonomous institution name with 3AG category and AI branch. Verified PDF Page 3.",
    },
    {
        "id": "Q7",
        "category": "Structured SQL Numerical Filtering (Range)",
        "question": "Give me colleges between 4000 and 5000 for GM in IS branch",
        "expected_college_code": "E001",
        "expected_branch": "IS",
        "expected_cutoff": 4016,
        "expected_page": 1,
        "evaluation_notes": "Rank range 4000-5000 in IS GM. UVCE is the only college in this window. Verified PDF Page 1.",
    },
    {
        "id": "Q8",
        "category": "Structured SQL Numerical Filtering (Eligibility)",
        "question": "Which colleges can I get in Computer Science with rank 2500 in GM category?",
        "expected_college_code": "E007", # DSCE (3898), BIT (4839)
        "expected_branch": "CS",
        "expected_cutoff": None, # Dynamic multiple matches >= 2500
        "expected_page": None,
        "evaluation_notes": "Eligibility filtering: must return colleges with closing_rank >= 2500, excluding RVCE (266) & BMSCE (2084).",
    },
    {
        "id": "Q9",
        "category": "Structured SQL Numerical Filtering (Category Specific)",
        "question": "What is the 2AG cutoff for Computer Science at Bangalore Institute of Technology (E008)?",
        "expected_college_code": "E008",
        "expected_branch": "CS",
        "expected_cutoff": 6951,
        "expected_page": 3,
        "evaluation_notes": "Category 2AG, E008 CS. Verified PDF Page 3.",
    },
    {
        "id": "Q10",
        "category": "Guardrails & Out-of-Domain Refusal",
        "question": "What is the MBBS NEET cutoff for Bangalore Medical College?",
        "expected_college_code": None,
        "expected_branch": None,
        "expected_cutoff": None,
        "expected_page": None,
        "evaluation_notes": "Medical NEET query out of domain. Must politely state it only covers KCET Engineering.",
    },
]

def run_tests():
    print("=" * 80)
    print("RUNNING 10 VERIFIED BENCHMARK TESTS AGAINST KCET RAG SYSTEM")
    print("=" * 80)

    chatbot = get_chatbot_service()
    results_summary = []

    for test in BENCHMARK_TESTS:
        t_id = test["id"]
        t_cat = test["category"]
        question = test["question"]
        print(f"\n[{t_id}] ({t_cat}): {question}")

        try:
            res = chatbot.process_query(question=question)
            answer = res.get("answer", "")
            results = res.get("results", [])
            sources = res.get("sources", [])
            evidence_status = res.get("evidence_status", "")

            # Check if expected cutoff or college appears in results or answer
            pass_criteria = True
            reasons = []

            if test["expected_cutoff"] is not None:
                cutoff_str = str(test["expected_cutoff"])
                found_in_results = any(
                    str(r.get("closing_rank")) == cutoff_str or r.get("closing_rank") == test["expected_cutoff"]
                    for r in results
                )
                found_in_answer = cutoff_str in answer

                if not (found_in_results or found_in_answer):
                    pass_criteria = False
                    reasons.append(f"Cutoff {cutoff_str} not found in results or answer")

            if test["expected_college_code"] is not None:
                code = test["expected_college_code"]
                found_code_results = any(
                    r.get("college_code") == code
                    for r in results
                )
                found_code_answer = code in answer or code.lower() in answer.lower()

                if not (found_code_results or found_code_answer):
                    pass_criteria = False
                    reasons.append(f"College code {code} not found")

            if t_id == "Q7":
                # Ensure no other branch bled into the results
                non_is_matches = [r for r in results if r.get("branch_code", r.get("course_code")) != "IS"]
                if non_is_matches:
                    pass_criteria = False
                    reasons.append(f"Branch bleed: found non-IS branches {set(r.get('branch_code', r.get('course_code')) for r in non_is_matches)}")

            if t_id == "Q8":
                # Ensure all returned colleges have closing_rank >= 2500
                lower_ranks = [r for r in results if r.get("closing_rank") and r.get("closing_rank") < 2500]
                if lower_ranks:
                    pass_criteria = False
                    reasons.append(f"Returned colleges with closing rank < 2500: {[r.get('closing_rank') for r in lower_ranks]}")
                if not results:
                    pass_criteria = False
                    reasons.append("No eligible colleges returned")

            if t_id == "Q10":
                # Should not hallucinate medical cutoffs
                lower_ans = answer.lower()
                is_refusal = any(phrase in lower_ans for phrase in ["engineering", "kcet", "not contain", "medical", "neet", "only covers", "do not have", "does not contain"])
                if not is_refusal:
                    pass_criteria = False
                    reasons.append("Did not identify as out-of-domain medical query")

            status = "PASS" if pass_criteria else "FAIL"
            print(f"Status: {status}")
            if not pass_criteria:
                print(f"Reasons: {reasons}")
            print(f"Answer snippet: {answer[:250]}...")
            print(f"Number of structured/fused cards: {len(results)}")
            if results:
                print(f"Top result: {results[0]}")

            results_summary.append({
                "id": t_id,
                "category": t_cat,
                "question": question,
                "status": status,
                "expected": f"College {test['expected_college_code']}, Cutoff {test['expected_cutoff']}, Pg {test['expected_page']}",
                "reasons": reasons,
                "answer": answer,
                "results_count": len(results),
            })

        except Exception as e:
            print(f"Status: ERROR ({e})")
            results_summary.append({
                "id": t_id,
                "category": t_cat,
                "question": question,
                "status": "ERROR",
                "expected": f"College {test['expected_college_code']}, Cutoff {test['expected_cutoff']}",
                "reasons": [str(e)],
                "answer": "",
                "results_count": 0,
            })

    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    passed_count = sum(1 for r in results_summary if r["status"] == "PASS")
    print(f"Total: {len(results_summary)} | Passed: {passed_count} | Failed: {len(results_summary) - passed_count}\n")
    for r in results_summary:
        print(f"[{r['id']}] {r['status']} - {r['question'][:50]}... (Expected: {r['expected']})")

if __name__ == "__main__":
    run_tests()

