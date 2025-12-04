#!/usr/bin/env python3
"""Example usage of the Suna Ultra SDK."""

import os
from suna_ultra import SunaClient
from suna_ultra.exceptions import SunaError, AuthenticationError

def main():
    """Demonstrate basic SDK usage."""
    
    # Initialize client (will use SUNA_API_KEY env var if not provided)
    try:
        client = SunaClient(
            api_key=os.getenv("SUNA_API_KEY", "sk-test-key"),
            base_url=os.getenv("SUNA_BASE_URL", "http://localhost:8000")
        )
        print("✓ Client initialized successfully")
    except AuthenticationError as e:
        print(f"✗ Authentication failed: {e.message}")
        return
    
    # Example 1: List agents
    print("\n--- Example 1: List Agents ---")
    try:
        agents = client.agents.list(limit=5)
        print(f"Found {len(agents)} agents:")
        for agent in agents:
            print(f"  - {agent.name} ({agent.agent_id})")
    except SunaError as e:
        print(f"Error listing agents: {e.message}")
    except Exception as e:
        print(f"Connection error (API not running): {type(e).__name__}")
    
    # Example 2: Create an agent (commented out to avoid side effects)
    print("\n--- Example 2: Create Agent (example) ---")
    print("To create an agent:")
    print("""
    agent = client.agents.create(
        name="Research Assistant",
        type="research",
        system_prompt="You are a helpful research assistant.",
        capabilities=["web_search"]
    )
    print(f"Created agent: {agent.agent_id}")
    """)
    
    # Example 3: Submit a task (example)
    print("\n--- Example 3: Submit Task (example) ---")
    print("To submit a task:")
    print("""
    task = client.tasks.submit(
        agent_id="agent-123",
        description="Research AI trends in 2024",
        priority=5
    )
    print(f"Task submitted: {task.id}")
    
    # Wait for completion
    result = client.tasks.wait(task.id, timeout=300)
    print(f"Task completed: {result.output}")
    """)
    
    # Example 4: Stream task events (example)
    print("\n--- Example 4: Stream Task Events (example) ---")
    print("To stream task events:")
    print("""
    for event in client.tasks.stream(task.id):
        print(f"[{event.event}] {event.data}")
    """)
    
    # Example 5: List tools (example)
    print("\n--- Example 5: List Tools (example) ---")
    print("To list available tools:")
    print("""
    tools = client.tools.list()
    for tool in tools:
        print(f"  - {tool.name}: {tool.description}")
    """)
    
    # Close the client
    client.close()
    print("\n✓ Client closed")


if __name__ == "__main__":
    main()
