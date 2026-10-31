from typing import Optional, Any
from pydantic import BaseModel, Field, model_validator


class ChatRequest(BaseModel):
    question: Optional[str] = Field(None, description="Student's natural language question regarding cutoffs.")
    student_rank: Optional[int] = Field(None, description="Optional KCET engineering rank.")
    category: Optional[str] = Field("GM", description="Reservation category (default: GM).")
    branch: Optional[str] = Field(None, description="Preferred engineering branch (e.g. CS, EC, ME).")
    round: int = Field(1, description="Counselling round (default: 1).")
    seat_region: str = Field("Rest of Karnataka", description="Seat region.")
    session_id: Optional[str] = Field(None, description="Lightweight session ID for conversation context.")

    @model_validator(mode="before")
    @classmethod
    def normalize_request_aliases(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Map 'query' alias to 'question'
            if not data.get("question") and data.get("query"):
                data["question"] = data["query"]
            # Map 'rank' alias to 'student_rank'
            if data.get("student_rank") is None and data.get("rank") is not None:
                try:
                    data["student_rank"] = int(data["rank"])
                except (ValueError, TypeError):
                    pass
            # Map 'region' alias to 'seat_region'
            if not data.get("seat_region") or data.get("seat_region") == "General":
                if data.get("region") and data.get("region") != "General":
                    data["seat_region"] = data["region"]
                else:
                    data["seat_region"] = "Rest of Karnataka"
        return data
