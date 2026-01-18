import asyncio
from app.core.ai_client import ai_client
from app.core.config import settings

async def main():
    print("🤖 Testing AI connection...\n")
    print(f"Provider: {settings.AI_PROVIDER}")
    print(f"Model: {settings.ai_model}")
    print(f"Base URL: {settings.ai_base_url}\n")
    
    try:
        # Simple test message
        response = await ai_client.chat.completions.create(
            model=settings.ai_model,
            messages=[
                {
                    "role": "user", 
                    "content": "Say 'AI is working!' in exactly 3 words."
                }
            ],
            max_tokens=10,
            temperature=0.7
        )
        
        message = response.choices[0].message.content
        print(f"AI Response: {message}\n")
        print("AI connection successful!")
        print("\nYou're ready to build agents! ")
        
    except Exception as e:
        print(f"Connection failed!")
        print(f"Error: {e}\n")
        print("Troubleshooting:")
        print("1. Check if GROQ_API_KEY is set in .env")
        print("2. Make sure key starts with 'gsk_'")
        print("3. Verify you have internet connection")
        print("4. Try running: pip install openai --upgrade")

if __name__ == "__main__":
    asyncio.run(main())