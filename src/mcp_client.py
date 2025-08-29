"""
MCP (Model Context Protocol) Client Integration
Handles communication with Atlas and Common servers for ability execution
"""
import httpx
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
from .config import get_atlas_config, get_common_config
from .models import AbilityExecution

logger = logging.getLogger(__name__)

class MCPClient:
    """Base MCP Client for server communication"""
    
    def __init__(self, server_name: str, config: Dict[str, str]):
        self.server_name = server_name
        self.url = config["url"]
        self.api_key = config["key"]
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def execute_ability(self, ability_name: str, payload: Dict[str, Any]) -> AbilityExecution:
        """Execute an ability on the MCP server"""
        start_time = datetime.now()
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            request_data = {
                "ability": ability_name,
                "payload": payload,
                "timestamp": start_time.isoformat()
            }
            
            logger.info(f"Executing ability '{ability_name}' on {self.server_name} server")
            
            # Simulate server call (replace with actual HTTP call)
            response = await self._simulate_server_call(ability_name, payload)
            
            return AbilityExecution(
                ability_name=ability_name,
                server_used=self.server_name,
                execution_time=start_time,
                status="success",
                result=response
            )
            
        except Exception as e:
            logger.error(f"Error executing ability '{ability_name}' on {self.server_name}: {str(e)}")
            return AbilityExecution(
                ability_name=ability_name,
                server_used=self.server_name,
                execution_time=start_time,
                status="error",
                error=str(e)
            )
    
    async def _simulate_server_call(self, ability_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate server response (replace with actual HTTP client call)"""
        # Simulate network delay
        await asyncio.sleep(0.1)
        
        # Simulate different responses based on ability and server
        if self.server_name == "ATLAS":
            return await self._atlas_ability_response(ability_name, payload)
        elif self.server_name == "COMMON":
            return await self._common_ability_response(ability_name, payload)
        else:
            return {"status": "unknown_server", "result": None}
    
    async def _atlas_ability_response(self, ability_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate ATLAS server responses"""
        responses = {
            "extract_entities": {
                "entities": {
                    "product": "User Account",
                    "issue_type": "Authentication",
                    "urgency": "High",
                    "account_id": "user_12345"
                }
            },
            "enrich_records": {
                "sla_info": {"response_time": "2 hours", "resolution_time": "24 hours"},
                "historical_tickets": [
                    {"ticket_id": "T-001", "issue": "Password reset", "resolved": True},
                    {"ticket_id": "T-002", "issue": "Account locked", "resolved": True}
                ]
            },
            "clarify_question": {
                "question": "Have you tried using the 'Forgot Password' feature on the login page?"
            },
            "extract_answer": {
                "answer": "Yes, I tried the forgot password feature but I'm not receiving the reset email."
            },
            "knowledge_base_search": {
                "results": [
                    {
                        "title": "Email delivery issues",
                        "content": "Check spam folder, verify email address, contact support if no email received within 10 minutes",
                        "relevance": 0.95
                    },
                    {
                        "title": "Password reset troubleshooting", 
                        "content": "Common issues include blocked emails, incorrect email address, or account lockout",
                        "relevance": 0.89
                    }
                ]
            },
            "escalation_decision": {
                "escalate": False,
                "reason": "Standard troubleshooting available"
            },
            "update_ticket": {
                "ticket_updated": True,
                "new_status": "In Progress"
            },
            "close_ticket": {
                "ticket_closed": True,
                "closure_reason": "Resolved"
            },
            "execute_api_calls": {
                "api_calls": [
                    {"api": "reset_password_email", "status": "triggered", "response": "Email sent"},
                    {"api": "unlock_account", "status": "success", "response": "Account unlocked"}
                ]
            },
            "trigger_notifications": {
                "notifications": [
                    {"type": "email", "recipient": payload.get("email", ""), "status": "sent"},
                    {"type": "sms", "recipient": payload.get("phone", ""), "status": "sent"}
                ]
            }
        }
        
        return responses.get(ability_name, {"status": "ability_not_found", "result": None})
    
    async def _common_ability_response(self, ability_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate COMMON server responses"""
        responses = {
            "parse_request_text": {
                "structured_data": {
                    "issue_category": "Authentication",
                    "priority_level": "High",
                    "keywords": ["login", "password", "incorrect", "urgent", "transaction"],
                    "sentiment": "frustrated"
                }
            },
            "normalize_fields": {
                "normalized": {
                    "email": payload.get("email", "").lower().strip(),
                    "priority": payload.get("priority", "").upper(),
                    "timestamp": datetime.now().isoformat()
                }
            },
            "add_flags_calculations": {
                "flags": {
                    "high_priority": True,
                    "sla_risk": False,
                    "escalation_score": 25
                }
            },
            "solution_evaluation": {
                "solutions": [
                    {"solution": "Send password reset email", "score": 85},
                    {"solution": "Unlock account manually", "score": 92},
                    {"solution": "Escalate to security team", "score": 40}
                ],
                "best_score": 92
            },
            "response_generation": {
                "response": f"""Dear {payload.get('customer_name', 'Customer')},

Thank you for contacting our support team regarding your login issue.

I understand you're having trouble accessing your account due to password authentication issues. Based on our investigation, I've taken the following steps to resolve this:

1. Unlocked your account (it appears to have been temporarily locked due to multiple failed login attempts)
2. Sent a new password reset email to your registered address
3. Verified that our email system is functioning properly

Please check your inbox (and spam folder) for the password reset email. If you don't receive it within 10 minutes, please reply to this ticket and we'll explore alternative solutions.

For immediate assistance with urgent transactions, you can also call our priority support line at 1-800-SUPPORT.

Best regards,
Langie - Customer Support Agent
Ticket ID: {payload.get('ticket_id', 'Unknown')}"""
            }
        }
        
        return responses.get(ability_name, {"status": "ability_not_found", "result": None})

class MCPManager:
    """Manager for MCP clients"""
    
    def __init__(self):
        self.clients = {
            "ATLAS": MCPClient("ATLAS", get_atlas_config()),
            "COMMON": MCPClient("COMMON", get_common_config())
        }
    
    async def execute_ability(self, server_name: str, ability_name: str, payload: Dict[str, Any]) -> AbilityExecution:
        """Execute ability on specified server"""
        if server_name not in self.clients:
            return AbilityExecution(
                ability_name=ability_name,
                server_used=server_name,
                execution_time=datetime.now(),
                status="error",
                error=f"Unknown server: {server_name}"
            )
        
        return await self.clients[server_name].execute_ability(ability_name, payload)
    
    async def close(self):
        """Close all client connections"""
        for client in self.clients.values():
            await client.client.aclose()
