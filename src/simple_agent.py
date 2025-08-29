"""
Simplified LangGraph Customer Support Agent - Working Implementation
A structured customer support workflow without complex dependencies
"""
import asyncio
import json
import yaml
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

from .models import (
    CustomerSupportState, InputPayload, OutputPayload, StageLog, 
    StageMode, Status, AbilityExecution, Priority
)
import logging

logger = logging.getLogger(__name__)

class SimpleLangGraphAgent:
    """
    Simplified Langie - Customer Support Agent without complex dependencies
    """
    
    def __init__(self, config_path: str = "simple_config.yaml"):
        """Initialize the simplified agent"""
        self.agent_name = "Langie"
        self.agent_version = "1.0.0"
        
        # Load configuration
        try:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        except FileNotFoundError:
            print(f"Warning: {config_path} not found, using default configuration")
            self.config = self._default_config()
        
        print(f"✅ {self.agent_name} v{self.agent_version} initialized successfully!")
        
    def _default_config(self) -> dict:
        """Default configuration if YAML file is missing"""
        return {
            "agent": {"name": "Langie", "version": "1.0.0"},
            "stages": [
                {"stage_id": 1, "name": "INTAKE", "emoji": "📥", "mode": "entry_only"},
                {"stage_id": 2, "name": "UNDERSTAND", "emoji": "🧠", "mode": "deterministic"},
                {"stage_id": 3, "name": "PREPARE", "emoji": "🛠", "mode": "deterministic"},
                {"stage_id": 4, "name": "ASK", "emoji": "❓", "mode": "human_interaction"},
                {"stage_id": 5, "name": "WAIT", "emoji": "⏳", "mode": "deterministic"},
                {"stage_id": 6, "name": "RETRIEVE", "emoji": "📚", "mode": "deterministic"},
                {"stage_id": 7, "name": "DECIDE", "emoji": "⚖", "mode": "non_deterministic"},
                {"stage_id": 8, "name": "UPDATE", "emoji": "🔄", "mode": "deterministic"},
                {"stage_id": 9, "name": "CREATE", "emoji": "✍", "mode": "deterministic"},
                {"stage_id": 10, "name": "DO", "emoji": "🏃", "mode": "deterministic"},
                {"stage_id": 11, "name": "COMPLETE", "emoji": "✅", "mode": "output_only"}
            ]
        }
    
    def _log_stage(self, stage_name: str, stage_id: int, emoji: str, mode: str) -> StageLog:
        """Create and log a stage"""
        stage_log = StageLog(
            stage_name=stage_name,
            stage_id=stage_id,
            emoji=emoji,
            mode=StageMode(mode.lower()),
            start_time=datetime.now()
        )
        
        print(f"{emoji} Stage {stage_id}: {stage_name} ({mode})")
        return stage_log
    
    def _complete_stage(self, stage_log: StageLog, success: bool = True) -> None:
        """Complete a stage log"""
        stage_log.end_time = datetime.now()
        stage_log.success = success
        
        if stage_log.start_time and stage_log.end_time:
            duration = (stage_log.end_time - stage_log.start_time).total_seconds()
            status = "✅" if success else "❌"
            print(f"  {status} Completed in {duration:.2f}s")
    
    async def _simulate_ability(self, ability_name: str, server: str, payload: dict) -> dict:
        """Simulate ability execution with realistic responses"""
        # Simulate processing delay
        await asyncio.sleep(0.1)
        
        responses = {
            "parse_request_text": {
                "structured_data": {
                    "issue_category": "Authentication",
                    "priority_level": "High", 
                    "keywords": ["login", "password", "incorrect", "urgent"],
                    "sentiment": "frustrated"
                }
            },
            "extract_entities": {
                "entities": {
                    "product": "User Account",
                    "issue_type": "Authentication",
                    "urgency": "High",
                    "account_id": f"user_{hash(payload.get('email', '')) % 10000}"
                }
            },
            "normalize_fields": {
                "normalized": {
                    "email": payload.get("email", "").lower().strip(),
                    "priority": payload.get("priority", "").upper(),
                    "timestamp": datetime.now().isoformat()
                }
            },
            "enrich_records": {
                "sla_info": {"response_time": "2 hours", "resolution_time": "24 hours"},
                "historical_tickets": [
                    {"ticket_id": "T-001", "issue": "Password reset", "resolved": True}
                ]
            },
            "add_flags_calculations": {
                "flags": {
                    "high_priority": True,
                    "sla_risk": False,
                    "escalation_score": 25
                }
            },
            "knowledge_base_search": {
                "results": [
                    {
                        "title": "Password reset troubleshooting",
                        "content": "Common solutions for password issues",
                        "relevance": 0.92
                    }
                ]
            },
            "solution_evaluation": {
                "solutions": [
                    {"solution": "Password reset email", "score": 85},
                    {"solution": "Account unlock", "score": 92},
                    {"solution": "Escalate to security", "score": 40}
                ],
                "best_score": 92
            },
            "response_generation": {
                "response": f"""Dear {payload.get('customer_name', 'Customer')},

Thank you for contacting support regarding your login issue. 

I've identified that your account was temporarily locked due to multiple failed login attempts. I've unlocked your account and sent a password reset email to your registered address.

Please check your inbox (and spam folder) for the reset email. If you don't receive it within 10 minutes, please let us know.

Best regards,
Langie - Customer Support Agent
Ticket: {payload.get('ticket_id', 'N/A')}"""
            }
        }
        
        return responses.get(ability_name, {"status": "simulated", "ability": ability_name})
    
    async def process_ticket(self, input_payload: InputPayload) -> OutputPayload:
        """Process a customer support ticket through all 11 stages"""
        print(f"\n🎯 Starting ticket processing for: {input_payload.ticket_id}")
        print(f"   Customer: {input_payload.customer_name} ({input_payload.priority.value.upper()} priority)")
        print(f"   Issue: {input_payload.query[:60]}...")
        print(f"\n{'='*60}")
        
        start_time = datetime.now()
        stage_logs = []
        
        # Initialize state
        state = CustomerSupportState(input_payload=input_payload)
        
        try:
            # Stage 1: INTAKE 📥
            stage_log = self._log_stage("INTAKE", 1, "📥", "entry_only")
            # Accept payload (already in state)
            stage_log.abilities_executed = [
                AbilityExecution(
                    ability_name="accept_payload",
                    server_used="internal",
                    execution_time=datetime.now(),
                    status="success",
                    result={"status": "payload_accepted", "ticket_id": input_payload.ticket_id}
                )
            ]
            self._complete_stage(stage_log)
            stage_logs.append(stage_log)
            
            # Stage 2: UNDERSTAND 🧠
            stage_log = self._log_stage("UNDERSTAND", 2, "🧠", "deterministic")
            parse_result = await self._simulate_ability("parse_request_text", "COMMON", input_payload.dict())
            entity_result = await self._simulate_ability("extract_entities", "ATLAS", input_payload.dict())
            
            state.extracted_entities.update(parse_result.get("structured_data", {}))
            state.extracted_entities.update(entity_result.get("entities", {}))
            
            stage_log.abilities_executed = [
                AbilityExecution(
                    ability_name="parse_request_text",
                    server_used="COMMON",
                    execution_time=datetime.now(),
                    status="success",
                    result=parse_result
                ),
                AbilityExecution(
                    ability_name="extract_entities",
                    server_used="ATLAS",
                    execution_time=datetime.now(),
                    status="success",
                    result=entity_result
                )
            ]
            self._complete_stage(stage_log)
            stage_logs.append(stage_log)
            
            # Stage 3: PREPARE 🛠
            stage_log = self._log_stage("PREPARE", 3, "🛠", "deterministic")
            norm_result = await self._simulate_ability("normalize_fields", "COMMON", input_payload.dict())
            enrich_result = await self._simulate_ability("enrich_records", "ATLAS", input_payload.dict())
            flags_result = await self._simulate_ability("add_flags_calculations", "COMMON", input_payload.dict())
            
            state.normalized_fields.update(norm_result.get("normalized", {}))
            state.enriched_data.update(enrich_result)
            state.enriched_data.update(flags_result.get("flags", {}))
            
            stage_log.abilities_executed = [
                AbilityExecution(ability_name="normalize_fields", server_used="COMMON", execution_time=datetime.now(), status="success", result=norm_result),
                AbilityExecution(ability_name="enrich_records", server_used="ATLAS", execution_time=datetime.now(), status="success", result=enrich_result),
                AbilityExecution(ability_name="add_flags_calculations", server_used="COMMON", execution_time=datetime.now(), status="success", result=flags_result)
            ]
            self._complete_stage(stage_log)
            stage_logs.append(stage_log)
            
            # Stage 4: ASK ❓ (Human Interaction)
            stage_log = self._log_stage("ASK", 4, "❓", "human_interaction")
            # Simple logic: high priority tickets don't need clarification
            clarification_needed = input_payload.priority not in [Priority.HIGH, Priority.CRITICAL]
            if clarification_needed:
                state.clarification_requested = True
                state.clarification_question = "Could you provide more details about when this issue started?"
            self._complete_stage(stage_log)
            stage_logs.append(stage_log)
            
            # Stage 5: WAIT ⏳ (Skip if no clarification needed)
            if state.clarification_requested:
                stage_log = self._log_stage("WAIT", 5, "⏳", "deterministic")
                # Simulate human response
                state.human_response = "The issue started this morning when I tried to login for an important transaction."
                self._complete_stage(stage_log)
                stage_logs.append(stage_log)
            
            # Stage 6: RETRIEVE 📚
            stage_log = self._log_stage("RETRIEVE", 6, "📚", "deterministic")
            kb_result = await self._simulate_ability("knowledge_base_search", "ATLAS", input_payload.dict())
            state.knowledge_base_results = kb_result.get("results", [])
            
            stage_log.abilities_executed = [
                AbilityExecution(ability_name="knowledge_base_search", server_used="ATLAS", execution_time=datetime.now(), status="success", result=kb_result)
            ]
            self._complete_stage(stage_log)
            stage_logs.append(stage_log)
            
            # Stage 7: DECIDE ⚖ (Non-Deterministic - Key Decision Point)
            stage_log = self._log_stage("DECIDE", 7, "⚖", "non_deterministic")
            solution_result = await self._simulate_ability("solution_evaluation", "COMMON", input_payload.dict())
            
            state.confidence_score = solution_result.get("best_score", 0)
            state.solution_scores = {sol["solution"]: sol["score"] for sol in solution_result.get("solutions", [])}
            
            # Apply escalation rule: escalate if confidence < 90
            if state.confidence_score < 90:
                state.escalation_needed = True
                state.escalation_reason = f"Low confidence score: {state.confidence_score}%"
                state.ticket_status = Status.ESCALATED
                print(f"  ⚠️  Escalation triggered: {state.escalation_reason}")
            else:
                state.ticket_status = Status.RESOLVED
                print(f"  ✅ High confidence resolution: {state.confidence_score}%")
            
            stage_log.abilities_executed = [
                AbilityExecution(ability_name="solution_evaluation", server_used="COMMON", execution_time=datetime.now(), status="success", result=solution_result)
            ]
            self._complete_stage(stage_log)
            stage_logs.append(stage_log)
            
            # Continue only if not escalated
            if not state.escalation_needed:
                # Stage 8: UPDATE 🔄
                stage_log = self._log_stage("UPDATE", 8, "🔄", "deterministic")
                # Simulate ticket updates
                self._complete_stage(stage_log)
                stage_logs.append(stage_log)
                
                # Stage 9: CREATE ✍
                stage_log = self._log_stage("CREATE", 9, "✍", "deterministic")
                response_result = await self._simulate_ability("response_generation", "COMMON", input_payload.dict())
                state.generated_response = response_result.get("response", "")
                
                stage_log.abilities_executed = [
                    AbilityExecution(ability_name="response_generation", server_used="COMMON", execution_time=datetime.now(), status="success", result=response_result)
                ]
                self._complete_stage(stage_log)
                stage_logs.append(stage_log)
                
                # Stage 10: DO 🏃
                stage_log = self._log_stage("DO", 10, "🏃", "deterministic")
                # Simulate API calls and notifications
                state.api_calls_executed = [
                    {"api": "unlock_account", "status": "success"},
                    {"api": "send_reset_email", "status": "sent"}
                ]
                state.notifications_sent = [
                    {"type": "email", "recipient": input_payload.email, "status": "sent"}
                ]
                self._complete_stage(stage_log)
                stage_logs.append(stage_log)
            
            # Stage 11: COMPLETE ✅
            stage_log = self._log_stage("COMPLETE", 11, "✅", "output_only")
            state.processing_complete = True
            state.updated_at = datetime.now()
            self._complete_stage(stage_log)
            stage_logs.append(stage_log)
            
        except Exception as e:
            print(f"❌ Error during processing: {str(e)}")
            state.ticket_status = Status.PENDING
            
        # Calculate total processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Create output payload
        output = OutputPayload(
            ticket_id=input_payload.ticket_id,
            status=state.ticket_status,
            response=state.generated_response,
            confidence_score=state.confidence_score,
            escalation_reason=state.escalation_reason,
            stage_logs=[log.dict() for log in stage_logs],
            final_payload=state.dict(),
            processing_time=processing_time
        )
        
        print(f"\n{'='*60}")
        print(f"🎉 Processing completed in {processing_time:.2f}s")
        print(f"📊 Final Status: {output.status.value.upper()}")
        print(f"🎯 Confidence Score: {output.confidence_score}%")
        
        if output.escalation_reason:
            print(f"⚠️  Escalation Reason: {output.escalation_reason}")
        
        return output

# Create sample function for easy testing
def create_sample_ticket() -> InputPayload:
    """Create a sample ticket for testing"""
    return InputPayload(
        customer_name="John Smith",
        email="john.smith@example.com",
        query="I can't login to my account. It says my password is incorrect but I'm sure it's right. This is urgent as I need to access my account for an important transaction.",
        priority=Priority.HIGH
    )
