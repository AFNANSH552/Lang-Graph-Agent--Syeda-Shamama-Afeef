"""
Demo Script for LangGraph Customer Support Agent
Run this to see Langie in action!
"""
import asyncio
import json
import logging
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn

# Correct langgraph imports
from langgraph.graph import StateGraph, END
from src.langgraph_agent import LangGraphCustomerSupportAgent
from src.models import InputPayload, Priority, create_sample_input
from src.config import settings, get_primary_api_key, get_secondary_api_key

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rich console for output
console = Console()

def print_banner():
    banner = Text("🤖 Langie - LangGraph Customer Support Agent 🤖", style="bold cyan")
    console.print(Panel(banner, border_style="blue", padding=(1, 2)))

def print_input_payload(payload: InputPayload):
    table = Table(title="📥 Input Payload", border_style="green")
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="white")
    table.add_row("Customer Name", payload.customer_name)
    table.add_row("Email", payload.email)
    table.add_row("Priority", f"[bold {get_priority_color(payload.priority)}]{payload.priority.value.upper()}[/]")
    table.add_row("Ticket ID", getattr(payload, "ticket_id", "N/A"))
    table.add_row("Query", payload.query[:100] + "..." if len(payload.query) > 100 else payload.query)
    console.print(table)
    console.print()

def get_priority_color(priority: Priority) -> str:
    colors = {
        Priority.LOW: "green",
        Priority.MEDIUM: "yellow", 
        Priority.HIGH: "red",
        Priority.CRITICAL: "bold red"
    }
    return colors.get(priority, "white")

def print_stage_logs(stage_logs):
    table = Table(title="📋 Stage Execution Log", border_style="blue")
    table.add_column("Stage", style="cyan", width=12)
    table.add_column("Name", style="white", width=15)
    table.add_column("Mode", style="yellow", width=15)
    table.add_column("Abilities", style="green", width=20)
    table.add_column("Duration", style="magenta", width=10)
    table.add_column("Status", style="white", width=8)

    for log in stage_logs:
        # dict ya object handle
        if isinstance(log, dict):
            start_time = log.get("start_time")
            end_time = log.get("end_time")
            abilities = [ex["ability_name"] for ex in log.get("abilities_executed", [])]
            success = log.get("success", True)
            stage_id = log.get("stage_id", "")
            emoji = log.get("emoji", "")
            stage_name = log.get("stage_name", "")
            mode = log.get("mode", "")
        else:  # assume StageLog object
            start_time = getattr(log, "start_time", None)
            end_time = getattr(log, "end_time", None)
            abilities = [ex.ability_name for ex in getattr(log, "abilities_executed", [])]
            success = getattr(log, "success", True)
            stage_id = getattr(log, "stage_id", "")
            emoji = getattr(log, "emoji", "")
            stage_name = getattr(log, "stage_name", "")
            mode = getattr(log, "mode", "")

        # duration calculation
        start, end = None, None
        if isinstance(start_time, str):
            start = datetime.fromisoformat(start_time)
        elif isinstance(start_time, datetime):
            start = start_time

        if isinstance(end_time, str):
            end = datetime.fromisoformat(end_time)
        elif isinstance(end_time, datetime):
            end = end_time

        duration = f"{(end - start).total_seconds():.2f}s" if start and end else "N/A"

        abilities_str = ", ".join(abilities) if abilities else "None"
        status = "✅" if success else "❌"

        table.add_row(
            f"{emoji} {stage_id}",
            stage_name,
            mode,
            abilities_str[:20] + "..." if len(abilities_str) > 20 else abilities_str,
            duration,
            status
        )

    console.print(table)
    console.print()

def print_final_output(output):
    status_color = "green" if output.status.value == "resolved" else "red" if output.status.value == "escalated" else "yellow"
    console.print(Panel(
        f"[bold {status_color}]{output.status.value.upper()}[/]\n"
        f"Confidence Score: [bold]{output.confidence_score}%[/]\n"
        f"Processing Time: [bold]{output.processing_time:.2f}s[/]",
        title="🎯 Final Status",
        border_style=status_color
    ))
    if output.response:
        console.print(Panel(output.response, title="📝 Generated Response", border_style="blue"))
    if getattr(output, "escalation_reason", None):
        console.print(Panel(f"[bold red]{output.escalation_reason}[/]", title="⚠️ Escalation Reason", border_style="red"))

async def run_demo():
    print_banner()
    console.print("[bold yellow]Creating sample customer support ticket...[/]")
    sample_input = create_sample_input()
    print_input_payload(sample_input)
    
    console.print("[bold yellow]Initializing Langie (LangGraph Customer Support Agent)...[/]")
    agent = LangGraphCustomerSupportAgent("agent_config.yaml")
    
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task = progress.add_task("Processing customer support ticket...", total=None)
        try:
            output = await agent.process_ticket(sample_input)
            progress.update(task, description="✅ Processing completed!")
        except Exception as e:
            progress.update(task, description=f"❌ Processing failed: {str(e)}")
            raise
    
    console.print()
    print_stage_logs(output.stage_logs)
    print_final_output(output)
    
    output_file = f"output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(output.dict(), f, indent=2, default=str)
    console.print(f"[bold green]✅ Detailed output saved to {output_file}[/]")
    return output

def main():
    console.print("[bold cyan]Welcome to the Langie Demo![/]")
    choice = console.input("\n[cyan]Choose: 1-Sample / 2-Custom: [/]") or "1"
    if choice == "2":
        asyncio.run(run_demo())  # You can extend run_custom_demo similarly
    else:
        asyncio.run(run_demo())

if __name__ == "__main__":
    main()
