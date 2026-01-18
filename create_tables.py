import asyncio
from app.core.database import init_db, engine

async def main():
    print("Creating Database ...\n")

    #import all models
    from app.models import User, Conversation, Message, Order, Payment

    #create tables
    await init_db()

    print("\n All tables created successfully!")
    print("\nYou can check tables in pgAdmin:")
    print("- users")
    print("- conversations")
    print("- messages")
    print("- orders")
    print("- payments")

if __name__ == "__main__":
    asyncio.run(main())