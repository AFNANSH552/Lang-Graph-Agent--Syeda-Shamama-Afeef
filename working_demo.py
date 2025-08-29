#!/usr/bin/env python3
"""
🤖 LANGIE - LangGraph Customer Support Agent Demo
Working implementation without external dependencies
All 11 stages with realistic simulation
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any
from enum import Enum

# === DATA MODELS ===
class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Status(str, Enum):
    PENDING = "pending"
    RESOLVED = "resolved"
    ESCALATED = "escalated"

class InputPayload:
    def __init__(self, customer_name: str, email: str, query: str, priority: Priority, ticket_id: str = None):
        self.customer_name = customer_name
        self.email = email
        self.query = query
        self.priority = priority
        self.ticket_id = ticket_id or f"TICKET-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8]}"
    
    def dict(self):
        return {
            "customer_name": self.customer_name,
            "email": self.email,
            "query": self.query,
            "priority": self.priority.value,
            "ticket_id": self.ticket_id
        }

class StageLog:
    def __init__(self, stage_name: str, stage_id: int, emoji: str):
        self.stage_name = stage_name
        self.stage_id = stage_id
        self.emoji = emoji
        self.start_time = datetime.now()
        self.end_time = None
        self.abilities_executed = []
        self.success = True
        self.duration = 0

class OutputPayload:
    def __init__(self, ticket_id: str, status: Status, confidence_score: float, 
                 response: str = None, escalation_reason: str = None, stage_logs: List = None, 
                 processing_time: float = 0):
        self.ticket_id = ticket_id
        self.status = status
        self.confidence_score = confidence_score
        self.response = response
        self.escalation_reason = escalation_reason
        self.stage_logs = stage_logs or []
        self.processing_time = processing_time
        self.agent_name = "Langie"
        self.agent_version = "1.0.0"
        self.completion_time = datetime.now()
    
    def dict(self):
        return {
            "ticket_id": self.ticket_id,
            "status": self.status.value,
            "confidence_score": self.confidence_score,
            "response": self.response,
            "escalation_reason": self.escalation_reason,
            "stage_logs": [log.__dict__ for log in self.stage_logs],
            "processing_time": self.processing_time,
            "agent_name": self.agent_name,
            "agent_version": self.agent_version,
            "completion_time": self.completion_time.isoformat()
        }

# === MAIN AGENT CLASS ===
class LangGraphCustomerSupportAgent:
    """
    Langie - LangGraph Customer Support Agent
    Processes tickets through 11 structured stages
    """
    
    def __init__(self):
        self.agent_name = "Langie"
        self.agent_version = "1.0.0"
        print(f"✅ {self.agent_name} v{self.agent_version} initialized successfully!")
    
    def _log_stage(self, stage_name: str, stage_id: int, emoji: str, mode: str) -> StageLog:
        """Log the start of a stage"""
        stage_log = StageLog(stage_name, stage_id, emoji)
        print(f"{emoji} Stage {stage_id}: {stage_name} ({mode})")
        return stage_log
    
    def _complete_stage(self, stage_log: StageLog, success: bool = True):
        """Complete a stage"""
        stage_log.end_time = datetime.now()
        stage_log.success = success
        stage_log.duration = (stage_log.end_time - stage_log.start_time).total_seconds()
        status = "✅" if success else "❌"
        print(f"  {status} Completed in {stage_log.duration:.2f}s")
    
    async def _simulate_ability(self, ability_name: str, server: str, payload: Dict) -> Dict:
        """Simulate ability execution with realistic responses"""
        await asyncio.sleep(0.05)  # Simulate processing time
        
        responses = {
            "parse_request_text": {
                "issue_category": "Authentication",
                "keywords": ["login", "password", "incorrect", "urgent"],
                "sentiment": "frustrated"
            },
            "extract_entities": {
                "product": "User Account",
                "issue_type": "Authentication",
                "urgency": "High",
                "account_id": f"user_{hash(payload.get('email', '')) % 10000}"
            },
            "normalize_fields": {
                "email": payload.get("email", "").lower(),
                "priority": payload.get("priority", "").upper(),
                "timestamp": datetime.now().isoformat()
            },
            "enrich_records": {
                "sla_response_time": "2 hours",
                "historical_issues": 2,
                "customer_tier": "Premium"
            },
            "knowledge_base_search": {
                "relevant_articles": [
                    {"title": "Password Reset Guide", "relevance": 0.95},
                    {"title": "Account Lockout Solutions", "relevance": 0.88}
                ]
            },
            "solution_evaluation": {
                "solutions": [
                    {"solution": "Password reset email", "score": 85},
                    {"solution": "Account unlock", "score": 92},
                    {"solution": "Escalate to security", "score": 45}
                ],
                "best_score": 92
            },
            "response_generation": {
                "response": f"""Dear {payload.get('customer_name', 'Customer')},

Thank you for contacting our support team regarding your login issue.

I've analyzed your account and found that it was temporarily locked due to multiple failed login attempts. I have:

1. ✅ Unlocked your account 
2. ✅ Sent a password reset email to {payload.get('email', 'your registered email')}
3. ✅ Verified our email delivery system is working

Please check your inbox (and spam folder) for the password reset email. If you don't receive it within 10 minutes, please reply to this ticket.

For urgent assistance, you can call our priority support line at 1-800-SUPPORT.

Best regards,
Langie - AI Customer Support Agent
Ticket ID: {payload.get('ticket_id', 'Unknown')}"""
            }
        }
        
        result = responses.get(ability_name, {"status": "simulated", "ability": ability_name})
        print(f"    🔧 {ability_name} → {server}")
        return result
    
    async def process_ticket(self, input_payload: InputPayload) -> OutputPayload:
        """Process a customer support ticket through all 11 stages"""
        print(f"\n🎯 Starting ticket processing: {input_payload.ticket_id}")
        print(f"   👤 Customer: {input_payload.customer_name}")
        print(f"   📧 Email: {input_payload.email}")
        print(f"   🚨 Priority: {input_payload.priority.value.upper()}")
        print(f"   💬 Issue: {input_payload.query[:50]}...")
        print(f"\n{'='*60}")
        
        start_time = datetime.now()
        stage_logs = []
        
        # Processing state
        extracted_entities = {}
        knowledge_results = []
        confidence_score = 0
        escalation_needed = False
        escalation_reason = None
        generated_response = ""
        ticket_status = Status.PENDING
        
        try:
            # Stage 1: INTAKE 📥 (Entry Only)
            stage_log = self._log_stage("INTAKE", 1, "📥", "entry_only")
            stage_log.abilities_executed.append("accept_payload")
            self._complete_stage(stage_log)
            stage_logs.append(stage_log)
            
            # Stage 2: UNDERSTAND 🧠 (Deterministic)
            stage_log = self._log_stage("UNDERSTAND", 2, "🧠", "deterministic")
            parse_result = await self._simulate_ability("parse_request_text", "COMMON", input_payload.dict())
            entity_result = await self._simulate_ability("extract_entities", "ATLAS", input_payload.dict())
            
            extracted_entities.update(parse_result)
            extracted_entities.update(entity_result)
            stage_log.abilities_executed.extend(["parse_request_text", "extract_entities"])
            self._complete_stage(stage_log)
            stage_logs.append(stage_log)
            
            # Stage 3: PREPARE 🛠 (Deterministic)
            stage_log = self._log_stage("PREPARE", 3, "🛠", "deterministic")
            await self._simulate_ability("normalize_fields", "COMMON", input_payload.dict())
            await self._simulate_ability("enrich_records", "ATLAS", input_payload.dict())
            await self._simulate_ability("add_flags_calculations", "COMMON", input_payload.dict())
            stage_log.abilities_executed.extend(["normalize_fields", "enrich_records", "add_flags_calculations"])
            self._complete_stage(stage_log)
            stage_logs.append(stage_log)
            
            # Stage 4: ASK ❓ (Human Interaction)
            stage_log = self._log_stage("ASK", 4, "❓", "human_interaction")
            clarification_needed = input_payload.priority in [Priority.LOW, Priority.MEDIUM]
            if clarification_needed:
                print("    💭 Clarification requested from customer")
            else:
                print("    ⚡ No clarification needed for high priority ticket")
            stage_log.abilities_executed.append("clarification_check")
            self._complete_stage(stage_log)
            stage_logs.append(stage_log)
            
            # Stage 5: WAIT ⏳ (Deterministic - skip if no clarification)
            if clarification_needed:
                stage_log = self._log_stage("WAIT", 5, "⏳", "deterministic")
                print("    ⏰ Simulating customer response: 'Issue started this morning'")
                stage_log.abilities_executed.extend(["extract_answer", "store_answer"])
                self._complete_stage(stage_log)
                stage_logs.append(stage_log)
            
            # Stage 6: RETRIEVE 📚 (Deterministic)
            stage_log = self._log_stage("RETRIEVE", 6, "📚", "deterministic")
            kb_result = await self._simulate_ability("knowledge_base_search", "ATLAS", input_payload.dict())
            knowledge_results = kb_result.get("relevant_articles", [])
            print(f"    📖 Found {len(knowledge_results)} relevant knowledge base articles")
            stage_log.abilities_executed.extend(["knowledge_base_search", "store_data"])
            self._complete_stage(stage_log)
            stage_logs.append(stage_log)
            
            # Stage 7: DECIDE ⚖ (Non-Deterministic - KEY DECISION STAGE)
            stage_log = self._log_stage("DECIDE", 7, "⚖", "non_deterministic")
            solution_result = await self._simulate_ability("solution_evaluation", "COMMON", input_payload.dict())
            
            confidence_score = solution_result.get("best_score", 0)
            print(f"    🎯 Confidence score: {confidence_score}%")
            
            # Apply escalation rule: escalate if confidence < 90
            if confidence_score < 90:
                escalation_needed = True
                escalation_reason = f"Low confidence score: {confidence_score}%"
                ticket_status = Status.ESCALATED
                print(f"    ⚠️  ESCALATION TRIGGERED: {escalation_reason}")
            else:
                ticket_status = Status.RESOLVED
                print(f"    ✅ HIGH CONFIDENCE - Proceeding with automated resolution")
            
            stage_log.abilities_executed.extend(["solution_evaluation", "escalation_decision"])
            self._complete_stage(stage_log)
            stage_logs.append(stage_log)
            
            # Continue processing only if not escalated
            if not escalation_needed:
                # Stage 8: UPDATE 🔄 (Deterministic)
                stage_log = self._log_stage("UPDATE", 8, "🔄", "deterministic")
                print("    📝 Updating ticket status and priority")
                stage_log.abilities_executed.extend(["update_ticket", "close_ticket"])
                self._complete_stage(stage_log)
                stage_logs.append(stage_log)
                
                # Stage 9: CREATE ✍ (Deterministic)
                stage_log = self._log_stage("CREATE", 9, "✍", "deterministic")
                response_result = await self._simulate_ability("response_generation", "COMMON", input_payload.dict())
                generated_response = response_result.get("response", "")
                print("    ✏️  Generated personalized customer response")
                stage_log.abilities_executed.append("response_generation")
                self._complete_stage(stage_log)
                stage_logs.append(stage_log)
                
                # Stage 10: DO 🏃 (Deterministic)
                stage_log = self._log_stage("DO", 10, "🏃", "deterministic")
                print("    🔧 Executing account unlock API call")
                print("    📧 Sending password reset email")
                print("    🔔 Triggering customer notification")
                stage_log.abilities_executed.extend(["execute_api_calls", "trigger_notifications"])
                self._complete_stage(stage_log)
                stage_logs.append(stage_log)
            
            # Stage 11: COMPLETE ✅ (Output Only)
            stage_log = self._log_stage("COMPLETE", 11, "✅", "output_only")
            print("    🎁 Generating final structured payload")
            stage_log.abilities_executed.append("output_payload")
            self._complete_stage(stage_log)
            stage_logs.append(stage_log)
            
        except Exception as e:
            print(f"❌ Error during processing: {str(e)}")
            ticket_status = Status.PENDING
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Create final output
        output = OutputPayload(
            ticket_id=input_payload.ticket_id,
            status=ticket_status,
            confidence_score=confidence_score,
            response=generated_response,
            escalation_reason=escalation_reason,
            stage_logs=stage_logs,
            processing_time=processing_time
        )
        
        print(f"\n{'='*60}")
        print(f"🎉 PROCESSING COMPLETED in {processing_time:.2f} seconds")
        print(f"📊 Final Status: {output.status.value.upper()}")
        print(f"🎯 Confidence Score: {output.confidence_score}%")
        print(f"🔧 Stages Executed: {len(stage_logs)} of 11")
        
        if escalation_reason:
            print(f"⚠️  Escalation: {escalation_reason}")
        
        return output

# === DEMO FUNCTIONS ===
def print_banner():
    """Print demo banner"""
    print("=" * 70)
    print("🤖 LANGIE - LANGGRAPH CUSTOMER SUPPORT AGENT 🤖")
    print("    Structured 11-Stage Workflow | v1.0.0")
    print("=" * 70)

def print_stage_summary(output: OutputPayload):
    """Print execution summary"""
    print(f"\n📋 STAGE EXECUTION SUMMARY")
    print("-" * 50)
    
    for log in output.stage_logs:
        abilities_count = len(log.abilities_executed)
        status = "✅" if log.success else "❌"
        print(f"{log.emoji} {log.stage_name:12} | {log.duration:5.2f}s | {abilities_count} abilities | {status}")

def print_final_results(output: OutputPayload):
    """Print final results"""
    print(f"\n📋 FINAL RESULTS")
    print("=" * 50)
    print(f"📍 Ticket ID: {output.ticket_id}")
    print(f"🎯 Status: {output.status.value.upper()}")
    print(f"📊 Confidence: {output.confidence_score}%")
    print(f"⏱️  Total Time: {output.processing_time:.2f}s")
    
    if output.escalation_reason:
        print(f"⚠️  Escalation: {output.escalation_reason}")
    
    if output.response:
        print(f"\n📝 GENERATED CUSTOMER RESPONSE:")
        print("-" * 50)
        print(output.response)

def create_sample_ticket() -> InputPayload:
    """Create sample ticket for testing"""
    return InputPayload(
        customer_name="John Smith",
        email="john.smith@example.com",
        query="I can't login to my account. It says my password is incorrect but I'm sure it's right. This is urgent as I need to access my account for an important transaction today!",
        priority=Priority.HIGH
    )

async def run_sample_demo():
    """Run demo with sample data"""
    print_banner()
    
    # Create sample ticket
    ticket = create_sample_ticket()
    print(f"🎫 Sample Ticket Generated:")
    print(f"   Customer: {ticket.customer_name}")
    print(f"   Priority: {ticket.priority.value.upper()}")
    print(f"   Issue: {ticket.query[:60]}...")
    
    # Process ticket
    agent = LangGraphCustomerSupportAgent()
    output = await agent.process_ticket(ticket)
    
    # Display results
    print_stage_summary(output)
    print_final_results(output)
    
    # Save output
    output_file = f"langie_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output.dict(), f, indent=2, default=str, ensure_ascii=False)
    
    print(f"\n💾 Complete output saved to: {output_file}")
    return output

async def run_custom_demo():
    """Run demo with custom input"""
    print_banner()
    
    print("🛠️  Create your custom support ticket:")
    name = input("Customer Name: ").strip() or "Test Customer"
    email = input("Email Address: ").strip() or "test@example.com"
    query = input("Support Issue: ").strip() or "I need help with my account"
    
    print("\nPriority levels: low, medium, high, critical")
    priority_input = input("Priority: ").strip().lower() or "medium"
    
    priority_map = {
        "low": Priority.LOW,
        "medium": Priority.MEDIUM,
        "high": Priority.HIGH,
        "critical": Priority.CRITICAL
    }
    priority = priority_map.get(priority_input, Priority.MEDIUM)
    
    # Create and process ticket
    ticket = InputPayload(name, email, query, priority)
    agent = LangGraphCustomerSupportAgent()
    output = await agent.process_ticket(ticket)
    
    # Display results
    print_stage_summary(output)
    print_final_results(output)
    
    return output

async def main():
    """Main entry point"""
    print("🚀 Welcome to Langie Demo!")
    print("\nChoose an option:")
    print("1. 🎯 Run sample demo (recommended)")
    print("2. 🛠️  Run custom demo")
    
    choice = input("\nYour choice (1 or 2): ").strip() or "1"
    
    if choice == "2":
        await run_custom_demo()
    else:
        await run_sample_demo()
    
    print(f"\n🎉 Thank you for using Langie!")
    print("   - 11 stages executed")
    print("   - State persisted across stages")
    print("   - MCP server integration simulated")
    print("   - Deterministic & non-deterministic flows")
    print("   - Intelligent escalation logic")

if __name__ == "__main__":
    asyncio.run(main())
