"""
Simple Demo for LangGraph Customer Support Agent
This version works without complex dependencies
"""
import asyncio
import json
from datetime import datetime
from src.simple_agent import SimpleLangGraphAgent, create_sample_ticket
from src.models import InputPayload, Priority

def print_banner():
    """Print banner"""
    print("=" * 70)
    print("🤖 LANGIE - LANGGRAPH CUSTOMER SUPPORT AGENT 🤖")
    print("          Structured workflow with 11 stages")
    print("=" * 70)

def print_final_results(output):
    """Print final results"""
    print("\n" + "=" * 70)
    print("📋 FINAL RESULTS")
    print("=" * 70)
    print(f"📍 Ticket ID: {output.ticket_id}")
    print(f"🎯 Status: {output.status.value.upper()}")
    print(f"📊 Confidence: {output.confidence_score}%")
    print(f"⏱️  Processing Time: {output.processing_time:.2f} seconds")
    print(f"🔧 Stages Executed: {len(output.stage_logs)}")
    
    if output.escalation_reason:
        print(f"⚠️  Escalation: {output.escalation_reason}")
    
    if output.response:
        print(f"\n📝 Generated Response:")
        print("-" * 50)
        print(output.response)
    
    print("\n" + "=" * 70)

def print_stage_summary(output):
    """Print stage execution summary"""
    print("\n📋 STAGE EXECUTION SUMMARY")
    print("-" * 50)
    
    for i, log in enumerate(output.stage_logs, 1):
        duration = 0
        if log.get('end_time') and log.get('start_time'):
            start = datetime.fromisoformat(log['start_time'])
            end = datetime.fromisoformat(log['end_time'])
            duration = (end - start).total_seconds()
        
        abilities_count = len(log.get('abilities_executed', []))
        status = "✅" if log.get('success', True) else "❌"
        
        print(f"{log['emoji']} {log['stage_name']:12} | {duration:5.2f}s | {abilities_count} abilities | {status}")

async def run_sample_demo():
    """Run demo with sample data"""
    print_banner()
    
    # Create sample ticket
    sample_ticket = create_sample_ticket()
    
    print(f"🎫 Sample Ticket Created:")
    print(f"   Customer: {sample_ticket.customer_name}")
    print(f"   Email: {sample_ticket.email}")
    print(f"   Priority: {sample_ticket.priority.value.upper()}")
    print(f"   Query: {sample_ticket.query[:80]}...")
    
    # Initialize agent
    agent = SimpleLangGraphAgent()
    
    # Process ticket
    output = await agent.process_ticket(sample_ticket)
    
    # Print results
    print_stage_summary(output)
    print_final_results(output)
    
    # Save output
    output_file = f"demo_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(output.dict(), f, indent=2, default=str)
    
    print(f"💾 Output saved to: {output_file}")

async def run_custom_demo():
    """Run demo with custom input"""
    print_banner()
    
    print("Enter your custom support ticket details:")
    
    customer_name = input("Customer Name: ").strip() or "Test Customer"
    email = input("Email: ").strip() or "test@example.com"
    query = input("Support Query: ").strip() or "I need help with my account"
    
    print("Priority options: low, medium, high, critical")
    priority_input = input("Priority: ").strip().lower() or "medium"
    
    priority_map = {
        "low": Priority.LOW,
        "medium": Priority.MEDIUM,
        "high": Priority.HIGH,
        "critical": Priority.CRITICAL
    }
    priority = priority_map.get(priority_input, Priority.MEDIUM)
    
    # Create custom ticket
    custom_ticket = InputPayload(
        customer_name=customer_name,
        email=email,
        query=query,
        priority=priority
    )
    
    # Initialize agent and process
    agent = SimpleLangGraphAgent()
    output = await agent.process_ticket(custom_ticket)
    
    # Print results
    print_stage_summary(output)
    print_final_results(output)

def main():
    """Main entry point"""
    print("🚀 Welcome to Langie Demo!")
    print("\nChoose an option:")
    print("1. Run sample demo")
    print("2. Run custom demo")
    
    choice = input("\nYour choice (1 or 2): ").strip() or "1"
    
    if choice == "2":
        asyncio.run(run_custom_demo())
    else:
        asyncio.run(run_sample_demo())

if __name__ == "__main__":
    main()
