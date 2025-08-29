"""
LangGraph Customer Support Agent - Main Implementation
A structured and logical LangGraph Agent for customer support workflows
"""
import asyncio
import yaml
from typing import Dict, Any, List, Optional
from datetime import datetime
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

from .models import (
    CustomerSupportState, InputPayload, OutputPayload, StageLog, 
    StageMode, Status, AbilityExecution
)
from .mcp_client import MCPManager
from .config import get_primary_api_key, settings
import logging

logger = logging.getLogger(__name__)

class LangGraphCustomerSupportAgent:
    """
    Langie - A structured and logical LangGraph Agent for customer support workflows
    """
    
    def __init__(self, config_path: str = "agent_config.yaml"):
        """Initialize the agent with configuration"""
        self.agent_name = "Langie"
        self.agent_version = "1.0.0"
        
        # Load configuration
        with open("agent_config.yaml", encoding="utf-8") as f:
             self.config = yaml.safe_load(f)

        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model_name=settings.model_name,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
            openai_api_key=get_primary_api_key()
        )
        
        # Initialize MCP Manager
        self.mcp_manager = MCPManager()
        
        # Build the workflow graph
        self.workflow = self._build_workflow()
        
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow with all 11 stages"""
        
        # Define the workflow
        workflow = StateGraph(CustomerSupportState)
        
        # Add all 11 stages as nodes
        workflow.add_node("intake", self.stage_01_intake)
        workflow.add_node("understand", self.stage_02_understand)
        workflow.add_node("prepare", self.stage_03_prepare)
        workflow.add_node("ask", self.stage_04_ask)
        workflow.add_node("wait", self.stage_05_wait)
        workflow.add_node("retrieve", self.stage_06_retrieve)
        workflow.add_node("decide", self.stage_07_decide)
        workflow.add_node("update", self.stage_08_update)
        workflow.add_node("create", self.stage_09_create)
        workflow.add_node("do", self.stage_10_do)
        workflow.add_node("complete", self.stage_11_complete)
        
        # Define the flow (conditional routing will be added)
        workflow.set_entry_point("intake")
        workflow.add_edge("intake", "understand")
        workflow.add_edge("understand", "prepare")
        workflow.add_edge("prepare", "ask")
        workflow.add_conditional_edges(
            "ask",
            self._should_wait,
            {"wait": "wait", "retrieve": "retrieve"}
        )
        workflow.add_edge("wait", "retrieve")
        workflow.add_edge("retrieve", "decide")
        workflow.add_conditional_edges(
            "decide",
            self._should_escalate,
            {"escalate": END, "continue": "update"}
        )
        workflow.add_edge("update", "create")
        workflow.add_edge("create", "do")
        workflow.add_edge("do", "complete")
        workflow.add_edge("complete", END)
        
        return workflow.compile()
    
    def _log_stage_start(self, state: CustomerSupportState, stage_name: str, stage_id: int, emoji: str, mode: StageMode) -> StageLog:
        """Log the start of a stage"""
        stage_log = StageLog(
            stage_name=stage_name,
            stage_id=stage_id,
            emoji=emoji,
            mode=mode,
            start_time=datetime.now()
        )
        state.stage_logs.append(stage_log)
        state.current_stage = stage_id
        
        logger.info(f"{emoji} Starting stage {stage_id}: {stage_name} (mode: {mode.value})")
        return stage_log
    
    def _log_stage_complete(self, state: CustomerSupportState, stage_log: StageLog, success: bool = True, error: Optional[str] = None):
        """Log the completion of a stage"""
        stage_log.end_time = datetime.now()
        stage_log.success = success
        if error:
            stage_log.error = error
        
        duration = (stage_log.end_time - stage_log.start_time).total_seconds()
        logger.info(f"✅ Completed stage {stage_log.stage_id}: {stage_log.stage_name} ({duration:.2f}s)")
        
    async def _execute_abilities(self, state: CustomerSupportState, stage_log: StageLog, abilities: List[Dict[str, str]]) -> Dict[str, Any]:
        """Execute abilities for a stage"""
        results = {}
        payload_dict = state.input_payload.dict()
        
        for ability_config in abilities:
            ability_name = ability_config["name"]
            server = ability_config["server"]
            
            if server == "internal":
                # Handle internal abilities
                result = await self._execute_internal_ability(ability_name, state)
            else:
                # Execute via MCP
                execution = await self.mcp_manager.execute_ability(server, ability_name, payload_dict)
                stage_log.abilities_executed.append(execution)
                result = execution.result
            
            results[ability_name] = result
            logger.debug(f"Executed ability '{ability_name}' on {server} server")
        
        return results
    
    async def _execute_internal_ability(self, ability_name: str, state: CustomerSupportState) -> Dict[str, Any]:
        """Execute internal abilities (state management)"""
        if ability_name == "accept_payload":
            return {"status": "payload_accepted", "ticket_id": state.input_payload.ticket_id}
        elif ability_name == "store_answer":
            return {"status": "answer_stored"}
        elif ability_name == "store_data":
            return {"status": "data_stored"}
        elif ability_name == "update_payload":
            return {"status": "payload_updated"}
        elif ability_name == "output_payload":
            return {"status": "payload_output", "final_payload": state.dict()}
        else:
            return {"status": "unknown_internal_ability"}
    
    # Stage 1: INTAKE 📥
    async def stage_01_intake(self, state: CustomerSupportState) -> CustomerSupportState:
        """Stage 1: Accept payload"""
        stage_log = self._log_stage_start(state, "INTAKE", 1, "📥", StageMode.ENTRY_ONLY)
        
        try:
            # Accept the payload (already in state)
            results = await self._execute_abilities(state, stage_log, [
                {"name": "accept_payload", "server": "internal"}
            ])
            
            self._log_stage_complete(state, stage_log)
            
        except Exception as e:
            self._log_stage_complete(state, stage_log, success=False, error=str(e))
            
        return state
    
    # Stage 2: UNDERSTAND 🧠
    async def stage_02_understand(self, state: CustomerSupportState) -> CustomerSupportState:
        """Stage 2: Parse and extract entities from request (Deterministic)"""
        stage_log = self._log_stage_start(state, "UNDERSTAND", 2, "🧠", StageMode.DETERMINISTIC)
        
        try:
            abilities = [
                {"name": "parse_request_text", "server": "COMMON"},
                {"name": "extract_entities", "server": "ATLAS"}
            ]
            
            results = await self._execute_abilities(state, stage_log, abilities)
            
            # Store results in state
            if "parse_request_text" in results:
                state.extracted_entities.update(results["parse_request_text"].get("structured_data", {}))
            
            if "extract_entities" in results:
                state.extracted_entities.update(results["extract_entities"].get("entities", {}))
            
            self._log_stage_complete(state, stage_log)
            
        except Exception as e:
            self._log_stage_complete(state, stage_log, success=False, error=str(e))
            
        return state
    
    # Stage 3: PREPARE 🛠
    async def stage_03_prepare(self, state: CustomerSupportState) -> CustomerSupportState:
        """Stage 3: Normalize and enrich data (Deterministic)"""
        stage_log = self._log_stage_start(state, "PREPARE", 3, "🛠", StageMode.DETERMINISTIC)
        
        try:
            abilities = [
                {"name": "normalize_fields", "server": "COMMON"},
                {"name": "enrich_records", "server": "ATLAS"},
                {"name": "add_flags_calculations", "server": "COMMON"}
            ]
            
            results = await self._execute_abilities(state, stage_log, abilities)
            
            # Store results in state
            for ability, result in results.items():
                if ability == "normalize_fields":
                    state.normalized_fields.update(result.get("normalized", {}))
                elif ability == "enrich_records":
                    state.enriched_data.update(result)
                elif ability == "add_flags_calculations":
                    state.enriched_data.update(result.get("flags", {}))
            
            self._log_stage_complete(state, stage_log)
            
        except Exception as e:
            self._log_stage_complete(state, stage_log, success=False, error=str(e))
            
        return state
    
    # Stage 4: ASK ❓
    async def stage_04_ask(self, state: CustomerSupportState) -> CustomerSupportState:
        """Stage 4: Request clarification if needed (Human Interaction)"""
        stage_log = self._log_stage_start(state, "ASK", 4, "❓", StageMode.HUMAN_INTERACTION)
        
        try:
            # Determine if clarification is needed using LLM
            prompt = f"""As Langie, a customer support agent, analyze this ticket and determine if clarification is needed:
            
Customer: {state.input_payload.customer_name}
Query: {state.input_payload.query}
Priority: {state.input_payload.priority}
Extracted entities: {state.extracted_entities}
            
Should we ask for clarification? Respond with 'YES' or 'NO' and explain why."""
            
            messages = [
                SystemMessage(content="You are Langie, a structured customer support agent."),
                HumanMessage(content=prompt)
            ]
            
            llm_response = await self.llm.ainvoke(messages)
            clarification_needed = "YES" in llm_response.content.upper()
            
            if clarification_needed:
                abilities = [{"name": "clarify_question", "server": "ATLAS"}]
                results = await self._execute_abilities(state, stage_log, abilities)
                
                state.clarification_requested = True
                state.clarification_question = results.get("clarify_question", {}).get("question", "")
                
            self._log_stage_complete(state, stage_log)
            
        except Exception as e:
            self._log_stage_complete(state, stage_log, success=False, error=str(e))
            
        return state
    
    # Stage 5: WAIT ⏳
    async def stage_05_wait(self, state: CustomerSupportState) -> CustomerSupportState:
        """Stage 5: Wait and process response (Deterministic)"""
        stage_log = self._log_stage_start(state, "WAIT", 5, "⏳", StageMode.DETERMINISTIC)
        
        try:
            abilities = [
                {"name": "extract_answer", "server": "ATLAS"},
                {"name": "store_answer", "server": "internal"}
            ]
            
            results = await self._execute_abilities(state, stage_log, abilities)
            
            # Store human response
            if "extract_answer" in results:
                state.human_response = results["extract_answer"].get("answer", "")
            
            self._log_stage_complete(state, stage_log)
            
        except Exception as e:
            self._log_stage_complete(state, stage_log, success=False, error=str(e))
            
        return state
    
    # Stage 6: RETRIEVE 📚
    async def stage_06_retrieve(self, state: CustomerSupportState) -> CustomerSupportState:
        """Stage 6: Search knowledge base (Deterministic)"""
        stage_log = self._log_stage_start(state, "RETRIEVE", 6, "📚", StageMode.DETERMINISTIC)
        
        try:
            abilities = [
                {"name": "knowledge_base_search", "server": "ATLAS"},
                {"name": "store_data", "server": "internal"}
            ]
            
            results = await self._execute_abilities(state, stage_log, abilities)
            
            # Store knowledge base results
            if "knowledge_base_search" in results:
                state.knowledge_base_results = results["knowledge_base_search"].get("results", [])
            
            self._log_stage_complete(state, stage_log)
            
        except Exception as e:
            self._log_stage_complete(state, stage_log, success=False, error=str(e))
            
        return state
    
    # Stage 7: DECIDE ⚖ (Non-Deterministic)
    async def stage_07_decide(self, state: CustomerSupportState) -> CustomerSupportState:
        """Stage 7: Evaluate solutions and make decisions (Non-Deterministic)"""
        stage_log = self._log_stage_start(state, "DECIDE", 7, "⚖", StageMode.NON_DETERMINISTIC)
        
        try:
            # Use LLM for intelligent decision making
            context = f"""Current ticket analysis:
Customer: {state.input_payload.customer_name}
Issue: {state.input_payload.query}
Priority: {state.input_payload.priority}
Entities: {state.extracted_entities}
KB Results: {len(state.knowledge_base_results)} relevant articles found
            
As Langie, evaluate the situation and provide guidance on next steps."""
            
            messages = [
                SystemMessage(content="You are Langie, making intelligent decisions about customer support resolution."),
                HumanMessage(content=context)
            ]
            
            llm_response = await self.llm.ainvoke(messages)
            
            abilities = [
                {"name": "solution_evaluation", "server": "COMMON"},
                {"name": "escalation_decision", "server": "ATLAS"},
                {"name": "update_payload", "server": "internal"}
            ]
            
            results = await self._execute_abilities(state, stage_log, abilities)
            
            # Process decision results
            if "solution_evaluation" in results:
                solutions = results["solution_evaluation"].get("solutions", [])
                state.solution_scores = {sol["solution"]: sol["score"] for sol in solutions}
                state.confidence_score = results["solution_evaluation"].get("best_score", 0)
            
            if "escalation_decision" in results:
                state.escalation_needed = results["escalation_decision"].get("escalate", False)
                state.escalation_reason = results["escalation_decision"].get("reason", "")
            
            # Apply escalation rule: escalate if confidence score < 90
            if state.confidence_score < 90:
                state.escalation_needed = True
                state.escalation_reason = f"Low confidence score: {state.confidence_score}"
                state.ticket_status = Status.ESCALATED
            
            self._log_stage_complete(state, stage_log)
            
        except Exception as e:
            self._log_stage_complete(state, stage_log, success=False, error=str(e))
            
        return state
    
    # Stage 8: UPDATE 🔄
    async def stage_08_update(self, state: CustomerSupportState) -> CustomerSupportState:
        """Stage 8: Update ticket status (Deterministic)"""
        stage_log = self._log_stage_start(state, "UPDATE", 8, "🔄", StageMode.DETERMINISTIC)
        
        try:
            abilities = [
                {"name": "update_ticket", "server": "ATLAS"},
                {"name": "close_ticket", "server": "ATLAS"}
            ]
            
            results = await self._execute_abilities(state, stage_log, abilities)
            
            # Update ticket status based on results
            if state.confidence_score >= 90 and not state.escalation_needed:
                state.ticket_status = Status.RESOLVED
            
            self._log_stage_complete(state, stage_log)
            
        except Exception as e:
            self._log_stage_complete(state, stage_log, success=False, error=str(e))
            
        return state
    
    # Stage 9: CREATE ✍
    async def stage_09_create(self, state: CustomerSupportState) -> CustomerSupportState:
        """Stage 9: Generate customer response (Deterministic)"""
        stage_log = self._log_stage_start(state, "CREATE", 9, "✍", StageMode.DETERMINISTIC)
        
        try:
            abilities = [{"name": "response_generation", "server": "COMMON"}]
            
            results = await self._execute_abilities(state, stage_log, abilities)
            
            # Store generated response
            if "response_generation" in results:
                state.generated_response = results["response_generation"].get("response", "")
            
            self._log_stage_complete(state, stage_log)
            
        except Exception as e:
            self._log_stage_complete(state, stage_log, success=False, error=str(e))
            
        return state
    
    # Stage 10: DO 🏃
    async def stage_10_do(self, state: CustomerSupportState) -> CustomerSupportState:
        """Stage 10: Execute actions and notifications (Deterministic)"""
        stage_log = self._log_stage_start(state, "DO", 10, "🏃", StageMode.DETERMINISTIC)
        
        try:
            abilities = [
                {"name": "execute_api_calls", "server": "ATLAS"},
                {"name": "trigger_notifications", "server": "ATLAS"}
            ]
            
            results = await self._execute_abilities(state, stage_log, abilities)
            
            # Store execution results
            if "execute_api_calls" in results:
                state.api_calls_executed = results["execute_api_calls"].get("api_calls", [])
            
            if "trigger_notifications" in results:
                state.notifications_sent = results["trigger_notifications"].get("notifications", [])
            
            self._log_stage_complete(state, stage_log)
            
        except Exception as e:
            self._log_stage_complete(state, stage_log, success=False, error=str(e))
            
        return state
    
    # Stage 11: COMPLETE ✅
    async def stage_11_complete(self, state: CustomerSupportState) -> CustomerSupportState:
        """Stage 11: Output final payload (Output Only)"""
        stage_log = self._log_stage_start(state, "COMPLETE", 11, "✅", StageMode.OUTPUT_ONLY)
        
        try:
            abilities = [{"name": "output_payload", "server": "internal"}]
            
            results = await self._execute_abilities(state, stage_log, abilities)
            
            # Mark processing as complete
            state.processing_complete = True
            state.updated_at = datetime.now()
            
            self._log_stage_complete(state, stage_log)
            
        except Exception as e:
            self._log_stage_complete(state, stage_log, success=False, error=str(e))
            
        return state
    
    # Conditional routing functions
    def _should_wait(self, state: CustomerSupportState) -> str:
        """Determine if we should wait for human response"""
        if state.clarification_requested and not state.human_response:
            return "wait"
        return "retrieve"
    
    def _should_escalate(self, state: CustomerSupportState) -> str:
        """Determine if we should escalate"""
        if state.escalation_needed:
            return "escalate"
        return "continue"
    
    async def process_ticket(self, input_payload: InputPayload) -> OutputPayload:
        """Process a customer support ticket through the entire workflow"""
        start_time = datetime.now()
        
        # Initialize state
        initial_state = CustomerSupportState(input_payload=input_payload)
        
        logger.info(f"🎯 Starting ticket processing for {input_payload.ticket_id}")
        logger.info(f"Customer: {input_payload.customer_name} ({input_payload.priority.value} priority)")
        
        try:
            # Run the workflow
            final_state = await self.workflow.ainvoke(initial_state)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Convert StageLog objects to dicts
            stage_logs = [log.dict() if hasattr(log, "dict") else log for log in final_state.get("stage_logs", [])]

            # Create output payload
            output = OutputPayload(
                ticket_id=input_payload.ticket_id,
                status=final_state.get("ticket_status"),
                response=final_state.get("generated_response"),
                confidence_score=final_state.get("confidence_score"),
                escalation_reason=final_state.get("escalation_reason"),
                stage_logs=stage_logs,
                final_payload=final_state,
                processing_time=processing_time
            )

            logger.info(f"🎉 Ticket processing completed in {processing_time:.2f}s")
            logger.info(f"Status: {output.status.value}, Confidence: {output.confidence_score}")
            
            return output
            
        except Exception as e:
            logger.error(f"❌ Error processing ticket {input_payload.ticket_id}: {str(e)}")
            raise
        
        finally:
            # Cleanup
            await self.mcp_manager.close()
