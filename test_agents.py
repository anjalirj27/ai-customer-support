import asyncio
from app.core.database import AsyncSessionLocal
from app.services.agent_service import AgentService

async def main():
    print("Testing multi agent system\n")
    print("=*50")

    async with AsyncSessionLocal() as db:
        agent_service = AgentService(db)

        #Test queries
        test_queries = [
            "Where is my order ORD-2024-002?",
            "I want to check invoice INV-2024-004",
            "How do I reset my password?",
            "Cancel order ORD-2024-003"
        ]

        for i, query in enumerate(test_queries, 1):
            print(f"\n{i}. Query: {query}")
            print("-" * 50)

            response = await agent_service.process_message(query)

            print(f"Agent: {response['agent']}")
            print(f"Confidence: {response.get('routing',{}).get('confidence', 'N/A')}")
            print(f"Response: {response['content'][:200]}...")
            if response.get('tool_calls'):
                print(f"Tools Used: {[t['tool'] for t in response['tool_calls']]}")
            print("="*50)


if __name__ == "__main__":
    asyncio.run(main())