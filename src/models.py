"""
Data models for LangGraph Customer Support Agent
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
import uuid

class Priority(str, Enum):
    """Ticket priority levels"""
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"
    CRITICAL = "critical"

class Status(str, Enum):
    """Ticket status"""
    PENDING = "pending"
    RESOLVED = "resolved"
    ESCALATED = "escalated"
    CLOSED = "closed"

class StageMode(str, Enum):
    """Stage execution modes"""
    ENTRY_ONLY = "entry_only"
    DETERMINISTIC = "deterministic"
    NON_DETERMINISTIC = "non_deterministic"
    HUMAN_INTERACTION = "human_interaction"
    OUTPUT_ONLY = "output_only"

class InputPayload(BaseModel):
    """Input payload schema for customer support requests"""
    customer_name: str = Field(..., description="Name of the customer")
    email: str = Field(..., description="Customer email address")
    query: str = Field(..., description="Customer support query/issue")
    priority: Priority = Field(..., description="Priority level of the ticket")
    ticket_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique ticket identifier")

class AbilityExecution(BaseModel):
    """Record of ability execution"""
    ability_name: str
    server_used: str
    execution_time: datetime
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class StageLog(BaseModel):
    """Log entry for stage execution"""
    stage_name: str
    stage_id: int
    emoji: str
    mode: StageMode
    abilities_executed: List[AbilityExecution] = []
    start_time: datetime
    end_time: Optional[datetime] = None
    success: bool = True
    error: Optional[str] = None

class CustomerSupportState(BaseModel):
    """Complete state for customer support workflow"""
    
    # Original input
    input_payload: InputPayload
    
    # Processing state
    current_stage: int = 1
    processing_complete: bool = False
    
    # Extracted and processed data
    extracted_entities: Dict[str, Any] = {}
    normalized_fields: Dict[str, Any] = {}
    enriched_data: Dict[str, Any] = {}
    knowledge_base_results: List[Dict[str, Any]] = []
    
    # Decision making
    solution_scores: Dict[str, float] = {}
    escalation_needed: bool = False
    escalation_reason: Optional[str] = None
    confidence_score: float = 0.0
    
    # Human interaction
    clarification_requested: bool = False
    clarification_question: Optional[str] = None
    human_response: Optional[str] = None
    
    # Output generation
    generated_response: Optional[str] = None
    api_calls_executed: List[Dict[str, Any]] = []
    notifications_sent: List[Dict[str, Any]] = []
    
    # Metadata
    ticket_status: Status = Status.PENDING
    stage_logs: List[StageLog] = []
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class OutputPayload(BaseModel):
    """Final output payload after processing"""
    ticket_id: str
    status: Status
    response: Optional[str] = None
    confidence_score: float
    escalation_reason: Optional[str] = None
    stage_logs: List[Dict[str, Any]]
    final_payload: Dict[str, Any]
    processing_time: float
    agent_name: str = "Langie"
    agent_version: str = "1.0.0"
    completion_time: datetime = Field(default_factory=datetime.now)

class StageDefinition(BaseModel):
    """Definition of a workflow stage"""
    stage_id: int
    name: str
    emoji: str
    mode: StageMode
    description: str
    abilities: List[Dict[str, str]]
    user_prompt: Optional[str] = None

class AgentConfig(BaseModel):
    """Configuration for the LangGraph agent"""
    agent_name: str = "Langie"
    agent_version: str = "1.0.0"
    stages: List[StageDefinition]
    mcp_servers: Dict[str, Dict[str, str]]
    
def create_sample_input() -> InputPayload:
    """Create a sample input payload for testing"""
    return InputPayload(
        customer_name="John Smith",
        email="john.smith@example.com", 
        query="I can't login to my account. It says my password is incorrect but I'm sure it's right. This is urgent as I need to access my account for an important transaction.",
        priority=Priority.HIGH,
        ticket_id=str(uuid.uuid4())
    )
