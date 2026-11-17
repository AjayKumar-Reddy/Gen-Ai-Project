export interface SourceCitation {
  college_code: string;
  college_name: string;
  course_code?: string | null;
  course_name?: string | null;
  category: string;
  closing_rank: number | null;
  page_number: number;
  filename?: string;
  round?: number | null;
  region?: string | null;
}

export interface CollegeOption {
  college_code: string;
  college_name: string;
  location?: string | null;
  course_code: string;
  course_name: string;
  category: string;
  closing_rank: number;
  round: number;
  region: string;
  page_number: number;
}

export interface ChatRequest {
  question: string;
  /** Only sent for eligibility checks from the form. */
  rank?: number | null;
  category?: string | null;
  branch?: string | null;
  session_id?: string;
}

export interface RetrievalMetadata {
  dense_results?: number;
  bm25_results?: number;
  hybrid_results?: number;
  student_rank_applied?: number | null;
  category_applied?: string | null;
  branch_applied?: string | null;
  sql_matches?: number;
  pipeline_steps?: string[];
}

export interface ChatResponse {
  answer: string;
  evidence_status?: string;
  sources: SourceCitation[];
  colleges: CollegeOption[];
  retrieval_method: string;
  query_type: string;
  disclaimer: string;
  retrieval_metadata?: RetrievalMetadata;
}

export interface StatsResponse {
  dataset_year?: number;
  total_cutoff_combinations?: number;
  total_cutoff_records?: number;
  non_null_cutoffs?: number;
  college_count?: number;
  total_colleges?: number;
  embedding_model?: string;
  llm_model?: string;
  pgvector_dimension?: number;
  available_categories?: string[];
  available_branches?: { code: string; name: string }[];
}

export interface Message {
  id: string;
  sender: 'user' | 'assistant';
  content: string;
  timestamp: string;
  sources?: SourceCitation[];
  colleges?: CollegeOption[];
  queryType?: string;
  disclaimer?: string;
  retrievalMetadata?: RetrievalMetadata;
  evidenceStatus?: string;
  /** Set on assistant messages that failed, so the user can retry. */
  failedQuestion?: ChatRequest;
}

export interface EligibilityForm {
  rank: string;
  category: string;
  branch: string;
}
