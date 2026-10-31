from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    Index,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base, relationship
from pgvector.sqlalchemy import Vector

Base = declarative_base()


class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(255), nullable=False)
    source_url = Column(String(1024), nullable=True)
    year = Column(Integer, nullable=False, default=2026)
    counselling_round = Column(Integer, nullable=False, default=1)
    seat_region = Column(String(100), nullable=False, default="Rest of Karnataka")
    uploaded_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    cutoff_records = relationship(
        "CutoffRecord", back_populates="source", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Source(id={self.id}, filename='{self.filename}', year={self.year}, round={self.counselling_round})>"


class CutoffRecord(Base):
    __tablename__ = "cutoff_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    college_code = Column(String(20), nullable=False, index=True)
    college_name = Column(String(500), nullable=False, index=True)
    location = Column(String(255), nullable=True)
    course_code = Column(String(20), nullable=False, index=True)
    course_name = Column(String(500), nullable=False, index=True)
    category = Column(String(20), nullable=False, index=True)
    # Closing rank can be NULL if not allotted / missing. NEVER 0.
    closing_rank = Column(Integer, nullable=True, index=True)
    year = Column(Integer, nullable=False, index=True)
    counselling_round = Column(Integer, nullable=False, index=True)
    seat_region = Column(String(100), nullable=False, index=True)
    source_id = Column(Integer, ForeignKey("sources.id", ondelete="CASCADE"), nullable=False)
    page_number = Column(Integer, nullable=False)

    source = relationship("Source", back_populates="cutoff_records")
    document = relationship(
        "DocumentRecord", back_populates="cutoff_record", uselist=False, cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint(
            "college_code",
            "course_name",
            "category",
            "year",
            "counselling_round",
            "seat_region",
            name="uq_cutoff_unique_combination",
        ),
        Index("ix_cutoff_lookup", "category", "course_code", "closing_rank", "counselling_round"),
    )

    def __repr__(self) -> str:
        return (
            f"<CutoffRecord(code='{self.college_code}', course='{self.course_code}', "
            f"cat='{self.category}', rank={self.closing_rank})>"
        )


class DocumentRecord(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cutoff_record_id = Column(
        Integer,
        ForeignKey("cutoff_records.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    content = Column(Text, nullable=False)
    # JSONB metadata for fast retrieval and structured filtering
    metadata_ = Column("metadata", JSONB, nullable=False)
    # 768-dimension vector for gemini-embedding-001
    embedding = Column(Vector(768), nullable=True)

    cutoff_record = relationship("CutoffRecord", back_populates="document")

    def __repr__(self) -> str:
        return f"<DocumentRecord(id={self.id}, cutoff_record_id={self.cutoff_record_id})>"

