import asyncio
from sqlalchemy import text
from app.core.database import engine

async def main():
    print("🗑️  Dropping all tables and types...\n")
    
    async with engine.begin() as conn:
        # Drop tables first (in correct order due to foreign keys)
        print("   Dropping tables...")
        await conn.execute(text("DROP TABLE IF EXISTS messages CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS conversations CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS orders CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS payments CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))
        print("   ✅ Tables dropped")
        
        # Drop custom enum types
        print("\n   Dropping enum types...")
        await conn.execute(text("DROP TYPE IF EXISTS messagerole CASCADE"))
        await conn.execute(text("DROP TYPE IF EXISTS agenttype CASCADE"))
        await conn.execute(text("DROP TYPE IF EXISTS conversationstatus CASCADE"))
        await conn.execute(text("DROP TYPE IF EXISTS orderstatus CASCADE"))
        await conn.execute(text("DROP TYPE IF EXISTS paymentstatus CASCADE"))
        print("   ✅ Enum types dropped")
    
    print("\n✅ Database cleaned successfully!")
    print("\nNext steps:")
    print("1. Run: python create_tables.py")
    print("2. Run: python seed_database.py")

if __name__ == "__main__":
    asyncio.run(main())