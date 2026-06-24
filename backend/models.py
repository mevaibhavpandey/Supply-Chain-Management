from sqlalchemy import Column, String, Float, Integer, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class ValidationRun(Base):
    __tablename__ = "validation_runs"
    
    id = Column(String, primary_key=True)
    agent_name = Column(String, nullable=False)
    submission_type = Column(String, nullable=False)  # repo_url | zip | files
    submission_url = Column(String, nullable=True)
    files_path = Column(String, nullable=True)
    status = Column(String, nullable=False, default="pending")  # pending|running|complete|failed
    progress = Column(Integer, default=0)
    current_step = Column(String, default="Queued")
    scm_use_case = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    expected_input = Column(Text, nullable=True)
    expected_output = Column(Text, nullable=True)
    enable_llm = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    
    scores = relationship("TrustScore", back_populates="run", cascade="all, delete-orphan")
    findings = relationship("Finding", back_populates="run", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="run", cascade="all, delete-orphan")
    evidence = relationship("Evidence", back_populates="run", cascade="all, delete-orphan")
    ai_insights = relationship("AIInsight", back_populates="run", cascade="all, delete-orphan")

class TrustScore(Base):
    __tablename__ = "trust_scores"
    
    id = Column(String, primary_key=True)
    run_id = Column(String, ForeignKey("validation_runs.id"), nullable=False)
    dimension = Column(String, nullable=False)  # 'overall' or dimension name
    score = Column(Float, nullable=False)
    max_score = Column(Float, nullable=False, default=100.0)
    remarks = Column(Text, nullable=True)
    
    run = relationship("ValidationRun", back_populates="scores")

class Finding(Base):
    __tablename__ = "findings"
    
    id = Column(String, primary_key=True)
    run_id = Column(String, ForeignKey("validation_runs.id"), nullable=False)
    rule_id = Column(String, nullable=False)
    severity = Column(String, nullable=False)  # Critical | High | Medium | Low
    category = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    why_it_matters = Column(Text, nullable=False)
    score_impact = Column(Float, nullable=False)
    dimension = Column(String, nullable=False)
    
    run = relationship("ValidationRun", back_populates="findings")
    evidence = relationship("Evidence", back_populates="finding")
    recommendations = relationship("Recommendation", back_populates="finding")

class Recommendation(Base):
    __tablename__ = "recommendations"
    
    id = Column(String, primary_key=True)
    run_id = Column(String, ForeignKey("validation_runs.id"), nullable=False)
    finding_id = Column(String, ForeignKey("findings.id"), nullable=False)
    title = Column(String, nullable=False)
    recommendation = Column(Text, nullable=False)
    implementation_guidance = Column(Text, nullable=True)
    priority = Column(String, nullable=False)  # Critical | High | Medium | Low
    expected_impact = Column(Text, nullable=False)
    impacted_dimension = Column(String, nullable=True)
    
    run = relationship("ValidationRun", back_populates="recommendations")
    finding = relationship("Finding", back_populates="recommendations")

class Evidence(Base):
    __tablename__ = "evidence"
    
    id = Column(String, primary_key=True)
    run_id = Column(String, ForeignKey("validation_runs.id"), nullable=False)
    finding_id = Column(String, ForeignKey("findings.id"), nullable=True)
    file_path = Column(String, nullable=False)
    line_start = Column(Integer, nullable=True)
    line_end = Column(Integer, nullable=True)
    snippet = Column(Text, nullable=True)
    reason = Column(Text, nullable=False)
    
    run = relationship("ValidationRun", back_populates="evidence")
    finding = relationship("Finding", back_populates="evidence")

class AIInsight(Base):
    __tablename__ = "ai_insights"
    
    id = Column(String, primary_key=True)
    run_id = Column(String, ForeignKey("validation_runs.id"), nullable=False)
    insight_type = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    run = relationship("ValidationRun", back_populates="ai_insights")
